from datetime import date, datetime
from collections import defaultdict
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.repositories.BIRepository import BIRepository


@dataclass
class KPIExecutivos:
    receita_bruta: float = 0.0
    despesas_totais: float = 0.0
    saldo_liquido: float = 0.0
    margem_lucro: float = 0.0
    ticket_medio_reserva: float = 0.0
    ocupacao_hoje: float = 0.0
    adr: float = 0.0  # Average Daily Rate
    revpar: float = 0.0  # Revenue Per Available Room
    receita_projetada: float = 0.0
    qtd_reservas: int = 0
    qtd_pedidos: int = 0


class BIService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BIRepository(db)

    # ── KPIs Executivos & Hospitalidade ───────────────────────────────────────

    def obter_kpis_executivos(self, data_inicio: date | None = None, data_fim: date | None = None) -> KPIExecutivos:
        receita, qtd_res = self.repository.receita_bruta_total(data_inicio, data_fim)
        despesas, qtd_ped = self.repository.despesas_totais(data_inicio, data_fim)
        saldo = receita - despesas
        margem = (saldo / receita * 100.0) if receita > 0 else 0.0
        ticket_medio = (receita / qtd_res) if qtd_res > 0 else 0.0

        if data_inicio is not None and data_fim is not None:
            ocup_taxa = self.suites_ocupadas_periodo(data_inicio, data_fim)
        else:
            ocup_taxa = self.suites_ocupadas_hoje()

        # ADR: Diária média baseada no valor total de diárias divididas pelas reservas válidas
        adr = ticket_medio
        revpar = (ocup_taxa / 100.0) * adr

        projecao = self.repository.receita_projetada_futura()

        return KPIExecutivos(
            receita_bruta=receita,
            despesas_totais=despesas,
            saldo_liquido=saldo,
            margem_lucro=margem,
            ticket_medio_reserva=ticket_medio,
            ocupacao_hoje=ocup_taxa,
            adr=adr,
            revpar=revpar,
            receita_projetada=projecao,
            qtd_reservas=qtd_res,
            qtd_pedidos=qtd_ped,
        )

    def obter_alertas_desempenho(self) -> list[dict[str, str]]:
        alertas = []

        # 1. Alerta de Ocupação
        ocup_hoje = self.suites_ocupadas_hoje()
        if ocup_hoje < 40.0:
            alertas.append({
                "nivel": "warning",
                "titulo": "Baixa Ocupação Hoje",
                "mensagem": f"A taxa de ocupação atual está em {ocup_hoje:.1f}% (abaixo da meta operacional de 50%)."
            })
        elif ocup_hoje >= 85.0:
            alertas.append({
                "nivel": "success",
                "titulo": "Alta Demanda de Suítes",
                "mensagem": f"Ocupação alta em {ocup_hoje:.1f}%. Recomendada revisão de preços para maximizar RevPAR."
            })

        # 2. Alerta de Cancelamento de Reservas
        taxa_canc_res = self.taxa_cancelamento_reservas()
        if taxa_canc_res > 15.0:
            alertas.append({
                "nivel": "error",
                "titulo": "Taxa de Cancelamento Elevada",
                "mensagem": f"Taxa histórica de cancelamento de reservas atingiu {taxa_canc_res:.1f}%."
            })

        # 3. Alerta de Chamados Pendentes/Manutenção
        st_chamados = self.distribuicao_chamados_por_status()
        pendentes_chamados = st_chamados.get("Aberto", 0) + st_chamados.get("Em Andamento", 0)
        if pendentes_chamados > 5:
            alertas.append({
                "nivel": "warning",
                "titulo": "Acúmulo de Chamados Operacionais",
                "mensagem": f"Existem {pendentes_chamados} chamados de limpeza/manutenção aguardando resolução."
            })

        # 4. Alerta de Estoque
        resumo_est = self.repository.resumo_estoque()
        if resumo_est["estoque_baixo"] > 0:
            alertas.append({
                "nivel": "error",
                "titulo": "Insumos com Estoque Baixo/Crítico",
                "mensagem": f"{resumo_est['estoque_baixo']} produtos atingiram ou ficaram abaixo do estoque mínimo de segurança."
            })

        if not alertas:
            alertas.append({
                "nivel": "info",
                "titulo": "Operação Estável",
                "mensagem": "Todos os indicadores operacionais e financeiros estão dentro das faixas normais."
            })

        return alertas

    def obter_metas_gerenciais(self, data_inicio: date | None = None, data_fim: date | None = None) -> dict[str, dict[str, float | str]]:
        kpis = self.obter_kpis_executivos(data_inicio, data_fim)
        
        meta_ocup = 75.0
        status_ocup = "🟢 Meta Atingida" if kpis.ocupacao_hoje >= meta_ocup else "🟡 Abaixo da Meta" if kpis.ocupacao_hoje >= 50 else "🔴 Crítico"

        meta_margem = 30.0
        status_margem = "🟢 Meta Atingida" if kpis.margem_lucro >= meta_margem else "🟡 Atenção" if kpis.margem_lucro >= 15 else "🔴 Abaixo do Esperado"

        meta_revpar = 350.0
        status_revpar = "🟢 Meta Atingida" if kpis.revpar >= meta_revpar else "🟡 Atenção"

        return {
            "Ocupação": {"atual": kpis.ocupacao_hoje, "meta": meta_ocup, "unidade": "%", "status": status_ocup},
            "Margem Líquida": {"atual": kpis.margem_lucro, "meta": meta_margem, "unidade": "%", "status": status_margem},
            "RevPAR": {"atual": kpis.revpar, "meta": meta_revpar, "unidade": "R$", "status": status_revpar},
        }

    # ── Suítes ───────────────────────────────────────────────────────────────

    def suites_ocupadas_hoje(self, tipo: str | None = None) -> float:
        suites_ocupadas = self.repository.suites_ocupadas_hoje(tipo)
        suites_total = self.repository.quantidade_suites(tipo)
        if suites_total == 0:
            return 0.0
        return (suites_ocupadas / suites_total) * 100.0

    def suites_ocupadas_periodo(self, data_inicio: date, data_fim: date, tipo: str | None = None) -> float:
        if data_inicio is None or data_fim is None:
            raise ValueError("Data início e data fim devem ser preenchidos.")
        if data_inicio > data_fim:
            raise ValueError("A data de início deve ser anterior ou igual à data final.")

        suites_ocupadas = self.repository.suites_ocupadas_periodo(data_inicio, data_fim, tipo)
        suites_total = self.repository.quantidade_suites(tipo)

        dias = max(1, (data_fim - data_inicio).days)
        if suites_total == 0:
            return 0.0

        return (suites_ocupadas / (suites_total * dias)) * 100.0

    def suites_mais_utilizadas(
        self, data_inicio: date | None = None, data_fim: date | None = None, tipo: str | None = None
    ):
        if (data_inicio is None) != (data_fim is None):
            raise ValueError("Data início e data fim devem ser preenchidos juntos, ou nenhum dos dois.")
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ValueError("A data de início deve ser anterior à data final.")

        resultado = self.repository.suites_mais_utilizadas(data_inicio, data_fim, tipo)
        return [{"suite": suite, "qtd_reservas": qtd} for suite, qtd in resultado]

    def distribuicao_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_por_status()

    def composicao_por_tipo(self) -> dict[str, int]:
        return self.repository.distribuicao_por_tipo()

    def ocupacao_por_tipo(self, data_inicio: date, data_fim: date) -> dict[str, float]:
        if data_inicio is None or data_fim is None:
            raise ValueError("Data início e data fim devem ser preenchidos.")
        if data_inicio > data_fim:
            raise ValueError("A data de início deve ser anterior à data final.")

        dias = max(1, (data_fim - data_inicio).days)
        dias_ocupados_por_tipo = self.repository.ocupacao_por_tipo_periodo(data_inicio, data_fim)
        total_por_tipo = self.repository.distribuicao_por_tipo()

        resultado = {}
        for tipo, total_suites in total_por_tipo.items():
            ocupados = dias_ocupados_por_tipo.get(tipo, 0)
            resultado[tipo] = (ocupados / (total_suites * dias)) * 100.0 if total_suites > 0 else 0.0

        return resultado

    # ── Eventos & Lazer ──────────────────────────────────────────────────────

    def evento_taxa_ocupacao(self, id_evento: int) -> float:
        dados = self.repository.evento_capacidade_inscritos(id_evento)
        if dados is None:
            raise ValueError("Evento não encontrado.")
        capacidade, inscritos = dados
        return (inscritos / capacidade) * 100.0 if capacidade > 0 else 0.0

    def eventos_mais_procurados(self, data_inicio: datetime | None = None, data_fim: datetime | None = None):
        if (data_inicio is None) != (data_fim is None):
            raise ValueError("Data início e data fim devem ser preenchidos juntos, ou nenhum dos dois.")
        if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
            raise ValueError("A data de início deve ser anterior à data final.")

        resultado = self.repository.eventos_mais_procurados(data_inicio, data_fim)
        return [{"evento": evento, "qtd_inscricoes": qtd} for evento, qtd in resultado]

    def ocupacao_media_eventos_periodo(self, data_inicio: datetime, data_fim: datetime) -> float:
        if data_inicio is None or data_fim is None:
            raise ValueError("Data início e data fim devem ser preenchidos.")
        if data_inicio > data_fim:
            raise ValueError("A data de início deve ser anterior à data final.")

        eventos = self.repository.eventos_periodo_com_inscritos(data_inicio, data_fim)
        if not eventos:
            return 0.0

        taxas = [(qtd / evento.capacidade) * 100.0 if evento.capacidade > 0 else 0.0 for evento, qtd in eventos]
        return sum(taxas) / len(taxas)

    def lead_time_medio_inscricao(self) -> float:
        inscricoes = self.repository.inscricoes_com_evento()
        diffs = [
            (i.evento.inicio_evento - i.data_inscricao).days
            for i in inscricoes
            if i.data_inscricao is not None and i.evento.inicio_evento >= i.data_inscricao
        ]
        return sum(diffs) / len(diffs) if diffs else 0.0

    def distribuicao_eventos_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_eventos_por_status()

    def eventos_por_mes(self) -> dict[str, int]:
        eventos = self.repository.listar_eventos_com_data()
        contagem = defaultdict(int)
        for e in eventos:
            chave = e.inicio_evento.strftime("%Y-%m")
            contagem[chave] += 1
        return dict(contagem)

    # ── Reservas & CRM ───────────────────────────────────────────────────────

    def reservas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes()

    def reservas_canceladas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes(status="Cancelada")

    def reservas_concluidas_por_mes(self) -> dict[str, int]:
        return self.repository.contar_reservas_por_mes(status="Finalizada")

    def reservas_futuras(self) -> int:
        return self.repository.contar_reservas_futuras()

    def duracao_media_reservas(self) -> float:
        return self.repository.duracao_media_reservas_realizada()

    def taxa_cancelamento_reservas(self) -> float:
        canceladas, total = self.repository.taxa_cancelamento_reservas()
        return (canceladas / total) * 100.0 if total > 0 else 0.0

    def taxa_atraso_checkin(self) -> dict[str, float]:
        reservas = self.repository.reservas_com_checkin_realizado()
        if not reservas:
            return {"taxa_atraso": 0.0, "atraso_medio_dias": 0.0}

        atrasadas = [r for r in reservas if r.checkin_realizado > r.checkin_previsto]
        taxa = (len(atrasadas) / len(reservas)) * 100.0
        atraso_medio = (
            sum((r.checkin_realizado - r.checkin_previsto).days for r in atrasadas) / len(atrasadas)
            if atrasadas else 0.0
        )
        return {"taxa_atraso": taxa, "atraso_medio_dias": atraso_medio}

    def distribuicao_reservas_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_reservas_por_status()

    # ── Chamados & Operacional ───────────────────────────────────────────────

    def tempo_medio_conclusao_chamado(self) -> float:
        chamados = self.repository.chamados_concluidos()
        if not chamados:
            return 0.0
        duracoes = [(c.data_conclusao - c.data_abertura).days for c in chamados if c.data_conclusao >= c.data_abertura]
        return sum(duracoes) / len(duracoes) if duracoes else 0.0

    def chamados_por_tipo_suite(self) -> dict[str, int]:
        return self.repository.chamados_por_tipo_suite()

    def quantidade_por_tipo_chamado(self) -> dict[str, int]:
        return self.repository.quantidade_por_tipo_chamado()

    def distribuicao_chamados_por_status(self) -> dict[str, int]:
        return self.repository.distribuicao_chamados_por_status()

    def distribuicao_chamados_por_prioridade(self) -> dict[str, int]:
        return self.repository.distribuicao_chamados_por_prioridade()

    def taxa_cancelamento_chamados(self) -> float:
        cancelados, total = self.repository.taxa_cancelamento_chamados()
        return (cancelados / total) * 100.0 if total > 0 else 0.0

    def suites_mais_chamados(self, limite: int = 10):
        resultado = self.repository.suites_mais_chamados(limite)
        return [{"suite": suite, "qtd_chamados": qtd} for suite, qtd in resultado]

    # ── Hóspedes & CRM ───────────────────────────────────────────────────────

    def cadastros_hospedes_por_mes(self) -> dict[str, int]:
        hospedes = self.repository.listar_hospedes_com_cadastro()
        contagem = defaultdict(int)
        for h in hospedes:
            contagem[h.data_cadastro.strftime("%Y-%m")] += 1
        return dict(contagem)

    def mes_com_mais_cadastros(self) -> tuple[str, int] | None:
        por_mes = self.cadastros_hospedes_por_mes()
        if not por_mes:
            return None
        return max(por_mes.items(), key=lambda item: item[1])

    def hospedes_recorrentes(self):
        resultado = self.repository.hospedes_com_multiplas_reservas()
        return [{"hospede": hospede, "qtd_reservas": qtd} for hospede, qtd in resultado]

    # ── Estoque & Consumo ───────────────────────────────────────────────────

    def resumo_estoque(self) -> dict[str, int | float]:
        return self.repository.resumo_estoque()

    def produtos_mais_comprados(self, limite: int = 5):
        return self.repository.produtos_mais_comprados(limite)

    def pedidos_por_status(self) -> dict[str, int]:
        return self.repository.pedidos_por_status()

    def obter_comparativo_mom(self) -> dict[str, float | str]:
        """Calcula a variação Month-over-Month (MoM) entre o mês atual e o mês anterior."""
        hoje = date.today()
        ano_atual, mes_atual = hoje.year, hoje.month

        if mes_atual == 1:
            ano_ant, mes_ant = ano_atual - 1, 12
        else:
            ano_ant, mes_ant = ano_atual, mes_atual - 1

        dados_atual = self.repository.obter_dados_mes(ano_atual, mes_atual)
        dados_ant = self.repository.obter_dados_mes(ano_ant, mes_ant)

        def _calc_delta(atual: float, ant: float) -> float:
            if ant == 0.0:
                return 100.0 if atual > 0.0 else 0.0
            return ((atual - ant) / ant) * 100.0

        rec_delta = _calc_delta(dados_atual["receita"], dados_ant["receita"])
        desp_delta = _calc_delta(dados_atual["despesas"], dados_ant["despesas"])
        ocup_delta = dados_atual["taxa_ocupacao"] - dados_ant["taxa_ocupacao"]

        return {
            "receita_atual": dados_atual["receita"],
            "receita_ant": dados_ant["receita"],
            "receita_delta_pct": rec_delta,
            "despesas_atual": dados_atual["despesas"],
            "despesas_ant": dados_ant["despesas"],
            "despesas_delta_pct": desp_delta,
            "ocupacao_atual": dados_atual["taxa_ocupacao"],
            "ocupacao_ant": dados_ant["taxa_ocupacao"],
            "ocupacao_delta_pct": ocup_delta,
        }