import streamlit as st
import re
from datetime import date, datetime, time
from app.database import SessionLocal
from app.services.EventoService import EventoService
from app.services.HospedeEventoService import HospedeEventoService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item
from app.utils.search_utils import atende_termo_busca

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()


def _somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


aplicar_tema()
cabecalho("Eventos", "Crie eventos e gerencie as inscrições dos hóspedes do resort", "🎉")


@st.dialog("➕ Criar Novo Evento")
def modal_criar_evento():
    with st.form("form_modal_evento"):
        nome = st.text_input("Nome do Evento")
        descricao = st.text_area("Descrição do Evento")

        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de Início", value=date.today())
            hora_inicio = st.time_input("Hora de Início", value=time(9, 0))
        with col2:
            data_fim = st.date_input("Data de Término", value=date.today())
            hora_fim = st.time_input("Hora de Término", value=time(18, 0))

        capacidade = st.number_input("Capacidade de Participantes", min_value=1, value=50, step=1)
        submitted = st.form_submit_button("Cadastrar Evento", type="primary", width="stretch")

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
            st.success(f"Evento #{evento.id} - '{nome}' cadastrado com sucesso!")
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar evento: {e}")


@st.dialog("👤 Inscrever Hóspede no Evento")
def modal_inscrever_hospede(id_evento, nome_evento):
    st.caption(f"Inscrevendo participante no evento **#{id_evento} - {nome_evento}**")
    cpf_hospede_insc = st.text_input("CPF do Hóspede", max_chars=14, placeholder="000.000.000-00")
    if st.button("Confirmar Inscrição", type="primary", width="stretch"):
        try:
            with SessionLocal() as db:
                HospedeEventoService(db).inscrever_hospede(
                    cpf_hospede=_somente_digitos(cpf_hospede_insc),
                    id_evento=id_evento,
                )
            st.success("Hóspede inscrito com sucesso!")
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao inscrever hóspede: {e}")


@st.dialog("🧾 Hóspedes Inscritos no Evento")
def modal_ver_inscritos(id_evento, nome_evento):
    st.caption(f"Inscritos no evento **#{id_evento} - {nome_evento}**")
    try:
        with SessionLocal() as db:
            inscricoes = HospedeEventoService(db).listar_hospedes_por_evento(id_evento)
            evento = EventoService(db).buscar_por_id(id_evento)

        cap_txt = f"{evento.capacidade} pax" if evento else "—"
        st.metric("Total Inscritos / Vagas", f"{len(inscricoes)} / {cap_txt}")

        st.divider()

        if not inscricoes:
            st.info("Nenhum hóspede inscrito neste evento ainda.")
        else:
            for idx, i in enumerate(inscricoes):
                nome_hospede = i.hospede.nome if (hasattr(i, "hospede") and i.hospede) else "Hóspede"
                cpf_fmt = f"{i.cpf_hospede[:3]}.***.***-{i.cpf_hospede[-2:]}" if len(i.cpf_hospede) == 11 else i.cpf_hospede
                dt_str = i.data_inscricao.strftime("%d/%m/%Y %H:%M") if hasattr(i.data_inscricao, "strftime") else str(i.data_inscricao)

                with st.container(border=True):
                    col_info, col_btn = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"👤 **{nome_hospede}** &nbsp;·&nbsp; <small style='color:#64748B;'>CPF: {cpf_fmt}</small>", unsafe_allow_html=True)
                        st.caption(f"📅 Inscrito em: {dt_str}")
                    with col_btn:
                        if st.button("🗑️ Cancelar", key=f"btn_canc_modal_evt_{i.id}_{idx}", width="stretch"):
                            try:
                                with SessionLocal() as db:
                                    HospedeEventoService(db).cancelar_inscricao(i.id)
                                st.success("Inscrição cancelada com sucesso.")
                                st.rerun()
                            except ValueError as err:
                                st.error(str(err))
    except Exception as err:
        st.error(f"Erro ao carregar inscritos: {err}")


