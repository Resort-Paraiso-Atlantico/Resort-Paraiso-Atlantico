import streamlit as st
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


tab_suites, tab_eventos, tab_reservas = st.tabs(["Suítes", "Eventos", "Reservas"])

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
            dt_fim = datetime.combine(procurados_fim, time.min) + timedelta(days=1) if procurados_fim else None
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

# ── Reservas ──────────────────────────────────────────────────────────────
with tab_reservas:
    import pandas as pd

    with SessionLocal() as db:
        bi = BIService(db)
        total_futuras     = bi.reservas_futuras()
        duracao_media     = bi.duracao_media_reservas()
        por_mes_todas     = bi.reservas_por_mes()
        por_mes_canceladas = bi.reservas_canceladas_por_mes()
        por_mes_concluidas = bi.reservas_concluidas_por_mes()

    # ── KPIs do topo ──
    c1, c2 = st.columns(2)
    c1.metric("📅 Reservas Futuras", total_futuras)
    c2.metric("🛌 Duração Média das Estadias", f"{duracao_media:.1f} dias")

    st.divider()

    # ── Tabela de volume por mês ──
    st.subheader("📊 Volume de Reservas por Mês")

    meses = sorted(set(list(por_mes_todas.keys()) + list(por_mes_canceladas.keys()) + list(por_mes_concluidas.keys())))

    if not meses:
        st.info("Nenhuma reserva cadastrada.")
    else:
        dados_tabela = []
        for mes in meses:
            todas      = por_mes_todas.get(mes, 0)
            canceladas = por_mes_canceladas.get(mes, 0)
            concluidas = por_mes_concluidas.get(mes, 0)
            ativas     = todas - canceladas
            taxa_cancel = round((canceladas / todas) * 100, 1) if todas > 0 else 0.0
            dados_tabela.append({
                "Mês":             mes,
                "Total":           todas,
                "Ativas":          ativas,
                "Concluídas":      concluidas,
                "Canceladas":      canceladas,
                "Taxa Cancelamento (%)": taxa_cancel,
            })

        df = pd.DataFrame(dados_tabela).sort_values("Mês")

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Mês":                   st.column_config.TextColumn("Mês", width="small"),
                "Total":                 st.column_config.NumberColumn("Total", width="small"),
                "Ativas":                st.column_config.NumberColumn("Ativas", width="small"),
                "Concluídas":            st.column_config.NumberColumn("Concluídas", width="small"),
                "Canceladas":            st.column_config.NumberColumn("Canceladas", width="small"),
                "Taxa Cancelamento (%)": st.column_config.ProgressColumn(
                    "Cancelamento (%)", min_value=0, max_value=100, format="%.1f%%"
                ),
            },
        )

        st.divider()

        # ── Gráfico de barras ──
        st.subheader("📈 Evolução Mensal")
        df_plot = df.set_index("Mês")[["Ativas", "Concluídas", "Canceladas"]]
        st.bar_chart(df_plot)