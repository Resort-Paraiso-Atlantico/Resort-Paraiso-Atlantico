from sqlalchemy import String, DateTime 
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime
from app.models import Base

class Hospede(Base):
    __tablename__ = "hospedes"
    cpf: Mapped[str] = mapped_column(String(11),primary_key=True)
    nome: Mapped[str] = mapped_column(String(100),nullable=False)
    telefone: Mapped[str] = mapped_column(String(15),nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True,nullable=False)
    endereco: Mapped[str] = mapped_column(String(200))
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    reservas = relationship("Reserva", back_populates="hospede")

    hospede_evento: Mapped[list["HospedeEvento"]] = relationship(back_populates="hospede")
