import streamlit as st

from app.database import SessionLocal

from app.services.estoque_service.EstoqueService import EstoqueService
from app.services.produto_service.ProdutoService import ProdutoService
from app.services.pedido_service.PedidoCompraService import PedidoCompraService

from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()

cabecalho(
    "Estoque",
    "Controle de entrada e saída de produtos",
    "📦"
)

db = SessionLocal()

estoque_service = EstoqueService(db)
produto_service = ProdutoService(db)
pedido_service = PedidoCompraService(db)

aba_consultar, aba_entrada, aba_saida, aba_receber = st.tabs(
    [
        "Consultar",
        "Entrada",
        "Saída",
        "Receber Pedido"
    ]
)

with aba_consultar:

    produtos = produto_service.listar_todos()

    if not produtos:
        st.info("Nenhum produto cadastrado.")

    else:

        dados = []

        for produto in produtos:

            dados.append(
                {
                    "Código": produto.id_produto,
                    "Produto": produto.nome,
                    "Categoria": produto.categoria,
                    "Quantidade": produto.quantidade,
                    "Estoque mínimo": produto.estoque_minimo,
                    "Valor Unitário": produto.valor_unitario
                }
            )

        st.dataframe(
            dados,
            use_container_width=True
        )

with aba_entrada:

    produtos = produto_service.listar_todos()

    with st.form("entrada"):

        produto = st.selectbox(
            "Produto",
            produtos,
            format_func=lambda p: p.nome
        )

        quantidade = st.number_input(
            "Quantidade",
            min_value=1,
            step=1
        )

        enviar = st.form_submit_button(
            "Registrar Entrada"
        )

        if enviar:

            try:

                estoque_service.registrar_entrada(
                    produto.id_produto,
                    quantidade
                )

                st.success("Entrada registrada.")

            except ValueError as e:

                st.error(str(e))

with aba_saida:

    produtos = produto_service.listar_todos()

    with st.form("saida"):

        produto = st.selectbox(
            "Produto",
            produtos,
            key="saida_produto",
            format_func=lambda p: p.nome
        )

        quantidade = st.number_input(
            "Quantidade",
            min_value=1,
            step=1,
            key="saida_quantidade"
        )

        enviar = st.form_submit_button(
            "Registrar Saída"
        )

        if enviar:

            try:

                estoque_service.registrar_saida(
                    produto.id_produto,
                    quantidade
                )

                st.success("Saída registrada.")

            except ValueError as e:

                st.error(str(e))

with aba_receber:

    pedidos = pedido_service.buscar_por_status("PENDENTE")

    if not pedidos:

        st.info("Não há pedidos pendentes.")

    else:

        pedido = st.selectbox(
            "Pedido",
            pedidos,
            format_func=lambda p:
                f"Pedido {p.id_pedido} - {p.cnpj_fornecedor}"
        )

        if st.button("Receber Pedido"):

            try:

                estoque_service.receber_pedido(
                    pedido.id_pedido
                )

                st.success("Pedido recebido.")

                st.rerun()

            except ValueError as e:

                st.error(str(e))