import streamlit as st
from app.database import engine
from app.models.Base import Base
from app.pages.TesteSuite import form_criar_suite

Base.metadata.create_all(engine)
st.toast("Tabelas verificadas/criadas com sucesso!")
form_criar_suite()