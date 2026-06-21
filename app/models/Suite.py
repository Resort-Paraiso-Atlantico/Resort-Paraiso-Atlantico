from models import Base
from sqlalchemy import String, DateTime, Integer, Float,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime
from models import Base

class Suite(Base):
    __tablename__ = "suites"
    id_suite:  Mapped[int] = mapped_column(Integer,primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True) ## não seria bom colocar o numero da suite como seu ID?
    id_reserva: Mapped[int] = mapped_column(Integer,ForeignKey("reservas.id_reserva"))
    tipo: Mapped[str] = mapped_column(String)
    capacidade: Mapped[int] = mapped_column(Integer)
    valor_diaria: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String)

    reserva: Mapped["Reserva"] = relationship(back_populates="suites")