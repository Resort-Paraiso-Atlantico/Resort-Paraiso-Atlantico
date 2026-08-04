import streamlit as st

from app.database import SessionLocal
from app.models.pedido.PedidoCompra import PedidoCompra
from app.models.pedido.PedidoItem import PedidoItem
from app.services.pedido_service.PedidoCompraService import PedidoCompraService
from app.services.fornecedor_service.FornecedorService import FornecedorService
from app.services.produto_service.ProdutoService import ProdutoService

from app.theme import aplicar_tema, cabecalho, badge_status
from app.utils.search_utils import atende_termo_busca

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Pedidos de Compra", "Cadastre e gerencie os pedidos de compra", "🛒")

with SessionLocal() as db:
    pedido_service = PedidoCompraService(db)
    fornecedor_service = FornecedorService(db)
    produto_service = ProdutoService(db)

    if "itens_pedido" not in st.session_state:
        st.session_state.itens_pedido = []

    aba_cadastrar, aba_listar, aba_consultar, aba_cancelar = st.tabs(
        ["Cadastrar", "Listar", "Consultar", "Cancelar"]
    )

    with aba_cadastrar:
        st.subheader("Novo Pedido de Compra")

        fornecedores = fornecedor_service.listar_fornecedores()
        if not fornecedores:
            st.warning("Cadastre um fornecedor primeiro.")
        else:
            produtos = produto_service.listar_todos()
            if not produtos:
                st.warning("Cadastre um produto primeiro.")
            else:
                fornecedor = st.selectbox(
                    "Selecione o Fornecedor",
                    fornecedores,
                    format_func=lambda f: f"{f.nome} (CNPJ: {f.cnpj})",
                    index=None,
                    placeholder="Digite para buscar um fornecedor..."
                )

                st.divider()
                st.subheader("Adicionar Itens ao Pedido")

                col_prod, col_qtd, col_btn = st.columns([4, 2, 2])
                with col_prod:
                    produto = st.selectbox(
                        "Produto",
                        produtos,
                        format_func=lambda p: f"#{p.id_produto} - {p.nome} (R$ {p.valor_unitario:.2f})",
                        index=None,
                        placeholder="Selecione um produto..."
                    )
                with col_qtd:
                    quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

                with col_btn:
                    st.write("") # espaçamento
                    st.write("")
                    add_clicked = st.button("➕ Adicionar Item", type="secondary")

                if add_clicked:
                    if not produto:
                        st.error("Selecione um produto antes de adicionar.")
                    else:
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
                                    "valor_unitario": produto.valor_unitario,
                                }
                            )
                        st.rerun()

                st.divider()
                st.subheader("Resumo dos Itens Adicionados")

                if not st.session_state.itens_pedido:
                    st.info("Nenhum item adicionado ao pedido ainda.")
                else:
                    valor_total = 0
                    for indice, item in enumerate(st.session_state.itens_pedido):
                        total_item = item["quantidade"] * item["valor_unitario"]
                        valor_total += total_item

                        col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 2, 1])
                        col1.write(f"**{item['nome']}**")
                        col2.write(f"{item['quantidade']} un.")
                        col3.write(f"R$ {item['valor_unitario']:.2f}")
                        col4.write(f"R$ {total_item:.2f}")

                        if col5.button("🗑", key=f"remover_{indice}"):
                            st.session_state.itens_pedido.pop(indice)
                            st.rerun()

                    st.markdown(f"### Valor Total do Pedido: **R$ {valor_total:.2f}**")

                    if st.button("Finalizar e Cadastrar Pedido", type="primary"):
                        if not fornecedor:
                            st.error("Selecione um fornecedor para o pedido.")
                        else:
                            try:
                                itens = [
                                    PedidoItem(
                                        id_produto=item["id_produto"],
                                        quantidade=item["quantidade"],
                                        valor_unitario=item["valor_unitario"],
                                        valor_total=item["quantidade"] * item["valor_unitario"],
                                    )
                                    for item in st.session_state.itens_pedido
                                ]
                                pedido = PedidoCompra(
                                    cnpj_fornecedor=fornecedor.cnpj,
                                    pedidoItem=itens,
                                )
                                pedido_service.criar_pedido(pedido)
                                st.success("Pedido de compra cadastrado com sucesso!")
                                st.session_state.itens_pedido.clear()
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))

    with aba_listar:
        st.subheader("Todos os Pedidos de Compra")
        pedidos = pedido_service.listar_todos()

        if not pedidos:
            st.info("Nenhum pedido de compra cadastrado.")
        else:
            termo_busca = st.text_input("🔍 Pesquisar por ID, CNPJ ou Status", key="busca_pedidos")

            pedidos_filtrados = [
                p for p in pedidos
                if atende_termo_busca(termo_busca, p.id_pedido, p.cnpj_fornecedor, p.status)
            ]

            if not pedidos_filtrados:
                st.info(f"Nenhum pedido encontrado para '{termo_busca}'.")
            else:
                cols = st.columns(2)
                for i, pedido in enumerate(pedidos_filtrados):
                    with cols[i % 2]:
                        st.markdown(
                            f"""
                            <div class="resort-suite-card">
                                <span class="resort-suite-number">Pedido #{pedido.id_pedido}</span>
                                <div class="resort-suite-meta">
                                    <strong>Fornecedor CNPJ:</strong> {pedido.cnpj_fornecedor}<br>
                                    <strong>Status:</strong> {pedido.status}<br>
                                    <strong>Valor Total:</strong> R$ {pedido.valor_total:.2f}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    with aba_consultar:
        st.subheader("Consultar Detalhes do Pedido")
        pedidos = pedido_service.listar_todos()

        if not pedidos:
            st.info("Nenhum pedido cadastrado para consulta.")
        else:
            pedido_sel = st.selectbox(
                "Selecione o Pedido",
                pedidos,
                format_func=lambda p: f"Pedido #{p.id_pedido} - CNPJ: {p.cnpj_fornecedor} - R$ {p.valor_total:.2f} ({p.status})",
                index=None,
                placeholder="Busque por código ou fornecedor..."
            )

            if pedido_sel:
                st.markdown(f"### 📋 Detalhes do Pedido #{pedido_sel.id_pedido}")
                st.write(f"**Fornecedor (CNPJ):** {pedido_sel.cnpj_fornecedor}")
                st.write(f"**Status Atual:** {pedido_sel.status}")
                st.write(f"**Valor Total:** R$ {pedido_sel.valor_total:.2f}")

                st.divider()
                st.markdown("#### Itens Incluídos")
                for item in pedido_sel.pedidoItem:
                    nome_prod = item.produto.nome if item.produto else f"Produto #{item.id_produto}"
                    st.write(f"• **{nome_prod}**: {item.quantidade} un. x R$ {item.valor_unitario:.2f} = **R$ {item.valor_total:.2f}**")

    with aba_cancelar:
        st.subheader("Cancelar Pedido de Compra")
        pedidos_cancelaveis = [p for p in pedido_service.listar_todos() if p.status not in ("CANCELADO", "RECEBIDO")]

        if not pedidos_cancelaveis:
            st.info("Não há pedidos disponíveis para cancelamento.")
        else:
            pedido_cancelar = st.selectbox(
                "Selecione o Pedido a Cancelar",
                pedidos_cancelaveis,
                format_func=lambda p: f"Pedido #{p.id_pedido} - CNPJ: {p.cnpj_fornecedor} - R$ {p.valor_total:.2f}",
                index=None,
                placeholder="Busque o pedido que deseja cancelar..."
            )

            if pedido_cancelar:
                st.warning(f"Tem certeza que deseja cancelar o Pedido #{pedido_cancelar.id_pedido}?")
                if st.button("Confirmar Cancelamento", type="primary"):
                    try:
                        pedido_service.cancelar_pedido(pedido_cancelar.id_pedido)
                        st.success(f"Pedido #{pedido_cancelar.id_pedido} cancelado com sucesso.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
