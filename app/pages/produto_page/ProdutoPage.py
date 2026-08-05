import streamlit as st

from app.database import SessionLocal
from app.services.produto_service.ProdutoService import ProdutoService
from app.theme import aplicar_tema, cabecalho, card_item, badge_status
from app.utils.search_utils import atende_termo_busca, normalizar_texto

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Produtos", "Cadastre e controle o catálogo de produtos do resort", "📦")

with SessionLocal() as db:
    service = ProdutoService(db)
    produtos = service.listar_todos()

    aba_listar, aba_cadastrar, aba_atualizar, aba_remover = st.tabs(
        ["📋 Listar", "➕ Cadastrar", "✏️ Editar", "🗑️ Remover"]
    )

    with aba_listar:
        st.subheader("Produtos Cadastrados")

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            col_busca, col_cat = st.columns([2, 1])
            with col_busca:
                pesquisa = st.text_input(
                    "🔍 Pesquisar produto",
                    placeholder="Nome, categoria ou código...",
                    key="busca_produtos"
                )
            with col_cat:
                categorias = ["Todas"] + sorted(list(set(p.categoria for p in produtos)))
                categoria_filtro = st.selectbox("Filtrar Categoria", categorias)

            produtos_filtrados = [
                p for p in produtos
                if atende_termo_busca(pesquisa, p.nome, p.categoria, p.id_produto)
                and (categoria_filtro == "Todas" or p.categoria == categoria_filtro)
            ]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Produtos", len(produtos_filtrados))
            c2.metric("Sem Estoque", sum(1 for p in produtos_filtrados if p.quantidade == 0))
            c3.metric("Estoque Baixo", sum(1 for p in produtos_filtrados if 0 < p.quantidade <= p.estoque_minimo))
            valor_total = sum(p.quantidade * p.valor_unitario for p in produtos_filtrados)
            c4.metric("Valor em Estoque", f"R$ {valor_total:,.2f}")

            st.divider()

            if not produtos_filtrados:
                st.info("Nenhum produto encontrado com os filtros aplicados.")
            else:
                cols = st.columns(2)
                for i, produto in enumerate(produtos_filtrados):
                    if produto.quantidade == 0:
                        status_str = "Sem estoque"
                    elif produto.quantidade <= produto.estoque_minimo:
                        status_str = "Estoque baixo"
                    else:
                        status_str = "Normal"

                    detalhes = f"""
                    <strong>Categoria:</strong> {produto.categoria}<br>
                    <strong>Preço Unitário:</strong> R$ {produto.valor_unitario:,.2f}<br>
                    <strong>Estoque Atual:</strong> {produto.quantidade} un. (Mínimo: {produto.estoque_minimo})<br>
                    <strong>Valor Total:</strong> R$ {(produto.quantidade * produto.valor_unitario):,.2f}
                    """
                    with cols[i % 2]:
                        st.markdown(
                            card_item(
                                f"#{produto.id_produto} - {produto.nome}",
                                f"Categoria: {produto.categoria}",
                                detalhes,
                                status=status_str
                            ),
                            unsafe_allow_html=True,
                        )

    with aba_cadastrar:
        st.subheader("Cadastrar novo produto")
        with st.form("form_cadastro_produto"):
            nome = st.text_input("Nome do Produto")
            categoria = st.selectbox("Categoria", ["Alimentos", "Bebidas", "Limpeza", "Utensílios", "Outros"])
            estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=5)
            valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.01, value=10.00, format="%.2f")
            submitted = st.form_submit_button("Cadastrar", type="primary")

            if submitted:
                try:
                    service.criar_produto(nome, categoria, estoque_minimo, valor_unitario)
                    st.success("Produto cadastrado com sucesso.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    with aba_atualizar:
        st.subheader("Atualizar produto")
        if not produtos:
            st.info("Nenhum produto cadastrado para edição.")
        else:
            produto_sel = st.selectbox(
                "Selecione o produto",
                produtos,
                format_func=lambda p: f"#{p.id_produto} - {p.nome} ({p.categoria})",
                key="select_produto_atualizar",
                index=None,
                placeholder="Digite para buscar um produto..."
            )

            if produto_sel:
                with st.form("form_atualizar_produto"):
                    nome = st.text_input("Nome", value=produto_sel.nome)
                    categoria = st.text_input("Categoria", value=produto_sel.categoria)
                    estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=int(produto_sel.estoque_minimo))
                    valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.01, value=float(produto_sel.valor_unitario), format="%.2f")
                    submitted = st.form_submit_button("Salvar Alterações", type="primary")

                    if submitted:
                        try:
                            produto_sel.nome = nome
                            produto_sel.categoria = categoria
                            produto_sel.estoque_minimo = estoque_minimo
                            produto_sel.valor_unitario = valor_unitario
                            db.commit()
                            st.success("Produto atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar produto: {str(e)}")

    with aba_remover:
        st.subheader("Remover produto")
        if not produtos:
            st.info("Nenhum produto cadastrado para remoção.")
        else:
            produto_rem = st.selectbox(
                "Selecione o produto a remover",
                produtos,
                format_func=lambda p: f"#{p.id_produto} - {p.nome} ({p.categoria})",
                key="select_produto_remover",
                index=None,
                placeholder="Digite para buscar um produto..."
            )

            if produto_rem:
                st.warning(f"Tem certeza que deseja remover o produto **#{produto_rem.id_produto} - {produto_rem.nome}**?")
                if st.button("Confirmar Remoção", type="primary"):
                    try:
                        service.remover_produto(produto_rem.id_produto)
                        st.success("Produto removido com sucesso.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))