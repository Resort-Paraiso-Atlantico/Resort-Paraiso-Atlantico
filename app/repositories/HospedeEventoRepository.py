# repositories/HospedeEventoRepository.py
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.HospedeEvento import HospedeEvento


class HospedeEventoRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, hospede_evento: HospedeEvento) -> HospedeEvento:
        self.session.add(hospede_evento)
        self.session.commit()
        self.session.refresh(hospede_evento)
        return hospede_evento

    def buscar_por_id(self, id: int) -> HospedeEvento | None:
        return self.session.get(HospedeEvento, id)

    def listar_por_hospede(self, cpf_hospede: str) -> list[HospedeEvento]:
        return (
            self.session.query(HospedeEvento)
            .options(joinedload(HospedeEvento.evento))
            .filter(HospedeEvento.cpf_hospede == cpf_hospede)
            .all()
        )

    def listar_por_evento(self, id_evento: int) -> list[HospedeEvento]:
        return (
            self.session.query(HospedeEvento)
            .options(joinedload(HospedeEvento.hospede))
            .filter(HospedeEvento.id_evento == id_evento)
            .all()
        )

    def buscar_inscricao(self, cpf_hospede: str, id_evento: int) -> HospedeEvento | None:
        return (
            self.session.query(HospedeEvento)
            .filter(
                HospedeEvento.cpf_hospede == cpf_hospede,
                HospedeEvento.id_evento == id_evento,
            )
            .first()
        )

    def contar_inscritos(self, id_evento: int) -> int:
        return (
            self.session.query(HospedeEvento)
            .filter(HospedeEvento.id_evento == id_evento)
            .count()
        )

    def remover_por_id(self, id: int) -> bool:
        inscricao = self.buscar_por_id(id)

        if inscricao is None:
            return False

        self.session.delete(inscricao)
        self.session.commit()
        return True