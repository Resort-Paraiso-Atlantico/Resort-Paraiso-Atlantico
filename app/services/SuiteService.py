from datetime import date, datetime

from app.models import Suite

from sqlalchemy.orm import Session
from app.repositories.SuiteRepository import SuiteRepository
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository

class SuiteService:

    #fazendo o repository
    def __init__(self, db: Session):
        self.repository = SuiteRepository(db)
        self.reserva_suite_repository = ReservaSuiteRepository(db)

    def criar_suite(self,numero: int ,tipo: str , capacidade:int,valor_diaria: float,status: str):

        if capacidade <= 0: raise ValueError("Capacidade deve ser no minimo 1.")

        if valor_diaria <= 0: raise ValueError("Valor da diaria deve ser no minimo 1.")
        if self.repository.buscar_por_numero(numero):
            raise ValueError(
                f"A suíte número {numero} já está cadastrada."
            )
        
        suite = Suite(
        numero= numero,
        tipo=tipo,
        capacidade=capacidade,
        valor_diaria=valor_diaria,
        status=status,
        ultima_limpeza=datetime.now(),
        )
        
        return self.repository.criar(suite)
        
    def listar_suites(self):
        return self.repository.listar_todas()
    
    def alterar_status(self, id_suite: int, novo_status: str) -> Suite:
        status_validos = ("Disponível", "Limpeza", "Manutenção")
        if novo_status not in status_validos:
            raise ValueError(f"Status inválido. Escolha um entre: {', '.join(status_validos)}.")
        
        suite = self.repository.buscar_por_id(id_suite)
        if suite is None:
            raise ValueError("Suíte não encontrada")
        
        suite.status = novo_status
        if novo_status == "Disponível" and suite.status == "Limpeza":
            suite.ultima_limpeza = datetime.now()
            
        return self.repository.atualizar(suite)

    def deixar_disponivel(self, id_suite: int) -> Suite:
        suite = self.repository.buscar_por_id(id_suite)
        if suite is None:
            raise ValueError("Suíte não encontrada")

        suite.status = "Disponível"
        return self.repository.atualizar(suite)

    def colocar_em_manutencao(self, id_suite: int) -> Suite:
        suite = self.repository.buscar_por_id(id_suite)
        if suite is None:
            raise ValueError("Suíte não encontrada")
        suite.status = "Manutenção"
        return self.repository.atualizar(suite)

    def colocar_em_limpeza(self, id_suite: int) -> Suite:
        suite = self.repository.buscar_por_id(id_suite)
        if suite is None:
            raise ValueError("Suíte não encontrada")
        suite.status = "Limpeza"
        return self.repository.atualizar(suite)

    def registrar_limpeza(self, id_suite: int) -> Suite:
        suite = self.repository.buscar_por_id(id_suite)
        if suite is None:
            raise ValueError("Suíte não encontrada")
        suite.ultima_limpeza = datetime.now()
        suite.status = "Disponível"
        return self.repository.atualizar(suite)

    def listar_disponiveis_no_periodo(self, data_entrada: date, data_saida: date) -> list[Suite]:
        suites = self.repository.listar_todas()
        return [
            s for s in suites
            if s.status not in ("Manutenção", "Limpeza")
            and not self.reserva_suite_repository.existe_conflito(s.id_suite, data_entrada, data_saida)
        ]