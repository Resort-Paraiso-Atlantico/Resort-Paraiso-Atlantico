from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Base import Base


class PedidoCompra(Base):
    __tablename__ = "pedido_compra"
    id_pedido: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    cnpj_fornecedor: Mapped[str] = mapped_column(ForeignKey("fornecedor.cnpj"))
    data_pedido: Mapped[date] = mapped_column(Date, nullable = False)
    valor_total: Mapped[float] = mapped_column(Float, nullable = False)
    status: Mapped[str] = mapped_column(String(20), nullable = False)

    fornecedor = relationship("Fornecedor", back_populates = "pedidoCompra")
    pedidoItem = relationship("PedidoItem", uselist = False, back_populates = "pedidoCompra")