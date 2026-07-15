from sqlalchemy import Date, Float, Integer, String, DateTime 
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.orm import Mapped, mapped_column 
from datetime import date, datetime
from app.models import Base

class ReservaSuite(Base):
    __tablename__ = "reserva_suite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_reserva: Mapped[int] = mapped_column(ForeignKey("reservas.id_reserva"))
    id_suite: Mapped[int] = mapped_column(ForeignKey("suites.id_suite"))
    data_entrada: Mapped[date] = mapped_column(Date)
    data_saida: Mapped[date] = mapped_column(Date,nullable=True)
    valor_diaria: Mapped[float] = mapped_column(Float)
    
    reserva: Mapped["Reserva"] = relationship(back_populates="reserva_suites")
    suite: Mapped["Suite"] = relationship(back_populates="reserva_suites")