from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base


class PedidoItem(Base):
    __tablename__ = "pedido_item"
    id_pedido_item: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedido_compra.id_pedido"))
    id_produto: Mapped[int] = mapped_column(ForeignKey("produto.id_produto"))
    quantidade: Mapped[int] = mapped_column(Integer, nullable = False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable = False)
    valor_total: Mapped[float] = mapped_column(Float, nullable = False)

    pedidoCompra = relationship("PedidoCompra", back_populates = "pedidoItem")
    produto = relationship("Produto", back_populates = "pedidoItem")