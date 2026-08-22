from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.funcionario.Funcionario import Funcionario

class FuncionarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_funcionario(self, funcionario: Funcionario) -> Funcionario:
        self.session.add(funcionario)
        self.session.commit()
        self.session.refresh(funcionario)
        return funcionario

    def buscar_por_cpf(self, cpf: str) -> Funcionario | None:
        return self.session.get(Funcionario, cpf)

    def listar_todos(self) -> list[Funcionario]:
        stmt = select(Funcionario)
        return list(self.session.execute(stmt).scalars().all())

    def atualizar(self, funcionario: Funcionario) -> Funcionario:
        funcionario_gerenciado = self.session.merge(funcionario)
        self.session.commit()
        return funcionario_gerenciado

    def remover(self, cpf: str) -> bool:
        funcionario = self.buscar_por_cpf(cpf)
        if funcionario is None:
            return False
        self.session.delete(funcionario)
        self.session.commit()
        return True