@st.dialog("✏️ Editar Evento")
def modal_editar_evento(id_evento):
    with SessionLocal() as db:
        evento_atual = EventoService(db).buscar_por_id(id_evento)

    with st.form("form_modal_editar_evento"):
        st.caption(f"Editando evento **#{evento_atual.id} - {evento_atual.nome_evento}**")
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
        atualizar_submitted = st.form_submit_button("Salvar Alterações", type="primary", width="stretch")

    if atualizar_submitted:
        try:
            with SessionLocal() as db:
                EventoService(db).atualizar_evento(
                    id=id_evento,
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


tab_listar, tab_criar, tab_editar, tab_inscrever, tab_inscritos, tab_por_hospede = st.tabs([
    "📋 Listar Eventos",
    "➕ Criar Evento",
    "✏️ Editar / Remover",
    "👤 Inscrever Hóspede",
    "🧾 Inscritos por Evento",
    "🔎 Eventos por Hóspede",
])

# ── Listar Eventos ────────────────────────────────────────────────────────────
with tab_listar:
    c_busca, c_filtro, c_vis, c_btn = st.columns([3, 2, 2, 2])
    with c_busca:
        termo_busca = st.text_input("🔍 Pesquisar por Nome ou Descrição", key="busca_eventos", placeholder="Digite para buscar...")
    with c_filtro:
        filtro_status = st.selectbox("Status", ["Todos", "Não encerrados"], key="filtro_status_eventos")
    with c_vis:
        modo_vis = st.radio("Modo de Visão", ["🎴 Cards", "📊 Tabela"], horizontal=True, label_visibility="collapsed", key="vis_eventos")
    with c_btn:
        if st.button("➕ Novo Evento", type="primary", width="stretch", key="btn_novo_evento_top"):
            modal_criar_evento()

    try:
        with SessionLocal() as db:
            service = EventoService(db)
            service.atualizar_status_eventos()
            eventos = (
                service.listar_eventos_nao_encerrados()
                if filtro_status == "Não encerrados"
                else service.listar_eventos()
            )

        eventos_filtrados = [
            e for e in eventos
            if atende_termo_busca(termo_busca, e.id, e.nome_evento, e.descricao)
        ]

        st.divider()

        if not eventos_filtrados:
            st.info("Nenhum evento encontrado.")
        else:
            if modo_vis == "📊 Tabela":
                dados_tabela = [
                    {
                        "Código": f"#{e.id}",
                        "Nome do Evento": e.nome_evento,
                        "Início": e.inicio_evento.strftime("%d/%m/%Y %H:%M"),
                        "Término": e.fim_evento.strftime("%d/%m/%Y %H:%M"),
                        "Capacidade": f"{e.capacidade} pax",
                        "Status": e.status
                    }
                    for e in eventos_filtrados
                ]
                st.dataframe(
                    dados_tabela,
                    width="stretch",
                    column_config={
                        "Código": st.column_config.TextColumn("Código", width="small"),
                        "Nome do Evento": st.column_config.TextColumn("Evento", width="large"),
                        "Início": st.column_config.TextColumn("Início", width="medium"),
                        "Término": st.column_config.TextColumn("Término", width="medium"),
                    }
                )
            else:
                cols = st.columns(2)
                for i, e in enumerate(eventos_filtrados):
                    inicio_txt = e.inicio_evento.strftime("%d/%m/%Y %H:%M")
                    fim_txt = e.fim_evento.strftime("%d/%m/%Y %H:%M")
                    detalhes = f"""
                    <strong>Descrição:</strong> {e.descricao or 'Sem descrição'}<br>
                    <strong>Período:</strong> {inicio_txt} → {fim_txt}<br>
                    <strong>Capacidade:</strong> {e.capacidade} pax
                    """
                    with cols[i % 2]:
                        st.markdown(
                            card_item(f"#{e.id} - {e.nome_evento}", "Evento do Resort", detalhes, status=e.status),
                            unsafe_allow_html=True,
                        )
                        c_r1_a, c_r1_b = st.columns(2)
                        with c_r1_a:
                            if st.button("🧾 Inscritos", key=f"btn_ver_insc_{e.id}", width="stretch"):
                                modal_ver_inscritos(e.id, e.nome_evento)
                        with c_r1_b:
                            if st.button("👤 Inscrever", key=f"btn_insc_evt_{e.id}", width="stretch"):
                                modal_inscrever_hospede(e.id, e.nome_evento)

                        c_r2_a, c_r2_b = st.columns(2)
                        with c_r2_a:
                            if st.button("✏️ Editar", key=f"btn_edit_evt_{e.id}", width="stretch"):
                                modal_editar_evento(e.id)
                        with c_r2_b:
                            if st.button("🗑️ Excluir", key=f"btn_del_evt_{e.id}", width="stretch"):
                                try:
                                    with SessionLocal() as db:
                                        EventoService(db).remover_evento(e.id)
                                    st.success(f"Evento #{e.id} removido.")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(str(err))
    except Exception as err:
        st.error(f"Erro ao carregar eventos: {err}")

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

        submitted = st.form_submit_button("Cadastrar", width="stretch")

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
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao cadastrar evento: {e}")

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

            atualizar_submitted = st.form_submit_button("Salvar alterações", width="stretch")

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
        if st.button("Remover este evento", width="stretch"):
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

        if st.button("Inscrever", width="stretch"):
            try:
                with SessionLocal() as db:
                    HospedeEventoService(db).inscrever_hospede(
                        cpf_hospede=_somente_digitos(cpf_hospede_insc),
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

        if st.button("Buscar inscritos", width="stretch"):
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

    if st.button("Buscar eventos", width="stretch"):
        try:
            with SessionLocal() as db:
                inscricoes = HospedeEventoService(db).listar_eventos_por_hospede(cpf_busca.strip())

            if not inscricoes:
                st.info("Esse hóspede não está inscrito em nenhum evento.")
            else:
                for i in inscricoes:
                    evento = i.evento

                    with st.container(border=True):

                        st.subheader(f"🎉 {evento.nome_evento}")

                        st.write(evento.descricao)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("🟢 Início")
                            st.write(evento.inicio_evento)

                        with col2:
                            st.write("🔴 Término")
                            st.write(evento.fim_evento)

                        st.write(f"📌 Inscrição: {i.data_inscricao}")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro ao buscar eventos do hóspede: {e}")
