import streamlit as st
from datetime import date, datetime, time

from app.database import SessionLocal
from app.services.BIService import BIService

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

st.title("BI (Testes)")

TIPOS_SUITE = ["Todos", "Standard", "Luxo", "Master", "Presidencial", "Bangalô"]


def _tipo_selecionado(tipo: str) -> str | None:
    return None if tipo == "Todos" else tipo


tab_suites, tab_eventos = st.tabs(["Suítes", "Eventos"])

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
            for item in resultado:
                s = item["suite"]
                st.write(f"Suíte nº{s.numero} ({s.tipo}) — {item['qtd_reservas']} reservas")
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
                st.json(resultado)
            except Exception as e:
                st.error(f"Erro: {e}")

    with col2:
        st.subheader("Composição por tipo")
        if st.button("Ver composição por tipo"):
            try:
                with SessionLocal() as db:
                    resultado = BIService(db).composicao_por_tipo()
                st.json(resultado)
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
            for tipo, taxa in resultado.items():
                st.write(f"{tipo}: {taxa:.1f}%")
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
            dt_fim = datetime.combine(procurados_fim, time.min) if procurados_fim else None
            with SessionLocal() as db:
                resultado = BIService(db).eventos_mais_procurados(dt_inicio, dt_fim)
            if not resultado:
                st.info("Nenhum resultado.")
            for item in resultado:
                ev = item["evento"]
                st.write(f"{ev.nome_evento} — {item['qtd_inscricoes']} inscrições")
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
            dt_fim = datetime.combine(media_fim, time.min)
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
                st.json(resultado)
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()

    st.subheader("Eventos por mês")
    if st.button("Ver eventos por mês"):
        try:
            with SessionLocal() as db:
                resultado = BIService(db).eventos_por_mes()
            st.json(resultado)
        except Exception as e:
            st.error(f"Erro: {e}")