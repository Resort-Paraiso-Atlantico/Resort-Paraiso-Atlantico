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

pg = st.navigation([
    st.Page("app/pages/TesteSuite.py", title="Suítes", icon="🛏️"),
    st.Page("app/pages/TesteReserva.py", title="Reservas", icon="📋"),
    st.Page("app/pages/TesteHospede.py", title="Hóspedes", icon= "👤"),
])
pg.run()