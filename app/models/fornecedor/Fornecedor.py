from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class Fornecedor(Base):
    __tablename__ = "fornecedor"
    cnpj: Mapped[str] = mapped_column(String(14), primary_key = True)
    nome: Mapped[str] = mapped_column(String(100), nullable = False)
    telefone: Mapped[str] = mapped_column(String(15), nullable = False)
    email: Mapped[str] = mapped_column(String(100), unique = True, nullable = False)
    endereco: Mapped[str] = mapped_column(String(200))

    pedidoCompra = relationship("PedidoCompra", back_populates = "fornecedor")