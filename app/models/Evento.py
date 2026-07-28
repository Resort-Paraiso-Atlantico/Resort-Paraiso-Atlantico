from sqlalchemy import Integer, String, DateTime 
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime
from app.models import Base

class Evento(Base):
    __tablename__ = "eventos"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    nome_evento: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(String(200))
    data_criacao: Mapped[datetime] = mapped_column(DateTime,nullable=True, default=datetime.now)
    inicio_evento: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    fim_evento: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    capacidade: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)

    hospede_evento: Mapped[list["HospedeEvento"]] = relationship(back_populates="evento")