from app.repositories.pedido_compra_repository.PedidoCompraRepository import PedidoCompraRepository
from app.repositories.produto_repository.ProdutoRepository import ProdutoRepository



class EstoqueService:

    def __init__(self, db):
        self.produto_repository = ProdutoRepository(db)
        self.pedido_repository = PedidoCompraRepository(db)


    def consultar_produto(self, id_produto: int):
        return self.produto_repository.buscar_por_id_produto(id_produto)

    def listar_produtos(self):
        return self.produto_repository.listar_todos()

    def produtos_abaixo_minimo(self):
        produtos = self.produto_repository.listar_todos()

        return [
            produto
            for produto in produtos
            if produto.quantidade <= produto.estoque_minimo
        ]

    def registrar_entrada(self, id_produto: int, quantidade: int):
        if quantidade <= 0:
            raise ValueError("Quantidade inválida.")

        produto = self.produto_repository.buscar_por_id_produto(id_produto)

        if produto is None:
            raise ValueError("Produto não encontrado.")

        produto.quantidade += quantidade

        return self.produto_repository.atualizar(produto)

    def registrar_saida(self, id_produto: int, quantidade: int):
        if quantidade <= 0:
            raise ValueError("Quantidade inválida.")

        produto = self.produto_repository.buscar_por_id_produto(id_produto)

        if produto is None:
            raise ValueError("Produto não encontrado.")

        if produto.quantidade < quantidade:
            raise ValueError("Estoque Insuficiente.")

        produto.quantidade -= quantidade

        return self.produto_repository.atualizar(produto)

    def receber_pedido(self, id_pedido: int):
        pedido = self.pedido_repository.buscar_por_id(id_pedido)

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        if pedido.status == "RECEBIDO":
            raise ValueError("Pedido já recebido.")

        if pedido.status == "CANCELADO":
            raise ValueError("Pedido cancelado.")

        for item in pedido.pedidoItem:
            produto = self.produto_repository.buscar_por_id_produto(item.id_produto)

            if produto is None:
                raise ValueError(f"Produto {item.id_produto} não encontrado.")

            produto.quantidade += item.quantidade

            self.produto_repository.atualizar(produto)

        pedido.status = "RECEBIDO"

        self.pedido_repository.atualizar(pedido)

        return pedido