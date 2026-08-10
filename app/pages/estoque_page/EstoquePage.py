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
cabecalho("Estoque", "Controle de movimentações, entrada e saída de produtos", "📦")


@st.dialog("📥 Registrar Entrada Manual")
def modal_entrada_estoque(estoque_service, produtos):
    with st.form("form_modal_entrada"):
        produto = st.selectbox(
            "Selecione o Produto",
            produtos,
            format_func=lambda p: f"#{p.id_produto} - {p.nome} (Atual: {p.quantidade} un.)",
            index=None,
            placeholder="Digite para pesquisar o produto..."
        )
        quantidade = st.number_input("Quantidade de Entrada", min_value=1, step=1, value=1)
        enviar = st.form_submit_button("Confirmar Entrada", type="primary", width="stretch")

        if enviar:
            if not produto:
                st.error("Selecione um produto.")
            else:
                try:
                    estoque_service.registrar_entrada(produto.id_produto, quantidade)
                    st.success(f"Entrada de {quantidade} un. registrada para '{produto.nome}'.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


@st.dialog("📤 Registrar Saída / Baixa")
def modal_saida_estoque(estoque_service, produtos):
    with st.form("form_modal_saida"):
        produto = st.selectbox(
            "Selecione o Produto",
            produtos,
            format_func=lambda p: f"#{p.id_produto} - {p.nome} (Atual: {p.quantidade} un.)",
            index=None,
            placeholder="Digite para pesquisar o produto..."
        )
        quantidade = st.number_input("Quantidade de Saída", min_value=1, step=1, value=1)
        enviar = st.form_submit_button("Confirmar Saída", type="primary", width="stretch")

        if enviar:
            if not produto:
                st.error("Selecione um produto.")
            else:
                try:
                    estoque_service.registrar_saida(produto.id_produto, quantidade)
                    st.success(f"Saída de {quantidade} un. registrada para '{produto.nome}'.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


with SessionLocal() as db:
    estoque_service = EstoqueService(db)
    produto_service = ProdutoService(db)
    pedido_service = PedidoCompraService(db)

    aba_consultar, aba_entrada, aba_saida, aba_receber = st.tabs(
        ["📋 Consultar & Movimentar", "📥 Entrada Manual", "📤 Saída / Baixa", "🚚 Receber Pedido"]
    )

    with aba_consultar:
        produtos = produto_service.listar_todos()

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            c_busca, c_ent, c_sai = st.columns([4, 2, 2])
            with c_busca:
                pesquisa_estoque = st.text_input("🔍 Pesquisar produto no estoque por Nome ou Categoria", key="busca_estoque")
            with c_ent:
                if st.button("📥 Entrada Rápida", type="primary", width="stretch", key="btn_ent_top"):
                    modal_entrada_estoque(estoque_service, produtos)
            with c_sai:
                if st.button("📤 Saída Rápida", width="stretch", key="btn_sai_top"):
                    modal_saida_estoque(estoque_service, produtos)

            produtos_filtrados = [
                p for p in produtos
                if atende_termo_busca(pesquisa_estoque, p.nome, p.categoria, p.id_produto)
            ]

            st.divider()

            if not produtos_filtrados:
                st.info(f"Nenhum produto encontrado para '{pesquisa_estoque}'.")
            else:
                dados = [
                    {
                        "Código": f"#{p.id_produto}",
                        "Produto": p.nome,
                        "Categoria": p.categoria,
                        "Qtd Atual": p.quantidade,
                        "Estoque Mínimo": p.estoque_minimo,
                        "Ponto Reposição": getattr(p, 'ponto_reposicao', 0),
                        "Estoque Máximo": getattr(p, 'estoque_maximo', 0),
                        "Lead Time": f"{getattr(p, 'lead_time', 0)} d",
                        "Custo Unitário": float(p.valor_unitario),
                        "Preço de Venda": float(getattr(p, 'preco_venda', 0.0)),
                        "Valor em Estoque": float(p.quantidade * p.valor_unitario),
                        "Status": "🔴 Crítico" if p.quantidade == 0 else ("🟡 Baixo" if p.quantidade <= p.estoque_minimo else "🟢 Normal")
                    }
                    for p in produtos_filtrados
                ]

                st.dataframe(
                    dados,
                    width="stretch",
                    column_config={
                        "Código": st.column_config.TextColumn("Código", width="small"),
                        "Produto": st.column_config.TextColumn("Produto", width="medium"),
                        "Custo Unitário": st.column_config.NumberColumn("Custo Unitário", format="R$ %.2f"),
                        "Preço de Venda": st.column_config.NumberColumn("Preço de Venda", format="R$ %.2f"),
                        "Valor em Estoque": st.column_config.NumberColumn("Valor em Estoque", format="R$ %.2f"),
                        "Qtd Atual": st.column_config.NumberColumn("Qtd Atual"),
                        "Estoque Mínimo": st.column_config.NumberColumn("Mínimo"),
                        "Ponto Reposição": st.column_config.NumberColumn("Ponto Reposição"),
                        "Estoque Máximo": st.column_config.NumberColumn("Máximo"),
                        "Lead Time": st.column_config.TextColumn("Lead Time"),
                    }
                )

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