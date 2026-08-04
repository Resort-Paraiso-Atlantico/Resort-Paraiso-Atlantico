import streamlit as st

from app.database import SessionLocal
from app.services.estoque_service.EstoqueService import EstoqueService
from app.services.produto_service.ProdutoService import ProdutoService
from app.services.pedido_service.PedidoCompraService import PedidoCompraService
from app.theme import aplicar_tema, cabecalho
from app.utils.search_utils import atende_termo_busca

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Estoque", "Controle de entrada e saída de produtos", "📦")

with SessionLocal() as db:
    estoque_service = EstoqueService(db)
    produto_service = ProdutoService(db)
    pedido_service = PedidoCompraService(db)

    aba_consultar, aba_entrada, aba_saida, aba_receber = st.tabs(
        ["Consultar", "Entrada", "Saída", "Receber Pedido"]
    )

    with aba_consultar:
        st.subheader("Consulta de Estoque")
        produtos = produto_service.listar_todos()

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            pesquisa_estoque = st.text_input("🔍 Pesquisar produto no estoque por Nome ou Categoria", key="busca_estoque")

            produtos_filtrados = [
                p for p in produtos
                if atende_termo_busca(pesquisa_estoque, p.nome, p.categoria, p.id_produto)
            ]

            if not produtos_filtrados:
                st.info(f"Nenhum produto encontrado para '{pesquisa_estoque}'.")
            else:
                dados = [
                    {
                        "Código": p.id_produto,
                        "Produto": p.nome,
                        "Categoria": p.categoria,
                        "Quantidade Atual": p.quantidade,
                        "Estoque Mínimo": p.estoque_minimo,
                        "Valor Unitário (R$)": f"{p.valor_unitario:.2f}",
                        "Valor Total (R$)": f"{(p.quantidade * p.valor_unitario):.2f}",
                        "Status": "🔴 Crítico" if p.quantidade == 0 else ("🟡 Baixo" if p.quantidade <= p.estoque_minimo else "🟢 Normal")
                    }
                    for p in produtos_filtrados
                ]

                st.dataframe(dados, use_container_width=True)

    with aba_entrada:
        st.subheader("Registrar Entrada Manual")
        produtos = produto_service.listar_todos()

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            with st.form("entrada"):
                produto = st.selectbox(
                    "Selecione o Produto",
                    produtos,
                    format_func=lambda p: f"#{p.id_produto} - {p.nome} (Atual: {p.quantidade} un.)",
                    index=None,
                    placeholder="Digite para pesquisar o produto..."
                )

                quantidade = st.number_input("Quantidade de Entrada", min_value=1, step=1, value=1)
                enviar = st.form_submit_button("Registrar Entrada", type="primary")

                if enviar:
                    if not produto:
                        st.error("Selecione um produto.")
                    else:
                        try:
                            estoque_service.registrar_entrada(produto.id_produto, quantidade)
                            st.success(f"Entrada de {quantidade} un. registrada para o produto '{produto.nome}'.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

    with aba_saida:
        st.subheader("Registrar Saída / Baixa")
        produtos = produto_service.listar_todos()

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            with st.form("saida"):
                produto = st.selectbox(
                    "Selecione o Produto",
                    produtos,
                    key="saida_produto",
                    format_func=lambda p: f"#{p.id_produto} - {p.nome} (Atual: {p.quantidade} un.)",
                    index=None,
                    placeholder="Digite para pesquisar o produto..."
                )

                quantidade = st.number_input("Quantidade de Saída", min_value=1, step=1, value=1, key="saida_quantidade")
                enviar = st.form_submit_button("Registrar Saída", type="primary")

                if enviar:
                    if not produto:
                        st.error("Selecione um produto.")
                    else:
                        try:
                            estoque_service.registrar_saida(produto.id_produto, quantidade)
                            st.success(f"Saída de {quantidade} un. registrada para o produto '{produto.nome}'.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

    with aba_receber:
        st.subheader("Receber Pedido de Compra")
        pedidos = pedido_service.buscar_por_status("PENDENTE")

        if not pedidos:
            st.info("Não há pedidos de compra pendentes no momento.")
        else:
            pedido = st.selectbox(
                "Selecione o Pedido a Receber",
                pedidos,
                format_func=lambda p: f"Pedido #{p.id_pedido} - Fornecedor: {p.cnpj_fornecedor} (Status: {p.status})",
                index=None,
                placeholder="Selecione um pedido pendente..."
            )

            if pedido:
                st.write(f"**Itens do Pedido #{pedido.id_pedido}:**")
                for item in pedido.pedidoItem:
                    st.write(f"- {item.produto.nome if item.produto else 'Produto #' + str(item.id_produto)}: **{item.quantidade} un.**")

                if st.button("Confirmar Recebimento e Dar Entrada no Estoque", type="primary"):
                    try:
                        estoque_service.receber_pedido(pedido.id_pedido)
                        st.success(f"Pedido #{pedido.id_pedido} recebido e estoque atualizado com sucesso!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))