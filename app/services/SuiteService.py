from app.models.Suite import Suite

from datetime import date
from sqlalchemy.orm import Session
from app.repositories.SuiteRepository import SuiteRepository

class SuiteService:

    #fazendo o repository
    def __init__(self, db: Session):
        self.repository = SuiteRepository(db)

    def criar_suite(self,numero: int ,tipo: str , capacidade:int,valor_diaria: float,status: str):

        if capacidade <= 0: raise ValueError("Capacidade deve ser no minimo 1.")
        if valor_diaria <= 0: raise ValueError("Valor da diaria deve ser no minimo 1.")


        
        suite = Suite(
        numero= numero,
        tipo=tipo,
        capacidade=capacidade,
        valor_diaria=valor_diaria,
        status=status,
        )

        return self.repository.criar(suite)
        
    def listar_suites(self):
        return self.repository.listar_todas()