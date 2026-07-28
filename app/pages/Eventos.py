import streamlit as st
from datetime import date, datetime, time
from app.database import SessionLocal
from app.services.EventoService import EventoService
from app.services.HospedeEventoService import HospedeEventoService
from app.theme import aplicar_tema, cabecalho

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Eventos", "Crie eventos e gerencie inscrições dos hóspedes", "🎉")

tab_criar, tab_listar, tab_editar, tab_inscrever, tab_inscritos, tab_por_hospede = st.tabs([
    "🆕 Criar Evento",
    "📋 Listar Eventos",
    "✏️ Editar / Remover",
    "👤 Inscrever Hóspede",
    "🧾 Inscritos por Evento",
    "🔎 Eventos por Hóspede",
])

# ── Criar Evento ──────────────────────────────────────────────────────────────
with tab_criar:
    st.subheader("Cadastrar evento")

    with st.form("form_evento"):
        nome = st.text_input("Nome do evento")
        descricao = st.text_area("Descrição")

        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de início", value=date.today())
            hora_inicio = st.time_input("Hora de início", value=time(9, 0))
        with col2:
            data_fim = st.date_input("Data de término", value=date.today())
            hora_fim = st.time_input("Hora de término", value=time(18, 0))

        capacidade = st.number_input("Capacidade", min_value=1, step=1)

        submitted = st.form_submit_button("Cadastrar", use_container_width=True)

    if submitted:
        try:
            inicio_evento = datetime.combine(data_inicio, hora_inicio)
            fim_evento = datetime.combine(data_fim, hora_fim)

            with SessionLocal() as db:
                evento = EventoService(db).criar_evento(
                    nome=nome,
                    descricao=descricao,
                    inicio_evento=inicio_evento,
                    fim_evento=fim_evento,
                    capacidade=int(capacidade),
                )
            st.success(f"Evento #{evento.id} cadastrado com sucesso!")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar evento: {e}")

# ── Listar Eventos ────────────────────────────────────────────────────────────
with tab_listar:
    st.subheader("Eventos cadastrados")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Listar todos", use_container_width=True):
            st.session_state["filtro_evento"] = "todos"
    with col2:
        if st.button("Listar não encerrados", use_container_width=True):
            st.session_state["filtro_evento"] = "nao_encerrados"

    filtro = st.session_state.get("filtro_evento", "todos")

    try:
        with SessionLocal() as db:
            service = EventoService(db)
            service.atualizar_status_eventos()
            eventos = (
                service.listar_eventos_nao_encerrados()
                if filtro == "nao_encerrados"
                else service.listar_eventos()
            )

        if not eventos:
            st.info("Nenhum evento encontrado.")
        else:
            for e in eventos:
                with st.expander(f"#{e.id} — {e.nome_evento} ({e.status})"):
                    st.write(e.descricao)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Início", str(e.inicio_evento))
                    col2.metric("Término", str(e.fim_evento))
                    col3.metric("Capacidade", e.capacidade)
    except Exception as e:
        st.error(f"Erro ao listar eventos: {e}")

# ── Editar / Remover ──────────────────────────────────────────────────────────
with tab_editar:
    st.subheader("Editar ou remover evento")

    with SessionLocal() as db:
        eventos = EventoService(db).listar_eventos()

    if not eventos:
        st.info("Nenhum evento cadastrado.")
    else:
        opcoes_evento = {f"#{e.id} — {e.nome_evento}": e.id for e in eventos}
        evento_selecionado = st.selectbox("Selecione o evento", list(opcoes_evento.keys()), key="select_editar")
        id_evento_alvo = opcoes_evento[evento_selecionado]

        with SessionLocal() as db:
            evento_atual = EventoService(db).buscar_por_id(id_evento_alvo)

        with st.form("form_editar_evento"):
            nome_e = st.text_input("Nome do evento", value=evento_atual.nome_evento)
            descricao_e = st.text_area("Descrição", value=evento_atual.descricao)

            col1, col2 = st.columns(2)
            with col1:
                data_inicio_e = st.date_input("Data de início", value=evento_atual.inicio_evento.date())
                hora_inicio_e = st.time_input("Hora de início", value=evento_atual.inicio_evento.time())
            with col2:
                data_fim_e = st.date_input("Data de término", value=evento_atual.fim_evento.date())
                hora_fim_e = st.time_input("Hora de término", value=evento_atual.fim_evento.time())

            capacidade_e = st.number_input("Capacidade", min_value=1, step=1, value=evento_atual.capacidade)

            atualizar_submitted = st.form_submit_button("Salvar alterações", use_container_width=True)

        if atualizar_submitted:
            try:
                with SessionLocal() as db:
                    EventoService(db).atualizar_evento(
                        id=id_evento_alvo,
                        nome=nome_e,
                        descricao=descricao_e,
                        inicio_evento=datetime.combine(data_inicio_e, hora_inicio_e),
                        fim_evento=datetime.combine(data_fim_e, hora_fim_e),
                        capacidade=int(capacidade_e),
                    )
                st.success("Evento atualizado com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao atualizar evento: {e}")

        st.divider()
        if st.button("Remover este evento", use_container_width=True):
            try:
                with SessionLocal() as db:
                    EventoService(db).remover_evento(id_evento_alvo)
                st.success("Evento removido com sucesso!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao remover evento: {e}")

