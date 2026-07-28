# services/HospedeEventoService.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.HospedeEvento import HospedeEvento
from app.repositories.HospedeEventoRepository import HospedeEventoRepository
from app.repositories.EventoRepository import EventoRepository


class HospedeEventoService:
    def __init__(self, db: Session):
        self.repository = HospedeEventoRepository(db)
        self.evento_repository = EventoRepository(db)

    def inscrever_hospede(self, cpf_hospede: str, id_evento: int) -> HospedeEvento:
        evento = self.evento_repository.buscar_por_id(id_evento)
        if evento is None:
            raise ValueError(f"Evento #{id_evento} não encontrado.")

        if evento.status == "Encerrado":
            raise ValueError("Não é possível se inscrever em um evento encerrado.")

        if self.repository.buscar_inscricao(cpf_hospede, id_evento) is not None:
            raise ValueError("Hóspede já está inscrito neste evento.")

        if self.repository.contar_inscritos(id_evento) >= evento.capacidade:
            raise ValueError("Evento atingiu a capacidade máxima.")

        inscricao = HospedeEvento(
            cpf_hospede=cpf_hospede,
            id_evento=id_evento,
            data_inscricao=datetime.now(),
        )
        return self.repository.criar(inscricao)

    def listar_eventos_por_hospede(self, cpf_hospede: str) -> list[HospedeEvento]:
        return self.repository.listar_por_hospede(cpf_hospede)

    def listar_hospedes_por_evento(self, id_evento: int) -> list[HospedeEvento]:
        return self.repository.listar_por_evento(id_evento)

    def cancelar_inscricao(self, id: int) -> bool:
        inscricao = self.repository.buscar_por_id(id)
        if inscricao is None:
            raise ValueError(f"Inscrição #{id} não encontrada.")

        return self.repository.remover_por_id(id)