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
        valor_unitario: float,
        preco_venda: float = 0.0,
        estoque_maximo: int = 0,
        ponto_reposicao: int = 0,
        lead_time: int = 0
    ):
        if estoque_minimo <= 0:
            raise ValueError("A quantidade do estoque minimo deve ser superior a 0.")
        if valor_unitario <= 0:
            raise ValueError("O preço unitário do produto deve ser superior a 0.")
        if preco_venda <= 0:
            raise ValueError("O preço de venda do produto deve ser superior a 0.")
        if estoque_maximo < estoque_minimo:
            raise ValueError("O estoque máximo deve ser maior ou igual ao estoque mínimo.")
        if ponto_reposicao < 0:
            raise ValueError("O ponto de reposição deve ser maior ou igual a 0.")
        if lead_time < 0:
            raise ValueError("O lead time deve ser maior ou igual a 0.")

        cat_formatada = categoria.strip().title() if categoria else ""
        produto = Produto(
            nome = nome,
            categoria = cat_formatada,
            quantidade = 0,
            estoque_minimo = estoque_minimo,
            valor_unitario = valor_unitario,
            preco_venda = preco_venda,
            estoque_maximo = estoque_maximo,
            ponto_reposicao = ponto_reposicao,
            lead_time = lead_time
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
        quantidade: int,
        estoque_minimo: int,
        valor_unitario: float,
        categoria: str = "",
        preco_venda: float = 0.0,
        estoque_maximo: int = 0,
        ponto_reposicao: int = 0,
        lead_time: int = 0
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
        if preco_venda <= 0:
            raise ValueError("O preço de venda do produto deve ser superior a 0.")
        if estoque_maximo < estoque_minimo:
            raise ValueError("O estoque máximo deve ser maior ou igual ao estoque mínimo.")
        if ponto_reposicao < 0:
            raise ValueError("O ponto de reposição deve ser maior ou igual a 0.")
        if lead_time < 0:
            raise ValueError("O lead time deve ser maior ou igual a 0.")

        produto.nome = nome
        if categoria:
            produto.categoria = categoria.strip().title()
        produto.quantidade = quantidade
        produto.estoque_minimo = estoque_minimo
        produto.valor_unitario = valor_unitario
        produto.preco_venda = preco_venda
        produto.estoque_maximo = estoque_maximo
        produto.ponto_reposicao = ponto_reposicao
        produto.lead_time = lead_time
        return self.repository.atualizar(produto)

    def remover_produto(self, id_produto: int):
        if not id_produto:
            raise ValueError("Id inválido.")

        produto = self.repository.buscar_por_id_produto(id_produto)
        if produto is None:
            raise ValueError("Produto não encontrado.")

        if produto.pedidoItem:
            pedidos_ativos = [
                item.pedidoCompra for item in produto.pedidoItem
                if item.pedidoCompra and item.pedidoCompra.status != "CANCELADO"
            ]
            if pedidos_ativos:
                statuses = set(p.status for p in pedidos_ativos if p.status)
                status_str = ", ".join(statuses) if statuses else "ATIVO"
                raise ValueError(
                    f"Não é possível excluir o produto '{produto.nome}' pois ele está vinculado a um ou mais Pedidos de Compra ativos (Status: {status_str})."
                )

        removido = self.repository.remover(id_produto)
        if removido is None:
            raise ValueError("Produto não encontrado.")