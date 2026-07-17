from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Hospede import Hospede


class HospedeRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, hospede: Hospede) -> Hospede:
        self.session.add(hospede)
        self.session.commit()
        self.session.refresh(hospede)
        return hospede

    def buscar_por_cpf(self, cpf: str) -> Hospede | None:
        return self.session.get(Hospede, cpf)

    def buscar_por_email(self, email: str) -> Hospede | None:
        stmt = select(Hospede).where(Hospede.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def listar_todos(self) -> list[Hospede]:
        stmt = select(Hospede)
        return list(self.session.execute(stmt).scalars().all())

    def atualizar(self, hospede: Hospede) -> Hospede:
        hospede_gerenciado = self.session.merge(hospede)
        self.session.commit()
        return hospede_gerenciado

    def remover(self, cpf: str) -> bool:
        hospede = self.buscar_por_cpf(cpf)
        if hospede is None:
            return False
        self.session.delete(hospede)
        self.session.commit()
        return True