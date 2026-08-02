import streamlit as st

from app.database import SessionLocal
from app.models.pedido.PedidoCompra import PedidoCompra
from app.models.pedido.PedidoItem import PedidoItem
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

if "itens_pedido" not in st.session_state:
    st.session_state.itens_pedido = []

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

    fornecedor = st.selectbox(
        "Fornecedor",
        fornecedores,
        format_func=lambda f: f.nome
    )

    st.divider()

    st.subheader("Adicionar Item")

    produto = st.selectbox(
        "Produto",
        produtos,
        format_func=lambda p: p.nome
    )

    quantidade = st.number_input(
        "Quantidade",
        min_value=1,
        value=1,
        step=1
    )

    if st.button("Adicionar Item"):

        encontrado = False

        for item in st.session_state.itens_pedido:

            if item["id_produto"] == produto.id_produto:
                item["quantidade"] += quantidade
                encontrado = True
                break

        if not encontrado:

            st.session_state.itens_pedido.append(
                {
                    "id_produto": produto.id_produto,
                    "nome": produto.nome,
                    "quantidade": quantidade,
                    "valor_unitario": produto.valor_unitario
                }
            )

        st.rerun()

    st.divider()

    st.subheader("Itens do Pedido")

    if not st.session_state.itens_pedido:

        st.info("Nenhum item adicionado.")

    else:

        valor_total = 0

        for indice, item in enumerate(st.session_state.itens_pedido):

            total_item = (
                item["quantidade"] *
                item["valor_unitario"]
            )

            valor_total += total_item

            col1, col2, col3, col4, col5 = st.columns(
                [4, 2, 2, 2, 1]
            )

            col1.write(item["nome"])
            col2.write(item["quantidade"])
            col3.write(f"R$ {item['valor_unitario']:.2f}")
            col4.write(f"R$ {total_item:.2f}")

            if col5.button(
                "🗑",
                key=f"remover_{indice}"
            ):

                st.session_state.itens_pedido.pop(indice)

                st.rerun()

        st.markdown(
            f"### Valor Total: R$ {valor_total:.2f}"
        )

        if st.button("Cadastrar Pedido"):

            try:

                itens = []

                for item in st.session_state.itens_pedido:

                    itens.append(

                        PedidoItem(
                            id_produto=item["id_produto"],
                            quantidade=item["quantidade"],
                            valor_unitario=item["valor_unitario"],
                            valor_total=(
                                item["quantidade"] *
                                item["valor_unitario"]
                            )
                        )

                    )

                pedido = PedidoCompra(
                    cnpj_fornecedor=fornecedor.cnpj,
                    pedidoItem=itens
                )

                pedido_service.criar_pedido(pedido)

                st.success("Pedido cadastrado com sucesso.")

                st.session_state.itens_pedido.clear()

                st.rerun()

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

with aba_cancelar:

    id_cancelar = st.text_input(
        "Pedido",
        key="pedido_cancelar"
    )

    if st.button("Cancelar Pedido"):

        try:

            pedido_service.cancelar_pedido(
                id_cancelar
            )

            st.success("Pedido cancelado.")

        except ValueError as e:

            st.error(str(e))
   


