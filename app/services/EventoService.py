from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.Evento import Evento
from app.repositories.EventoRepository import EventoRepository


class EventoService:

    def __init__(self, db: Session):
        self.repository = EventoRepository(db)

    def criar_evento(
        self,
        nome: str,
        descricao: str,
        inicio_evento: datetime,
        fim_evento: datetime,
        capacidade: int,
    ) -> Evento:
        if not nome.strip():
            raise ValueError("Nome do evento é obrigatório.")

        if inicio_evento >= fim_evento:
            raise ValueError("O início do evento deve ser anterior ao término.")

        if capacidade <= 0:
            raise ValueError("Capacidade deve ser no mínimo 1.")

        evento = Evento(
            nome_evento=nome,
            descricao=descricao,
            data_criacao=datetime.now(),
            inicio_evento=inicio_evento,
            fim_evento=fim_evento,
            capacidade=capacidade,
            status="Ativo",
        )
        return self.repository.criar_evento(evento)

    def buscar_por_id(self, id: int) -> Evento:
        evento = self.repository.buscar_por_id(id)
        if not evento:
            raise ValueError(f"Evento #{id} não encontrado.")
        return evento

    def listar_eventos_apos(self, data: datetime) -> list[Evento]:
        return self.repository.listar_eventos_apos(data)

    def atualizar_evento(
    self,
    id: int,
    nome: str,
    descricao: str,
    inicio_evento: datetime,
    fim_evento: datetime,
    capacidade: int,
        ) -> Evento:
        evento = self.repository.buscar_por_id(id)

        if evento is None:
            raise ValueError(f"Evento #{id} não encontrado.")

        if inicio_evento >= fim_evento:
            raise ValueError("O início do evento deve ser anterior ao término.")

        if capacidade <= 0:
            raise ValueError("Capacidade deve ser no mínimo 1.")

        evento.nome_evento = nome
        evento.descricao = descricao
        evento.inicio_evento = inicio_evento
        evento.fim_evento = fim_evento
        evento.capacidade = capacidade

        return self.repository.atualizar(evento)

    def remover_evento(self, id: int) -> bool:
        evento = self.repository.buscar_por_id(id)

        if evento is None:
            raise ValueError(f"Evento #{id} não encontrado.")

        return self.repository.remover_por_id(id)

    def listar_eventos(self) -> list[Evento]:
        return self.repository.listar_eventos()

    def listar_eventos_nao_encerrados(self) -> list[Evento]:
        return self.repository.listar_eventos_nao_encerrados()


    #criei esse metodo para caso esteja depois de tal data, atualizar o status para encerrar o evento automaticamente.
    def atualizar_status_eventos(self):
        self.repository.atualizar_eventos_encerrados()