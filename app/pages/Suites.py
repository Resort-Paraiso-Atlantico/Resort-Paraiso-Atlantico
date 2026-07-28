import streamlit as st
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.services.SuiteService import SuiteService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.theme import aplicar_tema, cabecalho, badge_status

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Suítes", "Cadastro, status e limpeza dos quartos", "🛏️")

DIAS_LIMPEZA_ALERTA = 3

tab_listar, tab_cadastrar, tab_historico = st.tabs(["Listar & Limpeza", "Cadastrar Suíte", "Histórico por Suíte"])

# ── Listar & Limpeza ────────────────────────────────────────────────────────────
with tab_listar:
    with SessionLocal() as db:
        todas_suites = SuiteService(db).listar_suites()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(todas_suites))
    c2.metric("Disponíveis", sum(1 for s in todas_suites if s.status == "Disponível"))
    c3.metric("Ocupadas", sum(1 for s in todas_suites if s.status == "Ocupada"))
    c4.metric("Manutenção", sum(1 for s in todas_suites if s.status == "Manutenção"))

    st.divider()

    col_tipo, col_status, col_limpeza = st.columns([2, 2, 2])
    tipos = sorted({s.tipo for s in todas_suites})
    filtro_tipo = col_tipo.multiselect("Tipo", tipos, default=tipos)
    filtro_status = col_status.selectbox("Status", ["Todos", "Disponível", "Ocupada", "Manutenção"])
    somente_sujas = col_limpeza.checkbox("Só precisando de limpeza")

    limite_limpeza = datetime.now() - timedelta(days=DIAS_LIMPEZA_ALERTA)

    suites = [s for s in todas_suites if s.tipo in filtro_tipo]
    if filtro_status != "Todos":
        suites = [s for s in suites if s.status == filtro_status]
    if somente_sujas:
        suites = [s for s in suites if s.ultima_limpeza is None or s.ultima_limpeza < limite_limpeza]
    suites = sorted(suites, key=lambda s: s.numero)

    if not suites:
        st.info("Nenhuma suíte encontrada com esse filtro.")
    else:
        cols = st.columns(2)
        for i, s in enumerate(suites):
            precisa_limpeza = s.ultima_limpeza is None or s.ultima_limpeza < limite_limpeza
            limpeza_txt = s.ultima_limpeza.strftime("%d/%m/%Y %H:%M") if s.ultima_limpeza else "nunca registrada"
            aviso_limpeza = " · 🧹 <b>precisa de limpeza</b>" if precisa_limpeza else ""
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">
                        <span class="resort-suite-number">Suíte nº {s.numero}</span>
                        &nbsp;{badge_status(s.status)}
                        <div class="resort-suite-meta">
                            {s.tipo} · {s.capacidade} pax · R$ {s.valor_diaria:,.2f}/diária<br>
                            Última limpeza: {limpeza_txt}{aviso_limpeza}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if precisa_limpeza:
                    if st.button(f"🧹 Registrar limpeza — nº {s.numero}", key=f"limpar_{s.id_suite}", use_container_width=True):
                        try:
                            with SessionLocal() as db:
                                SuiteService(db).registrar_limpeza(s.id_suite)
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

# ── Cadastrar Suíte ─────────────────────────────────────────────────────────────
with tab_cadastrar:
    st.subheader("Cadastrar nova suíte")
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
                suite = SuiteService(db).criar_suite(
                    numero=int(numero),
                    tipo=tipo,
                    capacidade=int(capacidade),
                    valor_diaria=valor_diaria,
                    status=status,
                )
                numero_criado = suite.numero
            st.success(f"Suíte #{numero_criado} cadastrada! Última limpeza registrada como agora.")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar suíte: {e}")

# ── Histórico por Suíte ─────────────────────────────────────────────────────────
with tab_historico:
    st.subheader("Quais reservas essa suíte já teve")

    with SessionLocal() as db:
        suites = SuiteService(db).listar_suites()

    if not suites:
        st.info("Nenhuma suíte cadastrada.")
    else:
        opcoes_suite = {f"Nº {s.numero} — {s.tipo}": s.id_suite for s in suites}
        suite_selecionada = st.selectbox("Selecione a suíte", list(opcoes_suite.keys()))
        id_suite_alvo = opcoes_suite[suite_selecionada]

        try:
            with SessionLocal() as db:
                vinculos = ReservaSuiteService(db).listar_por_suite(id_suite_alvo)

            if not vinculos:
                st.info("Essa suíte ainda não foi vinculada a nenhuma reserva.")
            else:
                for v in vinculos:
                    situacao = "🟢 Em andamento" if v.data_saida is None else "⚪ Encerrada"
                    with st.expander(f"Reserva #{v.id_reserva} — {situacao}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Entrada", str(v.data_entrada))
                        col2.metric("Saída", str(v.data_saida) if v.data_saida else "—")
                        col3.metric("Diária", f"R$ {v.valor_diaria:,.2f}")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")
