import streamlit as st
from app.services.HospedeService import HospedeService
from app.database import SessionLocal  # ajuste esse import conforme o nome real da sua factory de Session
from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Hóspedes", "Cadastre e gerencie os dados dos hóspedes", "👤")

db = SessionLocal()
service = HospedeService(db)

aba_cadastrar, aba_listar, aba_atualizar, aba_remover = st.tabs(
    ["Cadastrar", "Listar", "Atualizar", "Remover"]
)

with aba_cadastrar:
    st.subheader("Cadastrar novo hóspede")
    with st.form("form_cadastro"):
        cpf = st.text_input("CPF")
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        endereco = st.text_input("Endereço")
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            try:
                service.criar_hospede(cpf, nome, telefone, email, endereco)
                st.success("Hóspede cadastrado com sucesso!")
            except ValueError as e:
                st.error(str(e))

with aba_listar:
    st.subheader("Todos os hóspedes")
    hospedes = service.listar_hospedes()
    if hospedes:
        cols = st.columns(2)
        for i, h in enumerate(hospedes):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">
                        <span class="resort-suite-number">{h.nome}</span>
                        <div class="resort-suite-meta">
                            CPF: {h.cpf}<br>
                            📞 {h.telefone or '—'} · ✉️ {h.email or '—'}<br>
                            📍 {h.endereco or '—'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Nenhum hóspede cadastrado.")

with aba_atualizar:
    st.subheader("Atualizar hóspede")
    cpf_busca = st.text_input("CPF do hóspede", key="cpf_atualizar")
    if st.button("Buscar", key="buscar_atualizar"):
        try:
            hospede = service.buscar_por_cpf(cpf_busca)
            if hospede is None:
                st.warning("Hóspede não encontrado.")
            else:
                st.session_state["hospede_editando"] = hospede
        except ValueError as e:
            st.error(str(e))

    if "hospede_editando" in st.session_state:
        h = st.session_state["hospede_editando"]
        with st.form("form_atualizar"):
            nome = st.text_input("Nome", value=h.nome)
            telefone = st.text_input("Telefone", value=h.telefone)
            email = st.text_input("Email", value=h.email)
            endereco = st.text_input("Endereço", value=h.endereco)
            submitted = st.form_submit_button("Salvar alterações")

            if submitted:
                try:
                    service.atualizar_hospede(h.cpf, nome, telefone, email, endereco)
                    st.success("Hóspede atualizado com sucesso!")
                    del st.session_state["hospede_editando"]
                except ValueError as e:
                    st.error(str(e))

with aba_remover:
    st.subheader("Remover hóspede")
    cpf_remover = st.text_input("CPF do hóspede", key="cpf_remover")
    if st.button("Remover"):
        try:
            service.remover_hospede(cpf_remover)
            st.success("Hóspede removido com sucesso!")
        except ValueError as e:
            st.error(str(e))