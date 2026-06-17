from sqlalchemy import String, DateTime 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 
from datetime import datetime
from Base import Base

#Acharia bom fazer alguma validação em email, telefone e talvez cpf. Mas o chat indica para fazer isso em outra "camada".

class Hospede(Base):
    __tablename__ = "hospedes"
    cpf: Mapped[str] = mapped_column(String(11),primary_key=True)
    nome: Mapped[str] = mapped_column(String(100),nullable=False)
    telefone: Mapped[str] = mapped_column(String(15))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    endereco: Mapped[str] = mapped_column(String(200))
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
