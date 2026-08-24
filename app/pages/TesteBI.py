import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, time, timedelta

from app.database import SessionLocal
from app.services.BIService import BIService
from app.theme import (
    aplicar_tema,
    cabecalho,
    PRIMARY_TEAL,
    PRIMARY_DARK,
    ACCENT_GOLD,
    ACCENT_CORAL,
    badge_status,
)

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()

# ── Cabeçalho Principal ───────────────────────────────────────────────────────
cabecalho(
    "Executive Business Intelligence (BI)",
    "Análises Estratégicas, Indicadores Gerenciais & Dashboards Interativos",
    "📊",
)

# ── Estado de Sessão e Controle de Acesso ────────────────────────────────────
if "perfil_gestor" not in st.session_state:
    st.session_state.perfil_gestor = True


def _fmt_moeda(val: float, e_gestor: bool = True) -> str:
    if not e_gestor:
        return "R$ ••••••"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_pct(val: float) -> str:
    return f"{val:.1f}%"


# ── Funções Auxiliares de Visualização Executiva Plotly ───────────────────────

def _plot_fluxo_financeiro(df_fin: pd.DataFrame, is_gestor: bool):
    if df_fin.empty:
        st.info("Ainda não há lançamentos para exibição do gráfico de fluxo financeiro.")
        return

    fig = go.Figure()

    # Barra de Receitas
    fig.add_trace(
        go.Bar(
            x=df_fin["Mês"],
            y=df_fin["Receitas (R$)"],
            name="Receita Bruta",
            marker_color="#0D9488",
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.2f}<extra></extra>",
        )
    )

    # Barra de Despesas
    fig.add_trace(
        go.Bar(
            x=df_fin["Mês"],
            y=df_fin["Despesas (R$)"],
            name="Despesas Operacionais",
            marker_color="#E11D48",
            hovertemplate="<b>%{x}</b><br>Despesas: R$ %{y:,.2f}<extra></extra>",
        )
    )

    # Linha de Saldo Líquido
    fig.add_trace(
        go.Scatter(
            x=df_fin["Mês"],
            y=df_fin["Saldo Líquido (R$)"],
            name="Resultado Líquido",
            mode="lines+markers",
            line=dict(color="#D97706", width=3, shape="spline"),
            marker=dict(size=8, color="#D97706"),
            hovertemplate="<b>%{x}</b><br>Saldo: R$ %{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#1E293B"),
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(size=11, color="#64748B"),
        ),
        yaxis=dict(
            title="Valor (R$)",
            gridcolor="#F1F5F9",
            tickfont=dict(size=11, color="#64748B"),
        ),
        height=320,
    )

    st.plotly_chart(fig, use_container_width=True)


def _plot_donut_chart(df_data: pd.DataFrame, names_col: str, values_col: str, title: str, colors: list = None):
    if df_data.empty or df_data[values_col].sum() == 0:
        st.info(f"Nenhum dado disponível para {title.lower()}.")
        return

    if colors is None:
        colors = ["#0D9488", "#0F172A", "#D97706", "#E11D48", "#0284C7", "#64748B"]

    fig = px.pie(
        df_data,
        names=names_col,
        values=values_col,
        hole=0.55,
        color_discrete_sequence=colors,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Qtd: %{value}<br>Proporção: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#FFFFFF", width=2)),
    )

    fig.update_layout(
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#475569"),
        ),
        height=280,
    )

    st.plotly_chart(fig, use_container_width=True)


