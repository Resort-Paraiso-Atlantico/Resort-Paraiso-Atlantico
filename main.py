import streamlit as st
from app.database import engine
from app.models.Base import Base

Base.metadata.create_all(engine)

if not st.user.is_logged_in:
    st.title("Resort Paraíso Atlântico")
    st.subheader("Faça login para continuar")
    st.button("Entrar com Google", on_click=st.login)
    st.stop()

col1, col2, col3 = st.columns([6, 2, 1])
with col2:
    st.write(f"👤 {st.user.name}")
with col3:
    st.image(st.user.picture, width=40)
    st.button("Sair", on_click=st.logout)
# se quiser usar as paginas antigas comenta esse pg e tira o comentario do outro.
pg = st.navigation([
    st.Page("app/pages/Painel.py", title="Painel", icon="🏠"),
    st.Page("app/pages/financeiro_page/FinanceiroPage.py", title="Financeiro", icon="💰"),
    st.Page("app/pages/Reservas.py", title="Reservas", icon="📋"),
    st.Page("app/pages/Recepcao.py", title="Recepção", icon="🔑"),
    st.Page("app/pages/Suites.py", title="Suítes", icon="🛏️"),
    st.Page("app/pages/Eventos.py", title="Eventos", icon="🎉"),
    st.Page("app/pages/fornecedor_page/FornecedorPage.py", title = "Fornecedores", icon = "🚚"),
    st.Page("app/pages/produto_page/ProdutoPage.py", title = "Produtos", icon = "📦"),
    st.Page("app/pages/pedido_page/PedidoCompraPage.py", title = "Pedidos de Compra", icon = "🛒"),
    st.Page("app/pages/estoque_page/EstoquePage.py", title = "Estoque", icon = "🏭")
])

# "front" antigo
#pg = st.navigation([st.Page("app/pages/TesteSuite.py", title="Suítes", icon="🛏️"),st.Page("app/pages/TesteReserva.py", title="Reservas", icon="📋"),st.Page("app/pages/TesteHospede.py", title="Hóspedes", icon= "👤"),st.Page("app/pages/TesteReservaSuite.py", title="Reserva ↔ Suíte", icon="🔗"),st.Page("app/pages/CheckIn.py", title="Check-in / Check-out", icon="🔑"),st.Page("app/pages/TesteEvento.py", title="Eventos", icon="🎉"),])
pg.run()