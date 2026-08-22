# BIRepository.py
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.Suite import Suite
from app.models.ReservaSuite import ReservaSuite
from app.models.Reserva import Reserva

from datetime import datetime
from sqlalchemy.orm import joinedload
from app.models.Evento import Evento
from app.models.HospedeEvento import HospedeEvento


class BIRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- básicos ----------

    def quantidade_suites(self, tipo: str | None = None) -> int:
        query = self.db.query(func.count(Suite.id_suite))
        if tipo is not None:
            query = query.filter(Suite.tipo == tipo)
        return query.scalar() or 0

    # ---------- ocupação ----------

    def suites_ocupadas_hoje(self, tipo: str | None = None) -> int:
        hoje = date.today()
        amanha = hoje + timedelta(days=1)

        query = (
            self.db.query(func.count(func.distinct(ReservaSuite.id_suite)))
            .join(Suite, ReservaSuite.id_suite == Suite.id_suite)
            .filter(
                ReservaSuite.data_entrada < amanha,
                or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida > hoje),
            )
            .filter(~ReservaSuite.reserva.has(Reserva.status == "Cancelada"))
        )
        if tipo is not None:
            query = query.filter(Suite.tipo == tipo)

        return query.scalar() or 0

    def suites_ocupadas_periodo(self, data_inicio: date, data_fim: date, tipo: str | None = None) -> int:
        """Soma acumulada de suíte-dias ocupadas no período (não é por dia individual)."""
        query = (
            self.db.query(ReservaSuite)
            .join(Suite, ReservaSuite.id_suite == Suite.id_suite)
            .options(joinedload(ReservaSuite.suite))
            .filter(
                ReservaSuite.data_entrada < data_fim,
                or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida > data_inicio),
            )
            .filter(~ReservaSuite.reserva.has(Reserva.status == "Cancelada"))
        )
        if tipo is not None:
            query = query.filter(Suite.tipo == tipo)

        vinculos = query.all()

        total_dias = 0
        for v in vinculos:
            inicio = max(v.data_entrada, data_inicio)
            fim = min(v.data_saida, data_fim) if v.data_saida else data_fim
            total_dias += (fim - inicio).days

        return total_dias

    def ocupacao_por_tipo_periodo(self, data_inicio: date, data_fim: date) -> dict[str, int]:
        """Retorna {tipo: soma de suíte-dias ocupados no período}."""
        vinculos = (
            self.db.query(ReservaSuite)
            .join(Suite, ReservaSuite.id_suite == Suite.id_suite)
            .options(joinedload(ReservaSuite.suite))
            .filter(
                ReservaSuite.data_entrada < data_fim,
                or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida > data_inicio),
            )
            .filter(~ReservaSuite.reserva.has(Reserva.status == "Cancelada"))
            .all()
        )

        dias_por_tipo = defaultdict(int)
        for v in vinculos:
            inicio = max(v.data_entrada, data_inicio)
            fim = min(v.data_saida, data_fim) if v.data_saida else data_fim
            dias_por_tipo[v.suite.tipo] += (fim - inicio).days

        return dict(dias_por_tipo)

    # ---------- uso ----------

    def suites_mais_utilizadas(
        self, data_inicio: date | None = None, data_fim: date | None = None, tipo: str | None = None
    ) -> list[tuple[Suite, int]]:
        query = (
            self.db.query(Suite, func.count(ReservaSuite.id).label("qtd_reservas"))
            .join(ReservaSuite, ReservaSuite.id_suite == Suite.id_suite)
            .join(Reserva, ReservaSuite.id_reserva == Reserva.id_reserva)
            .filter(Reserva.status != "Cancelada")
        )

        if data_inicio is not None and data_fim is not None:
            query = query.filter(
                ReservaSuite.data_entrada < data_fim,
                or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida > data_inicio),
            )
        if tipo is not None:
            query = query.filter(Suite.tipo == tipo)

        return (
            query.group_by(Suite.id_suite)
            .order_by(func.count(ReservaSuite.id).desc())
            .all()
        )

    # ---------- composição ----------

    def distribuicao_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(Suite.status, func.count(Suite.id_suite))
            .group_by(Suite.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    def distribuicao_por_tipo(self) -> dict[str, int]:
        resultado = (
            self.db.query(Suite.tipo, func.count(Suite.id_suite))
            .group_by(Suite.tipo)
            .all()
        )
        return {tipo: qtd for tipo, qtd in resultado}

    # ---------- evento individual ----------

    def evento_capacidade_inscritos(self, id_evento: int) -> tuple[int, int] | None:
        evento = self.db.get(Evento, id_evento)
        if evento is None:
            return None
        inscritos = (
            self.db.query(func.count(HospedeEvento.id))
            .filter(HospedeEvento.id_evento == id_evento)
            .scalar() or 0
        )
        return evento.capacidade, inscritos

    # ---------- ranking ----------

    def eventos_mais_procurados(self, data_inicio: datetime | None = None, data_fim: datetime | None = None):
        query = (
            self.db.query(Evento, func.count(HospedeEvento.id).label("qtd_inscricoes"))
            .join(HospedeEvento, HospedeEvento.id_evento == Evento.id)
        )
        if data_inicio is not None and data_fim is not None:
            query = query.filter(Evento.inicio_evento >= data_inicio, Evento.inicio_evento < data_fim)

        return (
            query.group_by(Evento.id)
            .order_by(func.count(HospedeEvento.id).desc())
            .all()
        )

    # ---------- ocupação média no período ----------

    def eventos_periodo_com_inscritos(self, data_inicio: datetime, data_fim: datetime):
        """Eventos cujo inicio_evento cai no período, com contagem de inscritos (0 incluído)."""
        return (
            self.db.query(Evento, func.count(HospedeEvento.id))
            .outerjoin(HospedeEvento, HospedeEvento.id_evento == Evento.id)
            .filter(Evento.inicio_evento >= data_inicio, Evento.inicio_evento < data_fim)
            .group_by(Evento.id)
            .all()
        )

    # ---------- lead time ----------

    def inscricoes_com_evento(self) -> list[HospedeEvento]:
        return (
            self.db.query(HospedeEvento)
            .options(joinedload(HospedeEvento.evento))
            .filter(HospedeEvento.evento.has(Evento.inicio_evento.isnot(None)))
            .all()
        )

    # ---------- composição ----------

    def distribuicao_eventos_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(Evento.status, func.count(Evento.id))
            .group_by(Evento.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    def listar_eventos_com_data(self) -> list[Evento]:
        return self.db.query(Evento).filter(Evento.inicio_evento.isnot(None)).all()