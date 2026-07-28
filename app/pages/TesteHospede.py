import re
import streamlit as st
from app.services.HospedeService import HospedeService
from app.database import SessionLocal  # ajuste esse import conforme o nome real da sua factory de Session
from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Hóspedes", "Cadastre e gerencie os dados dos hóspedes", "👤")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def _formatar_cpf(cpf: str) -> str:
    cpf = _somente_digitos(cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def _email_valido(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


db = SessionLocal()
service = HospedeService(db)

aba_cadastrar, aba_listar, aba_atualizar, aba_remover = st.tabs(
    ["Cadastrar", "Listar", "Atualizar", "Remover"]
)

with aba_cadastrar:
    st.subheader("Cadastrar novo hóspede")
    with st.form("form_cadastro"):
        cpf = st.text_input("CPF", placeholder="Somente números ou 000.000.000-00", max_chars=14)
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone", placeholder="(00) 00000-0000")
        email = st.text_input("Email")
        endereco = st.text_input("Endereço")
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            cpf_limpo = _somente_digitos(cpf)
            if len(cpf_limpo) != 11:
                st.error("CPF inválido — informe os 11 dígitos.")
            elif not nome.strip():
                st.error("Nome é obrigatório.")
            elif not _email_valido(email):
                st.error("Informe um e-mail válido.")
            else:
                try:
                    service.criar_hospede(
                        cpf_limpo, nome.strip(), telefone.strip(), email.strip(), endereco.strip()
                    )
                    st.success("Hóspede cadastrado com sucesso!")
                except ValueError as e:
                    st.error(str(e))

with aba_listar:
    st.subheader("Todos os hóspedes")
    hospedes = service.listar_hospedes()

    st.metric("Total de hóspedes", len(hospedes))

    busca_nome = st.text_input("Buscar por nome (opcional)", key="busca_nome_listar")
    if busca_nome.strip():
        hospedes = [h for h in hospedes if busca_nome.strip().lower() in h.nome.lower()]

    if hospedes:
        cols = st.columns(2)
        for i, h in enumerate(hospedes):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="resort-suite-card">
                        <span class="resort-suite-number">{h.nome}</span>
                        <div class="resort-suite-meta">
                            CPF: {_formatar_cpf(h.cpf)}<br>
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
    cpf_busca = st.text_input("CPF do hóspede", key="cpf_atualizar", placeholder="Somente números ou 000.000.000-00")
    if st.button("Buscar", key="buscar_atualizar"):
        try:
            hospede = service.buscar_por_cpf(_somente_digitos(cpf_busca))
            if hospede is None:
                st.warning("Hóspede não encontrado.")
                st.session_state.pop("hospede_editando", None)
            else:
                st.session_state["hospede_editando"] = hospede
        except ValueError as e:
            st.error(str(e))

    if "hospede_editando" in st.session_state:
        h = st.session_state["hospede_editando"]
        st.caption(f"Editando: {h.nome} — CPF {_formatar_cpf(h.cpf)}")
        with st.form("form_atualizar"):
            nome = st.text_input("Nome", value=h.nome)
            telefone = st.text_input("Telefone", value=h.telefone)
            email = st.text_input("Email", value=h.email)
            endereco = st.text_input("Endereço", value=h.endereco)
            submitted = st.form_submit_button("Salvar alterações")

            if submitted:
                if not nome.strip():
                    st.error("Nome é obrigatório.")
                elif not _email_valido(email):
                    st.error("Informe um e-mail válido.")
                else:
                    try:
                        service.atualizar_hospede(h.cpf, nome.strip(), telefone.strip(), email.strip(), endereco.strip())
                        st.success("Hóspede atualizado com sucesso!")
                        del st.session_state["hospede_editando"]
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

with aba_remover:
    st.subheader("Remover hóspede")
    st.caption("Só é possível remover hóspedes que não tenham nenhuma reserva cadastrada.")
    cpf_remover = st.text_input("CPF do hóspede", key="cpf_remover", placeholder="Somente números ou 000.000.000-00")
    confirmar = st.checkbox("Confirmo que desejo remover permanentemente este hóspede.")
    if st.button("Remover", disabled=not confirmar):
        try:
            service.remover_hospede(_somente_digitos(cpf_remover))
            st.success("Hóspede removido com sucesso!")
        except ValueError as e:
            st.error(str(e))
