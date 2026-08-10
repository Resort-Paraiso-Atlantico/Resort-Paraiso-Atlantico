import streamlit as st
from datetime import date, datetime, timedelta
from app.database import SessionLocal
from app.services.SuiteService import SuiteService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.repositories.ReservaSuiteRepository import ReservaSuiteRepository
from app.theme import aplicar_tema, cabecalho, badge_status, card_item
import pandas as pd

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Suítes", "Cadastro, status e limpeza dos quartos", "🛏️")

DIAS_LIMPEZA_ALERTA = 3


def _status_ocupacao(suite, ocupadas_agora: set) -> str:
    """Status 'de exibição': Manutenção ou Limpeza têm prioridade manual, senão calcula ocupação pela data de hoje."""
    if suite.status in ("Manutenção", "Limpeza"):
        return suite.status
    return "Ocupada" if suite.id_suite in ocupadas_agora else "Disponível"


@st.dialog("➕ Cadastrar Nova Suíte")
def modal_cadastrar_suite():
    st.caption("Suítes novas começam disponíveis. Ocupação é calculada automaticamente pelas reservas.")
    with st.form("form_modal_suite"):
        numero = st.number_input("Número da Suíte", min_value=1, step=1)
        tipo = st.selectbox("Tipo", ["Standard", "Luxo", "Master"])
        capacidade = st.number_input("Capacidade (Hóspedes)", min_value=1, step=1, value=2)
        valor_diaria = st.number_input("Valor da Diária (R$)", min_value=0.0, value=250.00, format="%.2f")
        status = st.selectbox("Status Inicial", ["Disponível", "Limpeza", "Manutenção"])
        submitted = st.form_submit_button("Cadastrar Suíte", type="primary", width="stretch")

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
            st.success(f"Suíte nº {numero_criado} cadastrada com sucesso!")
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar suíte: {e}")


tab_listar, tab_cadastrar, tab_historico = st.tabs(["📋 Listar & Status", "➕ Cadastrar Suíte", "📜 Histórico por Suíte"])

