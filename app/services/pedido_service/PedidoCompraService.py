from app.models.pedido.PedidoCompra import PedidoCompra
from app.repositories.pedido_compra_repository.PedidoCompraRepository import PedidoCompraRepository


class PedidoCompraService:

    def __init__(self, db):
        self.repository = PedidoCompraRepository(db)

    def criar_pedido(self, pedido: PedidoCompra) -> PedidoCompra:

        if pedido.cnpj_fornecedor is None:
            raise ValueError("O pedido deve possuir um fornecedor.")

        if not pedido.pedidoItem:
            raise ValueError("O pedido deve possuir pelo menos um item.")

        pedido.status = "PENDENTE"

        pedido.valor_total = sum(
            item.valor_total for item in pedido.pedidoItem
        )

        return self.repository.criar_pedido(pedido)

    def buscar_por_id(self, id_pedido: int) -> PedidoCompra | None:
        return self.repository.buscar_por_id(id_pedido)

    def listar_todos(self) -> list[PedidoCompra]:
        return self.repository.listar_todos()

    def buscar_por_fornecedor(self, cnpj: str):
        return self.repository.buscar_por_fornecedor(cnpj)

    def buscar_por_status(self, status: str):
        return self.repository.buscar_por_status(status)

    def atualizar(self, pedido: PedidoCompra) -> PedidoCompra:
        pedido.valor_total = sum(
            item.valor_total for item in pedido.pedidoItem
        )

        return self.repository.atualizar(pedido)

    def cancelar_pedido(self, id_pedido: int):
        pedido = self.repository.buscar_por_id(id_pedido)

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        if pedido.status == "RECEBIDO":
            raise ValueError("Não é possível cancelar um pedido já recebido.")

        pedido.status = "CANCELADO"

        return self.repository.atualizar(pedido)

    def remover(self, id_pedido: int):
        pedido = self.repository.buscar_por_id(id_pedido)

        if pedido is None:
            raise ValueError("Pedido não encontrado.")

        if pedido.status == "RECEBIDO":
            raise ValueError("Não é permitido remover um pedido já recebido.")

        return self.repository.remover(id_pedido)


    