import streamlit as st
from datetime import datetime
from app.database import SessionLocal
from app.services.ChamadoService import ChamadoService
from app.services.SuiteService import SuiteService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Chamados", "Gestão de limpeza e manutenção das suítes", "🔧")

ICONE_TIPO = {"Limpeza": "🧹", "Manutenção": "⚙️"}
ICONE_PRIORIDADE = {"Urgente": "🔴", "Alta": "🟠", "Média": "🟡", "Baixa": "🟢"}


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_abertos, tab_abrir, tab_historico = st.tabs([
    "📋 Chamados Abertos",
    "➕ Abrir Chamado",
    "📜 Histórico",
])


# ── Chamados Abertos ──────────────────────────────────────────────────────────
with tab_abertos:
    filtro_tipo = st.radio(
        "Filtrar por tipo",
        ["Todos", "Limpeza", "Manutenção"],
        horizontal=True,
    )

    with SessionLocal() as db:
        service = ChamadoService(db)
        tipo_param = None if filtro_tipo == "Todos" else filtro_tipo
        chamados = service.listar_pendentes(tipo=tipo_param)

    st.divider()

    if not chamados:
        st.success("✅ Nenhum chamado aberto no momento.")
    else:
        st.caption(f"**{len(chamados)} chamado(s)** aberto(s) — ordenados por prioridade e data de abertura.")
        for c in chamados:
            icone_tipo = ICONE_TIPO.get(c.tipo, "📋")
            icone_pri = ICONE_PRIORIDADE.get(c.prioridade, "")
            suite_label = f"Suíte nº {c.suite.numero}" if c.suite else f"Suite ID {c.id_suite}"
            detalhes = f"""
            <strong>Suíte:</strong> {suite_label} · <strong>Tipo:</strong> {icone_tipo} {c.tipo}<br>
            <strong>Prioridade:</strong> {icone_pri} {c.prioridade} · <strong>Aberto em:</strong> {c.data_abertura.strftime("%d/%m/%Y %H:%M")}<br>
            <strong>Descrição:</strong> {c.descricao}
            """
            st.markdown(
                card_item(
                    f"Chamado #{c.id_chamado}",
                    f"{icone_tipo} {c.tipo}",
                    detalhes,
                    status=c.prioridade if c.tipo == "Manutenção" else "Limpeza",
                ),
                unsafe_allow_html=True,
            )

            col_concluir, col_cancelar = st.columns(2)
            with col_concluir:
                if st.button(f"✅ Concluir #{c.id_chamado}", key=f"concluir_{c.id_chamado}", type="primary", width="stretch"):
                    try:
                        with SessionLocal() as db:
                            ChamadoService(db).concluir_chamado(c.id_chamado)
                        st.success(f"Chamado #{c.id_chamado} concluído! Suíte liberada.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
            with col_cancelar:
                if st.button(f"❌ Cancelar #{c.id_chamado}", key=f"cancelar_{c.id_chamado}", width="stretch"):
                    try:
                        with SessionLocal() as db:
                            ChamadoService(db).cancelar_chamado(c.id_chamado)
                        st.warning(f"Chamado #{c.id_chamado} cancelado. Suíte liberada.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))


# ── Abrir Chamado ─────────────────────────────────────────────────────────────
with tab_abrir:
    with SessionLocal() as db:
        suites = SuiteService(db).listar_suites()

    suites_disponiveis = [s for s in suites if s.status in ("Disponível", "Limpeza", "Manutenção")]

    if not suites_disponiveis:
        st.info("Nenhuma suíte disponível para abrir chamado.")
    else:
        with st.form("form_abrir_chamado"):
            opcoes_suite = {f"Nº {s.numero} — {s.tipo} ({s.status})": s.id_suite for s in suites_disponiveis}
            suite_sel = st.selectbox("Suíte", list(opcoes_suite.keys()))

            col_tipo, col_prioridade = st.columns(2)
            tipo = col_tipo.selectbox("Tipo", ["Limpeza", "Manutenção"])
            prioridade = col_prioridade.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])

            descricao = st.text_area("Descrição", placeholder="Descreva o problema ou necessidade...")

            submitted = st.form_submit_button("📨 Abrir Chamado", type="primary", width="stretch")

        if submitted:
            try:
                with SessionLocal() as db:
                    chamado = ChamadoService(db).abrir_chamado(
                        id_suite=opcoes_suite[suite_sel],
                        tipo=tipo,
                        prioridade=prioridade,
                        descricao=descricao,
                    )
                st.success(f"Chamado #{chamado.id_chamado} aberto com sucesso! Suíte marcada como {tipo}.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao abrir chamado: {e}")


# ── Histórico ─────────────────────────────────────────────────────────────────
with tab_historico:
    filtro_hist = st.radio(
        "Exibir",
        ["Concluídos", "Cancelados"],
        horizontal=True,
    )

    with SessionLocal() as db:
        service = ChamadoService(db)
        historico = service.listar_concluidos() if filtro_hist == "Concluídos" else service.listar_cancelados()

    st.divider()

    if not historico:
        st.info(f"Nenhum chamado {filtro_hist.lower()} encontrado.")
    else:
        st.caption(f"**{len(historico)} chamado(s)** {filtro_hist.lower()}.")
        for c in historico:
            icone_tipo = ICONE_TIPO.get(c.tipo, "📋")
            suite_label = f"Suíte nº {c.suite.numero}" if c.suite else f"Suite ID {c.id_suite}"
            duracao = ""
            if c.data_conclusao and c.data_abertura:
                delta = c.data_conclusao - c.data_abertura
                horas = int(delta.total_seconds() // 3600)
                minutos = int((delta.total_seconds() % 3600) // 60)
                duracao = f" · <strong>Duração:</strong> {horas}h {minutos}min"

            detalhes = f"""
            <strong>Suíte:</strong> {suite_label} · <strong>Tipo:</strong> {icone_tipo} {c.tipo}<br>
            <strong>Aberto em:</strong> {c.data_abertura.strftime("%d/%m/%Y %H:%M")} · 
            <strong>Encerrado em:</strong> {c.data_conclusao.strftime("%d/%m/%Y %H:%M") if c.data_conclusao else "—"}{duracao}<br>
            <strong>Descrição:</strong> {c.descricao}
            """
            st.markdown(
                card_item(
                    f"Chamado #{c.id_chamado}",
                    f"{icone_tipo} {c.tipo} · {c.prioridade}",
                    detalhes,
                    status=c.status,
                ),
                unsafe_allow_html=True,
            )