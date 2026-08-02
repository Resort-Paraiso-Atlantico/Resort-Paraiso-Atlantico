from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pedido.PedidoCompra import PedidoCompra


class PedidoCompraRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_pedido(self, pedido: PedidoCompra) -> PedidoCompra:
        self.session.add(pedido)
        self.session.commit()
        self.session.refresh(pedido)
        return pedido

    def buscar_por_id(self, id_pedido: int) -> PedidoCompra | None:
        return self.session.get(PedidoCompra, id_pedido)

    def listar_todos(self) -> list[PedidoCompra]:
        stmt = select(PedidoCompra)
        return list(self.session.execute(stmt).scalars().all())

    def buscar_por_fornecedor(self, cnpj_fornecedor: str) -> list[PedidoCompra]:
        stmt = (
            select(PedidoCompra)
            .where(PedidoCompra.cnpj_fornecedor == cnpj_fornecedor)
        )

        return list(self.session.execute(stmt).scalars().all())

    def buscar_por_status(self, status: str) -> list[PedidoCompra]:
        stmt = (
            select(PedidoCompra)
            .where(PedidoCompra.status == status)
        )

        return list(self.session.execute(stmt).scalars().all())

    def atualizar(self, pedido: PedidoCompra) -> PedidoCompra:
        pedido_gerenciado = self.session.merge(pedido)
        self.session.commit()
        return pedido_gerenciado

    def remover(self, id_pedido: int) -> bool:
        pedido = self.buscar_por_id(id_pedido)

        if pedido is None:
            return False

        self.session.delete(pedido)
        self.session.commit()

        return True