import streamlit as st
from datetime import date
from app.database import SessionLocal
from app.services.ReservaSuiteService import ReservaSuiteService
from app.services.SuiteService import SuiteService
from app.models.Reserva import Reserva
from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Reserva ↔ Suíte", "Histórico, valores e correções de vínculos", "🔗")

tab_por_suite, tab_valor_estadia, tab_valor_total, tab_corrigir = st.tabs([
    "Histórico por Suíte",
    "Calcular Valor da Estadia",
    "Valor Total da Reserva",
    "Corrigir Data de Entrada",
])

# ── Histórico por Suíte ────────────────────────────────────────────────────────
with tab_por_suite:
    st.subheader("Quais reservas essa suíte já teve")

    with SessionLocal() as db:
        suite_service = SuiteService(db)
        suites = suite_service.listar_suites()

    if not suites:
        st.info("Nenhuma suíte cadastrada.")
    else:
        opcoes_suite = {f"Nº {s.numero} — {s.tipo}": s.id_suite for s in suites}
        suite_selecionada = st.selectbox("Selecione a suíte", list(opcoes_suite.keys()))
        id_suite_alvo = opcoes_suite[suite_selecionada]

        if st.button("Buscar histórico", use_container_width=True):
            try:
                with SessionLocal() as db:
                    service = ReservaSuiteService(db)
                    vinculos = service.listar_por_suite(id_suite_alvo)

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

# ── Calcular Valor da Estadia ──────────────────────────────────────────────────
with tab_valor_estadia:
    st.subheader("Calcular valor de um vínculo específico")

    id_vinculo = st.number_input("ID do vínculo (ReservaSuite)", min_value=1, step=1, key="id_valor_estadia")

    if st.button("Calcular valor", use_container_width=True):
        try:
            with SessionLocal() as db:
                service = ReservaSuiteService(db)
                valor = service.calcular_valor_estadia(int(id_vinculo))
            st.success(f"Valor da estadia: R$ {valor:,.2f}")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao calcular valor: {e}")

# ── Valor Total da Reserva ─────────────────────────────────────────────────────
with tab_valor_total:
    st.subheader("Somar o valor de todas as suítes de uma reserva")

    with SessionLocal() as db:
        reservas = db.query(Reserva).all()

    if not reservas:
        st.info("Nenhuma reserva cadastrada.")
    else:
        opcoes_reserva = {
            f"#{r.id_reserva} — {r.cpf_hospede} ({r.status})": r.id_reserva
            for r in reservas
        }
        reserva_selecionada = st.selectbox("Selecione a reserva", list(opcoes_reserva.keys()), key="select_valor_total")
        id_reserva_alvo = opcoes_reserva[reserva_selecionada]

        if st.button("Calcular valor total", use_container_width=True):
            try:
                with SessionLocal() as db:
                    service = ReservaSuiteService(db)
                    valor_total = service.calcular_valor_total_reserva(id_reserva_alvo)
                st.success(f"Valor total da reserva: R$ {valor_total:,.2f}")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao calcular valor total: {e}")

# ── Corrigir Data de Entrada ───────────────────────────────────────────────────
with tab_corrigir:
    st.subheader("Corrigir a data de entrada de um vínculo")

    id_vinculo_corrigir = st.number_input("ID do vínculo (ReservaSuite)", min_value=1, step=1, key="id_corrigir")
    nova_data_entrada = st.date_input("Nova data de entrada", value=date.today(), key="nova_data_entrada")

    if st.button("Corrigir", use_container_width=True):
        try:
            with SessionLocal() as db:
                service = ReservaSuiteService(db)
                service.corrigir_data_entrada(int(id_vinculo_corrigir), nova_data_entrada)
            st.success("Data de entrada corrigida com sucesso!")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao corrigir data: {e}")