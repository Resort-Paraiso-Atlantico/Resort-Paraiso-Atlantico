from app.models import Suite,Reserva,ReservaSuite

from datetime import date
from sqlalchemy.orm import Session
from app.repositories.SuiteRepository import SuiteRepository
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository
from app.repositories.ReservaRepository import ReservaRepository

class ReservaSuiteService:

    def __init__(self, db: Session):
        self.repository = ReservaSuiteRepository(db)
        self.suite_repository = SuiteRepository(db)
        self.reserva_repository = ReservaRepository(db)

    def vincular_reserva_suite(self,id_reserva:int,id_suite:int,data_entrada:date,data_saida:date):
        if id_reserva is None:
            raise ValueError("Deve ter id da reserva.")

        reserva = self.reserva_repository.buscar_por_id(id_reserva)
        if  reserva == None:
            raise ValueError("Reserva não Encontrada.")
        if reserva.status == "Finalizada":
            raise ValueError("Reserva não pode estar finalizada.")
        
        if data_saida is not None:
            if data_entrada > data_saida:
                raise ValueError("A data de entrada não pode ser depois da data de saida.")
        
        if id_suite is None:
            raise ValueError("Deve ter id da suite.")
        
        suite = self.suite_repository.buscar_por_id(id_suite)
        if not suite:
            raise ValueError(f"Suíte #{id_suite} não encontrada.")

        if suite.status == "Manutenção":
            raise ValueError("Suíte está em manutenção.")
        if suite.status == "Limpeza":
            raise ValueError("Suíte está em processo de limpeza.")

        if self.repository.existe_conflito(id_suite, data_entrada, data_saida):
            raise ValueError("Suíte já está ocupada nesse período.")

        reserva_suite = ReservaSuite(
            id_reserva = id_reserva,
            id_suite = id_suite,
            data_entrada = data_entrada,
            valor_diaria=suite.valor_diaria,
            data_saida= data_saida

        )

        return self.repository.criar(reserva_suite)
    
    #ver todas as suites de uma reserva
    def listar_por_reserva(self,id_reserva:int):
        if id_reserva is None:
            raise ValueError("Deve ter id da reserva.")

        return self.repository.listar_por_reserva(id_reserva)
    
    def calcular_valor_estadia(self, id: int) -> float:
        reserva_suite = self.repository.buscar_por_id(id)

        if reserva_suite is None:
            raise ValueError("Vínculo Reserva-Suite não encontrado.")

        data_final = reserva_suite.data_saida or date.today()

        diarias = (data_final - reserva_suite.data_entrada).days

        if diarias <= 0:
            diarias = 1

        return diarias * reserva_suite.valor_diaria

    def calcular_valor_total_reserva(self, id_reserva: int) -> float:
        """Soma o valor de todas as suítes (vínculos) já ligadas a uma reserva."""
        if id_reserva is None:
            raise ValueError("Deve ter id da reserva.")

        vinculos = self.repository.listar_por_reserva(id_reserva)
        if not vinculos:
            raise ValueError(f"Nenhuma suíte vinculada à reserva #{id_reserva}.")

        return sum(self.calcular_valor_estadia(v.id) for v in vinculos)

    def corrigir_data_entrada(self, id: int, nova_data_entrada: date) -> ReservaSuite:
        """Corrige a data de entrada de um vínculo (ex: erro de digitação)."""
        reserva_suite = self.repository.buscar_por_id(id)

        if reserva_suite is None:
            raise ValueError("Vínculo Reserva-Suite não encontrado.")

        if reserva_suite.data_saida is not None and nova_data_entrada > reserva_suite.data_saida:
            raise ValueError("Data de entrada não pode ser posterior à data de saída já registrada.")

        if self.repository.existe_conflito(
            reserva_suite.id_suite, nova_data_entrada, reserva_suite.data_saida, excluir_id=id
        ):
            raise ValueError("Suíte já está ocupada nesse período.")

        reserva_suite.data_entrada = nova_data_entrada
        return self.repository.atualizar(reserva_suite)

    def listar_por_suite(self, id_suite: int):
        if id_suite is None:
            raise ValueError("Deve ter id da suite.")

        return self.repository.listar_por_suite(id_suite)