from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fornecedor.Fornecedor import Fornecedor


class FornecedorRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_fornecedor(self, fornecedor: Fornecedor) -> Fornecedor:
        self.session.add(fornecedor)
        self.session.commit()
        self.session.refresh(fornecedor)
        return fornecedor
    
    def buscar_por_cnpj(self, cnpj: str) -> Fornecedor | None:
        return self.session.get(Fornecedor, cnpj)
    
    def buscar_por_nome(self, nome: str) -> Fornecedor | None:
        stmt = select(Fornecedor).where(Fornecedor.nome == nome)
        return self.session.execute(stmt).scalar_one_or_none
    
    def listar_todos(self) -> list[Fornecedor]:
        stmt = select(Fornecedor)
        return list(self.session.execute(stmt).scalars().all())
    
    def atualizar(self, fornecedor: Fornecedor) -> Fornecedor:
        fornecedor_gerenciado = self.session.merge(fornecedor)
        self.session.commit()
        return fornecedor_gerenciado
    
    def remover(self, cnpj: str) -> bool:
        fornecedor = self.buscar_por_cnpj(cnpj)
        if fornecedor is None:
            return False
        self.session.delete(fornecedor)
        self.session.commit()
        return True