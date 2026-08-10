import streamlit as st
from datetime import date, datetime, timedelta
from app.database import SessionLocal
from app.services.ReservaService import ReservaService
from app.services.SuiteService import SuiteService
from app.services.EventoService import EventoService
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository
from app.theme import aplicar_tema, cabecalho, badge_status, card_item

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Painel", "Visão geral e indicadores do resort em tempo real", "🏠")

DIAS_LIMPEZA_ALERTA = 3

hoje = date.today()

with SessionLocal() as db:
    reservas = ReservaService(db).listar_reservas()
    suites = SuiteService(db).listar_suites()
    eventos = EventoService(db).listar_eventos_nao_encerrados()
    reserva_suite_repo = ReservaSuiteRepository(db)
    ocupadas_agora = {
        s.id_suite for s in suites
        if s.status not in ("Manutenção", "Limpeza") and reserva_suite_repo.existe_conflito(s.id_suite, hoje, hoje + timedelta(days=1))
    }

# ── KPIs principais ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hospedados agora", sum(1 for r in reservas if r.status == "Hospedado"))
c2.metric("Check-ins hoje", sum(1 for r in reservas if r.status == "Confirmada" and r.checkin_previsto == hoje))
c3.metric("Check-outs hoje", sum(1 for r in reservas if r.status == "Hospedado" and r.checkout_previsto == hoje))
c4.metric("Eventos ativos", len(eventos))

st.divider()

col_esq, col_dir = st.columns(2)

# ── Ocupação das suítes ────────────────────────────────────────────────────────
with col_esq:
    st.subheader("🛏️ Ocupação das suítes")
    total = len(suites) or 1
    ocupadas = len(ocupadas_agora)
    em_limpeza = sum(1 for s in suites if s.status == "Limpeza")
    manutencao = sum(1 for s in suites if s.status == "Manutenção")
    disponiveis = max(0, len(suites) - ocupadas - em_limpeza - manutencao)

    st.progress(ocupadas / total)
    st.caption(f"**{ocupadas}** de **{len(suites)}** suítes ocupadas no momento")

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Disponíveis", disponiveis)
    sc2.metric("Ocupadas", ocupadas)
    sc3.metric("Limpeza", em_limpeza)
    sc4.metric("Manutenção", manutencao)

# ── Alerta de limpeza ──────────────────────────────────────────────────────────
with col_dir:
    st.subheader("🧹 Limpeza pendente")
    limite = datetime.now() - timedelta(days=DIAS_LIMPEZA_ALERTA)
    pendentes = [
        s for s in suites
        if s.status == "Limpeza"
        or (s.id_suite not in ocupadas_agora and s.status != "Manutenção" and (s.ultima_limpeza is None or s.ultima_limpeza < limite))
    ]
    if not pendentes:
        st.success("✨ Nenhuma suíte precisa de limpeza no momento.")
    else:
        st.warning(f"⚠️ **{len(pendentes)} suíte(s)** necessitando de limpeza no momento.")
        for s in pendentes:
            desde = s.ultima_limpeza.strftime("%d/%m %H:%M") if s.ultima_limpeza else "nunca registrada"
            detalhes = f"Status atual: <strong>{s.status}</strong> · Última limpeza: <strong>{desde}</strong>"
            st.markdown(
                card_item(f"Suíte nº {s.numero}", f"{s.tipo} · {s.capacidade} pax", detalhes, status=s.status),
                unsafe_allow_html=True
            )
        st.caption("Registre a limpeza na página **Suítes**.")

st.divider()

# ── Reservas por status ────────────────────────────────────────────────────────
st.subheader("📋 Reservas por status")
status_labels = ["Pendente", "Confirmada", "Hospedado", "Finalizada", "Cancelada"]
cols = st.columns(len(status_labels))
for col, status in zip(cols, status_labels):
    qtd = sum(1 for r in reservas if r.status == status)
    col.metric(f"{status}", qtd)