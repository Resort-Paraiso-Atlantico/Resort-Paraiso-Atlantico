import streamlit as st

from app.database import SessionLocal
from app.repositories.pedido_compra_repository.PedidoCompraRepository import PedidoCompraRepository
from app.services.pedido_service.PedidoCompraService import PedidoCompraService
from app.services.fornecedor_service.FornecedorService import FornecedorService
from app.services.produto_service.ProdutoService import ProdutoService

from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho(
    "Pedidos de Compra",
    "Cadastre e gerencie os pedidos de compra",
    "🛒"
)

db = SessionLocal()

pedido_service = PedidoCompraService(db)
fornecedor_service = FornecedorService(db)
produto_service = ProdutoService(db)

aba_cadastrar, aba_listar, aba_consultar, aba_cancelar = st.tabs(
    [
        "Cadastrar",
        "Listar",
        "Consultar",
        "Cancelar"
    ]
)

with aba_cadastrar:
    st.subheader("Novo Pedido")

    fornecedores = fornecedor_service.listar_fornecedores()

    if not fornecedores:
        st.warning("Cadastre um fornecedor primeiro.")
        st.stop()

    produtos = produto_service.listar_todos()

    if not produtos:
        st.warning("Cadastre um produto primeiro.")
        st.stop()

        with st.form("novo_pedido"):

            fornecedor = st.selectbox(
                "Fornecedor",
                fornecedores,
                format_func = lambda f:f.nome
            )

        st.markdown("### Item 1")
        produto1 = st.selectbox(
            "Produto",
            produtos,
            key="produto1",
            format_func = lambda p:p.nome
        )
        quantidade1 = st.number_input(
            "Quantidade",
            min_value = 1,
            key = "qtd1"
        )

        st.markdown("### Item 2")
        produto2 = st.selectbox(
            "Produto",
            produtos,
            key="produto2",
            format_func = lambda p:p.nome
        )
        quantidade2 = st.number_input(
            "Quantidade",
            min_value = 1,
            key = "qtd2"
        )

        st.markdown("### Item 3")
        produto3 = st.selectbox(
            "Produto",
            produtos,
            key="produto3",
            format_func = lambda p:p.nome
        )
        quantidade3 = st.number_input(
            "Quantidade",
            min_value = 1,
            key = "qtd3"
        )

        submitted = st.form_submit_button("Cadastrar Pedido")

        if submitted:
            itens = []

            if quantidade1 > 0:
                itens.append(
                    (
                        produto1.id_produto,
                        quantidade1
                    )
                )
            if quantidade2 > 0:
                itens.append(
                    (
                        produto2.id_produto,
                        quantidade2
                    )
                )
            if quantidade3 > 0:
                itens.append(
                    (
                        produto3.id_produto,
                        quantidade3
                    )
                )
            try:
                pedido_service.criar_pedido(
                    fornecedor.cnpj,
                    itens
                )
                st.succes("Pedido criado.")
            except ValueError as e:
                st.error(str(e))

with aba_listar:
    pedidos = pedido_service.listar_todos()

    if pedidos:
        cols = st.columns(2)

        for i, pedido in enumerate(pedidos):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">

                    <span class="resort-suite-number">
                    Pedido #{pedido.id_pedido}
                    </span>

                    <div class="resort-suite-meta">

                    Fornecedor:
                    {pedido.cnpj_fornecedor}

                    <br>

                    Status:
                    {pedido.status}

                    <br>

                    Valor Total:
                    R$
                    {pedido.valor_total:.2f}

                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )
with aba_consultar:

    id_pedido = st.text_input("ID do pedido")

    if st.button("Buscar"):

        pedido = pedido_service.buscar_por_id(id_pedido)

        if pedido is None:

            st.warning("Pedido não encontrado.")

        else:

            st.write(f"Fornecedor: {pedido.cnpj_fornecedor}")
            st.write(f"Status: {pedido.status}")

            st.markdown("### Itens")

            for item in pedido.pedidoItem:

                st.write(
                    f"{item.produto.nome}"
                    f" - {item.quantidade}"
                )

   


