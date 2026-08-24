from datetime import date
from sqlalchemy.orm import Session
from app.models.Reserva import Reserva
from app.repositories.ReservaRepository import ReservaRepository
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository
from app.repositories.SuiteRepository import SuiteRepository
from app.services.ChamadoService import ChamadoService
import random


class ReservaService:

    #fazendo o repository
    def __init__(self, db: Session):
        self.repository = ReservaRepository(db)
        self.reserva_suite_repository = ReservaSuiteRepository(db)
        self.suite_repository = SuiteRepository(db)
        self.chamado_service = ChamadoService(db)
        

    def criar_reserva(
        self,
        cpf_hospede: str,
        checkin_previsto: date,
        checkout_previsto: date,
        status: str = "Pendente"):
        if checkin_previsto >= checkout_previsto:
            raise ValueError("A data de check-in deve ser anterior ao check-out.")

        reserva = Reserva(
            cpf_hospede=cpf_hospede,
            data_reserva=date.today(),
            checkin_previsto=checkin_previsto,
            checkout_previsto=checkout_previsto,
            status=status,
        )
        return self.repository.criar(reserva)

    def listar_reservas(self) -> list[Reserva]:
        return self.repository.listar_todas()

    def buscar_por_cpf(self, cpf: str) -> list[Reserva]:
        return self.repository.buscar_por_cpf(cpf)

    def buscar_por_id(self, id_reserva: int) -> Reserva | None:
        return self.repository.buscar_por_id(id_reserva)

    def cancelar_reserva(self, id_reserva: int) -> Reserva:
        reserva = self.repository.buscar_por_id(id_reserva)
        if not reserva:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")
        if reserva.status == "Cancelada":
            raise ValueError("Reserva já está cancelada.")
        if reserva.status == "Finalizada":
            raise ValueError("Não é possível cancelar uma reserva já finalizada.")
        reserva.status = "Cancelada"
        return self.repository.atualizar(reserva)

    def definir_valor_total(self, id_reserva: int, valor_total: float) -> Reserva:
        reserva = self.repository.buscar_por_id(id_reserva)
        if reserva is None:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")
        if valor_total < 0:
            raise ValueError("O valor total não pode ser negativo.")
        reserva.valor_total = valor_total
        return self.repository.atualizar(reserva)

    def atualizar_status_pagamento(self, id_reserva: int, novo_status: str) -> Reserva:
        """
        Alterna manualmente entre 'Pendente' e 'Confirmada' — o gatilho do
        módulo Financeiro até ele existir de verdade. Não permite pular
        direto para 'Hospedado'/'Finalizada' (isso só pode acontecer via
        check-in/check-out) nem mexer numa reserva já cancelada/finalizada.
        """
        if novo_status not in ("Pendente", "Confirmada"):
            raise ValueError(
                "Só é permitido alternar manualmente entre 'Pendente' e 'Confirmada'."
            )

        reserva = self.repository.buscar_por_id(id_reserva)
        if not reserva:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")

        if reserva.status not in ("Pendente", "Confirmada"):
            raise ValueError(
                f"Não é possível alterar manualmente uma reserva com status '{reserva.status}'."
            )

        reserva.status = novo_status
        return self.repository.atualizar(reserva)

    def fazer_checkin(self, id_reserva: int, usuario: str) -> tuple[Reserva, str | None]:
        """
        Regra do documento: check-in só pode ocorrer após confirmação financeira.
        Por enquanto usamos o status "Confirmada" da própria reserva como sinal
        dessa confirmação (ainda não existe módulo Financeiro separado).

        Regra de data: não é permitido check-in antes da data prevista.
        Check-in em atraso é permitido, mas retorna um aviso.

        Retorna uma tupla (reserva_atualizada, aviso_ou_None).
        """
        reserva = self.repository.buscar_por_id(id_reserva)
        if not reserva:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")

        if reserva.status != "Confirmada":
            raise ValueError(
                f"Não é possível fazer check-in: reserva está com status "
                f"'{reserva.status}'. É necessário confirmar o pagamento antes."
            )

        hoje = date.today()

        vinculos_ativos = [
            v for v in self.reserva_suite_repository.listar_por_reserva(id_reserva)
            if v.data_saida is None or v.data_saida >= hoje
        ]
        if not vinculos_ativos:
            raise ValueError(
                "Não é possível fazer check-in: nenhuma suíte vinculada a esta reserva."
            )

        aviso = None

        if reserva.checkin_previsto and hoje < reserva.checkin_previsto:
            raise ValueError(
                f"Não é possível fazer check-in antes da data prevista "
                f"({reserva.checkin_previsto.strftime('%d/%m/%Y')})."
            )

        if reserva.checkin_previsto and hoje > reserva.checkin_previsto:
            dias_atraso = (hoje - reserva.checkin_previsto).days
            aviso = (
                f"Check-in realizado com {dias_atraso} dia(s) de atraso "
                f"em relação à data prevista ({reserva.checkin_previsto.strftime('%d/%m/%Y')})."
            )

        reserva.status = "Hospedado"
        reserva.checkin_realizado = hoje
        reserva.checkin_por = usuario
        reserva = self.repository.atualizar(reserva)

        return reserva, aviso

    def fazer_checkout(self, id_reserva: int, usuario: str) -> Reserva:
        """
        Regra do documento: check-out só pode ocorrer após a quitação da conta
        e libera a(s) suíte(s) para a Governança (limpeza). Aqui já marcamos a
        suíte como "Disponível" novamente e encerra os vínculos ativos
        (data_saida) — diferente do botão "Desvincular" manual, que só encerra
        um vínculo específico sem finalizar a reserva inteira.
        """
        reserva = self.repository.buscar_por_id(id_reserva)
        if not reserva:
            raise ValueError(f"Reserva #{id_reserva} não encontrada.")

        if reserva.status != "Hospedado":
            raise ValueError(
                f"Não é possível fazer check-out: reserva está com status '{reserva.status}'."
            )

        hoje = date.today()

        vinculos_ativos = [
            v for v in self.reserva_suite_repository.listar_por_reserva(id_reserva)
            if v.data_saida is None or v.data_saida >= hoje
        ]

        for vinculo in vinculos_ativos:
            vinculo.data_saida = hoje
            self.reserva_suite_repository.atualizar(vinculo)

            suite = vinculo.suite or self.suite_repository.buscar_por_id(vinculo.id_suite)
            self.suite_repository.atualizar(suite)

            # Ao liberar a suíte, abre chamado automático de limpeza (95%) ou manutenção (5%)
            tipo_chamado = "Manutenção" if random.random() < 0.05 else "Limpeza"
            if tipo_chamado == "Manutenção":
                descricao = "Verificação de manutenção solicitada automaticamente após check-out."
                prioridade = "Média"
            else:
                descricao = "Limpeza de rotina solicitada automaticamente após check-out."
                prioridade = "Baixa"

            self.chamado_service.abrir_chamado(
                id_suite=vinculo.id_suite,
                tipo=tipo_chamado,
                prioridade=prioridade,
                descricao=descricao,
            )

        reserva.status = "Finalizada"
        reserva.checkout_realizado = hoje
        reserva.checkout_por = usuario
        return self.repository.atualizar(reserva)