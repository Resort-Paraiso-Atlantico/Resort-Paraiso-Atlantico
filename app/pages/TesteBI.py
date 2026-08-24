import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta

from app.database import SessionLocal
from app.services.BIService import BIService

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

st.title("BI (Testes)")

TIPOS_SUITE = ["Todos", "Standard", "Luxo", "Master", "Presidencial", "Bangalô"]


def _tipo_selecionado(tipo: str) -> str | None:
    return None if tipo == "Todos" else tipo


def _bar_chart(resultado: dict, index_label: str, value_label: str):
    """Renderiza um dict {chave: valor} como gráfico de barras, ordenado pela chave."""
    if not resultado:
        st.info("Nenhum resultado.")
        return
    df = pd.DataFrame(sorted(resultado.items()), columns=[index_label, value_label]).set_index(index_label)
    st.bar_chart(df)


tab_suites, tab_eventos, tab_reservas, tab_chamados, tab_hospedes = st.tabs(
    ["Suítes", "Eventos", "Reservas", "Chamados", "Hóspedes"]
)

# ── Suítes ────────────────────────────────────────────────────────────────
with tab_suites:
    st.subheader("Ocupação hoje")
    tipo_hoje = st.selectbox("Tipo", TIPOS_SUITE, key="tipo_hoje")
    if st.button("Calcular ocupação de hoje"):
        try:
            with SessionLocal() as db:
                taxa = BIService(db).suites_ocupadas_hoje(_tipo_selecionado(tipo_hoje))
            st.metric("Ocupação hoje", f"{taxa:.1f}%")
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Ocupação no período")
    col1, col2, col3 = st.columns(3)
    with col1:
        periodo_inicio = st.date_input("Data início", value=date.today(), key="periodo_inicio")
    with col2:
        periodo_fim = st.date_input("Data fim", value=date.today(), key="periodo_fim")
    with col3:
        tipo_periodo = st.selectbox("Tipo", TIPOS_SUITE, key="tipo_periodo")
    if st.button("Calcular ocupação do período"):
        try:
            with SessionLocal() as db:
                taxa = BIService(db).suites_ocupadas_periodo(
                    periodo_inicio, periodo_fim, _tipo_selecionado(tipo_periodo)
                )
            st.metric("Ocupação no período", f"{taxa:.1f}%")
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Suítes mais utilizadas")
    col1, col2, col3 = st.columns(3)
    with col1:
        usadas_inicio = st.date_input("Data início (opcional)", value=None, key="usadas_inicio")
    with col2:
        usadas_fim = st.date_input("Data fim (opcional)", value=None, key="usadas_fim")
    with col3:
        tipo_usadas = st.selectbox("Tipo", TIPOS_SUITE, key="tipo_usadas")
    if st.button("Listar mais utilizadas"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).suites_mais_utilizadas(
                    usadas_inicio, usadas_fim, _tipo_selecionado(tipo_usadas)
                )
            if not resultado:
                st.info("Nenhum resultado.")
            else:
                df = pd.DataFrame(
                    [{"Suíte": r["suite"].numero, "Tipo": r["suite"].tipo, "Reservas": r["qtd_reservas"]} for r in resultado]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribuição por status")
        if st.button("Ver distribuição por status"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).distribuicao_por_status()
                _bar_chart(resultado, "Status", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Composição por tipo")
        if st.button("Ver composição por tipo"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).composicao_por_tipo()
                _bar_chart(resultado, "Tipo", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Ocupação por tipo (período)")
    col1, col2 = st.columns(2)
    with col1:
        tipo_ocup_inicio = st.date_input("Data início", value=date.today(), key="tipo_ocup_inicio")
    with col2:
        tipo_ocup_fim = st.date_input("Data fim", value=date.today(), key="tipo_ocup_fim")
    if st.button("Calcular ocupação por tipo"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).ocupacao_por_tipo(tipo_ocup_inicio, tipo_ocup_fim)
            _bar_chart(resultado, "Tipo", "Ocupação (%)")
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

# ── Eventos ───────────────────────────────────────────────────────────────
with tab_eventos:
    st.subheader("Taxa de ocupação de um evento")
    id_evento = st.number_input("ID do evento", min_value=1, step=1, key="id_evento")
    if st.button("Calcular ocupação do evento"):
        try:
            with SessionLocal() as db:
                taxa = BIService(db).evento_taxa_ocupacao(int(id_evento))
            st.metric("Ocupação do evento", f"{taxa:.1f}%")
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Eventos mais procurados")
    col1, col2 = st.columns(2)
    with col1:
        procurados_inicio = st.date_input("Data início (opcional)", value=None, key="procurados_inicio")
    with col2:
        procurados_fim = st.date_input("Data fim (opcional)", value=None, key="procurados_fim")
    if st.button("Listar mais procurados"):
        try:
            dt_inicio = datetime.combine(procurados_inicio, time.min) if procurados_inicio else None
            dt_fim = datetime.combine(procurados_fim, time.min) + timedelta(days=1) if procurados_fim else None
            with SessionLocal() as db:
                resultado = BIService(db).eventos_mais_procurados(dt_inicio, dt_fim)
            if not resultado:
                st.info("Nenhum resultado.")
            else:
                df = pd.DataFrame(
                    [{"Evento": r["evento"].nome_evento, "Inscrições": r["qtd_inscricoes"]} for r in resultado]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Ocupação média dos eventos no período")
    col1, col2 = st.columns(2)
    with col1:
        media_inicio = st.date_input("Data início", value=date.today(), key="media_inicio")
    with col2:
        media_fim = st.date_input("Data fim", value=date.today(), key="media_fim")
    if st.button("Calcular ocupação média"):
        try:
            dt_inicio = datetime.combine(media_inicio, time.min)
            dt_fim = datetime.combine(media_fim, time.min) + timedelta(days=1)
            with SessionLocal() as db:
                taxa = BIService(db).ocupacao_media_eventos_periodo(dt_inicio, dt_fim)
            st.metric("Ocupação média", f"{taxa:.1f}%")
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lead time médio de inscrição")
        if st.button("Calcular lead time"):
            try:
                with SessionLocal() as db:
                    dias = BIService(db).lead_time_medio_inscricao()
                st.metric("Lead time médio", f"{dias:.1f} dias")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Distribuição por status")
        if st.button("Ver distribuição de eventos por status"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).distribuicao_eventos_por_status()
                _bar_chart(resultado, "Status", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Eventos por mês")
    if st.button("Ver eventos por mês"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).eventos_por_mes()
            _bar_chart(resultado, "Mês", "Eventos")
        except Exception as e:
            st.error(f"Erro: {e}")

# ── Reservas ─────────────────────────────────────────────────────────────
with tab_reservas:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Reservas por mês")
        if st.button("Ver reservas por mês"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).reservas_por_mes()
                _bar_chart(resultado, "Mês", "Reservas")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Canceladas por mês")
        if st.button("Ver canceladas por mês"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).reservas_canceladas_por_mes()
                _bar_chart(resultado, "Mês", "Canceladas")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col3:
        st.subheader("Concluídas por mês")
        if st.button("Ver concluídas por mês"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).reservas_concluidas_por_mes()
                _bar_chart(resultado, "Mês", "Concluídas")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Reservas futuras")
        if st.button("Calcular reservas futuras"):
            try:
                with SessionLocal() as db:
                    qtd = BIService(db).reservas_futuras()
                st.metric("Reservas futuras", qtd)
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Duração média")
        if st.button("Calcular duração média"):
            try:
                with SessionLocal() as db:
                    dias = BIService(db).duracao_media_reservas()
                st.metric("Duração média", f"{dias:.1f} dias")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col3:
        st.subheader("Taxa de cancelamento")
        if st.button("Calcular taxa de cancelamento"):
            try:
                with SessionLocal() as db:
                    taxa = BIService(db).taxa_cancelamento_reservas()
                st.metric("Cancelamento", f"{taxa:.1f}%")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Atraso no check-in")
    if st.button("Calcular atraso no check-in"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).taxa_atraso_checkin()
            col1, col2 = st.columns(2)
            col1.metric("Taxa de atraso", f"{resultado['taxa_atraso']:.1f}%")
            col2.metric("Atraso médio", f"{resultado['atraso_medio_dias']:.1f} dias")
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Distribuição por status")
    if st.button("Ver reservas por status"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).distribuicao_reservas_por_status()
            _bar_chart(resultado, "Status", "Quantidade")
        except Exception as e:
            st.error(f"Erro: {e}")

# ── Chamados ─────────────────────────────────────────────────────────────
with tab_chamados:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tempo médio de conclusão")
        if st.button("Calcular tempo médio de conclusão"):
            try:
                with SessionLocal() as db:
                    dias = BIService(db).tempo_medio_conclusao_chamado()
                st.metric("Tempo médio", f"{dias:.1f} dias")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Taxa de cancelamento")
        if st.button("Calcular taxa de cancelamento de chamados"):
            try:
                with SessionLocal() as db:
                    taxa = BIService(db).taxa_cancelamento_chamados()
                st.metric("Cancelamento", f"{taxa:.1f}%")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Chamados por tipo de suíte")
        if st.button("Ver chamados por tipo de suíte"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).chamados_por_tipo_suite()
                _bar_chart(resultado, "Tipo de suíte", "Chamados")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Quantidade por tipo de chamado")
        if st.button("Ver quantidade por tipo de chamado"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).quantidade_por_tipo_chamado()
                _bar_chart(resultado, "Tipo", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribuição por status")
        if st.button("Ver chamados por status"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).distribuicao_chamados_por_status()
                _bar_chart(resultado, "Status", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Distribuição por prioridade")
        if st.button("Ver chamados por prioridade"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).distribuicao_chamados_por_prioridade()
                _bar_chart(resultado, "Prioridade", "Quantidade")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Suítes com mais chamados")
    limite_chamados = st.number_input("Limite de suítes", min_value=1, max_value=50, value=10, key="limite_chamados")
    if st.button("Listar suítes com mais chamados"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).suites_mais_chamados(int(limite_chamados))
            if not resultado:
                st.info("Nenhum resultado.")
            else:
                df = pd.DataFrame(
                    [{"Suíte": r["suite"].numero, "Tipo": r["suite"].tipo, "Chamados": r["qtd_chamados"]} for r in resultado]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro: {e}")

# ── Hóspedes ─────────────────────────────────────────────────────────────
with tab_hospedes:
    st.subheader("Cadastros por mês")
    if st.button("Ver cadastros por mês"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).cadastros_hospedes_por_mes()
            _bar_chart(resultado, "Mês", "Cadastros")
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Mês com mais cadastros")
    if st.button("Calcular mês com mais cadastros"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).mes_com_mais_cadastros()
            if resultado is None:
                st.info("Nenhum resultado.")
            else:
                mes, qtd = resultado
                st.metric("Mês com mais cadastros", mes, delta=f"{qtd} cadastros")
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Hóspedes recorrentes")
    if st.button("Listar hóspedes recorrentes"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).hospedes_recorrentes()
            if not resultado:
                st.info("Nenhum resultado.")
            else:
                df = pd.DataFrame(
                    [{"Hóspede": r["hospede"].nome, "Reservas": r["qtd_reservas"]} for r in resultado]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erro: {e}")