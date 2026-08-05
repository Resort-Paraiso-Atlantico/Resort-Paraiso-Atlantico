import re
import streamlit as st
from app.database import SessionLocal
from app.services.HospedeService import HospedeService
from app.theme import aplicar_tema, cabecalho, card_item
from app.utils.search_utils import atende_termo_busca

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Hóspedes", "Cadastre e gerencie a base de clientes do resort", "👤")


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
    with st.form("form_modal_cadastrar_hospede"):
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
    with st.form("form_modal_editar_hospede"):
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


with SessionLocal() as db:
    service = HospedeService(db)
    hospedes = service.listar_hospedes()

    c_busca, c_vis, c_btn = st.columns([4, 2, 2])
    with c_busca:
        termo_busca = st.text_input("🔍 Pesquisar por Nome, CPF, Telefone ou E-mail", key="busca_hospedes", placeholder="Digite para buscar...")
    with c_vis:
        modo_vis = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_hospedes")
    with c_btn:
        if st.button("➕ Novo Hóspede", type="primary", width="stretch", key="btn_novo_hospede_top"):
            modal_cadastrar_hospede(service)

    hospedes_filtrados = [
        h for h in hospedes
        if atende_termo_busca(termo_busca, h.nome, h.cpf, h.email, h.telefone, h.endereco)
    ]

    st.divider()

    if not hospedes_filtrados:
        if termo_busca:
            st.info(f"Nenhum hóspede encontrado para '{termo_busca}'.")
        else:
            st.info("Nenhum hóspede cadastrado ainda.")
    else:
        if modo_vis == "📊 Tabela":
            dados_tabela = [
                {
                    "CPF": _formatar_cpf(h.cpf),
                    "Nome Completo": h.nome,
                    "Telefone": h.telefone or "—",
                    "E-mail": h.email or "—",
                    "Endereço": h.endereco or "—"
                }
                for h in hospedes_filtrados
            ]
            st.dataframe(
                dados_tabela,
                width="stretch",
                column_config={
                    "CPF": st.column_config.TextColumn("CPF", width="small"),
                    "Nome Completo": st.column_config.TextColumn("Hóspede", width="large"),
                    "Telefone": st.column_config.TextColumn("Telefone", width="medium"),
                    "E-mail": st.column_config.TextColumn("E-mail", width="medium"),
                }
            )
        else:
            cols = st.columns(2)
            for i, h in enumerate(hospedes_filtrados):
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
                        if st.button("✏️ Editar", key=f"btn_edit_card_hosp_{h.cpf}", width="stretch"):
                            modal_editar_hospede(service, h)
                    with c_del:
                        if st.button("🗑️ Excluir", key=f"btn_del_card_hosp_{h.cpf}", width="stretch"):
                            try:
                                service.remover_hospede(h.cpf)
                                st.success(f"Hóspede {h.nome} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
