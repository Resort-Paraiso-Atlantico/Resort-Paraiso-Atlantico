from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.pedido.PedidoCompra import PedidoCompra
from app.models.pedido.PedidoItem import PedidoItem


class PedidoCompraRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_pedido(self, pedido: PedidoCompra) -> PedidoCompra:
        self.session.add(pedido)
        self.session.commit()
        self.session.refresh(pedido)
        return self.buscar_por_id(pedido.id_pedido) or pedido

    def buscar_por_id(self, id_pedido: int) -> PedidoCompra | None:
        stmt = (
            select(PedidoCompra)
            .options(
                joinedload(PedidoCompra.pedidoItem).joinedload(PedidoItem.produto)
            )
            .where(PedidoCompra.id_pedido == id_pedido)
        )
        return self.session.execute(stmt).scalars().first()

    def listar_todos(self) -> list[PedidoCompra]:
        stmt = (
            select(PedidoCompra)
            .options(
                joinedload(PedidoCompra.pedidoItem).joinedload(PedidoItem.produto)
            )
            .order_by(PedidoCompra.id_pedido.desc())
        )
        return list(self.session.execute(stmt).unique().scalars().all())

    def buscar_por_fornecedor(self, cnpj_fornecedor: str) -> list[PedidoCompra]:
        stmt = (
            select(PedidoCompra)
            .options(
                joinedload(PedidoCompra.pedidoItem).joinedload(PedidoItem.produto)
            )
            .where(PedidoCompra.cnpj_fornecedor == cnpj_fornecedor)
            .order_by(PedidoCompra.id_pedido.desc())
        )
        return list(self.session.execute(stmt).unique().scalars().all())

    def buscar_por_status(self, status: str) -> list[PedidoCompra]:
        stmt = (
            select(PedidoCompra)
            .options(
                joinedload(PedidoCompra.pedidoItem).joinedload(PedidoItem.produto)
            )
            .where(PedidoCompra.status == status)
            .order_by(PedidoCompra.id_pedido.desc())
        )
        return list(self.session.execute(stmt).unique().scalars().all())

    def atualizar(self, pedido: PedidoCompra) -> PedidoCompra:
        pedido_gerenciado = self.session.merge(pedido)
        self.session.commit()
        return self.buscar_por_id(pedido_gerenciado.id_pedido) or pedido_gerenciado

    def remover(self, id_pedido: int) -> bool:
        pedido = self.buscar_por_id(id_pedido)
        if pedido is None:
            return False
        self.session.delete(pedido)
        self.session.commit()
        return True