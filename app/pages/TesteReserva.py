import re
import streamlit as st
from datetime import date, timedelta
from app.database import SessionLocal
from app.services.ReservaService import ReservaService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.services.SuiteService import SuiteService
from app.services.HospedeService import HospedeService
from app.theme import aplicar_tema, cabecalho, badge_status

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Reservas", "Crie reservas e vincule suítes aos hóspedes", "📋")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def _formatar_cpf(cpf: str) -> str:
    cpf = _somente_digitos(cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def _reset_wizard():
    st.session_state["wiz_reserva"] = {"step": 1}


if "wiz_reserva" not in st.session_state:
    _reset_wizard()

tab_criar, tab_listar, tab_suites = st.tabs(["🆕 Nova Reserva", "📋 Gerenciar Reservas", "🔗 Ajustar Suítes"])

# ── Nova Reserva (fluxo guiado) ────────────────────────────────────────────────
with tab_criar:
    wiz = st.session_state["wiz_reserva"]
    etapa = wiz["step"]

    if etapa <= 4:
        etapas_nome = ["1. Hóspede", "2. Datas", "3. Suítes", "4. Confirmação"]
        cols_step = st.columns(len(etapas_nome))
        for i, (col, nome) in enumerate(zip(cols_step, etapas_nome), start=1):
            if i < etapa:
                col.markdown(f"✅ {nome}")
            elif i == etapa:
                col.markdown(f"**➡️ {nome}**")
            else:
                col.markdown(f":gray[{nome}]")
        st.progress((etapa - 1) / len(etapas_nome))

        col_titulo, col_reiniciar = st.columns([5, 1])
        with col_reiniciar:
            if st.button("🔄 Recomeçar", use_container_width=True):
                _reset_wizard()
                st.rerun()
        st.divider()

    # ── Passo 1: Hóspede ──────────────────────────────────────────────────────
    if etapa == 1:
        st.subheader("Passo 1 — O hóspede já é cadastrado?")
        st.caption("Digite o CPF para buscar. Se não encontrarmos, você cadastra na hora, sem sair da tela.")

        cpf_input = st.text_input(
            "CPF do hóspede", placeholder="Somente números ou 000.000.000-00", max_chars=14
        )

        if st.button("🔍 Buscar hóspede", type="primary", use_container_width=True):
            cpf_limpo = _somente_digitos(cpf_input)
            if len(cpf_limpo) != 11:
                st.error("CPF inválido — informe os 11 dígitos.")
            else:
                with SessionLocal() as db:
                    hospede = HospedeService(db).buscar_por_cpf(cpf_limpo)
                wiz["cpf"] = cpf_limpo
                if hospede:
                    wiz["hospede_nome"] = hospede.nome
                    wiz["hospede_encontrado"] = True
                else:
                    wiz["hospede_encontrado"] = False
                st.rerun()

        if wiz.get("cpf") and wiz.get("hospede_encontrado"):
            st.success(f"✅ Hóspede encontrado: **{wiz['hospede_nome']}** ({_formatar_cpf(wiz['cpf'])})")
            if st.button("Próximo ➜", type="primary", use_container_width=True):
                wiz["step"] = 2
                st.rerun()

        elif wiz.get("cpf") and wiz.get("hospede_encontrado") is False:
            st.warning(f"Nenhum hóspede encontrado com o CPF {_formatar_cpf(wiz['cpf'])}. Cadastre abaixo:")
            with st.form("form_novo_hospede_wizard"):
                nome = st.text_input("Nome completo")
                telefone = st.text_input("Telefone")
                email = st.text_input("E-mail")
                endereco = st.text_input("Endereço")
                cadastrar = st.form_submit_button("Cadastrar e continuar", type="primary", use_container_width=True)

            if cadastrar:
                if not nome.strip() or not telefone.strip() or not email.strip():
                    st.error("Nome, telefone e e-mail são obrigatórios.")
                else:
                    try:
                        with SessionLocal() as db:
                            novo = HospedeService(db).criar_hospede(
                                wiz["cpf"], nome.strip(), telefone.strip(), email.strip(), endereco.strip()
                            )
                        wiz["hospede_nome"] = novo.nome
                        wiz["hospede_encontrado"] = True
                        wiz["step"] = 2
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro ao cadastrar hóspede: {e}")

    # ── Passo 2: Datas ────────────────────────────────────────────────────────
    elif etapa == 2:
        st.subheader("Passo 2 — Período da estadia")
        st.info(f"Hóspede: **{wiz['hospede_nome']}** · CPF {_formatar_cpf(wiz['cpf'])}")

        col1, col2 = st.columns(2)
        checkin = col1.date_input("Check-in previsto", value=wiz.get("checkin") or date.today(), min_value=date.today())
        checkout = col2.date_input(
            "Check-out previsto", value=wiz.get("checkout") or (date.today() + timedelta(days=1)), min_value=date.today()
        )

        if checkin < checkout:
            st.caption(f"🛎️ {(checkout - checkin).days} diária(s)")

        col_voltar, col_prox = st.columns(2)
        if col_voltar.button("⬅ Voltar", use_container_width=True):
            wiz["step"] = 1
            st.rerun()
        if col_prox.button("Próximo ➜", type="primary", use_container_width=True):
            if checkin >= checkout:
                st.error("A data de check-in deve ser anterior ao check-out.")
            else:
                wiz["checkin"] = checkin
                wiz["checkout"] = checkout
                wiz["step"] = 3
                st.rerun()

    # ── Passo 3: Suítes ───────────────────────────────────────────────────────
    elif etapa == 3:
        st.subheader("Passo 3 — Quais suítes o hóspede vai ocupar?")
        noites = (wiz["checkout"] - wiz["checkin"]).days
        st.info(
            f"Hóspede: **{wiz['hospede_nome']}** · {wiz['checkin'].strftime('%d/%m/%Y')} → "
            f"{wiz['checkout'].strftime('%d/%m/%Y')} ({noites} diária(s))"
        )

        with SessionLocal() as db:
            suites = SuiteService(db).listar_suites()
        disponiveis = [s for s in suites if s.status == "Disponível"]

        if not disponiveis:
            st.warning("Não há suítes disponíveis no momento.")
        else:
            tipos = sorted({s.tipo for s in disponiveis})
            filtro_tipo = st.multiselect("Filtrar por tipo", tipos, default=tipos)
            filtradas = [s for s in disponiveis if s.tipo in filtro_tipo]

            selecionadas = wiz.get("suites_sel", {})

            for s in filtradas:
                col1, col2, col3, col4 = st.columns([0.6, 1.4, 2, 2])
                marcado = col1.checkbox("Sel.", value=s.id_suite in selecionadas, key=f"wiz_suite_{s.id_suite}")
                col2.write(f"**Nº {s.numero}**")
                col3.write(f"{s.tipo} · {s.capacidade} pax")
                col4.write(f"R$ {s.valor_diaria:,.2f}/diária")

                if marcado:
                    selecionadas[s.id_suite] = {
                        "numero": s.numero,
                        "tipo": s.tipo,
                        "capacidade": s.capacidade,
                        "valor_diaria": s.valor_diaria,
                    }
                else:
                    selecionadas.pop(s.id_suite, None)

            wiz["suites_sel"] = selecionadas

            if selecionadas:
                estimativa = noites * sum(s["valor_diaria"] for s in selecionadas.values())
                st.success(f"{len(selecionadas)} suíte(s) selecionada(s) · Estimativa: R$ {estimativa:,.2f}")

        col_voltar, col_prox = st.columns(2)
        if col_voltar.button("⬅ Voltar", use_container_width=True):
            wiz["step"] = 2
            st.rerun()
        if col_prox.button("Próximo ➜", type="primary", use_container_width=True):
            if not wiz.get("suites_sel"):
                st.error("Selecione ao menos uma suíte.")
            else:
                wiz["step"] = 4
                st.rerun()

    # ── Passo 4: Confirmação ──────────────────────────────────────────────────
    elif etapa == 4:
        st.subheader("Passo 4 — Confirme os dados da reserva")

        noites = (wiz["checkout"] - wiz["checkin"]).days
        suites_sel = wiz["suites_sel"]
        estimativa = noites * sum(s["valor_diaria"] for s in suites_sel.values())

        suites_texto = "".join(
            f"<br>🛏️ Nº {s['numero']} — {s['tipo']} · {s['capacidade']} pax · R$ {s['valor_diaria']:,.2f}/diária"
            for s in suites_sel.values()
        )

        st.markdown(
            f"""
            <div class="resort-suite-card">
                <span class="resort-suite-number">{wiz['hospede_nome']}</span>
                <div class="resort-suite-meta">
                    CPF: {_formatar_cpf(wiz['cpf'])}<br>
                    Check-in: {wiz['checkin'].strftime('%d/%m/%Y')} → Check-out: {wiz['checkout'].strftime('%d/%m/%Y')}
                    ({noites} diária(s))
                    {suites_texto}
                    <br><br><b>Valor estimado: R$ {estimativa:,.2f}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("A reserva é criada com status **Pendente**, aguardando confirmação de pagamento.")

        col_voltar, col_confirmar = st.columns(2)
        if col_voltar.button("⬅ Voltar", use_container_width=True):
            wiz["step"] = 3
            st.rerun()

        if col_confirmar.button("✅ Confirmar Reserva", type="primary", use_container_width=True):
            try:
                with SessionLocal() as db:
                    reserva = ReservaService(db).criar_reserva(
                        cpf_hospede=wiz["cpf"],
                        checkin_previsto=wiz["checkin"],
                        checkout_previsto=wiz["checkout"],
                        status="Pendente",
                    )
                    id_reserva_criada = reserva.id_reserva  # captura antes dos próximos commits expirarem o objeto

                    vinculo_service = ReservaSuiteService(db)
                    falhas = []
                    for id_suite in suites_sel:
                        try:
                            vinculo_service.vincular_reserva_suite(
                                id_reserva=id_reserva_criada, id_suite=id_suite, data_entrada=wiz["checkin"]
                            )
                        except ValueError as e:
                            falhas.append(str(e))

                wiz["step"] = 5
                wiz["resultado_id"] = id_reserva_criada
                wiz["resultado_falhas"] = falhas
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao criar reserva: {e}")

    # ── Passo 5: Concluído ────────────────────────────────────────────────────
    elif etapa == 5:
        st.success(f"🎉 Reserva #{wiz['resultado_id']} criada com sucesso para **{wiz['hospede_nome']}**!")
        if wiz.get("resultado_falhas"):
            st.warning("Algumas suítes não puderam ser vinculadas: " + "; ".join(wiz["resultado_falhas"]))
            st.caption("Use a aba **Ajustar Suítes** para tentar vincular novamente.")
        if st.button("➕ Cadastrar outra reserva", type="primary", use_container_width=True):
            _reset_wizard()
            st.rerun()

# ── Gerenciar Reservas ─────────────────────────────────────────────────────────
with tab_listar:
    st.subheader("Reservas cadastradas")

    with SessionLocal() as db:
        todas_reservas = ReservaService(db).listar_reservas()
        nomes = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in todas_reservas}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(todas_reservas))
    c2.metric("Pendentes", sum(1 for r in todas_reservas if r.status == "Pendente"))
    c3.metric("Confirmadas", sum(1 for r in todas_reservas if r.status == "Confirmada"))
    c4.metric("Hospedados", sum(1 for r in todas_reservas if r.status == "Hospedado"))

    st.divider()

    col_cpf, col_status = st.columns([2, 1])
    cpf_filtro = col_cpf.text_input("Filtrar por CPF (opcional)", placeholder="000.000.000-00")
    status_filtro = col_status.selectbox(
        "Status", ["Todos", "Pendente", "Confirmada", "Hospedado", "Finalizada", "Cancelada"]
    )

    reservas = todas_reservas
    if cpf_filtro.strip():
        cpf_limpo = _somente_digitos(cpf_filtro)
        reservas = [r for r in reservas if _somente_digitos(r.cpf_hospede) == cpf_limpo]
    if status_filtro != "Todos":
        reservas = [r for r in reservas if r.status == status_filtro]
    reservas = sorted(reservas, key=lambda r: r.id_reserva, reverse=True)

    if not reservas:
        st.info("Nenhuma reserva encontrada.")
    else:
        for r in reservas:
            valor_texto = f"R$ {r.valor_total:,.2f}" if r.valor_total is not None else "—"
            st.markdown(
                f"""
                <div class="resort-suite-card">
                    <span class="resort-suite-number">Reserva #{r.id_reserva}</span>
                    &nbsp;{badge_status(r.status)}
                    <div class="resort-suite-meta">
                        Hóspede: {nomes[r.id_reserva]} · {r.checkin_previsto} → {r.checkout_previsto}
                        · Valor: {valor_texto}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_a, col_b, col_c = st.columns(3)

            if r.status == "Pendente":
                if col_a.button("✅ Confirmar pagamento", key=f"confirmar_{r.id_reserva}", use_container_width=True):
                    try:
                        with SessionLocal() as db:
                            ReservaService(db).atualizar_status_pagamento(r.id_reserva, "Confirmada")
                        st.success(f"Reserva #{r.id_reserva} confirmada!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            elif r.status == "Confirmada":
                if col_a.button("↩️ Reverter p/ Pendente", key=f"reverter_{r.id_reserva}", use_container_width=True):
                    try:
                        with SessionLocal() as db:
                            ReservaService(db).atualizar_status_pagamento(r.id_reserva, "Pendente")
                        st.success(f"Reserva #{r.id_reserva} voltou para Pendente.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            if r.status in ("Pendente", "Confirmada"):
                if col_b.button("🚫 Cancelar reserva", key=f"cancelar_{r.id_reserva}", use_container_width=True):
                    try:
                        with SessionLocal() as db:
                            ReservaService(db).cancelar_reserva(r.id_reserva)
                        st.success(f"Reserva #{r.id_reserva} cancelada.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

# ── Ajustar Suítes ───────────────────────────────────────────────────────────
with tab_suites:
    st.subheader("Vincular ou remover suítes de uma reserva existente")
    st.caption("Use esta aba para acrescentar uma suíte extra depois que a reserva já foi criada.")

    with SessionLocal() as db:
        reservas = ReservaService(db).listar_reservas()
        nomes = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in reservas}
        suite_service = SuiteService(db)
        suites = suite_service.listar_suites()

    if not reservas:
        st.info("Nenhuma reserva cadastrada.")
    elif not suites:
        st.info("Nenhuma suíte cadastrada.")
    else:
        opcoes_reserva = {
            f"#{r.id_reserva} — {nomes[r.id_reserva]} ({r.status})": r.id_reserva for r in reservas
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