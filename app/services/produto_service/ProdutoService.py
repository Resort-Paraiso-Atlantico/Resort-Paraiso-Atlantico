from sqlalchemy.orm import Session

from app.models.produto.Produto import Produto
from app.repositories.produto_repository.ProdutoRepository import ProdutoRepository


class ProdutoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProdutoRepository(db)

    def criar_produto(
        self,
        nome: str,
        categoria: str,
        estoque_minimo: int,
        valor_unitario: float
    ):
        if estoque_minimo <= 0:
            raise ValueError("A quantidade do estoque minimo deve ser superior a 0.")
        if valor_unitario <= 0:
            raise ValueError("O preço unitário do produto deve ser superior a 0.")

        produto = Produto(
            nome = nome,
            categoria = categoria,
            quantidade = 0,
            estoque_minimo = estoque_minimo,
            valor_unitario = valor_unitario
        )
        return self.repository.criar_produto(produto)

    def buscar_por_id_produto(self, id_produto: int):
        if not id_produto:
            raise ValueError("Id vazio.")
        return self.repository.buscar_por_id_produto(id_produto)

    def buscar_por_nome(self, nome: str):
        if not nome:
            raise ValueError("Nome vazio.")
        return self.repository.buscar_por_nome(nome)

    def listar_todos(self):
        return self.repository.listar_todos()

    def atualizar_produto(
        self,
        id_produto: int,
        nome: str,
        categoria: str,
        quantidade: int,
        estoque_minimo: int,
        valor_unitario: int
    ) -> Produto:
        produto = self.repository.buscar_por_id_produto(id_produto)

        if produto is None:
            raise ValueError("Produto não encontrado.")
        if quantidade < 0:
            raise ValueError("quantidade deve ser um valor positivo")
        if estoque_minimo <= 0:
            raise ValueError("A quantidade do estoque minimo deve ser superior a 0.")
        if valor_unitario <= 0:
            raise ValueError("O preço unitário do produto deve ser superior a 0.")
        
        produto.nome = nome
        produto.categoria = categoria
        produto.quantidade = quantidade
        produto.estoque_minimo = estoque_minimo
        produto.valor_unitario = valor_unitario
        return self.repository.atualizar(produto)

    def remover_produto(self, id_produto: int):
        if not id_produto:
            raise ValueError("Id inválido.")

        produto = self.repository.buscar_por_id_produto(id_produto)
        if produto is None:
            raise ValueError("Produto não encontrado.")

        removido = self.repository.remover(id_produto)
        if removido is None:
            raise ValueError("Produto não encontrado.")