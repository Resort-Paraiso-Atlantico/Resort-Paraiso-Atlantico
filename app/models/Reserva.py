from sqlalchemy import Date, Float, Integer, String, DateTime 
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.orm import Mapped, mapped_column 
from datetime import date, datetime
from app.models import Base

class Reserva(Base):
    __tablename__ = "reservas"
    id_reserva: Mapped[int] = mapped_column(Integer,autoincrement=True,primary_key=True)
    cpf_hospede: Mapped[str] = mapped_column(ForeignKey("hospedes.cpf"))
    data_reserva: Mapped[date] = mapped_column(Date)
    checkin_previsto: Mapped[date] = mapped_column(Date,nullable=True)
    checkout_previsto: Mapped[date] = mapped_column(Date,nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    valor_total: Mapped[float] = mapped_column(Float,nullable=True)

    hospede = relationship("Hospede", back_populates="reservas")

    reserva_suites: Mapped[list["ReservaSuite"]] = relationship(back_populates="reserva")
    
