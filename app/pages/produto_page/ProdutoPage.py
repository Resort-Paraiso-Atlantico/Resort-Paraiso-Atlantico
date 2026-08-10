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


def obter_categorias_disponiveis(produtos):
    padrao = ["Alimentos", "Bebidas", "Limpeza", "Utensílios", "Outros"]
    existentes = [p.categoria for p in produtos if p.categoria]
    return sorted(list(set(padrao + existentes)))


@st.dialog("➕ Cadastrar Novo Produto")
def modal_cadastrar_produto(produtos_existentes):
    nome = st.text_input("Nome do Produto", key="cad_nome")
    
    opcoes_cat = obter_categorias_disponiveis(produtos_existentes) + ["➕ Outra (Nova Categoria...)"]
    cat_selecionada = st.selectbox("Categoria", opcoes_cat, key="cad_cat_sel")
    if cat_selecionada == "➕ Outra (Nova Categoria...)":
        categoria = st.text_input("Digite o Nome da Nova Categoria", placeholder="Ex: Higiene, Papelaria...", key="cad_cat_custom")
    else:
        categoria = cat_selecionada

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        valor_unitario = st.number_input("Valor Unitário / Custo (R$)", min_value=0.01, value=10.00, format="%.2f", key="cad_val_unit")
        estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=5, key="cad_est_min")
        ponto_reposicao = st.number_input("Ponto de Reposição", min_value=0, value=10, key="cad_ponto_rep")
    with col_c2:
        preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.01, value=15.00, format="%.2f", key="cad_preco_venda")
        estoque_maximo = st.number_input("Estoque Máximo", min_value=1, value=50, key="cad_est_max")
        lead_time = st.number_input("Lead Time (dias)", min_value=0, value=3, key="cad_lead_time")

    if st.button("Cadastrar Produto", type="primary", width="stretch", key="btn_cad_submit"):
        if not nome or not nome.strip():
            st.error("Por favor, informe o nome do produto.")
        elif not categoria or not categoria.strip():
            st.error("Por favor, informe a categoria do produto.")
        else:
            try:
                with SessionLocal() as db:
                    service = ProdutoService(db)
                    service.criar_produto(
                        nome=nome.strip(),
                        categoria=categoria.strip().title(),
                        estoque_minimo=estoque_minimo,
                        valor_unitario=valor_unitario,
                        preco_venda=preco_venda,
                        estoque_maximo=estoque_maximo,
                        ponto_reposicao=ponto_reposicao,
                        lead_time=lead_time
                    )
                st.success("Produto cadastrado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao cadastrar produto: {str(e)}")


@st.dialog("✏️ Editar Produto")
def modal_editar_produto(produto, produtos_existentes):
    st.caption(f"Editando produto **#{produto.id_produto} - {produto.nome}**")
    nome = st.text_input("Nome", value=produto.nome, key=f"edit_nome_{produto.id_produto}")
    
    opcoes_cat = obter_categorias_disponiveis(produtos_existentes) + ["➕ Outra (Nova Categoria...)"]
    idx_cat = opcoes_cat.index(produto.categoria) if produto.categoria in opcoes_cat[:-1] else len(opcoes_cat) - 1
    cat_selecionada = st.selectbox("Categoria", opcoes_cat, index=idx_cat, key=f"edit_cat_sel_{produto.id_produto}")
    
    if cat_selecionada == "➕ Outra (Nova Categoria...)":
        default_custom = produto.categoria if produto.categoria not in opcoes_cat[:-1] else ""
        categoria = st.text_input("Digite o Nome da Nova Categoria", value=default_custom, key=f"edit_cat_custom_{produto.id_produto}")
    else:
        categoria = cat_selecionada

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        valor_unitario = st.number_input("Valor Unitário / Custo (R$)", min_value=0.01, value=float(produto.valor_unitario), format="%.2f", key=f"edit_val_unit_{produto.id_produto}")
        estoque_minimo = st.number_input("Estoque Mínimo", min_value=1, value=int(produto.estoque_minimo), key=f"edit_est_min_{produto.id_produto}")
        ponto_reposicao = st.number_input("Ponto de Reposição", min_value=0, value=int(getattr(produto, 'ponto_reposicao', 0)), key=f"edit_ponto_rep_{produto.id_produto}")
    with col_e2:
        preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.01, value=float(getattr(produto, 'preco_venda', 0.0) or 0.01), format="%.2f", key=f"edit_preco_venda_{produto.id_produto}")
        estoque_maximo = st.number_input("Estoque Máximo", min_value=1, value=max(1, int(getattr(produto, 'estoque_maximo', 0))), key=f"edit_est_max_{produto.id_produto}")
        lead_time = st.number_input("Lead Time (dias)", min_value=0, value=int(getattr(produto, 'lead_time', 0)), key=f"edit_lead_time_{produto.id_produto}")

    if st.button("Salvar Alterações", type="primary", width="stretch", key=f"btn_edit_submit_{produto.id_produto}"):
        if not nome or not nome.strip():
            st.error("Por favor, informe o nome do produto.")
        elif not categoria or not categoria.strip():
            st.error("Por favor, informe a categoria do produto.")
        else:
            try:
                with SessionLocal() as db:
                    service = ProdutoService(db)
                    service.atualizar_produto(
                        id_produto=produto.id_produto,
                        nome=nome.strip(),
                        quantidade=produto.quantidade,
                        estoque_minimo=estoque_minimo,
                        valor_unitario=valor_unitario,
                        categoria=categoria.strip().title(),
                        preco_venda=preco_venda,
                        estoque_maximo=estoque_maximo,
                        ponto_reposicao=ponto_reposicao,
                        lead_time=lead_time
                    )
                st.success("Produto atualizado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
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
        categorias = ["Todas"] + obter_categorias_disponiveis(produtos)
        categoria_filtro = st.selectbox("Categoria", categorias, key="filtro_cat_prod")
    with col_vis:
        modo_vis = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_produtos")
    with col_btn:
        if st.button("➕ Novo Produto", type="primary", width="stretch", key="btn_novo_prod_top"):
            modal_cadastrar_produto(produtos)

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
                    "Ponto Reposição": getattr(p, 'ponto_reposicao', 0),
                    "Estoque Máximo": getattr(p, 'estoque_maximo', 0),
                    "Lead Time": f"{getattr(p, 'lead_time', 0)} dias",
                    "Custo Unitário": float(p.valor_unitario),
                    "Preço de Venda": float(getattr(p, 'preco_venda', 0.0)),
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
                    "Custo Unitário": st.column_config.NumberColumn("Custo Unitário", format="R$ %.2f"),
                    "Preço de Venda": st.column_config.NumberColumn("Preço de Venda", format="R$ %.2f"),
                    "Valor Total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
                    "Estoque Atual": st.column_config.NumberColumn("Qtd Atual"),
                    "Estoque Mínimo": st.column_config.NumberColumn("Mínimo"),
                    "Ponto Reposição": st.column_config.NumberColumn("Ponto Reposição"),
                    "Estoque Máximo": st.column_config.NumberColumn("Máximo"),
                    "Lead Time": st.column_config.TextColumn("Lead Time"),
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
                    modal_editar_produto(prod_sel_tab, produtos)
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
                <strong>Custo Unitário:</strong> R$ {produto.valor_unitario:,.2f} | <strong>Preço Venda:</strong> R$ {getattr(produto, 'preco_venda', 0.0):,.2f}<br>
                <strong>Estoque:</strong> {produto.quantidade} un. (Mín: {produto.estoque_minimo} | Ponto Reposição: {getattr(produto, 'ponto_reposicao', 0)} | Máx: {getattr(produto, 'estoque_maximo', 0)})<br>
                <strong>Lead Time:</strong> {getattr(produto, 'lead_time', 0)} dias<br>
                <strong>Valor Total em Custo:</strong> R$ {(produto.quantidade * produto.valor_unitario):,.2f}
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
                            modal_editar_produto(produto, produtos)
                    with c_del:
                        if st.button(f"🗑️ Excluir", key=f"btn_del_prod_{produto.id_produto}", width="stretch"):
                            try:
                                service.remover_produto(produto.id_produto)
                                st.success(f"Produto #{produto.id_produto} removido.")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))