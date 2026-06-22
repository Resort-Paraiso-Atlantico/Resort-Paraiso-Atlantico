from sqlalchemy import Date, Float, Integer, String, DateTime 
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.orm import Mapped, mapped_column 
from datetime import date, datetime
from app.models import Base

#Fiz a alteração que tinha comentado. No documento a relacao era uma reserva-> uma suite. Quando na verdade uma reserva pode ter diversas suites.

class Reserva(Base):
    __tablename__ = "reservas"
    id_reserva: Mapped[int] = mapped_column(Integer,autoincrement=True,primary_key=True)
    cpf_hospede: Mapped[str] = mapped_column(ForeignKey("hospedes.cpf"))
    data_reserva: Mapped[date] = mapped_column(Date)
    checkin_previsto: Mapped[date] = mapped_column(Date)
    checkout_previsto: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20))
    valor_total: Mapped[float] = mapped_column(Float)

    hospede = relationship("Hospede", back_populates="reservas")
    suites: Mapped[list["Suite"]] = relationship(back_populates="reserva")