# ── Inscrever Hóspede ─────────────────────────────────────────────────────────
with tab_inscrever:
    st.subheader("Inscrever hóspede em um evento")

    with SessionLocal() as db:
        eventos = EventoService(db).listar_eventos()

    if not eventos:
        st.info("Nenhum evento cadastrado.")
    else:
        opcoes_evento_insc = {f"#{e.id} — {e.nome_evento}": e.id for e in eventos}
        evento_insc = st.selectbox("Selecione o evento", list(opcoes_evento_insc.keys()), key="select_inscrever")
        id_evento_insc = opcoes_evento_insc[evento_insc]

        cpf_hospede_insc = st.text_input("CPF do Hóspede", max_chars=14, placeholder="000.000.000-00")

        if st.button("Inscrever", use_container_width=True):
            try:
                with SessionLocal() as db:
                    HospedeEventoService(db).inscrever_hospede(
                        cpf_hospede=cpf_hospede_insc.strip(),
                        id_evento=id_evento_insc,
                    )
                st.success("Hóspede inscrito com sucesso!")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao inscrever hóspede: {e}")

# ── Inscritos por Evento ──────────────────────────────────────────────────────
with tab_inscritos:
    st.subheader("Ver inscritos de um evento")

    with SessionLocal() as db:
        eventos = EventoService(db).listar_eventos()

    if not eventos:
        st.info("Nenhum evento cadastrado.")
    else:
        opcoes_evento_list = {f"#{e.id} — {e.nome_evento}": e.id for e in eventos}
        evento_list = st.selectbox("Selecione o evento", list(opcoes_evento_list.keys()), key="select_inscritos")
        id_evento_list = opcoes_evento_list[evento_list]

        if st.button("Buscar inscritos", use_container_width=True):
            try:
                with SessionLocal() as db:
                    inscricoes = HospedeEventoService(db).listar_hospedes_por_evento(id_evento_list)

                if not inscricoes:
                    st.info("Nenhum hóspede inscrito neste evento ainda.")
                else:
                    for i in inscricoes:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        col1.write(f"👤 {i.cpf_hospede}")
                        col2.write(f"Inscrito em {i.data_inscricao}")
                        if col3.button("Cancelar", key=f"btn_cancelar_{i.id}"):
                            try:
                                with SessionLocal() as db:
                                    HospedeEventoService(db).cancelar_inscricao(i.id)
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                            except Exception as e:
                                st.error(f"Erro ao cancelar: {e}")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Erro ao buscar inscritos: {e}")

# ── Eventos por Hóspede ───────────────────────────────────────────────────────
with tab_por_hospede:
    st.subheader("Ver em quais eventos um hóspede está inscrito")

    cpf_busca = st.text_input("CPF do Hóspede", max_chars=14, placeholder="000.000.000-00", key="cpf_busca_eventos")

    if st.button("Buscar eventos", use_container_width=True):
        try:
            with SessionLocal() as db:
                inscricoes = HospedeEventoService(db).listar_eventos_por_hospede(cpf_busca.strip())

            if not inscricoes:
                st.info("Esse hóspede não está inscrito em nenhum evento.")
            else:
                for i in inscricoes:
                    with st.expander(f"{i.evento.nome_evento} — inscrito em {i.data_inscricao}"):
                        st.write(i.evento.descricao)
                        col1, col2 = st.columns(2)
                        col1.metric("Início", str(i.evento.inicio_evento))
                        col2.metric("Término", str(i.evento.fim_evento))
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao buscar eventos do hóspede: {e}")
