import re
import streamlit as st
from datetime import date, timedelta
from app.database import SessionLocal
from app.services.ReservaService import ReservaService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.services.SuiteService import SuiteService
from app.services.HospedeService import HospedeService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item
from app.utils.search_utils import atende_termo_busca, sanitizar_documento
import pandas as pd

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


@st.dialog("➕ Cadastrar Novo Hóspede")
def modal_cadastrar_hospede(service):
    with st.form("form_modal_cadastrar_hospede_res"):
        cpf = st.text_input("CPF", placeholder="Somente números ou 000.000.000-00", max_chars=14)
        nome = st.text_input("Nome Completo")
        telefone = st.text_input("Telefone", placeholder="(00) 00000-0000")
        email = st.text_input("E-mail")
        endereco = st.text_input("Endereço Completo")
        submitted = st.form_submit_button("Cadastrar Hóspede", type="primary", width="stretch")

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
                    service.criar_hospede(
                        cpf_limpo, nome.strip(), telefone.strip(), email.strip(), endereco.strip()
                    )
                    st.success("Hóspede cadastrado com sucesso!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


@st.dialog("✏️ Editar Hóspede")
def modal_editar_hospede(service, hospede):
    with st.form("form_modal_editar_hospede_res"):
        st.caption(f"Editando hóspede **CPF: {_formatar_cpf(hospede.cpf)}**")
        nome = st.text_input("Nome Completo", value=hospede.nome)
        telefone = st.text_input("Telefone", value=hospede.telefone or "")
        email = st.text_input("E-mail", value=hospede.email or "")
        endereco = st.text_input("Endereço Completo", value=hospede.endereco or "")
        submitted = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")

        if submitted:
            if not nome.strip():
                st.error("Nome é obrigatório.")
            elif not _email_valido(email):
                st.error("Informe um e-mail válido.")
            else:
                try:
                    service.atualizar_hospede(hospede.cpf, nome.strip(), telefone.strip(), email.strip(), endereco.strip())
                    st.success("Hóspede atualizado com sucesso!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _reset_wizard():
    st.session_state["wiz_reserva"] = {"step": 1}


if "wiz_reserva" not in st.session_state:
    _reset_wizard()

tab_listar, tab_criar, tab_hospedes, tab_suites = st.tabs(
    ["📋 Gerenciar Reservas", "➕ Nova Reserva", "👤 Hóspedes", "🔗 Ajustar Suítes"]
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
            if st.button("🔄 Recomeçar", width="stretch"):
                _reset_wizard()
                st.rerun()
        st.divider()

    # ── Passo 1: Hóspede ────────────────────────────────────────────────────────
    if etapa == 1:
        st.subheader("Passo 1 — Selecione ou Cadastre o Hóspede")
        st.caption("Selecione um hóspede cadastrado na lista ou informe o CPF para buscar.")

        with SessionLocal() as db:
            todos_hospedes = HospedeService(db).listar_hospedes()

        if todos_hospedes:
            hospede_sel = st.selectbox(
                "🔎 Buscar hóspede cadastrado por Nome ou CPF",
                todos_hospedes,
                format_func=lambda h: f"{h.nome} (CPF: {_formatar_cpf(h.cpf)})",
                index=None,
                placeholder="Digite o nome ou CPF para pesquisar..."
            )

            if hospede_sel:
                wiz["cpf"] = hospede_sel.cpf
                wiz["hospede_nome"] = hospede_sel.nome
                wiz["hospede_encontrado"] = True

        st.markdown("**Ou digite o CPF manualmente:**")
        cpf_input = st.text_input(
            "CPF do hóspede", placeholder="Somente números ou 000.000.000-00", max_chars=14
        )

        if st.button("🔍 Buscar por CPF", type="secondary", width="stretch"):
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
            st.success(f"✅ Hóspede selecionado: **{wiz['hospede_nome']}** ({_formatar_cpf(wiz['cpf'])})")
            if st.button("Próximo ➜", type="primary", width="stretch"):
                wiz["step"] = 2
                st.rerun()

        elif wiz.get("cpf") and wiz.get("hospede_encontrado") is False:
            st.warning(f"Nenhum hóspede encontrado com o CPF {_formatar_cpf(wiz['cpf'])}. Cadastre abaixo:")
            with st.form("form_novo_hospede_wizard"):
                nome = st.text_input("Nome completo")
                telefone = st.text_input("Telefone")
                email = st.text_input("E-mail")
                endereco = st.text_input("Endereço")
                cadastrar = st.form_submit_button("Cadastrar e continuar", type="primary", width="stretch")

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
        st.subheader("Passo 2 — Período padrão da estadia")
        st.caption("Você poderá ajustar o período e a diária individualmente por suíte no próximo passo.")
        st.info(f"Hóspede: **{wiz['hospede_nome']}** · CPF {_formatar_cpf(wiz['cpf'])}")

        col1, col2 = st.columns(2)
        checkin = col1.date_input("Check-in previsto", value=wiz.get("checkin") or date.today(), min_value=date.today())
        checkout = col2.date_input(
            "Check-out previsto", value=wiz.get("checkout") or (date.today() + timedelta(days=1)), min_value=date.today()
        )

        if checkin < checkout:
            st.caption(f"🛎️ {(checkout - checkin).days} diária(s)")

        col_voltar, col_prox = st.columns(2)
        if col_voltar.button("⬅ Voltar", width="stretch"):
            wiz["step"] = 1
            st.rerun()
        if col_prox.button("Próximo ➜", type="primary", width="stretch"):
            if checkin >= checkout:
                st.error("A data de check-in deve ser anterior ao check-out.")
            else:
                wiz["checkin"] = checkin
                wiz["checkout"] = checkout
                wiz["step"] = 3
                st.rerun()

    # ── Passo 3: Suítes (período e diária negociada por suíte) ──────────────────
    elif etapa == 3:
        st.subheader("Passo 3 — Escolha as suítes e configure as diárias")
        st.info(f"Hóspede: **{wiz['hospede_nome']}**")
        st.caption("Cada suíte pode ter seu próprio período e um valor de diária customizado para esta reserva.")

        with SessionLocal() as db:
            disponiveis = SuiteService(db).listar_disponiveis_no_periodo(wiz["checkin"], wiz["checkout"])

        if not disponiveis:
            st.warning("Não existem suítes disponíveis.")
        else:
            selecionadas = wiz.get("suites_sel", {})
            total = 0

            for suite in disponiveis:
                with st.container(border=True):
                    marcar = st.checkbox(
                        f"Suíte {suite.numero} - {suite.tipo} (Padrão: R$ {suite.valor_diaria:,.2f}/dia)",
                        value=suite.id_suite in selecionadas,
                        key=f"wiz_marcar_{suite.id_suite}",
                    )

                    if marcar:
                        col1, col2, col3 = st.columns([1.5, 1.5, 1.2])

                        entrada = col1.date_input(
                            "Entrada",
                            value=selecionadas.get(suite.id_suite, {}).get("entrada", wiz["checkin"]),
                            key=f"wiz_entrada_{suite.id_suite}",
                        )

                        saida_padrao = selecionadas.get(suite.id_suite, {}).get("saida", wiz["checkout"])
                        if saida_padrao <= entrada:
                            saida_padrao = entrada + timedelta(days=1)

                        saida = col2.date_input(
                            "Saída",
                            value=saida_padrao,
                            min_value=entrada + timedelta(days=1),
                            key=f"wiz_saida_{suite.id_suite}",
                        )

                        val_diaria_default = float(
                            selecionadas.get(suite.id_suite, {}).get("valor_diaria", suite.valor_diaria)
                        )
                        valor_diaria_aplicado = col3.number_input(
                            "Diária p/ Reserva (R$)",
                            min_value=0.01,
                            value=val_diaria_default,
                            step=10.0,
                            format="%.2f",
                            key=f"wiz_diaria_{suite.id_suite}",
                        )

                        noites = (saida - entrada).days
                        subtotal = noites * valor_diaria_aplicado

                        st.write(f"**Diárias:** {noites} · **Diária acordada:** R$ {valor_diaria_aplicado:,.2f}")
                        st.success(f"Subtotal: R$ {subtotal:,.2f}")

                        total += subtotal

                        selecionadas[suite.id_suite] = {
                            "numero": suite.numero,
                            "tipo": suite.tipo,
                            "entrada": entrada,
                            "saida": saida,
                            "valor_diaria": valor_diaria_aplicado,
                            "subtotal": subtotal,
                        }
                    else:
                        selecionadas.pop(suite.id_suite, None)

            wiz["suites_sel"] = selecionadas

            st.divider()
            st.metric("Valor total estimado", f"R$ {total:,.2f}")

        col1, col2 = st.columns(2)
        if col1.button("⬅ Voltar"):
            wiz["step"] = 2
            st.rerun()
        if col2.button("Próximo ➜", type="primary"):
            if len(wiz.get("suites_sel", {})) == 0:
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

        st.metric("Valor total estimado", f"R$ {total:,.2f}")
        st.divider()

        col_voltar, col_confirmar = st.columns(2)
        if col_voltar.button("⬅ Voltar", width="stretch"):
            wiz["step"] = 3
            st.rerun()

        if col_confirmar.button("✅ Confirmar Reserva", type="primary", width="stretch"):
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
                                data_saida=dados["saida"],
                                valor_diaria=dados["valor_diaria"],  # <-- Diária específica gravada no vínculo
                            )
                        except ValueError as e:
                            falhas.append(str(e))

                    # Grava o total calculado no registro da reserva
                    try:
                        valor_total = vinculo_service.calcular_valor_total_reserva(id_reserva_criada)
                        ReservaService(db).definir_valor_total(id_reserva_criada, valor_total)
                    except ValueError:
                        pass

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
        if st.button("➕ Cadastrar outra reserva", type="primary", width="stretch"):
            _reset_wizard()
            st.rerun()

# ── Gerenciar Reservas ───────────────────────────────────────────────────────────
with tab_listar:
    with SessionLocal() as db:
        todas_reservas = ReservaService(db).listar_reservas()
        nomes = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in todas_reservas}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Reservas", len(todas_reservas))
    c2.metric("Pendentes", sum(1 for r in todas_reservas if r.status == "Pendente"))
    c3.metric("Confirmadas", sum(1 for r in todas_reservas if r.status == "Confirmada"))
    c4.metric("Hospedados", sum(1 for r in todas_reservas if r.status == "Hospedado"))

    st.divider()

    c_busca, c_status, c_vis = st.columns([4, 2, 2])
    with c_busca:
        termo_reserva = st.text_input("🔍 Pesquisar por Hóspede, CPF ou código ID", key="busca_gerenciar_reservas", placeholder="Digite o nome, CPF ou ID...")
    with c_status:
        status_filtro = st.selectbox(
            "Filtrar Status", ["Todos", "Pendente", "Confirmada", "Hospedado", "Finalizada", "Cancelada"], key="filtro_status_res"
        )
    with c_vis:
        modo_vis_res = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_gerenciar_reservas")

    reservas_filtradas = todas_reservas
    if termo_reserva.strip():
        reservas_filtradas = [
            r for r in reservas_filtradas
            if atende_termo_busca(termo_reserva, r.id_reserva, r.cpf_hospede, nomes.get(r.id_reserva, ""))
        ]
    if status_filtro != "Todos":
        reservas_filtradas = [r for r in reservas_filtradas if r.status == status_filtro]
    reservas_filtradas = sorted(reservas_filtradas, key=lambda r: r.id_reserva, reverse=True)

    st.divider()

    if not reservas_filtradas:
        st.info("Nenhuma reserva encontrada com os filtros aplicados.")
    else:
        if modo_vis_res == "📊 Tabela":
            dados_tabela_res = []
            for r in reservas_filtradas:
                dt_in = r.checkin_previsto.strftime("%d/%m/%Y") if hasattr(r.checkin_previsto, "strftime") else str(r.checkin_previsto)
                dt_out = r.checkout_previsto.strftime("%d/%m/%Y") if hasattr(r.checkout_previsto, "strftime") else str(r.checkout_previsto)
                dados_tabela_res.append({
                    "ID": f"#{r.id_reserva}",
                    "Hóspede": nomes.get(r.id_reserva, r.cpf_hospede),
                    "CPF": _formatar_cpf(r.cpf_hospede),
                    "Check-in Previsto": dt_in,
                    "Check-out Previsto": dt_out,
                    "Valor Total": float(r.valor_total or 0.0),
                    "Status": r.status
                })
            st.dataframe(
                dados_tabela_res,
                width="stretch",
                column_config={
                    "ID": st.column_config.TextColumn("Código", width="small"),
                    "Hóspede": st.column_config.TextColumn("Hóspede", width="large"),
                    "Valor Total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
                }
            )

            st.caption("⚙️ **Ações Rápidas da Tabela:**")
            c_act1, c_act2, c_act3 = st.columns([4, 2, 2])
            with c_act1:
                res_sel_tab = st.selectbox(
                    "Selecione uma reserva da tabela para alterar status",
                    reservas_filtradas,
                    format_func=lambda r: f"Reserva #{r.id_reserva} — {nomes.get(r.id_reserva, r.cpf_hospede)} ({r.status})",
                    key="sel_tab_reserva_act",
                    index=None,
                    placeholder="Selecione uma reserva..."
                )
            with c_act2:
                if res_sel_tab and res_sel_tab.status == "Pendente":
                    if st.button("✅ Confirmar Pagamento", key="btn_conf_tab_res", width="stretch"):
                        try:
                            with SessionLocal() as db:
                                ReservaService(db).atualizar_status_pagamento(res_sel_tab.id_reserva, "Confirmada")
                                try:
                                    valor_total = ReservaSuiteService(db).calcular_valor_total_reserva(res_sel_tab.id_reserva)
                                    ReservaService(db).definir_valor_total(res_sel_tab.id_reserva, valor_total)
                                except ValueError:
                                    pass
                            st.success(f"Reserva #{res_sel_tab.id_reserva} confirmada!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                elif res_sel_tab and res_sel_tab.status == "Confirmada":
                    if st.button("↩️ Reverter p/ Pendente", key="btn_rev_tab_res", width="stretch"):
                        try:
                            with SessionLocal() as db:
                                ReservaService(db).atualizar_status_pagamento(res_sel_tab.id_reserva, "Pendente")
                            st.success(f"Reserva #{res_sel_tab.id_reserva} voltou para Pendente.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
            with c_act3:
                if res_sel_tab and res_sel_tab.status in ("Pendente", "Confirmada"):
                    if st.button("🚫 Cancelar Reserva", key="btn_canc_tab_res", width="stretch"):
                        try:
                            with SessionLocal() as db:
                                ReservaService(db).cancelar_reserva(res_sel_tab.id_reserva)
                            st.success(f"Reserva #{res_sel_tab.id_reserva} cancelada.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
        else:
            cols = st.columns(2)
            for i, r in enumerate(reservas_filtradas):
                valor_texto = f"R$ {r.valor_total:,.2f}" if r.valor_total is not None else "R$ 0,00"
                dt_in = r.checkin_previsto.strftime("%d/%m/%Y") if hasattr(r.checkin_previsto, "strftime") else str(r.checkin_previsto)
                dt_out = r.checkout_previsto.strftime("%d/%m/%Y") if hasattr(r.checkout_previsto, "strftime") else str(r.checkout_previsto)

                detalhes = f"""
                <strong>Hóspede:</strong> {nomes.get(r.id_reserva, r.cpf_hospede)}<br>
                <strong>Período:</strong> {dt_in} → {dt_out}<br>
                <strong>Valor Total:</strong> {valor_texto}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(f"Reserva #{r.id_reserva}", f"CPF: {_formatar_cpf(r.cpf_hospede)}", detalhes, status=r.status),
                        unsafe_allow_html=True,
                    )
                    c_act_a, c_act_b = st.columns(2)
                    with c_act_a:
                        if r.status == "Pendente":
                            if st.button("✅ Confirmar pagamento", key=f"conf_card_res_{r.id_reserva}", width="stretch"):
                                try:
                                    with SessionLocal() as db:
                                        ReservaService(db).atualizar_status_pagamento(r.id_reserva, "Confirmada")
                                        try:
                                            valor_total = ReservaSuiteService(db).calcular_valor_total_reserva(r.id_reserva)
                                            ReservaService(db).definir_valor_total(r.id_reserva, valor_total)
                                        except ValueError:
                                            pass
                                    st.success(f"Reserva #{r.id_reserva} confirmada!")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                        elif r.status == "Confirmada":
                            if st.button("↩️ Reverter p/ Pendente", key=f"rev_card_res_{r.id_reserva}", width="stretch"):
                                try:
                                    with SessionLocal() as db:
                                        ReservaService(db).atualizar_status_pagamento(r.id_reserva, "Pendente")
                                    st.success(f"Reserva #{r.id_reserva} voltou para Pendente.")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                    with c_act_b:
                        if r.status in ("Pendente", "Confirmada"):
                            if st.button("🚫 Cancelar reserva", key=f"canc_card_res_{r.id_reserva}", width="stretch"):
                                try:
                                    with SessionLocal() as db:
                                        ReservaService(db).cancelar_reserva(r.id_reserva)
                                    st.success(f"Reserva #{r.id_reserva} cancelada.")
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))

# ── Hóspedes ──────────────────────────────────────────────────────────────────────
with tab_hospedes:
    st.subheader("Cadastro e Gerenciamento de Hóspedes")

    with SessionLocal() as db:
        hospedes_reserva = HospedeService(db).listar_hospedes()

    c_busca, c_vis, c_btn = st.columns([4, 2, 2])
    with c_busca:
        termo_busca_h = st.text_input("🔍 Pesquisar por Nome, CPF, Telefone ou E-mail", key="busca_hospedes_tab_reserva", placeholder="Digite para buscar...")
    with c_vis:
        modo_vis_h = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_hospedes_tab_reserva")
    with c_btn:
        if st.button("➕ Novo Hóspede", type="primary", width="stretch", key="btn_novo_hospede_reserva_tab"):
            modal_cadastrar_hospede(HospedeService(db))

    hospedes_filtrados_res = [
        h for h in hospedes_reserva
        if atende_termo_busca(termo_busca_h, h.nome, h.cpf, h.email, h.telefone, h.endereco)
    ]

    st.divider()

    if not hospedes_filtrados_res:
        if termo_busca_h:
            st.info(f"Nenhum hóspede encontrado para '{termo_busca_h}'.")
        else:
            st.info("Nenhum hóspede cadastrado ainda.")
    else:
        if modo_vis_h == "📊 Tabela":
            dados_tabela_h = [
                {
                    "CPF": _formatar_cpf(h.cpf),
                    "Nome Completo": h.nome,
                    "Telefone": h.telefone or "—",
                    "E-mail": h.email or "—",
                    "Endereço": h.endereco or "—"
                }
                for h in hospedes_filtrados_res
            ]
            st.dataframe(
                dados_tabela_h,
                width="stretch",
                column_config={
                    "CPF": st.column_config.TextColumn("CPF", width="small"),
                    "Nome Completo": st.column_config.TextColumn("Hóspede", width="large"),
                    "Telefone": st.column_config.TextColumn("Telefone", width="medium"),
                    "E-mail": st.column_config.TextColumn("E-mail", width="medium"),
                }
            )

            st.caption("⚙️ **Ações Rápidas da Tabela:**")
            c_act1, c_act2, c_act3 = st.columns([4, 2, 2])
            with c_act1:
                hosp_sel_tab = st.selectbox(
                    "Selecione um hóspede da tabela para alterar",
                    hospedes_filtrados_res,
                    format_func=lambda h: f"{h.nome} (CPF: {_formatar_cpf(h.cpf)})",
                    key="sel_tab_hosp_reserva",
                    index=None,
                    placeholder="Selecione um hóspede..."
                )
            with c_act2:
                if st.button("✏️ Editar Hóspede", key="btn_edit_tab_hosp_reserva", width="stretch", disabled=not hosp_sel_tab):
                    modal_editar_hospede(HospedeService(db), hosp_sel_tab)
            with c_act3:
                if st.button("🗑️ Excluir Hóspede", key="btn_del_tab_hosp_reserva", width="stretch", disabled=not hosp_sel_tab):
                    try:
                        with SessionLocal() as db_del:
                            HospedeService(db_del).remover_hospede(hosp_sel_tab.cpf)
                        st.success(f"Hóspede {hosp_sel_tab.nome} removido.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        else:
            cols = st.columns(2)
            for i, h in enumerate(hospedes_filtrados_res):
                detalhes = f"""
                <strong>CPF:</strong> {_formatar_cpf(h.cpf)}<br>
                📞 {h.telefone or '—'} &nbsp;·&nbsp; ✉️ {h.email or '—'}<br>
                📍 {h.endereco or '—'}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(h.nome, "Hóspede Registrado", detalhes, status="Ativo"),
                        unsafe_allow_html=True,
                    )
                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        if st.button("✏️ Editar", key=f"btn_edit_res_hosp_{h.cpf}", width="stretch"):
                            modal_editar_hospede(HospedeService(db), h)
                    with c_del:
                        if st.button("🗑️ Excluir", key=f"btn_del_res_hosp_{h.cpf}", width="stretch"):
                            try:
                                with SessionLocal() as db_del:
                                    HospedeService(db_del).remover_hospede(h.cpf)
                                st.success(f"Hóspede {h.nome} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))

# ── Ajustar Suítes ────────────────────────────────────────────────────────────────
with tab_suites:
    st.subheader("Vincular ou remover suítes de uma reserva existente")
    st.caption("Use esta aba para acrescentar uma suíte extra depois que a reserva já foi criada.")

    if "msg_vinculo" in st.session_state:
        st.success(st.session_state.pop("msg_vinculo"))

    with SessionLocal() as db:
        reserva_service = ReservaService(db)
        reserva_suite_service = ReservaSuiteService(db)
        suite_service = SuiteService(db)

        reservas = reserva_service.listar_reservas()
        nomes = {
            r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede)
            for r in reservas
        }
        suites = suite_service.listar_suites()

        if not reservas:
            st.info("Nenhuma reserva cadastrada.")

        elif not suites:
            st.info("Nenhuma suíte cadastrada.")

        else:
            opcoes_reserva = {
                f"#{r.id_reserva} — {nomes[r.id_reserva]} ({r.status})": r.id_reserva
                for r in reservas
            }

            reserva_selecionada = st.selectbox(
                "Selecione a reserva",
                list(opcoes_reserva.keys())
            )

            id_reserva_alvo = opcoes_reserva[reserva_selecionada]
            vinculos_da_reserva = reserva_suite_service.listar_por_reserva(id_reserva_alvo)
            vinculos_ativos = vinculos_da_reserva

            st.divider()
            st.markdown("**Suítes disponíveis para vincular**")
            st.caption(
                "A disponibilidade de cada suíte é checada na hora, de acordo com o período escolhido abaixo."
            )

            suites_selecionaveis = [
                s for s in suites if s.status != "Manutenção"
            ]

            if not suites_selecionaveis:
                st.warning("Não há suítes disponíveis (todas em manutenção).")

            else:
                for suite in suites_selecionaveis:
                    col1, col2, col3, col4, col4b, col5 = st.columns([1.2, 1.8, 1.8, 1.8, 1.8, 1.2])

                    col1.write(f"**Nº {suite.numero}**")
                    col2.write(f"{suite.tipo} · {suite.capacidade} pax")

                    diaria_ajuste = col3.number_input(
                        "Diária (R$)",
                        min_value=0.01,
                        value=float(suite.valor_diaria),
                        step=10.0,
                        format="%.2f",
                        key=f"ajustar_diaria_{suite.id_suite}",
                        label_visibility="collapsed",
                    )

                    data_entrada = col4.date_input(
                        "Entrada",
                        value=date.today(),
                        key=f"ajustar_entrada_{suite.id_suite}",
                        label_visibility="collapsed",
                    )

                    saida_padrao = date.today() + timedelta(days=1)
                    if saida_padrao <= data_entrada:
                        saida_padrao = data_entrada + timedelta(days=1)

                    data_saida = col4b.date_input(
                        "Saída",
                        value=saida_padrao,
                        min_value=data_entrada + timedelta(days=1),
                        key=f"ajustar_saida_{suite.id_suite}",
                        label_visibility="collapsed",
                    )

                    if col5.button("Vincular", key=f"btn_vincular_{suite.id_suite}"):
                        try:
                            reserva_suite_service.vincular_reserva_suite(
                                id_reserva=id_reserva_alvo,
                                id_suite=suite.id_suite,
                                data_entrada=data_entrada,
                                data_saida=data_saida,
                                valor_diaria=diaria_ajuste,  # <-- Envia a diária ajustada
                            )

                            # Recalcula o valor total da reserva com a nova suíte e diária
                            novo_valor = reserva_suite_service.calcular_valor_total_reserva(id_reserva_alvo)
                            reserva_service.definir_valor_total(id_reserva_alvo, novo_valor)

                            st.session_state["msg_vinculo"] = "Suíte vinculada com sucesso!"
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

                    col1, col2, col3 = st.columns([1, 2, 3])

                    col1.write(f"🛏️ Nº {suite.numero}")
                    col2.write(f"{suite.tipo} · {suite.capacidade} pax")
                    col3.write(
                        f"R$ {vinculo.valor_diaria:,.2f}/dia · {vinculo.data_entrada} → {vinculo.data_saida}"
                    )

            st.divider()
            st.subheader("Corrigir data de entrada de um vínculo")
            id_vinculo_corrigir = st.number_input(
                "ID do vínculo (ReservaSuite)", min_value=1, step=1, key="id_corrigir"
            )
            nova_data_entrada = st.date_input(
                "Nova data de entrada", value=date.today(), key="nova_data_entrada"
            )

            if st.button("Corrigir", width="stretch", key="btn_corrigir"):
                try:
                    with SessionLocal() as db:
                        ReservaSuiteService(db).corrigir_data_entrada(int(id_vinculo_corrigir), nova_data_entrada)
                    st.success("Data de entrada corrigida com sucesso!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))