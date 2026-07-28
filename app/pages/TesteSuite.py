# TesteSuite.py
import streamlit as st
from app.database import SessionLocal
from app.services.SuiteService import SuiteService
from app.theme import aplicar_tema, cabecalho, badge_status

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Suítes", "Cadastre e acompanhe os quartos do resort", "🛏️")

tab_criar, tab_listar = st.tabs(["Cadastrar Suíte", "Listar Suítes"])

# ── Cadastrar Suíte ───────────────────────────────────────────────────────────
with tab_criar:
    st.subheader("Cadastrar suíte")

    with st.form("form_suite"):
        numero = st.number_input("Número", min_value=1, step=1)
        tipo = st.selectbox("Tipo", ["Standard", "Luxo", "Master"])
        capacidade = st.number_input("Capacidade", min_value=1, step=1)
        valor_diaria = st.number_input("Valor da Diária (R$)", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["Disponível", "Ocupada", "Manutenção"])

        submitted = st.form_submit_button("Cadastrar", use_container_width=True)

    if submitted:
        try:
            with SessionLocal() as db:
                service = SuiteService(db)
                suite = service.criar_suite(
                    numero=int(numero),
                    tipo=tipo,
                    capacidade=int(capacidade),
                    valor_diaria=valor_diaria,
                    status=status,
                )
                numero_criado = suite.numero
            st.success(f"Suíte #{numero_criado} cadastrada com sucesso!")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar suíte: {e}")

# ── Listar Suítes ─────────────────────────────────────────────────────────────
with tab_listar:
    st.subheader("Suítes cadastradas")

    try:
        with SessionLocal() as db:
            service = SuiteService(db)
            todas_suites = service.listar_suites()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(todas_suites))
        c2.metric("Disponíveis", sum(1 for s in todas_suites if s.status == "Disponível"))
        c3.metric("Ocupadas", sum(1 for s in todas_suites if s.status == "Ocupada"))
        c4.metric("Manutenção", sum(1 for s in todas_suites if s.status == "Manutenção"))

        st.divider()

        col_tipo, col_status, col_atualizar = st.columns([2, 2, 1])
        tipos = sorted({s.tipo for s in todas_suites})
        filtro_tipo = col_tipo.multiselect("Filtrar por tipo", tipos, default=tipos)
        filtro_status = col_status.selectbox(
            "Filtrar por status", ["Todos", "Disponível", "Ocupada", "Manutenção"]
        )
        with col_atualizar:
            st.write("")
            if st.button("🔄 Atualizar", use_container_width=True):
                st.rerun()

        suites = [s for s in todas_suites if s.tipo in filtro_tipo]
        if filtro_status != "Todos":
            suites = [s for s in suites if s.status == filtro_status]
        suites = sorted(suites, key=lambda s: s.numero)

        if not suites:
            st.info("Nenhuma suíte encontrada com esse filtro.")
        else:
            cols = st.columns(2)
            for i, s in enumerate(suites):
                with cols[i % 2]:
                    st.markdown(
                        f"""
                        <div class="resort-suite-card">
                            <span class="resort-suite-number">Suíte nº {s.numero}</span>
                            &nbsp;{badge_status(s.status)}
                            <div class="resort-suite-meta">
                                {s.tipo} · {s.capacidade} pax · R$ {s.valor_diaria:,.2f}/diária
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.error(f"Erro ao buscar suítes: {e}")
