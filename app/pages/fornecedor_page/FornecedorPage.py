import re
import streamlit as st
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.services.fornecedor_service.FornecedorService import FornecedorService
from app.theme import aplicar_tema, cabecalho, card_item
from app.utils.search_utils import atende_termo_busca, sanitizar_documento

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Fornecedores", "Cadastre e gerencie os parceiros e fornecedores do resort", "🚚")

def _formatar_cnpj(cnpj: str) -> str:
    cnpj = sanitizar_documento(cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def _email_valido(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))

@st.dialog("➕ Cadastrar Novo Fornecedor")
def modal_cadastrar_fornecedor(service):
    with st.form("form_modal_cadastrar_fornecedor"):
        cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00 ou números")
        nome = st.text_input("Nome / Razão Social")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        endereco = st.text_input("Endereço Completo")
        submitted = st.form_submit_button("Cadastrar Fornecedor", type="primary", width="stretch")

        if submitted:
            cnpj_limpo = sanitizar_documento(cnpj)
            if len(cnpj_limpo) != 14:
                st.error("CNPJ inválido! informe os 14 dígitos corretamente.")
            elif not nome.strip():
                st.error("Nome é obrigatório.")
            elif not telefone.strip():
                st.error("Telefone é obrigatório.")
            elif not _email_valido(email):
                st.error("Informe um e-mail válido.")
            elif not endereco.strip():
                st.error("Endereço é obrigatório.")
            try:
                service.criar_fornecedor(cnpj_limpo, nome, telefone, email, endereco)
                st.success("Fornecedor cadastrado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except IntegrityError:
                st.error("Já existe um fornecedor cadastrado com este CNPJ.")


@st.dialog("✏️ Editar Fornecedor")
def modal_editar_fornecedor(service, fornecedor):
    with st.form("form_modal_editar_fornecedor"):
        st.caption(f"Editando dados de **CNPJ: {_formatar_cnpj(fornecedor.cnpj)}**")
        nome = st.text_input("Nome / Razão Social", value=fornecedor.nome)
        telefone = st.text_input("Telefone", value=fornecedor.telefone or "")
        email = st.text_input("Email", value=fornecedor.email or "")
        endereco = st.text_input("Endereço", value=fornecedor.endereco or "")
        submitted = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")

        if submitted:
            try:
                service.atualizar_fornecedor(fornecedor.cnpj, nome, telefone, email, endereco)
                st.success("Fornecedor atualizado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


with SessionLocal() as db:
    service = FornecedorService(db)
    fornecedores = service.listar_fornecedores()

    col_busca, col_vis, col_btn = st.columns([4, 2, 2])
    with col_busca:
        termo_busca = st.text_input("🔍 Pesquisar por Nome, CNPJ, E-mail ou Telefone", key="busca_fornecedores", placeholder="Digite para buscar...")
    with col_vis:
        modo_vis = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_fornecedores")
    with col_btn:
        if st.button("➕ Novo Fornecedor", type="primary", width="stretch", key="btn_novo_fornecedor_top"):
            modal_cadastrar_fornecedor(service)

    fornecedores_filtrados = [
        f for f in fornecedores
        if atende_termo_busca(termo_busca, f.nome, f.cnpj, f.email, f.telefone, f.endereco)
    ]

    st.divider()

    if not fornecedores_filtrados:
        if termo_busca:
            st.info(f"Nenhum fornecedor encontrado para '{termo_busca}'.")
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")
    else:
        if modo_vis == "📊 Tabela":
            dados_tabela = [
                {
                    "CNPJ": _formatar_cnpj(f.cnpj),
                    "Nome / Razão Social": f.nome,
                    "Telefone": f.telefone or "—",
                    "E-mail": f.email or "—",
                    "Endereço": f.endereco or "—"
                }
                for f in fornecedores_filtrados
            ]
            st.dataframe(
                dados_tabela,
                width="stretch",
                column_config={
                    "CNPJ": st.column_config.TextColumn("CNPJ", width="medium"),
                    "Nome / Razão Social": st.column_config.TextColumn("Nome / Razão Social", width="large"),
                    "Telefone": st.column_config.TextColumn("Telefone", width="small"),
                    "E-mail": st.column_config.TextColumn("E-mail", width="medium"),
                }
            )

            st.caption("⚙️ **Ações Rápidas da Tabela:**")
            c_act1, c_act2, c_act3 = st.columns([4, 2, 2])
            with c_act1:
                forn_sel_tab = st.selectbox(
                    "Selecione um fornecedor da tabela para alterar",
                    fornecedores_filtrados,
                    format_func=lambda f: f"{f.nome} (CNPJ: {f.cnpj})",
                    key="sel_tab_forn",
                    index=None,
                    placeholder="Selecione um fornecedor..."
                )
            with c_act2:
                if st.button("✏️ Editar Fornecedor", key="btn_edit_tab_forn", width="stretch", disabled=not forn_sel_tab):
                    modal_editar_fornecedor(service, forn_sel_tab)
            with c_act3:
                if st.button("🗑️ Excluir Fornecedor", key="btn_del_tab_forn", width="stretch", disabled=not forn_sel_tab):
                    try:
                        service.remover_fornecedor(forn_sel_tab.cnpj)
                        st.success(f"Fornecedor {forn_sel_tab.nome} removido.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        else:
            cols = st.columns(2)
            for i, h in enumerate(fornecedores_filtrados):
                detalhes = f"""
                <strong>CNPJ:</strong> {_formatar_cnpj(h.cnpj)}<br>
                📞 {h.telefone or '—'} &nbsp;·&nbsp; ✉️ {h.email or '—'}<br>
                📍 {h.endereco or '—'}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(h.nome, "Fornecedor Registrado", detalhes, status="Ativo"),
                        unsafe_allow_html=True,
                    )
                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        if st.button(f"✏️ Editar", key=f"btn_edit_card_{h.cnpj}", width="stretch"):
                            modal_editar_fornecedor(service, h)
                    with c_del:
                        if st.button(f"🗑️ Excluir", key=f"btn_del_card_{h.cnpj}", width="stretch"):
                            try:
                                service.remover_fornecedor(h.cnpj)
                                st.success(f"Fornecedor {h.nome} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
