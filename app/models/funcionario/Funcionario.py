from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.models.Base import Base


class Funcionario(Base):
    __tablename__ = "funcionario"
    cpf_funcionario: Mapped[str] = mapped_column(String(9), primary_key = True)
    nome: Mapped[str] = mapped_column(String(100), nullable = False)
    telefone: Mapped[str] = mapped_column(String(15), nullable = False)
    email: Mapped[str] = mapped_column(String(100), nullable = False)
    cargo: Mapped[str] = mapped_column(String(50), nullable = False)
    salario: Mapped[float] = mapped_column(Float, nullable = False)

    ##ordemServico = relationship("OrdemServico", back_populates = "funcionario")