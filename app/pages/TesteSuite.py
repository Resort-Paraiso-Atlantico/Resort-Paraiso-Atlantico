# TesteSuite.py
import streamlit as st
from app.database import SessionLocal
from app.services.SuiteService import SuiteService

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

st.title("Suítes")

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

    if st.button("Atualizar", use_container_width=True):
        st.rerun()

    try:
        with SessionLocal() as db:
            service = SuiteService(db)
            suites = service.listar_suites()

        if not suites:
            st.info("Nenhuma suíte encontrada.")
        else:
            for s in suites:
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 2, 2, 2])
                col1.write(f"**Nº {s.numero}**")
                col2.write(f"{s.tipo} · {s.capacidade} pax")
                col3.write(f"R$ {s.valor_diaria:,.2f}")
                col4.write(s.status)

                if s.status != "Disponível":
                    if col5.button("Deixar disponível", key=f"btn_disponivel_{s.id_suite}"):
                        try:
                            with SessionLocal() as db:
                                service = SuiteService(db)
                                service.deixar_disponivel(s.id_suite)
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error(f"Erro: {e}")
    except Exception as e:
        st.error(f"Erro ao buscar suítes: {e}")