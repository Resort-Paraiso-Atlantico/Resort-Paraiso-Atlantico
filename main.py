import streamlit as st
from app.database import engine
from app.models.Base import Base
from app.theme import aplicar_tema

Base.metadata.create_all(engine)
aplicar_tema()

# ── Login Portal (Banner Encorpado em 1 Tela) ───────────────────────────────────
if not st.user.is_logged_in:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #0D9488 100%);
            padding: 1.4rem 2rem;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 12px 25px -8px rgba(15, 23, 42, 0.25);
            margin-bottom: 0.9rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
        ">
            <div style="font-size: 2.8rem; line-height: 1; margin-bottom: 0.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));">🏝️🌊🌴</div>
            <h1 style="font-family: 'Playfair Display', serif; font-size: 2.1rem; font-weight: 700; margin: 0; color: #FFFFFF; letter-spacing: -0.015em; line-height: 1.15;">
                Resort Paraíso Atlântico
            </h1>
            <p style="color: #D97706; font-size: 0.88rem; font-weight: 600; margin-top: 0.25rem; letter-spacing: 0.05em; text-transform: uppercase;">
                Sua experiência de alto padrão à beira-mar · Portal de Gestão
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_left, c_center, c_right = st.columns([1, 2, 1])

    with c_center:
        st.markdown(
            """
            <div style="
                background: #FFFFFF;
                padding: 1.1rem 1.4rem;
                border-radius: 16px;
                box-shadow: 0 4px 15px -3px rgba(15,23,42,0.06);
                border: 1px solid #E2E8F0;
                text-align: center;
                margin-bottom: 0.6rem;
            ">
                <h4 style="margin: 0 0 0.15rem 0; color: #0F172A; font-weight: 700; font-size: 1.1rem;">Acesso Corporativo</h4>
                <p style="color: #64748B; font-size: 0.8rem; margin: 0 0 0.75rem 0;">Utilize sua conta corporativa do Google para prosseguir</p>
            """,
            unsafe_allow_html=True,
        )
        st.button("🔑 Entrar com Google", on_click=st.login, type="primary", width="stretch")
        st.markdown(
            """
                <div style="margin-top: 0.45rem; font-size: 0.72rem; color: #0D9488; font-weight: 600;">
                    🔒 Conexão Segura & Autenticada
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 12px; border: 1px solid #E2E8F0;">
            <div style="font-size: 1.25rem;">🛏️</div>
            <div style="font-weight: 700; color: #0F172A; margin-top: 0.15rem; font-size: 0.78rem;">Suítes Exclusivas</div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 12px; border: 1px solid #E2E8F0;">
            <div style="font-size: 1.25rem;">🔑</div>
            <div style="font-weight: 700; color: #0F172A; margin-top: 0.15rem; font-size: 0.78rem;">Recepção Ágil</div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 12px; border: 1px solid #E2E8F0;">
            <div style="font-size: 1.25rem;">🎉</div>
            <div style="font-weight: 700; color: #0F172A; margin-top: 0.15rem; font-size: 0.78rem;">Eventos & Lazer</div>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem; background: white; border-radius: 12px; border: 1px solid #E2E8F0;">
            <div style="font-size: 1.25rem;">💰</div>
            <div style="font-weight: 700; color: #0F172A; margin-top: 0.15rem; font-size: 0.78rem;">Finanças & Estoque</div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ── User Logged In Header ───────────────────────────────────────────────────────
c_brand, c_user = st.columns([6, 4])
with c_brand:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 14px; padding: 0.3rem 0;">
            <div style="background: linear-gradient(135deg, #0F172A, #0D9488); border-radius: 12px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 4px 6px -1px rgba(15,23,42,0.15);">🏝️</div>
            <div>
                <span style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #0F172A; letter-spacing: -0.01em; display: block; line-height: 1.1;">Resort Paraíso Atlântico</span>
                <span style="font-size: 0.78rem; color: #0D9488; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">Sistema de Gestão & Operações</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_user:
    u_col1, u_col2, u_col3 = st.columns([2, 5, 3])
    with u_col1:
        if hasattr(st.user, "picture") and st.user.picture:
            st.markdown(
                f'<img src="{st.user.picture}" style="border-radius: 50%; width: 42px; height: 42px; border: 2px solid #0D9488; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-top: 4px;">',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="font-size: 1.4rem; background: #E2E8F0; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border: 2px solid #0D9488; margin-top: 4px;">👤</div>',
                unsafe_allow_html=True
            )
    with u_col2:
        st.markdown(
            f'<div style="font-weight: 700; color: #0F172A; font-size: 0.95rem; line-height: 1.2; margin-top: 6px;">{st.user.name}</div><div style="font-size: 0.75rem; color: #64748B;">Usuário Autenticado</div>',
            unsafe_allow_html=True
        )
    with u_col3:
        st.button("🚪 Sair", on_click=st.logout, type="secondary", width="stretch")

st.divider()

pg = st.navigation([
    st.Page("app/pages/Painel.py", title="Painel", icon="🏠"),
    st.Page("app/pages/financeiro_page/FinanceiroPage.py", title="Financeiro", icon="💰"),
    st.Page("app/pages/Reservas.py", title="Reservas", icon="📋"),
    st.Page("app/pages/Recepcao.py", title="Recepção", icon="🔑"),
    st.Page("app/pages/Suites.py", title="Suítes", icon="🛏️"),
    st.Page("app/pages/Eventos.py", title="Eventos", icon="🎉"),
    st.Page("app/pages/Chamados.py", title="Chamados", icon="📋"),
    st.Page("app/pages/fornecedor_page/FornecedorPage.py", title="Fornecedores", icon="🚚"),
    st.Page("app/pages/produto_page/ProdutoPage.py", title="Produtos", icon="📦"),
    st.Page("app/pages/pedido_page/PedidoCompraPage.py", title="Pedidos de Compra", icon="🛒"),
    st.Page("app/pages/estoque_page/EstoquePage.py", title="Estoque", icon="🏭"),
    st.Page("app/pages/TesteBI.py", title="Business Intelligence (BI)", icon="📊")
])

pg.run()