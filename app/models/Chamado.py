from sqlalchemy import ForeignKey, Integer, String, DateTime, Text 
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from datetime import datetime
from app.models import Base


class Chamado(Base):
    __tablename__ = "chamados"
    id_chamado: Mapped[int] = mapped_column(Integer,primary_key=True)
    id_suite: Mapped[int] = mapped_column(Integer,ForeignKey("suites.id_suite"))
    tipo: Mapped[str] = mapped_column(String(30)) # Manutenção ou Limpeza
    status: Mapped[str] = mapped_column(String(30)) # Aberto, Cancelado ou Concluido
    prioridade: Mapped[str] = mapped_column(String(30)) # baixa media alta urgente
    data_abertura: Mapped[datetime] = mapped_column(DateTime)
    data_conclusao: Mapped[datetime] = mapped_column(DateTime,nullable=True)
    descricao: Mapped[str] = mapped_column(Text)

    suite: Mapped["Suite"] = relationship(back_populates="chamados")