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

with SessionLocal() as db:
    service = FornecedorService(db)
    fornecedores = service.listar_fornecedores()

    aba_listar, aba_cadastrar, aba_atualizar, aba_remover = st.tabs(
        ["📋 Listar", "➕ Cadastrar", "✏️ Editar", "🗑️ Remover"]
    )

    with aba_listar:
        st.subheader("Todos os fornecedores")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            termo_busca = st.text_input("🔍 Pesquisar por Nome, CNPJ, E-mail ou Telefone", key="busca_fornecedores")
        with c2:
            st.metric("Total Cadastrado", len(fornecedores))

        fornecedores_filtrados = [
            f for f in fornecedores
            if atende_termo_busca(termo_busca, f.nome, f.cnpj, f.email, f.telefone, f.endereco)
        ]

        st.divider()

        if fornecedores_filtrados:
            cols = st.columns(2)
            for i, h in enumerate(fornecedores_filtrados):
                detalhes = f"""
                <strong>CNPJ:</strong> {h.cnpj}<br>
                📞 {h.telefone or '—'} &nbsp;·&nbsp; ✉️ {h.email or '—'}<br>
                📍 {h.endereco or '—'}
                """
                with cols[i % 2]:
                    st.markdown(
                        card_item(h.nome, "Fornecedor Registrado", detalhes, status="Ativo"),
                        unsafe_allow_html=True,
                    )
        else:
            if termo_busca:
                st.info(f"Nenhum fornecedor encontrado para '{termo_busca}'.")
            else:
                st.info("Nenhum fornecedor cadastrado.")

    with aba_cadastrar:
        st.subheader("Cadastrar novo fornecedor")
        with st.form("form_cadastro"):
            cnpj = st.text_input("CNPJ", placeholder="00.000.000/0000-00 ou números")
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone")
            email = st.text_input("Email")
            endereco = st.text_input("Endereço")
            submitted = st.form_submit_button("Cadastrar", type="primary")

            if submitted:
                cnpj_limpo = sanitizar_documento(cnpj)
                try:
                    service.criar_fornecedor(cnpj_limpo or cnpj, nome, telefone, email, endereco)
                    st.success("Fornecedor cadastrado com sucesso.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except IntegrityError:
                    st.error("Já existe um fornecedor cadastrado com este CNPJ.")

    with aba_atualizar:
        st.subheader("Atualizar fornecedor")
        if not fornecedores:
            st.info("Nenhum fornecedor disponível para edição.")
        else:
            fornecedor_sel = st.selectbox(
                "Selecione o fornecedor",
                fornecedores,
                format_func=lambda f: f"{f.nome} (CNPJ: {f.cnpj})",
                key="select_fornecedor_atualizar",
                index=None,
                placeholder="Busque por nome ou CNPJ..."
            )

            if fornecedor_sel:
                with st.form("form_atualizar"):
                    nome = st.text_input("Nome", value=fornecedor_sel.nome)
                    telefone = st.text_input("Telefone", value=fornecedor_sel.telefone or "")
                    email = st.text_input("Email", value=fornecedor_sel.email or "")
                    endereco = st.text_input("Endereço", value=fornecedor_sel.endereco or "")
                    submitted = st.form_submit_button("Salvar alterações", type="primary")

                    if submitted:
                        try:
                            service.atualizar_fornecedor(fornecedor_sel.cnpj, nome, telefone, email, endereco)
                            st.success("Fornecedor atualizado com sucesso.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

    with aba_remover:
        st.subheader("Remover fornecedor")
        if not fornecedores:
            st.info("Nenhum fornecedor disponível para remoção.")
        else:
            fornecedor_rem = st.selectbox(
                "Selecione o fornecedor a remover",
                fornecedores,
                format_func=lambda f: f"{f.nome} (CNPJ: {f.cnpj})",
                key="select_fornecedor_remover",
                index=None,
                placeholder="Busque por nome ou CNPJ..."
            )

            if fornecedor_rem:
                st.warning(f"Tem certeza que deseja remover o fornecedor **{fornecedor_rem.nome}** (CNPJ: {fornecedor_rem.cnpj})?")
                if st.button("Confirmar Remoção", type="primary"):
                    try:
                        service.remover_fornecedor(fornecedor_rem.cnpj)
                        st.success("Fornecedor removido com sucesso.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