# ── Listar & Limpeza ────────────────────────────────────────────────────────────
with tab_listar:
    hoje = date.today()

    with SessionLocal() as db:
        todas_suites = SuiteService(db).listar_suites()
        reserva_suite_repo = ReservaSuiteRepository(db)
        ocupadas_agora = {
            s.id_suite for s in todas_suites
            if s.status not in ("Manutenção", "Limpeza") and reserva_suite_repo.existe_conflito(s.id_suite, hoje, hoje + timedelta(days=1))
        }

    status_exibicao = {s.id_suite: _status_ocupacao(s, ocupadas_agora) for s in todas_suites}

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", len(todas_suites))
    c2.metric("Disponíveis", sum(1 for s in todas_suites if status_exibicao[s.id_suite] == "Disponível"))
    c3.metric("Ocupadas", sum(1 for s in todas_suites if status_exibicao[s.id_suite] == "Ocupada"))
    c4.metric("Em Limpeza", sum(1 for s in todas_suites if status_exibicao[s.id_suite] == "Limpeza"))
    c5.metric("Manutenção", sum(1 for s in todas_suites if status_exibicao[s.id_suite] == "Manutenção"))

    st.divider()

    c_filtros, c_vis, c_btn = st.columns([4, 2, 2])
    with c_filtros:
        tipos = sorted({s.tipo for s in todas_suites})
        filtro_tipo = st.multiselect("Filtrar Categoria", tipos, default=tipos)
    with c_vis:
        modo_vis = st.radio("Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_suites")
    with c_btn:
        if st.button("➕ Nova Suíte", type="primary", width="stretch", key="btn_nova_suite_top"):
            modal_cadastrar_suite()

    col_status, col_limpeza = st.columns(2)
    filtro_status = col_status.selectbox("Status", ["Todos", "Disponível", "Ocupada", "Limpeza", "Manutenção"])
    somente_sujas = col_limpeza.checkbox("Só precisando de limpeza")

    limite_limpeza = datetime.now() - timedelta(days=DIAS_LIMPEZA_ALERTA)

    suites = [s for s in todas_suites if s.tipo in filtro_tipo]
    if filtro_status != "Todos":
        suites = [s for s in suites if status_exibicao[s.id_suite] == filtro_status]
    if somente_sujas:
        suites = [s for s in suites if s.status == "Limpeza" or s.ultima_limpeza is None or s.ultima_limpeza < limite_limpeza]
    suites = sorted(suites, key=lambda s: s.numero)

    if not suites:
        st.info("Nenhuma suíte encontrada com esse filtro.")
    else:
        if modo_vis == "📊 Tabela":
            dados_tabela = [
                {
                    "Número": f"Nº {s.numero}",
                    "Tipo": s.tipo,
                    "Capacidade": f"{s.capacidade} pax",
                    "Diária": float(s.valor_diaria),
                    "Última Limpeza": s.ultima_limpeza.strftime("%d/%m/%Y %H:%M") if s.ultima_limpeza else "nunca",
                    "Status": status_exibicao[s.id_suite]
                }
                for s in suites
            ]
            st.dataframe(
                dados_tabela,
                width="stretch",
                column_config={
                    "Número": st.column_config.TextColumn("Quarto", width="small"),
                    "Diária": st.column_config.NumberColumn("Valor Diária", format="R$ %.2f"),
                }
            )
        else:
            cols = st.columns(2)
            for i, s in enumerate(suites):
                precisa_limpeza = s.status == "Limpeza" or s.ultima_limpeza is None or s.ultima_limpeza < limite_limpeza
                limpeza_txt = s.ultima_limpeza.strftime("%d/%m/%Y %H:%M") if s.ultima_limpeza else "nunca registrada"
                aviso_limpeza = " · 🧹 <b>em/precisa de limpeza</b>" if precisa_limpeza else ""
                status_atual = status_exibicao[s.id_suite]
                detalhes = f"""
                <strong>Tipo & Cap:</strong> {s.tipo} · {s.capacidade} pax · R$ {s.valor_diaria:,.2f}/diária<br>
                <strong>Última limpeza:</strong> {limpeza_txt}{aviso_limpeza}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(f"Suíte nº {s.numero}", f"Categoria: {s.tipo}", detalhes, status=status_atual),
                        unsafe_allow_html=True,
                    )
                    
                    if status_atual == "Limpeza":
                        if st.button(f"✨ Concluir Limpeza & Liberar — nº {s.numero}", key=f"limpar_{s.id_suite}", type="primary", width="stretch"):
                            try:
                                with SessionLocal() as db:
                                    SuiteService(db).registrar_limpeza(s.id_suite)
                                st.success(f"Limpeza da Suíte nº {s.numero} concluída!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                    elif status_atual == "Manutenção":
                        if st.button(f"🔓 Concluir Manutenção (Liberar) — nº {s.numero}", key=f"forcar_disp_{s.id_suite}", type="primary", width="stretch"):
                            try:
                                with SessionLocal() as db:
                                    SuiteService(db).deixar_disponivel(s.id_suite)
                                st.success(f"Suíte nº {s.numero} liberada para uso!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                    elif precisa_limpeza:
                        if st.button(f"🧹 Registrar limpeza — nº {s.numero}", key=f"limpar_manual_{s.id_suite}", width="stretch"):
                            try:
                                with SessionLocal() as db:
                                    SuiteService(db).registrar_limpeza(s.id_suite)
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))

                    with st.expander(f"⚙️ Gerenciar Status — nº {s.numero}"):
                        st.caption("Alteração manual de status da suíte:")
                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            if st.button("✅ Disponível", key=f"btn_disp_{s.id_suite}", width="stretch", disabled=(s.status == "Disponível")):
                                try:
                                    with SessionLocal() as db:
                                        SuiteService(db).alterar_status(s.id_suite, "Disponível")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                        with col_m2:
                            if st.button("🧹 Limpeza", key=f"btn_limp_{s.id_suite}", width="stretch", disabled=(s.status == "Limpeza")):
                                try:
                                    with SessionLocal() as db:
                                        SuiteService(db).alterar_status(s.id_suite, "Limpeza")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                        with col_m3:
                            if st.button("⚙️ Manutenção", key=f"btn_manut_{s.id_suite}", width="stretch", disabled=(s.status == "Manutenção")):
                                try:
                                    with SessionLocal() as db:
                                        SuiteService(db).alterar_status(s.id_suite, "Manutenção")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))

# ── Cadastrar Suíte ─────────────────────────────────────────────────────────────
with tab_cadastrar:
    st.subheader("Cadastrar nova suíte")
    st.caption("Suítes novas começam disponíveis. Ocupação é calculada automaticamente pelas reservas — não é um status manual.")
    with st.form("form_suite"):
        numero = st.number_input("Número", min_value=1, step=1)
        tipo = st.selectbox("Tipo", ["Standard", "Luxo", "Master"])
        capacidade = st.number_input("Capacidade", min_value=0, step=1)
        valor_diaria = st.number_input("Valor da Diária (R$)", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["Disponível", "Limpeza", "Manutenção"])
        submitted = st.form_submit_button("Cadastrar", width="stretch")

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
    st.subheader("Histórico de Ocupação")

    with SessionLocal() as db:
        suites = SuiteService(db).listar_suites()

    if not suites:
        st.info("Nenhuma suíte cadastrada.")
    else:

        opcoes_suite = {
            f"Nº {s.numero} — {s.tipo}": s
            for s in suites
        }

        suite_selecionada = st.selectbox(
            "Selecione a suíte",
            list(opcoes_suite.keys())
        )

        suite = opcoes_suite[suite_selecionada]

        # ───── Dados da suíte ─────
        st.divider()

        st.subheader(f"Suíte nº {suite.numero}")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Tipo",
            suite.tipo
        )

        col2.metric(
            "Capacidade",
            f"{suite.capacidade} hóspedes"
        )

        col3.metric(
            "Diária",
            f"R$ {suite.valor_diaria:,.2f}"
        )


        col1, col2 = st.columns(2)

        col1.metric(
            "Status",
            suite.status
        )

        col2.metric(
            "Última limpeza",
            suite.ultima_limpeza.strftime("%d/%m/%Y %H:%M")
            if suite.ultima_limpeza
            else "Nunca registrada"
        )


        # ───── Histórico ─────

        st.divider()
        st.subheader("Histórico de ocupação")

        try:
            with SessionLocal() as db:
                vinculos = ReservaSuiteService(db).listar_por_suite(
                    suite.id_suite
                )


            if not vinculos:

                st.info(
                    "Essa suíte ainda não foi vinculada a nenhuma reserva."
                )

            else:

                dados = []

                hoje = date.today()

                for v in vinculos:

                    if v.reserva.status == "Cancelada":
                        situacao = "🔴 Cancelada"

                    elif (
                        v.data_entrada <= hoje
                        and (
                            v.data_saida is None
                            or hoje <= v.data_saida
                        )
                    ):
                        situacao = "🟢 Em andamento"

                    elif v.data_entrada > hoje:
                        situacao = "🟡 Futura"

                    else:
                        situacao = "⚪ Encerrada"


                    dados.append(
                        {
                            "Reserva": f"#{v.id_reserva}",
                            "Entrada": v.data_entrada.strftime("%d/%m/%Y"),
                            "Saída": (
                                v.data_saida.strftime("%d/%m/%Y")
                                if v.data_saida
                                else "-"
                            ),
                            "Situação": situacao
                        }
                    )


                df = pd.DataFrame(dados)

                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True
                )


                # ───── Indicadores ─────

                st.divider()

                total_hospedagens = len(vinculos)

                ultima_ocupacao = max(
                    v.data_entrada
                    for v in vinculos
                )


                ocupada = any(
                    v.reserva.status != "Cancelada"
                    and v.data_entrada <= hoje
                    and (
                        v.data_saida is None
                        or hoje <= v.data_saida
                    )
                    for v in vinculos
                )


                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Total de hospedagens",
                    total_hospedagens
                )

                c2.metric(
                    "Última ocupação",
                    ultima_ocupacao.strftime("%d/%m/%Y")
                )

                c3.metric(
                    "Situação atual",
                    "🟢 Ocupada"
                    if ocupada
                    else "⚪ Disponível"
                )


        except ValueError as e:
            st.error(str(e))

        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")