def _plot_ranking_bar(df_data: pd.DataFrame, x_col: str, y_col: str, color_hex: str = "#0D9488"):
    if df_data.empty:
        st.info("Nenhum dado para exibição.")
        return

    fig = px.bar(
        df_data,
        x=x_col,
        y=y_col,
        orientation="h",
        text=x_col,
        color_discrete_sequence=[color_hex],
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Total: %{x}<extra></extra>",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title=""),
        yaxis=dict(title="", tickfont=dict(size=11, color="#1E293B")),
        height=260,
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Barra Superior de Filtros & Controles ────────────────────────────────────
f1, f2, f3, f4 = st.columns([1.6, 1.2, 1.2, 1.1])

with f1:
    preset_periodo = st.selectbox(
        "📅 Período Estratégico de Análise:",
        ["Últimos 30 Dias", "Este Mês", "Ano Atual", "Personalizado"],
        index=0,
        key="preset_bi"
    )

hoje = date.today()
if preset_periodo == "Últimos 30 Dias":
    dt_inicio_default = hoje - timedelta(days=30)
    dt_fim_default = hoje
elif preset_periodo == "Este Mês":
    dt_inicio_default = hoje.replace(day=1)
    dt_fim_default = hoje
elif preset_periodo == "Ano Atual":
    dt_inicio_default = hoje.replace(month=1, day=1)
    dt_fim_default = hoje
else:
    dt_inicio_default = hoje - timedelta(days=30)
    dt_fim_default = hoje

with f2:
    data_inicio_global = st.date_input(
        "Data Inicial",
        value=dt_inicio_default,
        disabled=(preset_periodo != "Personalizado"),
        key="bi_dt_inc"
    )

with f3:
    data_fim_global = st.date_input(
        "Data Final",
        value=dt_fim_default,
        disabled=(preset_periodo != "Personalizado"),
        key="bi_dt_fim"
    )

with f4:
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    is_gestor = st.toggle("🔓 Modo Gestor", value=st.session_state.perfil_gestor, key="toggle_gestor")
    st.session_state.perfil_gestor = is_gestor

# Faixa Informativa da Operação
st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #FFFFFF 0%, #F0FDFA 100%);
        border: 1px solid #CCFBF1;
        padding: 0.65rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(13,148,136,0.05);
    ">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #0D9488;"></span>
            <span style="font-size: 0.86rem; color: #0F766E; font-weight: 700;">Conexão Direta ao Banco PostgreSQL (SQLAlchemy Session)</span>
        </div>
        <span style="font-size: 0.8rem; color: #64748B; font-weight: 600;">🔒 Registros Históricos Imutáveis · Auditabilidade Garantida</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ── Abertura da Conexão e Inicialização do BIService ─────────────────────────
with SessionLocal() as db:
    service = BIService(db)

    # Abas Executivas
    tab_overview, tab_financeiro, tab_ocupacao, tab_operacao, tab_crm, tab_estoque = st.tabs([
        "🎯 Painel Executivo",
        "💰 Financeiro & Faturamento",
        "🛏️ Ocupação & Suítes",
        "⚡ Operação & Recepção",
        "👥 CRM, Satisfação & Lazer",
        "📦 Consumo & Estoque"
    ])

    # ── 1. PAINEL EXECUTIVO (OVERVIEW) ───────────────────────────────────────
    with tab_overview:
        kpis = service.obter_kpis_executivos()
        mom = service.obter_comparativo_mom()

        st.subheader("📊 Indicadores Chave de Desempenho (KPIs)")
        k1, k2, k3, k4, k5, k6 = st.columns(6)

        with k1:
            st.metric(
                "🟢 RECEITA BRUTA",
                _fmt_moeda(kpis.receita_bruta, is_gestor),
                delta=f"{mom['receita_delta_pct']:+.1f}% MoM"
            )
        with k2:
            st.metric(
                "🔴 DESPESAS TOTAIS",
                _fmt_moeda(kpis.despesas_totais, is_gestor),
                delta=f"{mom['despesas_delta_pct']:+.1f}% MoM",
                delta_color="inverse"
            )
        with k3:
            st.metric(
                "💵 SALDO LÍQUIDO",
                _fmt_moeda(kpis.saldo_liquido, is_gestor),
                delta=f"Margem {_fmt_pct(kpis.margem_lucro)}"
            )
        with k4:
            st.metric(
                "🏨 REVPAR",
                _fmt_moeda(kpis.revpar, is_gestor),
                delta="Receita/Suíte Disponível"
            )
        with k5:
            st.metric(
                "🏷️ ADR (DIÁRIA MÉDIA)",
                _fmt_moeda(kpis.adr, is_gestor),
                delta=f"{kpis.qtd_reservas} reservas válidas"
            )
        with k6:
            st.metric(
                "📈 OCUPAÇÃO HOJE",
                _fmt_pct(kpis.ocupacao_hoje),
                delta=f"{mom['ocupacao_delta_pct']:+.1f}% MoM"
            )

        st.divider()

        # Medidores de Metas Executivas & Card de Projeção
        c_metas, c_projecao = st.columns([1.5, 1])

        with c_metas:
            st.subheader("🎯 Monitoramento Automático de Metas Gerenciais")
            metas = service.obter_metas_gerenciais()

            for nome_meta, dados in metas.items():
                val_atual = dados['atual']
                meta_val = dados['meta']
                unid = dados['unidade']
                status_txt = dados['status']

                pct_progresso = min(100.0, max(0.0, (val_atual / meta_val * 100.0) if meta_val > 0 else 0.0))

                fmt_val = f"R$ {val_atual:,.2f}" if unid == "R$" else f"{val_atual:.1f}%"
                fmt_meta = f"R$ {meta_val:,.2f}" if unid == "R$" else f"{meta_val:.1f}%"

                if not is_gestor and unid == "R$":
                    fmt_val = "R$ ••••••"
                    fmt_meta = "R$ ••••••"

                cor_prog = "#0D9488" if pct_progresso >= 80 else "#D97706" if pct_progresso >= 50 else "#E11D48"

                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; padding: 0.9rem 1.2rem; border-radius: 14px; border: 1px solid #E2E8F0; margin-bottom: 0.65rem; box-shadow: 0 2px 8px rgba(15,23,42,0.03);">
                        <div style="display: flex; justify-content: space-between; font-weight: 700; color: #0F172A; font-size: 0.92rem;">
                            <span>{nome_meta}</span>
                            <span>{fmt_val} / Meta: {fmt_meta} ({status_txt})</span>
                        </div>
                        <div style="background: #F1F5F9; border-radius: 999px; height: 10px; margin-top: 8px; overflow: hidden;">
                            <div style="background: {cor_prog}; width: {pct_progresso:.1f}%; height: 100%; border-radius: 999px; transition: width 0.4s ease;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with c_projecao:
            st.subheader("🔮 Projeção Automática de Receita")
            proj_val = kpis.receita_projetada
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #0D9488 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 18px;
                    box-shadow: 0 10px 25px -5px rgba(15,23,42,0.2);
                    border: 1px solid rgba(255,255,255,0.15);
                ">
                    <div style="font-size: 0.82rem; color: #D97706; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;">Faturamento Projetado (Reservas Futuras)</div>
                    <div style="font-size: 2.1rem; font-weight: 800; color: #FFFFFF; margin: 0.4rem 0; font-family: 'Playfair Display', serif;">{_fmt_moeda(proj_val, is_gestor)}</div>
                    <div style="font-size: 0.82rem; color: #CBD5E1; line-height: 1.4;">Calculado em tempo real sobre reservas com status <b>Confirmada</b> ou <b>Pendente</b> com check-in futuro.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # Alertas Automáticos de Desempenho
        st.subheader("🚨 Alertas Automáticos de Desempenho Operacional")
        alertas = service.obter_alertas_desempenho()

        a_col1, a_col2 = st.columns(2)
        for idx, a in enumerate(alertas):
            target_col = a_col1 if idx % 2 == 0 else a_col2
            with target_col:
                if a["nivel"] == "error":
                    st.error(f"**{a['titulo']}**: {a['mensagem']}")
                elif a["nivel"] == "warning":
                    st.warning(f"**{a['titulo']}**: {a['mensagem']}")
                elif a["nivel"] == "success":
                    st.success(f"**{a['titulo']}**: {a['mensagem']}")
                else:
                    st.info(f"**{a['titulo']}**: {a['mensagem']}")

    # ── 2. FINANCEIRO & FATURAMENTO ──────────────────────────────────────────
    with tab_financeiro:
        st.subheader("📊 Demonstrativo de Resultados & Análise de Faturamento")

        col_dre, col_fluxo = st.columns([1, 1.4])

        with col_dre:
            st.markdown("### 📑 DRE Sintético do Resort")
            st.caption("Validação em tempo real integrada ao Módulo Financeiro")

            rec_tot, _ = service.repository.receita_bruta_total()
            desp_tot, _ = service.repository.despesas_totais()
            saldo_tot = rec_tot - desp_tot
            margem_tot = (saldo_tot / rec_tot * 100.0) if rec_tot > 0 else 0.0

            dre_html = f"""
            <div style="background-color: #FFFFFF; padding: 1.3rem; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding: 10px 0;">
                    <span style="font-weight: 600; color: #1E293B;">(+) Receita Bruta de Hospedagem</span>
                    <span style="font-weight: 700; color: #047857;">{_fmt_moeda(rec_tot, is_gestor)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding: 10px 0;">
                    <span style="font-weight: 600; color: #1E293B;">(-) Custos com Pedidos & Suprimentos</span>
                    <span style="font-weight: 700; color: #B91C1C;">({_fmt_moeda(desp_tot, is_gestor)})</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #CBD5E1; padding: 12px 0; margin-top: 4px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">(=) Resultado Líquido Operacional</span>
                    <span style="font-weight: 800; font-size: 1.05rem; color: {'#047857' if saldo_tot >= 0 else '#B91C1C'};">{_fmt_moeda(saldo_tot, is_gestor)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 10px 0; margin-top: 4px; font-size: 0.88rem; color: #64748B;">
                    <span>Margem Operacional Líquida</span>
                    <span style="font-weight: 700; color: #0D9488;">{_fmt_pct(margem_tot)}</span>
                </div>
            </div>
            """
            st.markdown(dre_html, unsafe_allow_html=True)

        with col_fluxo:
            st.markdown("### 📈 Fluxo Financeiro & Lucratividade Mensal")
            rec_mes = service.repository.receita_por_mes_dict()
            desp_mes = service.repository.despesas_por_mes_dict()

            todos_meses = sorted(set(rec_mes.keys()) | set(desp_mes.keys()))
            if todos_meses:
                df_fin = pd.DataFrame({
                    "Mês": todos_meses,
                    "Receitas (R$)": [rec_mes.get(m, 0.0) for m in todos_meses],
                    "Despesas (R$)": [desp_mes.get(m, 0.0) for m in todos_meses],
                    "Saldo Líquido (R$)": [rec_mes.get(m, 0.0) - desp_mes.get(m, 0.0) for m in todos_meses]
                })

                _plot_fluxo_financeiro(df_fin, is_gestor)
            else:
                st.info("Nenhum histórico financeiro registrado até o momento.")

        st.divider()

        # Botão de Exportação CSV Financeiro
        st.subheader("📥 Emissão Automática de Relatório Financeiro Executivo")
        if todos_meses:
            df_exp_fin = pd.DataFrame([
                {
                    "Mês": m,
                    "Receitas (R$)": rec_mes.get(m, 0.0),
                    "Despesas (R$)": desp_mes.get(m, 0.0),
                    "Saldo Líquido (R$)": rec_mes.get(m, 0.0) - desp_mes.get(m, 0.0)
                } for m in todos_meses
            ])

            st.download_button(
                "📥 Exportar Relatório Financeiro Executivo (CSV)",
                data=df_exp_fin.to_csv(index=False).encode("utf-8"),
                file_name=f"relatorio_bi_financeiro_{hoje.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    # ── 3. OCUPAÇÃO & SUÍTES ─────────────────────────────────────────────────
    with tab_ocupacao:
        st.subheader("🛏️ Indicadores de Ocupação & Desempenho por Suíte")

        oc1, oc2, oc3 = st.columns(3)
        with oc1:
            taxa_hoje = service.suites_ocupadas_hoje()
            st.metric("Ocupação Hoje", _fmt_pct(taxa_hoje))
        with oc2:
            try:
                taxa_per = service.suites_ocupadas_periodo(data_inicio_global, data_fim_global)
                st.metric("Ocupação no Período Selecionado", _fmt_pct(taxa_per))
            except Exception as e:
                st.warning(str(e))
        with oc3:
            dist_stat = service.distribuicao_por_status()
            disponiveis = dist_stat.get("Disponível", 0)
            st.metric("Suítes Disponíveis Agora", disponiveis)

        st.divider()

        col_tipo, col_status = st.columns(2)

        with col_tipo:
            st.markdown("### 📊 Taxa de Ocupação por Tipo de Suíte")
            try:
                ocup_tipo = service.ocupacao_por_tipo(data_inicio_global, data_fim_global)
                if ocup_tipo:
                    df_t = pd.DataFrame(sorted(ocup_tipo.items()), columns=["Tipo de Suíte", "Taxa %"])
                    fig_bar = px.bar(
                        df_t,
                        x="Tipo de Suíte",
                        y="Taxa %",
                        color="Tipo de Suíte",
                        color_discrete_sequence=["#0D9488", "#0F172A", "#D97706", "#E11D48", "#0284C7"],
                        text_auto=".1f"
                    )
                    fig_bar.update_layout(
                        showlegend=False,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=20, b=10),
                        yaxis=dict(title="Ocupação (%)", gridcolor="#F1F5F9"),
                        xaxis=dict(title=""),
                        height=280
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Nenhum dado para ocupação por tipo.")
            except Exception as e:
                st.error(f"Erro ao calcular ocupação por tipo: {e}")

        with col_status:
            st.markdown("### 🏷️ Distribuição de Suítes por Status Atual")
            comp_stat = service.distribuicao_por_status()
            if comp_stat:
                df_st = pd.DataFrame(list(comp_stat.items()), columns=["Status", "Quantidade"])
                _plot_donut_chart(
                    df_st,
                    "Status",
                    "Quantidade",
                    "Status das Suítes",
                    colors=["#047857", "#E11D48", "#D97706", "#B45309", "#475569"]
                )

        st.divider()

        st.markdown("### 🏆 Ranking das Suítes Mais Utilizadas no Período")
        try:
            mais_usadas = service.suites_mais_utilizadas(data_inicio_global, data_fim_global)
            if mais_usadas:
                df_u = pd.DataFrame([
                    {
                        "Suíte Número": r["suite"].numero,
                        "Tipo": r["suite"].tipo,
                        "Valor Diária": r["suite"].valor_diaria,
                        "Total de Reservas": r["qtd_reservas"]
                    } for r in mais_usadas
                ])

                st.dataframe(
                    df_u,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Suíte Número": st.column_config.NumberColumn("Suíte #", format="%d"),
                        "Tipo": st.column_config.TextColumn("Tipo de Suíte"),
                        "Valor Diária": st.column_config.NumberColumn("Valor Diária", format="R$ %.2f"),
                        "Total de Reservas": st.column_config.ProgressColumn(
                            "Total de Reservas",
                            format="%d",
                            min_value=0,
                            max_value=int(df_u["Total de Reservas"].max() or 1)
                        )
                    }
                )

                st.download_button(
                    "📥 Exportar Relatório de Ocupação (CSV)",
                    data=df_u.to_csv(index=False).encode("utf-8"),
                    file_name=f"relatorio_bi_ocupacao_{hoje.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhuma reserva registrada no período para ranking de suítes.")
        except Exception as e:
            st.error(f"Erro: {e}")

    # ── 4. OPERAÇÃO & RECEPÇÃO ───────────────────────────────────────────────
    with tab_operacao:
        st.subheader("⚡ Controle de Desempenho Operacional & Recepção")

        op1, op2, op3, op4 = st.columns(4)

        with op1:
            try:
                atraso = service.taxa_atraso_checkin()
                st.metric("Taxa Atraso Check-in", _fmt_pct(atraso["taxa_atraso"]))
            except Exception:
                st.metric("Taxa Atraso Check-in", "0.0%")

        with op2:
            try:
                st.metric("Atraso Médio Check-in", f"{atraso['atraso_medio_dias']:.1f} dias")
            except Exception:
                st.metric("Atraso Médio Check-in", "0.0 dias")

        with op3:
            tempo_cham = service.tempo_medio_conclusao_chamado()
            st.metric("Tempo Solução Chamados", f"{tempo_cham:.1f} dias")

        with op4:
            taxa_canc_ch = service.taxa_cancelamento_chamados()
            st.metric("Cancelamento Chamados", _fmt_pct(taxa_canc_ch))

        st.divider()

        col_ch_prio, col_ch_tipo = st.columns(2)

        with col_ch_prio:
            st.markdown("### 🎯 Chamados por Prioridade")
            ch_prio = service.distribuicao_chamados_por_prioridade()
            if ch_prio:
                df_cp = pd.DataFrame(list(ch_prio.items()), columns=["Prioridade", "Quantidade"])
                _plot_donut_chart(
                    df_cp,
                    "Prioridade",
                    "Quantidade",
                    "Prioridade dos Chamados",
                    colors=["#E11D48", "#D97706", "#047857"]
                )

        with col_ch_tipo:
            st.markdown("### 🛠️ Chamados por Tipo (Limpeza / Manutenção)")
            ch_tipo = service.quantidade_por_tipo_chamado()
            if ch_tipo:
                df_ct = pd.DataFrame(list(ch_tipo.items()), columns=["Tipo Chamado", "Quantidade"])
                _plot_donut_chart(
                    df_ct,
                    "Tipo Chamado",
                    "Quantidade",
                    "Tipo de Chamado",
                    colors=["#0D9488", "#0F172A", "#0284C7"]
                )

        st.divider()

        st.markdown("### ⚠️ Incidência de Chamados Operacionais por Suíte")
        s_mais_ch = service.suites_mais_chamados(limite=10)
        if s_mais_ch:
            df_smc = pd.DataFrame([
                {
                    "Suíte": f"Suíte {r['suite'].numero}",
                    "Tipo": r["suite"].tipo,
                    "Status Atual": r["suite"].status,
                    "Total Chamados": r["qtd_chamados"]
                } for r in s_mais_ch
            ])

            _plot_ranking_bar(df_smc, "Total Chamados", "Suíte", color_hex="#E11D48")

            st.download_button(
                "📥 Exportar Relatório Operacional (CSV)",
                data=df_smc.to_csv(index=False).encode("utf-8"),
                file_name=f"relatorio_bi_operacional_{hoje.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhum chamado operacional registrado.")

    # ── 5. CRM, SATISFAÇÃO & LAZER ───────────────────────────────────────────
    with tab_crm:
        st.subheader("👥 CRM, Satisfação de Hóspedes & Eventos de Lazer")

        crm1, crm2, crm3 = st.columns(3)

        with crm1:
            rec = service.hospedes_recorrentes()
            st.metric("Hóspedes Recorrentes", len(rec))
        with crm2:
            pico = service.mes_com_mais_cadastros()
            pico_str = f"{pico[0]} ({pico[1]} cad.)" if pico else "N/A"
            st.metric("Mês com Mais Cadastros", pico_str)
        with crm3:
            lt_evt = service.lead_time_medio_inscricao()
            st.metric("Lead Time Inscrição Eventos", f"{lt_evt:.1f} dias")

        st.divider()

        col_h_mes, col_evt_st = st.columns(2)

        with col_h_mes:
            st.markdown("### 📈 Cadastros de Hóspedes por Mês")
            h_mes = service.cadastros_hospedes_por_mes()
            if h_mes:
                df_hm = pd.DataFrame(sorted(h_mes.items()), columns=["Mês", "Cadastros"])
                fig_hm = px.line(
                    df_hm,
                    x="Mês",
                    y="Cadastros",
                    markers=True,
                    color_discrete_sequence=["#0D9488"]
                )
                fig_hm.update_traces(line=dict(width=3))
                fig_hm.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=10),
                    yaxis=dict(gridcolor="#F1F5F9", title="Cadastros"),
                    xaxis=dict(title=""),
                    height=280
                )
                st.plotly_chart(fig_hm, use_container_width=True)

        with col_evt_st:
            st.markdown("### 🎉 Eventos por Status")
            e_stat = service.distribuicao_eventos_por_status()
            if e_stat:
                df_es = pd.DataFrame(list(e_stat.items()), columns=["Status", "Eventos"])
                _plot_donut_chart(
                    df_es,
                    "Status",
                    "Eventos",
                    "Status dos Eventos",
                    colors=["#047857", "#D97706", "#E11D48", "#475569"]
                )

        st.divider()

        st.markdown("### 🌟 Ranking dos Eventos Mais Procurados")
        evts_proc = service.eventos_mais_procurados()
        if evts_proc:
            df_ep = pd.DataFrame([
                {
                    "Nome do Evento": r["evento"].nome_evento,
                    "Capacidade Total": r["evento"].capacidade,
                    "Inscrições": r["qtd_inscricoes"],
                    "Status": r["evento"].status
                } for r in evts_proc
            ])

            st.dataframe(
                df_ep,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome do Evento": st.column_config.TextColumn("Nome do Evento"),
                    "Capacidade Total": st.column_config.NumberColumn("Capacidade Total", format="%d"),
                    "Inscrições": st.column_config.ProgressColumn(
                        "Inscrições",
                        format="%d",
                        min_value=0,
                        max_value=int(df_ep["Capacidade Total"].max() or 1)
                    ),
                    "Status": st.column_config.TextColumn("Status")
                }
            )

            st.download_button(
                "📥 Exportar Relatório de CRM & Eventos (CSV)",
                data=df_ep.to_csv(index=False).encode("utf-8"),
                file_name=f"relatorio_bi_crm_eventos_{hoje.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhum evento registrado com inscrições.")

    # ── 6. CONSUMO & ESTOQUE ─────────────────────────────────────────────────
    with tab_estoque:
        st.subheader("📦 Análise de Consumo, Suprimentos e Insumos")

        e_resumo = service.resumo_estoque()

        st1, st2, st3, st4 = st.columns(4)

        with st1:
            st.metric("Total de Produtos", e_resumo["total_produtos"])
        with st2:
            st.metric("⚠️ Estoque Baixo/Crítico", e_resumo["estoque_baixo"], delta_color="inverse")
        with st3:
            st.metric("🚫 Sem Estoque", e_resumo["sem_estoque"], delta_color="inverse")
        with st4:
            st.metric("💰 Inventário Total", _fmt_moeda(e_resumo["valor_inventario"], is_gestor))

        st.divider()

        col_ped_st, col_prod_top = st.columns(2)

        with col_ped_st:
            st.markdown("### 🛒 Pedidos de Compra por Status")
            ped_stat = service.pedidos_por_status()
            if ped_stat:
                df_ps = pd.DataFrame(list(ped_stat.items()), columns=["Status Pedido", "Quantidade"])
                _plot_donut_chart(
                    df_ps,
                    "Status Pedido",
                    "Quantidade",
                    "Status dos Pedidos",
                    colors=["#047857", "#D97706", "#E11D48", "#0284C7"]
                )

        with col_prod_top:
            st.markdown("### 🏆 Produtos Mais Comprados / Consumidos")
            prods_top = service.produtos_mais_comprados(limite=5)
            if prods_top:
                df_pt = pd.DataFrame(
                    prods_top,
                    columns=["Produto", "Qtd Comprada", "Valor Investido"]
                )

                st.dataframe(
                    df_pt,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Produto": st.column_config.TextColumn("Nome do Produto"),
                        "Qtd Comprada": st.column_config.NumberColumn("Quantidade", format="%d"),
                        "Valor Investido": st.column_config.NumberColumn("Valor Investido", format="R$ %.2f")
                    }
                )

        st.divider()

        st.subheader("📥 Exportação de Relatório de Consumo & Insumos")
        if prods_top:
            df_exp_est = pd.DataFrame(prods_top, columns=["Produto", "Qtd Comprada", "Valor Investido"])
            st.download_button(
                "📥 Exportar Relatório de Consumo (CSV)",
                data=df_exp_est.to_csv(index=False).encode("utf-8"),
                file_name=f"relatorio_bi_estoque_{hoje.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )