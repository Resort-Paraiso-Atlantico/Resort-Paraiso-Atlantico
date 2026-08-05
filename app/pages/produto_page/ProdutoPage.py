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


@st.dialog("➕ Cadastrar Novo Produto")
def modal_cadastrar_produto(service):
    with st.form("form_modal_cadastro_produto"):
        nome = st.text_input("Nome do Produto")
        categoria = st.selectbox("Categoria", ["Alimentos", "Bebidas", "Limpeza", "Utensílios", "Outros"])
        estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=5)
        valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.01, value=10.00, format="%.2f")
        submitted = st.form_submit_button("Cadastrar Produto", type="primary", width="stretch")

        if submitted:
            try:
                service.criar_produto(nome, categoria, estoque_minimo, valor_unitario)
                st.success("Produto cadastrado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


@st.dialog("✏️ Editar Produto")
def modal_editar_produto(db, produto):
    with st.form("form_modal_atualizar_produto"):
        st.caption(f"Editando produto **#{produto.id_produto} - {produto.nome}**")
        nome = st.text_input("Nome", value=produto.nome)
        categoria = st.text_input("Categoria", value=produto.categoria)
        estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=int(produto.estoque_minimo))
        valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.01, value=float(produto.valor_unitario), format="%.2f")
        submitted = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")

        if submitted:
            try:
                produto.nome = nome
                produto.categoria = categoria
                produto.estoque_minimo = estoque_minimo
                produto.valor_unitario = valor_unitario
                db.commit()
                st.success("Produto atualizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar produto: {str(e)}")


with SessionLocal() as db:
    service = ProdutoService(db)
    produtos = service.listar_todos()

    col_busca, col_cat, col_vis, col_btn = st.columns([3, 2, 2, 2])
    with col_busca:
        pesquisa = st.text_input(
            "🔍 Pesquisar produto",
            placeholder="Nome, categoria ou código...",
            key="busca_produtos"
        )
    with col_cat:
        categorias = ["Todas"] + sorted(list(set(p.categoria for p in produtos)))
        categoria_filtro = st.selectbox("Categoria", categorias, key="filtro_cat_prod")
    with col_vis:
        modo_vis = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_produtos")
    with col_btn:
        if st.button("➕ Novo Produto", type="primary", width="stretch", key="btn_novo_prod_top"):
            modal_cadastrar_produto(service)

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
        if modo_vis == "📊 Tabela":
            dados_tabela = [
                {
                    "Código": f"#{p.id_produto}",
                    "Nome": p.nome,
                    "Categoria": p.categoria,
                    "Estoque Atual": p.quantidade,
                    "Estoque Mínimo": p.estoque_minimo,
                    "Preço Unitário": float(p.valor_unitario),
                    "Valor Total": float(p.quantidade * p.valor_unitario),
                    "Status": "🔴 Sem estoque" if p.quantidade == 0 else ("🟡 Estoque baixo" if p.quantidade <= p.estoque_minimo else "🟢 Normal")
                }
                for p in produtos_filtrados
            ]
            st.dataframe(
                dados_tabela,
                width="stretch",
                column_config={
                    "Código": st.column_config.TextColumn("Código", width="small"),
                    "Nome": st.column_config.TextColumn("Produto", width="medium"),
                    "Preço Unitário": st.column_config.NumberColumn("Preço Unitário", format="R$ %.2f"),
                    "Valor Total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
                    "Estoque Atual": st.column_config.NumberColumn("Qtd Atual"),
                    "Estoque Mínimo": st.column_config.NumberColumn("Mínimo"),
                }
            )

            st.caption("⚙️ **Ações Rápidas da Tabela:**")
            c_act1, c_act2, c_act3 = st.columns([4, 2, 2])
            with c_act1:
                prod_sel_tab = st.selectbox(
                    "Selecione um produto da tabela para alterar",
                    produtos_filtrados,
                    format_func=lambda p: f"#{p.id_produto} - {p.nome} ({p.categoria})",
                    key="sel_tab_prod",
                    index=None,
                    placeholder="Selecione um produto..."
                )
            with c_act2:
                if st.button("✏️ Editar Produto", key="btn_edit_tab_prod", width="stretch", disabled=not prod_sel_tab):
                    modal_editar_produto(db, prod_sel_tab)
            with c_act3:
                if st.button("🗑️ Excluir Produto", key="btn_del_tab_prod", width="stretch", disabled=not prod_sel_tab):
                    try:
                        service.remover_produto(prod_sel_tab.id_produto)
                        st.success(f"Produto #{prod_sel_tab.id_produto} removido.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
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
                <strong>Valor Total em Estoque:</strong> R$ {(produto.quantidade * produto.valor_unitario):,.2f}
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
                    c_edit, c_del = st.columns(2)
                    with c_edit:
                        if st.button(f"✏️ Editar", key=f"btn_edit_prod_{produto.id_produto}", width="stretch"):
                            modal_editar_produto(db, produto)
                    with c_del:
                        if st.button(f"🗑️ Excluir", key=f"btn_del_prod_{produto.id_produto}", width="stretch"):
                            try:
                                service.remover_produto(produto.id_produto)
                                st.success(f"Produto #{produto.id_produto} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))