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
cabecalho("Reservas", "Hóspedes, reservas e suítes em um só lugar", "📋")


# ── Helpers ──────────────────────────────────────────────────────────────────────
def _somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def _formatar_cpf(cpf: str) -> str:
    cpf = _somente_digitos(cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def _email_valido(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def _reset_wizard():
    st.session_state["wiz_reserva"] = {"step": 1}


if "wiz_reserva" not in st.session_state:
    _reset_wizard()

tab_criar, tab_listar, tab_hospedes, tab_suites, tab_financeiro = st.tabs(
    ["🆕 Nova Reserva", "📋 Gerenciar Reservas", "👤 Hóspedes", "🔗 Ajustar Suítes", "💰 Financeiro"]
)

# ── Nova Reserva (fluxo guiado) ─────────────────────────────────────────────────
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

    # ── Passo 1: Hóspede ────────────────────────────────────────────────────────
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

    # ── Passo 2: Datas ──────────────────────────────────────────────────────────
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

    # ── Passo 3: Suítes ─────────────────────────────────────────────────────────
    elif etapa == 3:
        st.subheader("Passo 3 — Escolha as suítes")

        st.info(
            f"Hóspede: **{wiz['hospede_nome']}**"
        )

        with SessionLocal() as db:
            suites = SuiteService(db).listar_suites()

        disponiveis = [s for s in suites if s.status == "Disponível"]

        if not disponiveis:
            st.warning("Não existem suítes disponíveis.")
        else:

            selecionadas = wiz.get("suites_sel", {})

            total = 0

            for suite in disponiveis:

                with st.container(border=True):

                    marcar = st.checkbox(
                        f"Suíte {suite.numero} - {suite.tipo}",
                        key=f"suite_{suite.id_suite}"
                    )

                    if marcar:

                        col1, col2 = st.columns(2)

                        entrada = col1.date_input(
                            "Entrada",
                            value=selecionadas.get(suite.id_suite, {}).get("entrada", wiz["checkin"]),
                            key=f"entrada_{suite.id_suite}"
                        )

                        # Recupera a saída salva para essa suíte (ou usa o checkout do passo 2)
                        saida_padrao = selecionadas.get(suite.id_suite, {}).get("saida", wiz["checkout"])

                        # Garante que ela nunca fique antes da entrada
                        if saida_padrao <= entrada:
                            saida_padrao = entrada + timedelta(days=1)

                        saida = col2.date_input(
                            "Saída",
                            value=saida_padrao,
                            min_value=entrada + timedelta(days=1),
                            key=f"saida_{suite.id_suite}"
                        )

                        noites = (saida - entrada).days
                        subtotal = noites * suite.valor_diaria

                        st.write(f"**Diárias:** {noites}")
                        st.write(f"**Valor da diária:** R$ {suite.valor_diaria:,.2f}")
                        st.success(f"Subtotal: R$ {subtotal:,.2f}")

                        total += subtotal

                        selecionadas[suite.id_suite] = {
                            "numero": suite.numero,
                            "tipo": suite.tipo,
                            "entrada": entrada,
                            "saida": saida,
                            "valor_diaria": suite.valor_diaria,
                            "subtotal": subtotal
                        }

                    else:
                        selecionadas.pop(suite.id_suite, None)

            wiz["suites_sel"] = selecionadas

            st.divider()

            st.metric(
                "Valor estimado",
                f"R$ {total:,.2f}"
            )

        col1, col2 = st.columns(2)

        if col1.button("⬅ Voltar"):
            wiz["step"] = 2
            st.rerun()

        if col2.button("Próximo ➜", type="primary"):

            if len(wiz["suites_sel"]) == 0:
                st.error("Selecione ao menos uma suíte.")
            else:
                wiz["step"] = 4
                st.rerun()
    # ── Passo 4: Confirmação ────────────────────────────────────────────────────
    elif etapa == 4:

        st.subheader("Resumo da reserva")

        st.write(f"**Hóspede:** {wiz['hospede_nome']}")
        st.write(f"**CPF:** {_formatar_cpf(wiz['cpf'])}")

        total = 0

        for dados in wiz["suites_sel"].values():

            noites = (dados["saida"] - dados["entrada"]).days
            total += dados["subtotal"]

            with st.container(border=True):

                st.markdown(f"### 🛏️ Suíte {dados['numero']}")

                st.write(f"**Tipo:** {dados['tipo']}")
                st.write(
                    f"**Período:** {dados['entrada'].strftime('%d/%m/%Y')} "
                    f"→ {dados['saida'].strftime('%d/%m/%Y')}"
                )
                st.write(f"**Diárias:** {noites}")
                st.write(f"**Valor da diária:** R$ {dados['valor_diaria']:,.2f}")

                st.success(f"Subtotal: R$ {dados['subtotal']:,.2f}")

        st.metric(
            "Valor total estimado",
            f"R$ {total:,.2f}"
        )

        st.divider()

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

                    id_reserva_criada = reserva.id_reserva

                    vinculo_service = ReservaSuiteService(db)
                    falhas = []

                    for id_suite, dados in wiz["suites_sel"].items():
                        try:
                            vinculo_service.vincular_reserva_suite(
                                id_reserva=id_reserva_criada,
                                id_suite=id_suite,
                                data_entrada=dados["entrada"],
                                data_saida=dados["saida"]   # se o método aceitar
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
    # ── Passo 5: Concluído ──────────────────────────────────────────────────────
    elif etapa == 5:
        st.success(f"🎉 Reserva #{wiz['resultado_id']} criada com sucesso para **{wiz['hospede_nome']}**!")
        if wiz.get("resultado_falhas"):
            st.warning("Algumas suítes não puderam ser vinculadas: " + "; ".join(wiz["resultado_falhas"]))
            st.caption("Use a aba **Ajustar Suítes** para tentar vincular novamente.")
        if st.button("➕ Cadastrar outra reserva", type="primary", use_container_width=True):
            _reset_wizard()
            st.rerun()


# ── Gerenciar Reservas ───────────────────────────────────────────────────────────
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

# ── Hóspedes ──────────────────────────────────────────────────────────────────────
with tab_hospedes:
    st.subheader("Cadastro de hóspedes")

    aba_cadastrar, aba_listar, aba_atualizar, aba_remover = st.tabs(
        ["Cadastrar", "Listar", "Atualizar", "Remover"]
    )

    with aba_cadastrar:
        with st.form("form_cadastro_hospede"):
            cpf = st.text_input("CPF", placeholder="Somente números ou 000.000.000-00", max_chars=14)
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone", placeholder="(00) 00000-0000")
            email = st.text_input("Email")
            endereco = st.text_input("Endereço")
            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                cpf_limpo = _somente_digitos(cpf)
                if len(cpf_limpo) != 11:
                    st.error("CPF inválido — informe os 11 dígitos.")
                elif not nome.strip():
                    st.error("Nome é obrigatório.")
                elif not _email_valido(email):
                    st.error("Informe um e-mail válido.")
                else:
                    try:
                        with SessionLocal() as db:
                            HospedeService(db).criar_hospede(
                                cpf_limpo, nome.strip(), telefone.strip(), email.strip(), endereco.strip()
                            )
                        st.success("Hóspede cadastrado com sucesso!")
                    except ValueError as e:
                        st.error(str(e))

    with aba_listar:
        with SessionLocal() as db:
            hospedes = HospedeService(db).listar_hospedes()

        st.metric("Total de hóspedes", len(hospedes))

        busca_nome = st.text_input("Buscar por nome (opcional)", key="busca_nome_listar")
        if busca_nome.strip():
            hospedes = [h for h in hospedes if busca_nome.strip().lower() in h.nome.lower()]

        if hospedes:
            cols = st.columns(2)
            for i, h in enumerate(hospedes):
                with cols[i % 2]:
                    st.markdown(
                        f"""
                        <div class="resort-suite-card">
                            <span class="resort-suite-number">{h.nome}</span>
                            <div class="resort-suite-meta">
                                CPF: {_formatar_cpf(h.cpf)}<br>
                                📞 {h.telefone or '—'} · ✉️ {h.email or '—'}<br>
                                📍 {h.endereco or '—'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Nenhum hóspede cadastrado.")

    with aba_atualizar:
        cpf_busca = st.text_input("CPF do hóspede", key="cpf_atualizar", placeholder="Somente números ou 000.000.000-00")
        if st.button("Buscar", key="buscar_atualizar"):
            try:
                with SessionLocal() as db:
                    hospede = HospedeService(db).buscar_por_cpf(_somente_digitos(cpf_busca))
                if hospede is None:
                    st.warning("Hóspede não encontrado.")
                    st.session_state.pop("hospede_editando", None)
                else:
                    st.session_state["hospede_editando"] = hospede
            except ValueError as e:
                st.error(str(e))

        if "hospede_editando" in st.session_state:
            h = st.session_state["hospede_editando"]
            st.caption(f"Editando: {h.nome} — CPF {_formatar_cpf(h.cpf)}")
            with st.form("form_atualizar_hospede"):
                nome = st.text_input("Nome", value=h.nome)
                telefone = st.text_input("Telefone", value=h.telefone)
                email = st.text_input("Email", value=h.email)
                endereco = st.text_input("Endereço", value=h.endereco)
                submitted = st.form_submit_button("Salvar alterações")

                if submitted:
                    if not nome.strip():
                        st.error("Nome é obrigatório.")
                    elif not _email_valido(email):
                        st.error("Informe um e-mail válido.")
                    else:
                        try:
                            with SessionLocal() as db:
                                HospedeService(db).atualizar_hospede(
                                    h.cpf, nome.strip(), telefone.strip(), email.strip(), endereco.strip()
                                )
                            st.success("Hóspede atualizado com sucesso!")
                            del st.session_state["hospede_editando"]
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

    with aba_remover:
        st.caption("Só é possível remover hóspedes que não tenham nenhuma reserva cadastrada.")
        cpf_remover = st.text_input("CPF do hóspede", key="cpf_remover", placeholder="Somente números ou 000.000.000-00")
        confirmar = st.checkbox("Confirmo que desejo remover permanentemente este hóspede.")
        if st.button("Remover", disabled=not confirmar):
            try:
                with SessionLocal() as db:
                    HospedeService(db).remover_hospede(_somente_digitos(cpf_remover))
                st.success("Hóspede removido com sucesso!")
            except ValueError as e:
                st.error(str(e))

# ── Ajustar Suítes ────────────────────────────────────────────────────────────────
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
            vinculos_da_reserva = ReservaSuiteService(db).listar_por_reserva(id_reserva_alvo)

        vinculos_ativos = [v for v in vinculos_da_reserva if v.data_saida is None]

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
                            ReservaSuiteService(db).vincular_reserva_suite(
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
                            ReservaSuiteService(db).registrar_saida(vinculo.id, data_saida)
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro: {e}")

# ── Financeiro ───────────────────────────────────────────────────────────────────
with tab_financeiro:
    st.subheader("Fechar o valor de uma reserva")
    st.caption("Soma o valor de todas as suítes vinculadas e, se quiser, salva como valor total da reserva.")

    with SessionLocal() as db:
        reservas_fin = ReservaService(db).listar_reservas()
        nomes_fin = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in reservas_fin}

    if not reservas_fin:
        st.info("Nenhuma reserva cadastrada.")
    else:
        opcoes_fin = {
            f"#{r.id_reserva} — {nomes_fin[r.id_reserva]} ({r.status})": r.id_reserva for r in reservas_fin
        }
        reserva_fin = st.selectbox("Selecione a reserva", list(opcoes_fin.keys()), key="select_financeiro")
        id_reserva_fin = opcoes_fin[reserva_fin]

        if st.button("Calcular valor total", use_container_width=True):
            try:
                with SessionLocal() as db:
                    valor_calculado = ReservaSuiteService(db).calcular_valor_total_reserva(id_reserva_fin)
                st.session_state["valor_calculado"] = valor_calculado
                st.success(f"Valor calculado: R$ {valor_calculado:,.2f}")
            except ValueError as e:
                st.error(str(e))
                st.session_state.pop("valor_calculado", None)

        if "valor_calculado" in st.session_state:
            if st.button("💾 Salvar como valor total da reserva", use_container_width=True):
                try:
                    with SessionLocal() as db:
                        ReservaService(db).definir_valor_total(id_reserva_fin, st.session_state["valor_calculado"])
                    st.success("Valor total da reserva atualizado!")
                    del st.session_state["valor_calculado"]
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        st.divider()
        st.subheader("Corrigir data de entrada de um vínculo")
        id_vinculo_corrigir = st.number_input("ID do vínculo (ReservaSuite)", min_value=1, step=1, key="id_corrigir")
        nova_data_entrada = st.date_input("Nova data de entrada", value=date.today(), key="nova_data_entrada")

        if st.button("Corrigir", use_container_width=True, key="btn_corrigir"):
            try:
                with SessionLocal() as db:
                    ReservaSuiteService(db).corrigir_data_entrada(int(id_vinculo_corrigir), nova_data_entrada)
                st.success("Data de entrada corrigida com sucesso!")
            except ValueError as e:
                st.error(str(e))
