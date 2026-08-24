# BIRepository.py
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.Suite import Suite
from app.models.ReservaSuite import ReservaSuite
from app.models.Reserva import Reserva
from app.models.Chamado import Chamado
from app.models.Hospede import Hospede
from app.models.Evento import Evento
from app.models.HospedeEvento import HospedeEvento
from app.models.pedido.PedidoCompra import PedidoCompra
from app.models.pedido.PedidoItem import PedidoItem
from app.models.produto.Produto import Produto
from app.models.fornecedor.Fornecedor import Fornecedor

STATUS_RECEITA_VALIDA = ("Confirmada", "Check-in", "Check-out", "Hospedado", "Finalizada")
STATUS_DESPESA_EXCLUIDOS = ("CANCELADO", "Cancelado")


class BIRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Suítes e Ocupação ----------

    def quantidade_suites(self, tipo: str | None = None) -> int:
        query = self.db.query(func.count(Suite.id_suite))
        if tipo is not None:
            query = query.filter(Suite.tipo == tipo)
        return query.scalar() or 0

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
        """Soma acumulada de suíte-dias ocupadas no período."""
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
            total_dias += max(0, (fim - inicio).days)

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
            dias_por_tipo[v.suite.tipo] += max(0, (fim - inicio).days)

        return dict(dias_por_tipo)

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

    # ---------- Eventos e Lazer ----------

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

    def eventos_periodo_com_inscritos(self, data_inicio: datetime, data_fim: datetime):
        return (
            self.db.query(Evento, func.count(HospedeEvento.id))
            .outerjoin(HospedeEvento, HospedeEvento.id_evento == Evento.id)
            .filter(Evento.inicio_evento >= data_inicio, Evento.inicio_evento < data_fim)
            .group_by(Evento.id)
            .all()
        )

    def inscricoes_com_evento(self) -> list[HospedeEvento]:
        return (
            self.db.query(HospedeEvento)
            .options(joinedload(HospedeEvento.evento))
            .filter(HospedeEvento.evento.has(Evento.inicio_evento.isnot(None)))
            .all()
        )

    def distribuicao_eventos_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(Evento.status, func.count(Evento.id))
            .group_by(Evento.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    def listar_eventos_com_data(self) -> list[Evento]:
        return self.db.query(Evento).filter(Evento.inicio_evento.isnot(None)).all()

    # ---------- Reservas e CRM ----------

    def contar_reservas_por_mes(self, status: str | None = None) -> dict[str, int]:
        query = self.db.query(Reserva).filter(Reserva.checkin_previsto.isnot(None))
        if status is not None:
            query = query.filter(Reserva.status == status)
        reservas = query.all()

        contagem = defaultdict(int)
        for r in reservas:
            contagem[r.checkin_previsto.strftime("%Y-%m")] += 1
        return dict(contagem)

    def contar_reservas_futuras(self) -> int:
        hoje = date.today()
        return (
            self.db.query(func.count(Reserva.id_reserva))
            .filter(Reserva.checkin_previsto > hoje)
            .filter(Reserva.status.in_(["Pendente", "Confirmada"]))
            .scalar() or 0
        )

    def duracao_media_reservas_realizada(self) -> float:
        reservas = (
            self.db.query(Reserva)
            .filter(Reserva.checkin_realizado.isnot(None))
            .filter(Reserva.checkout_realizado.isnot(None))
            .all()
        )
        if not reservas:
            return 0.0
        duracoes = [(r.checkout_realizado - r.checkin_realizado).days for r in reservas if r.checkout_realizado >= r.checkin_realizado]
        return sum(duracoes) / len(duracoes) if duracoes else 0.0

    def taxa_cancelamento_reservas(self) -> tuple[int, int]:
        total = self.db.query(func.count(Reserva.id_reserva)).scalar() or 0
        canceladas = (
            self.db.query(func.count(Reserva.id_reserva))
            .filter(Reserva.status == "Cancelada")
            .scalar() or 0
        )
        return canceladas, total

    def reservas_com_checkin_realizado(self) -> list[Reserva]:
        return (
            self.db.query(Reserva)
            .filter(Reserva.checkin_realizado.isnot(None))
            .filter(Reserva.checkin_previsto.isnot(None))
            .all()
        )

    def distribuicao_reservas_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(Reserva.status, func.count(Reserva.id_reserva))
            .group_by(Reserva.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    # ---------- Chamados e Operacional ----------

    def chamados_concluidos(self) -> list[Chamado]:
        return (
            self.db.query(Chamado)
            .filter(Chamado.status == "Concluido")
            .filter(Chamado.data_conclusao.isnot(None))
            .all()
        )

    def chamados_por_tipo_suite(self) -> dict[str, int]:
        resultado = (
            self.db.query(Suite.tipo, func.count(Chamado.id_chamado))
            .join(Chamado, Chamado.id_suite == Suite.id_suite)
            .group_by(Suite.tipo)
            .all()
        )
        return {tipo: qtd for tipo, qtd in resultado}

    def quantidade_por_tipo_chamado(self) -> dict[str, int]:
        resultado = (
            self.db.query(Chamado.tipo, func.count(Chamado.id_chamado))
            .group_by(Chamado.tipo)
            .all()
        )
        return {tipo: qtd for tipo, qtd in resultado}

    def distribuicao_chamados_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(Chamado.status, func.count(Chamado.id_chamado))
            .group_by(Chamado.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    def distribuicao_chamados_por_prioridade(self) -> dict[str, int]:
        resultado = (
            self.db.query(Chamado.prioridade, func.count(Chamado.id_chamado))
            .group_by(Chamado.prioridade)
            .all()
        )
        return {prioridade: qtd for prioridade, qtd in resultado}

    def taxa_cancelamento_chamados(self) -> tuple[int, int]:
        total = self.db.query(func.count(Chamado.id_chamado)).scalar() or 0
        cancelados = (
            self.db.query(func.count(Chamado.id_chamado))
            .filter(Chamado.status == "Cancelado")
            .scalar() or 0
        )
        return cancelados, total

    def suites_mais_chamados(self, limite: int = 10) -> list[tuple[Suite, int]]:
        return (
            self.db.query(Suite, func.count(Chamado.id_chamado).label("qtd_chamados"))
            .join(Chamado, Chamado.id_suite == Suite.id_suite)
            .group_by(Suite.id_suite)
            .order_by(func.count(Chamado.id_chamado).desc())
            .limit(limite)
            .all()
        )

    # ---------- Hóspedes & CRM ----------

    def listar_hospedes_com_cadastro(self) -> list[Hospede]:
        return self.db.query(Hospede).filter(Hospede.data_cadastro.isnot(None)).all()

    def hospedes_com_multiplas_reservas(self) -> list[tuple[Hospede, int]]:
        return (
            self.db.query(Hospede, func.count(Reserva.id_reserva).label("qtd_reservas"))
            .join(Reserva, Reserva.cpf_hospede == Hospede.cpf)
            .group_by(Hospede.cpf)
            .having(func.count(Reserva.id_reserva) > 1)
            .order_by(func.count(Reserva.id_reserva).desc())
            .all()
        )

    # ---------- Financeiro & Projeções ----------

    def receita_bruta_total(self) -> tuple[float, int]:
        """Retorna (valor_total_receitas, qtd_reservas_validas)."""
        reservas = (
            self.db.query(Reserva)
            .filter(Reserva.status.in_(STATUS_RECEITA_VALIDA))
            .all()
        )
        total = sum(r.valor_total or 0.0 for r in reservas)
        return float(total), len(reservas)

    def despesas_totais(self) -> tuple[float, int]:
        """Retorna (valor_total_despesas, qtd_pedidos_validos)."""
        pedidos = (
            self.db.query(PedidoCompra)
            .filter(~PedidoCompra.status.in_(STATUS_DESPESA_EXCLUIDOS))
            .all()
        )
        total = sum(p.valor_total or 0.0 for p in pedidos)
        return float(total), len(pedidos)

    def receita_por_mes_dict(self) -> dict[str, float]:
        reservas = (
            self.db.query(Reserva)
            .filter(Reserva.status.in_(STATUS_RECEITA_VALIDA))
            .all()
        )
        res = defaultdict(float)
        for r in reservas:
            if r.data_reserva:
                res[r.data_reserva.strftime("%Y-%m")] += float(r.valor_total or 0.0)
        return dict(res)

    def despesas_por_mes_dict(self) -> dict[str, float]:
        pedidos = (
            self.db.query(PedidoCompra)
            .filter(~PedidoCompra.status.in_(STATUS_DESPESA_EXCLUIDOS))
            .all()
        )
        res = defaultdict(float)
        for p in pedidos:
            if p.data_pedido:
                res[p.data_pedido.strftime("%Y-%m")] += float(p.valor_total or 0.0)
        return dict(res)

    def receita_projetada_futura(self) -> float:
        hoje = date.today()
        reservas = (
            self.db.query(Reserva)
            .filter(Reserva.checkin_previsto > hoje)
            .filter(Reserva.status.in_(["Pendente", "Confirmada"]))
            .all()
        )
        return float(sum(r.valor_total or 0.0 for r in reservas))

    # ---------- Consumo & Estoque ----------

    def resumo_estoque(self) -> dict[str, int | float]:
        produtos = self.db.query(Produto).all()
        total_produtos = len(produtos)
        estoque_baixo = sum(1 for p in produtos if p.quantidade <= p.estoque_minimo)
        sem_estoque = sum(1 for p in produtos if p.quantidade == 0)
        valor_total_inventario = sum(p.quantidade * (p.valor_unitario or 0.0) for p in produtos)
        return {
            "total_produtos": total_produtos,
            "estoque_baixo": estoque_baixo,
            "sem_estoque": sem_estoque,
            "valor_inventario": valor_total_inventario,
        }

    def produtos_mais_comprados(self, limite: int = 5) -> list[tuple[str, int, float]]:
        resultado = (
            self.db.query(
                Produto.nome,
                func.sum(PedidoItem.quantidade).label("qtd_total"),
                func.sum(PedidoItem.valor_total).label("valor_total"),
            )
            .join(PedidoItem, PedidoItem.id_produto == Produto.id_produto)
            .group_by(Produto.id_produto, Produto.nome)
            .order_by(func.sum(PedidoItem.valor_total).desc())
            .limit(limite)
            .all()
        )
        return [(r[0], int(r[1] or 0), float(r[2] or 0.0)) for r in resultado]

    def pedidos_por_status(self) -> dict[str, int]:
        resultado = (
            self.db.query(PedidoCompra.status, func.count(PedidoCompra.id_pedido))
            .group_by(PedidoCompra.status)
            .all()
        )
        return {status: qtd for status, qtd in resultado}

    def obter_dados_mes(self, ano: int, mes: int) -> dict[str, float | int]:
        """Retorna resumo financeiro e de ocupação para um mês específico."""
        import calendar
        _, num_dias = calendar.monthrange(ano, mes)
        dt_inc = date(ano, mes, 1)
        dt_fim = date(ano, mes, num_dias)

        # Receita do mês
        reservas = (
            self.db.query(Reserva)
            .filter(Reserva.status.in_(STATUS_RECEITA_VALIDA))
            .filter(Reserva.data_reserva >= dt_inc, Reserva.data_reserva <= dt_fim)
            .all()
        )
        receita = sum(r.valor_total or 0.0 for r in reservas)
        qtd_res = len(reservas)

        # Despesas do mês
        pedidos = (
            self.db.query(PedidoCompra)
            .filter(~PedidoCompra.status.in_(STATUS_DESPESA_EXCLUIDOS))
            .filter(PedidoCompra.data_pedido >= dt_inc, PedidoCompra.data_pedido <= dt_fim)
            .all()
        )
        despesas = sum(p.valor_total or 0.0 for p in pedidos)

        # Suíte-dias ocupados no mês
        vinculos = (
            self.db.query(ReservaSuite)
            .filter(
                ReservaSuite.data_entrada <= dt_fim,
                or_(ReservaSuite.data_saida.is_(None), ReservaSuite.data_saida >= dt_inc),
            )
            .filter(~ReservaSuite.reserva.has(Reserva.status == "Cancelada"))
            .all()
        )
        dias_ocupados = 0
        for v in vinculos:
            inicio = max(v.data_entrada, dt_inc)
            fim = min(v.data_saida, dt_fim) if v.data_saida else dt_fim
            if fim >= inicio:
                dias_ocupados += (fim - inicio).days + 1

        total_suites = self.quantidade_suites()
        capacidade_mes = total_suites * num_dias
        taxa_ocup = (dias_ocupados / capacidade_mes * 100.0) if capacidade_mes > 0 else 0.0

        return {
            "receita": float(receita),
            "despesas": float(despesas),
            "qtd_reservas": qtd_res,
            "taxa_ocupacao": taxa_ocup,
        }