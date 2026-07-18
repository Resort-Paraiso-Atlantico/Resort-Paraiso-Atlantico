from app.models import Suite,Reserva,ReservaSuite

from datetime import date
from sqlalchemy.orm import Session
from app.repositories.SuiteRepository import SuiteRepository
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository

class ReservaSuiteService:

    def __init__(self, db: Session):
        self.repository = ReservaSuiteRepository(db)
        self.suite_repository = SuiteRepository(db)

    def vincular_reserva_suite(self,id_reserva:int,id_suite:int,data_entrada:date):
        if id_reserva is None:
            raise ValueError("Deve ter id da reserva.")
        
        if id_suite is None:
            raise ValueError("Deve ter id da suite.")
        
        suite = self.suite_repository.buscar_por_id(id_suite)
        if not suite:
            raise ValueError(f"Suíte #{id_suite} não encontrada.")
        
        if suite.status != "Disponível":
            raise ValueError("Suite não está disponivel.")
        
        suite.status = "Ocupada"
        self.suite_repository.atualizar(suite)

        reserva_suite = ReservaSuite(
            id_reserva = id_reserva,
            id_suite = id_suite,
            data_entrada = data_entrada,
            valor_diaria=suite.valor_diaria

        )

        return self.repository.criar(reserva_suite)
    
    #ver todas as suites de uma reserva
    def listar_por_reserva(self,id_reserva:int):
        if id_reserva is None:
            raise ValueError("Deve ter id da reserva.")

        return self.repository.listar_por_reserva(id_reserva)
        
    #ver todas as reservas que ja tiveram essa suite
    def listar_por_suite(self,id_suite:int):
        if id_suite is None:
            raise ValueError("Deve ter id da suite.")
        
        return self.repository.listar_por_suite(id_suite)
    
    def registrar_saida(self, id: int, data_saida: date) -> ReservaSuite:
        reserva_suite = self.repository.buscar_por_id(id)

        if reserva_suite is None:
            raise ValueError("Vínculo Reserva-Suite não encontrado.")

        if reserva_suite.data_saida is not None:
            raise ValueError("Essa estadia já foi encerrada.")

        if data_saida < reserva_suite.data_entrada:
            raise ValueError("Data de saída não pode ser anterior à data de entrada.")

        reserva_suite.data_saida = data_saida
        reserva_suite = self.repository.atualizar(reserva_suite)

        # Libera a suíte de volta para uso em outras reservas
        suite = self.suite_repository.buscar_por_id(reserva_suite.id_suite)
        if suite:
            suite.status = "Disponível"
            self.suite_repository.atualizar(suite)

        return reserva_suite
    
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

        reserva_suite.data_entrada = nova_data_entrada
        return self.repository.atualizar(reserva_suite)