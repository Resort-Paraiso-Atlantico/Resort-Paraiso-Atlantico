from sqlalchemy import Date, ForeignKey, Integer, String, DateTime 
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import date, datetime
from app.models import Base

class HospedeEvento(Base):
    __tablename__ = "hospede_evento"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    cpf_hospede: Mapped[str] = mapped_column(ForeignKey("hospedes.cpf"))
    id_evento: Mapped[int] = mapped_column(ForeignKey("eventos.id"))
    data_inscricao: Mapped[datetime] = mapped_column(DateTime,nullable=False)

    evento: Mapped["Evento"] = relationship(back_populates="hospede_evento")
    hospede: Mapped["Hospede"] = relationship(back_populates="hospede_evento")