from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Evento import Evento


class EventoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar_evento(self,evento:Evento):
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def buscar_por_id(self, id: int) -> Evento | None:
            return self.session.get(Evento, id)

    def listar_eventos_apos(self, data: datetime) -> list[Evento]:
        return (
            self.session.query(Evento)
            .filter(Evento.inicio_evento > data)
            .all()
        )

    def atualizar(self, evento: Evento) -> Evento:
        evento = self.session.merge(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def remover_por_id(self, id: int) -> bool:
        evento = self.buscar_por_id(id)

        if evento is None:
            return False

        self.session.delete(evento)
        self.session.commit()
        return True

    def listar_eventos(self) -> list[Evento]:
        return self.session.query(Evento).all()

    def listar_eventos_nao_encerrados(self):
        return (
            self.session.query(Evento)
            .filter(Evento.status != "Encerrado")
            .all()
        )

    def atualizar_eventos_encerrados(self):
        eventos = self.listar_eventos_nao_encerrados()

        for evento in eventos:
            if evento.fim_evento is not None and datetime.now() > evento.fim_evento:
                evento.status = "Encerrado"

        self.session.commit()