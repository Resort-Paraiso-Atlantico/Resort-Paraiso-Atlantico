from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produto.Produto import Produto


class ProdutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_produto(self, produto: Produto) -> Produto:
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto
    
    def buscar_por_id_produto(self, id_produto: int) -> Produto | None:
        return self.session.get(Produto, id_produto)
    
    def buscar_por_nome(self, nome: str) -> Produto | None:
        stmt = select(Produto).where(Produto.nome == nome)
        return self.session.execute(stmt).scalar_one_or_none
    
    def buscar_por_categoria(self, categoria: str) -> Produto | None:
        stmt = select(Produto).where(Produto.categoria == categoria)
        return self.session.execute(stmt).scalar_one_or_none
    
    def listar_todos(self) -> list[Produto]:
        stmt = select(Produto)
        return list(self.session.execute(stmt).scalars().all())
    
    def atualizar(self, fornecedor: Produto) -> Produto:
        produto_gerenciado = self.session.merge(fornecedor)
        self.session.commit()
        return produto_gerenciado
    
    def remover(self, id_produto: str) -> bool:
        produto = self.buscar_por_id_produto(id_produto)
        if produto is None:
            return False
        self.session.delete(produto)
        self.session.commit()
        return True