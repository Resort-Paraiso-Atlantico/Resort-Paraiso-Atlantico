from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

class Produto(Base):
    __tablename__ = "produto"
    id_produto: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement= True)
    nome: Mapped[str] = mapped_column(String(100), nullable = False)
    categoria: Mapped[str] = mapped_column(String(100), nullable = False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable = False)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable = False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable = False)

    produto = relationship("Produto", back_populates = "pedido_Item")