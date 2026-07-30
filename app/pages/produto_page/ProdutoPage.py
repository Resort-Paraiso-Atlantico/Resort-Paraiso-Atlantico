import streamlit as st

from app.database import SessionLocal
from app.services.produto_service.ProdutoService import ProdutoService
from app.theme import aplicar_tema, cabecalho


if not st.user.is_logged_in:
    st.error("Você precista estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Produtos", "Cadastre e Gerencie os dados dos produtos", "📦")

db = SessionLocal()
service = ProdutoService(db)

aba_cadastrar, aba_listar, aba_atualizar, aba_remover = st.tabs(
    ["Cadastrar", "Listar", "Atualizar", "Remover"]
)

with aba_cadastrar:
    st.subheader("Cadastrar novo produto.")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        categoria = st.selectbox("Categoria", ["Cat1", "Cat2", "Cat3"])
        estoque_minimo = st.number_input("Estoque Mínimo", min_value = 1)
        valor_unitario = st.number_input("Valor Unitário", min_value = 0.1, format = "%.2f")
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            try:
                service.criar_produto(nome, categoria, estoque_minimo, valor_unitario)
                st.success("Produto cadastrado com sucesso.")
            except ValueError as e:
                st.error(str(e))

with aba_listar:
    st.subheader("Todos os produtos")
    produtos = service.listar_todos()
    if produtos:
        cols = st.columns(2)
        for i, h in enumerate(produtos):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">
                        <span class="resort-suite-number">{h.nome}</span>
                        <div class="resort-suite-meta">
                            ID: {h.id_produto}<br>
                            📞 {h.categoria or '—'} · ✉️ {h.quantidade or '—'}<br>
                            📍 {h.estoque_minimo or '—'} · ✉️ {h.valor_unitario or '—'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Nenhum produto cadastrado.")

with aba_atualizar:
    st.subheader("Atualizar produto.")
    id_buscar = st.text_input("ID do produto", key = "produto_atualizar")
    if st.button("Buscar", key = "buscar_atualizar"):
        try:
            produto = service.buscar_por_id_produto(id_buscar)
            if produto is None:
                st.warning("Produto não encontrado.")
            else:
                st.session_state["produto_editando"] = produto
        except ValueError as e:
            st.error(str(e))

    if "produto_editando" in st.session_state:
        p = st.session_state["produto_editando"]
        with st.form("form_atualizar"):
            nome = st.text_input("Nome", value = p.nome)
            categorias = ["Cat1", "Cat2", "Cat3"]
            categoria = st.selectbox("Categoria", categorias, index = categorias.index(p.categoria))
            quantidade = st.number_input("Quantidade", value = p.quantidade)
            estoque_minimo = st.number_input("Estoque Mínimo", min_value = 1, value = p.estoque_minimo)
            valor_unitario = st.number_input("Valor Unitário", min_value = 0.1, format = "%.2f", value = p.valor_unitario)
            submitted = st.form_submit_button("Salvar alterações.")

            if submitted:
                try:
                    service.atualizar_produto(p.id_produto, nome, categoria, quantidade, estoque_minimo, valor_unitario)
                    st.success("Produto atualizado com sucesso.")
                    del st.session_state["produto_editando"]
                except ValueError as e:
                    st.error(str(e))

with aba_remover:
    st.subheader("Remover produto")
    id_remover = st.text_input("ID do produto", key = "id_remover")
    if st.button("Remover"):
        try:
            service.remover_produto(id_remover)
            st.success("Produto removido com sucesso.")
        except ValueError as e:
            st.error(str(e))