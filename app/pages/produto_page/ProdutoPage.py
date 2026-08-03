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

    st.subheader("Produtos Cadastrados")

    produtos = service.listar_todos()

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        st.stop()

    pesquisa = st.text_input(
        "🔍 Pesquisar produto",
        placeholder="Digite o nome do produto..."
    )

    categoria_filtro = st.selectbox(
        "Categoria",
        ["Todas"] + sorted(
            list(
                set(p.categoria for p in produtos)
            )
        )
    )

    produtos_filtrados = []

    for produto in produtos:

        if pesquisa.lower() not in produto.nome.lower():
            continue

        if categoria_filtro != "Todas" and produto.categoria != categoria_filtro:
            continue

        produtos_filtrados.append(produto)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Produtos",
        len(produtos_filtrados)
    )

    col2.metric(
        "Sem Estoque",
        sum(
            1
            for p in produtos_filtrados
            if p.quantidade == 0
        )
    )

    col3.metric(
        "Estoque Baixo",
        sum(
            1
            for p in produtos_filtrados
            if 0 < p.quantidade <= p.estoque_minimo
        )
    )

    valor_total = sum(
        p.quantidade * p.valor_unitario
        for p in produtos_filtrados
    )

    col4.metric(
        "Valor em Estoque",
        f"R$ {valor_total:.2f}"
    )

    st.divider()

    for produto in produtos_filtrados:

        if produto.quantidade == 0:

            status = "🔴 Sem estoque"

        elif produto.quantidade <= produto.estoque_minimo:

            status = "🟡 Estoque baixo"

        else:

            status = "🟢 Normal"

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(f"### 📦 {produto.nome}")

                st.write(f"**Categoria:** {produto.categoria}")

                st.write(f"**Preço Unitário:** R$ {produto.valor_unitario:.2f}")

            with col2:

                st.metric(
                    "Estoque",
                    f"{produto.quantidade} un."
                )

                st.write(status)

            st.progress(
                min(
                    produto.quantidade /
                    max(produto.estoque_minimo * 2, 1),
                    1.0
                )
            )

            col1, col2 = st.columns(2)

            col1.write(
                f"**Estoque mínimo:** {produto.estoque_minimo}"
            )

            col2.write(
                f"**Valor em estoque:** "
                f"R$ {(produto.quantidade * produto.valor_unitario):.2f}"
            )

with aba_remover:
    st.subheader("Remover produto")
    id_remover = st.text_input("ID do produto", key = "id_remover")
    if st.button("Remover"):
        try:
            service.remover_produto(id_remover)
            st.success("Produto removido com sucesso.")
        except ValueError as e:
            st.error(str(e))