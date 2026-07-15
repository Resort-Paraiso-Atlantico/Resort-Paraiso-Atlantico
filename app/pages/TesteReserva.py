import streamlit as st
from datetime import date
from app.database import SessionLocal
from app.services.ReservaService import ReservaService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.services.SuiteService import SuiteService
from app.models.Reserva import Reserva

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

st.title("Reservas")

tab_criar, tab_listar, tab_suites = st.tabs(["Nova Reserva", "Listar Reservas", "Vincular Suítes"])

# ── Nova Reserva ──────────────────────────────────────────────────────────────
with tab_criar:
    st.subheader("Criar nova reserva")

    with st.form("form_reserva"):
        cpf_hospede = st.text_input("CPF do Hóspede", max_chars=14, placeholder="000.000.000-00")

        col1, col2 = st.columns(2)
        with col1:
            checkin = st.date_input("Check-in previsto", min_value=date.today())
        with col2:
            checkout = st.date_input("Check-out previsto", min_value=date.today())

        status = st.selectbox("Status", ["Pendente", "Confirmada", "Cancelada"])

        submitted = st.form_submit_button("Criar Reserva", use_container_width=True)

    if submitted:
        if not cpf_hospede.strip():
            st.error("Informe o CPF do hóspede.")
        elif checkin >= checkout:
            st.error("A data de check-in deve ser anterior ao check-out.")
        else:
            try:
                with SessionLocal() as db:
                    service = ReservaService(db)
                    reserva = service.criar_reserva(
                        cpf_hospede=cpf_hospede.strip(),
                        checkin_previsto=checkin,
                        checkout_previsto=checkout,
                        status=status,
                    )
                st.success(f"Reserva #{reserva.id_reserva} criada com sucesso!")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao criar reserva: {e}")

# ── Listar Reservas ───────────────────────────────────────────────────────────
with tab_listar:
    st.subheader("Reservas cadastradas")

    cpf_filtro = st.text_input("Filtrar por CPF (opcional)", placeholder="000.000.000-00")

    if st.button("Buscar", use_container_width=True):
        try:
            with SessionLocal() as db:
                service = ReservaService(db)
                reservas = (
                    service.buscar_por_cpf(cpf_filtro.strip())
                    if cpf_filtro.strip()
                    else service.listar_reservas()
                )

            if not reservas:
                st.info("Nenhuma reserva encontrada.")
            else:
                for r in reservas:
                    with st.expander(f"Reserva #{r.id_reserva} — {r.cpf_hospede} — {r.status}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Check-in", str(r.checkin_previsto))
                        col2.metric("Check-out", str(r.checkout_previsto))
                        valor = f"R$ {r.valor_total:,.2f}" if r.valor_total is not None else "—"
                        col3.metric("Valor Total", valor)
                        st.caption(f"Data da reserva: {r.data_reserva}")
        except Exception as e:
            st.error(f"Erro ao buscar reservas: {e}")

# ── Vincular Suítes ───────────────────────────────────────────────────────────
with tab_suites:
    st.subheader("Vincular suítes a uma reserva")

    with SessionLocal() as db:
        reservas = db.query(Reserva).all()
        suite_service = SuiteService(db)
        reserva_suite_service = ReservaSuiteService(db)
        suites = suite_service.listar_suites()

    if not reservas:
        st.info("Nenhuma reserva cadastrada.")
    elif not suites:
        st.info("Nenhuma suíte cadastrada.")
    else:
        opcoes_reserva = {
            f"#{r.id_reserva} — {r.cpf_hospede} ({r.status})": r.id_reserva
            for r in reservas
        }
        reserva_selecionada = st.selectbox("Selecione a reserva", list(opcoes_reserva.keys()))
        id_reserva_alvo = opcoes_reserva[reserva_selecionada]

        with SessionLocal() as db:
            reserva_suite_service = ReservaSuiteService(db)
            vinculos_da_reserva = reserva_suite_service.listar_por_reserva(id_reserva_alvo)

        vinculos_ativos = [v for v in vinculos_da_reserva if v.data_saida is None]
        ids_suites_vinculadas_ativas = {v.id_suite for v in vinculos_ativos}

        st.divider()
        st.markdown("**Suítes disponíveis para vincular**")

        suites_disponiveis = [s for s in suites if s.status == "Disponível"]

        if not suites_disponiveis:
            st.warning("Não há suítes disponíveis.")
        else:
            for suite in suites_disponiveis:
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
                col1.write(f"**Nº {suite.numero}**")
                col2.write(f"{suite.tipo} · {suite.capacidade} pax")
                col3.write(f"R$ {suite.valor_diaria:,.2f}/dia")
                data_entrada = col4.date_input(
                    "Entrada", value=date.today(), key=f"entrada_{suite.id_suite}", label_visibility="collapsed"
                )

                if col5.button("Vincular", key=f"btn_vincular_{suite.id_suite}"):
                    try:
                        with SessionLocal() as db:
                            service = ReservaSuiteService(db)
                            service.vincular_reserva_suite(
                                id_reserva=id_reserva_alvo,
                                id_suite=suite.id_suite,
                                data_entrada=data_entrada,
                            )
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro: {e}")

        st.divider()
        st.markdown("**Suítes vinculadas a esta reserva**")

        if not vinculos_ativos:
            st.info("Nenhuma suíte vinculada ainda.")
        else:
            for vinculo in vinculos_ativos:
                suite = vinculo.suite
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
                col1.write(f"🛏️ Nº {suite.numero}")
                col2.write(f"{suite.tipo} · {suite.capacidade} pax")
                col3.write(f"R$ {vinculo.valor_diaria:,.2f}/dia · desde {vinculo.data_entrada}")
                data_saida = col4.date_input(
                    "Saída", value=date.today(), key=f"saida_{vinculo.id}", label_visibility="collapsed"
                )

                if col5.button("Desvincular", key=f"btn_desvincular_{vinculo.id}"):
                    try:
                        with SessionLocal() as db:
                            service = ReservaSuiteService(db)
                            service.registrar_saida(vinculo.id, data_saida)
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro: {e}")