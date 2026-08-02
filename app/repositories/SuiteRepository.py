from sqlalchemy.orm import Session
from app.models.Suite import Suite


class SuiteRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def criar(self, suite:Suite):
        self.db.add(suite)
        self.db.commit()
        self.db.refresh(suite)
        return suite

    def listar_todas(self):
        return self.db.query(Suite).all()
    
    def buscar_por_id(self, id_suite: int) -> Suite | None:
        return self.db.get(Suite, id_suite)
    
    def atualizar(self, suite: Suite) -> Suite:
        self.db.commit()
        self.db.refresh(suite)
        return suite

    def buscar_por_numero(self, numero: int) -> Suite | None:
        return self.db.query(Suite)\
            .filter(Suite.numero == numero)\
            .first()