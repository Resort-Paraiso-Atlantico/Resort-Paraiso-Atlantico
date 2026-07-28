import streamlit as st

from app.database import SessionLocal
from app.services.fornecedor_service.FornecedorService import FornecedorService
from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precista estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Fornecedores", "Cadastre e gerencie os dados dos fornecedores", "🚚")

db = SessionLocal()
service = FornecedorService(db)

aba_cadastrar, aba_listar, aba_atualizar, aba_remover = st.tabs(
    ["Cadastrar", "Listar", "Atualizar", "Remover"]
)

with aba_cadastrar:
    st.subheader("Cadastrar novo fornecedor.")
    with st.form("form_cadastro"):
        cnpj = st.text_input("CNPJ")
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        endereco = st.text_input("Endereço")
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            try:
                service.criar_fornecedor(cnpj, nome, telefone, email, endereco)
                st.success("Fornecedor cadastrado com sucesso.")
            except ValueError as e:
                st.error(str(e))

with aba_listar:
    st.subheader("Todos os fornecedores.")
    fornecedores = service.listar_fornecedores()
    if fornecedores:
        cols = st.columns(2)
        for i, h in enumerate(fornecedores):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">
                        <span class="resort-suite-number">{h.nome}</span>
                        <div class="resort-suite-meta">
                            CNPJ: {h.cnpj}<br>
                            📞 {h.telefone or '—'} · ✉️ {h.email or '—'}<br>
                            📍 {h.endereco or '—'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Nenhum fornecedor cadastrado.")

with aba_atualizar:
    st.subheader("Atualizar fornecedor.")
    cnpj_busca = st.text_input("CNPJ do fornecedor", key = "cnpj_atualizar")
    if st.button("Buscar", key = "buscar_atualizar"):
        try:
            fornecedor = service.buscar_por_cnpj(cnpj_busca)
            if fornecedor is None:
                st.warning("Fornecedor não encontrado.")
            else:
                st.session_state["fornecedor_editando"] = fornecedor
        except ValueError as e:
            st.error(str(e))

    if "fornecedor_editando" in st.session_state:
        f = st.session_state["fornecedor_editando"]
        with st.form("form_atualizar"):
            nome = st.text_input("Nome", value = f.nome)
            telefone = st.text_input("Telefone", value = f.telefone)
            email = st.text_input("Email", value = f.email)
            endereco = st.text_input("Endereço", value = f.endereco)
            submitted = st.form_submit_button("Salvar alterações.")

            if submitted:
                try:
                    service.atualizar_fornecedor(f.cnpj, nome, telefone, email, endereco)
                    st.success("Fornecedor atualizado com sucesso.")
                    del st.session_state["fornecedor_editando"]
                except ValueError as e:
                    st.error(str(e))

with aba_remover:
    st.subheader("Remover fornecedor")
    cnpj_remover = st.text_input("CNPJ do fornecedor", key = "cnpj_remover")
    if st.button("Remover"):
        try:
            service.remover_fornecedor(cnpj_remover)
            st.success("Fornecedor removido com sucesso.")
        except ValueError as e:
            st.error(str(e))


