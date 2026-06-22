import streamlit as st
from app.database import engine
from app.models.Base import Base

Base.metadata.create_all(engine)

pg = st.navigation([
    st.Page("app/pages/TesteSuite.py", title="Suítes", icon="🛏️"),
    st.Page("app/pages/TesteReserva.py", title="Reservas", icon="📋"),
])
pg.run()