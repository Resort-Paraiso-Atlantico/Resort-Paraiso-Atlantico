from sqlalchemy import String, DateTime, Integer, Float,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime
from app.models import Base,Reserva

class Suite(Base):
    __tablename__ = "suites"
    id_suite:  Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True,nullable=False)
    tipo: Mapped[str] = mapped_column(String,nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer,nullable=False)
    valor_diaria: Mapped[float] = mapped_column(Float,nullable=False)
    status: Mapped[str] = mapped_column(String,nullable=False)

    reserva_suites: Mapped[list["ReservaSuite"]] = relationship(back_populates="suite")
    chamados: Mapped[list["Chamado"]] = relationship(back_populates="suite")
    
