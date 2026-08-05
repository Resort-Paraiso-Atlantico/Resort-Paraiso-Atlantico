import streamlit as st
from datetime import date
from app.database import SessionLocal
from app.services.ReservaService import ReservaService
from app.services.ReservaSuiteService import ReservaSuiteService
from app.services.HospedeService import HospedeService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Recepção", "Dê entrada ou saída dos hóspedes", "🔑")


def _suites_vinculadas_texto(db, id_reserva: int) -> str:
    vinculo_service = ReservaSuiteService(db)
    hoje = date.today()
    vinculos = [
        v for v in vinculo_service.listar_por_reserva(id_reserva)
        if v.data_saida is None or v.data_saida >= hoje
    ]
    if not vinculos:
        return "nenhuma suíte vinculada"
    numeros = ", ".join(f"nº {v.suite.numero}" for v in vinculos)
    return f"{len(vinculos)} suíte(s) vinculada(s) ({numeros})"


with SessionLocal() as db:
    todas_reservas = ReservaService(db).listar_reservas()

c1, c2, c3 = st.columns(3)
c1.metric("Aguardando check-in", sum(1 for r in todas_reservas if r.status == "Confirmada"))
c2.metric("Hospedados agora", sum(1 for r in todas_reservas if r.status == "Hospedado"))
c3.metric("Finalizadas", sum(1 for r in todas_reservas if r.status == "Finalizada"))

st.divider()

tab_checkin, tab_checkout, tab_consulta = st.tabs(["🔑 Fazer Check-in", "🚪 Fazer Check-out", "🔍 Consultar por CPF"])

# ── Fazer Check-in ──────────────────────────────────────────────────────────────
with tab_checkin:
    st.subheader("Reservas aguardando check-in")

    with SessionLocal() as db:
        service = ReservaService(db)
        reservas = [r for r in service.listar_reservas() if r.status == "Confirmada"]
        info_extra = {r.id_reserva: _suites_vinculadas_texto(db, r.id_reserva) for r in reservas}
        nomes = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in reservas}

    if not reservas:
        st.info("Nenhuma reserva confirmada aguardando check-in no momento.")
    else:
        for r in reservas:
            detalhes = f"""
            <strong>Hóspede:</strong> {nomes[r.id_reserva]}<br>
            <strong>Check-in previsto:</strong> {r.checkin_previsto}<br>
            <strong>Suítes:</strong> {info_extra[r.id_reserva]}
            """
            st.markdown(
                card_item(f"Reserva #{r.id_reserva}", "Aguardando Entrada", detalhes, status=r.status),
                unsafe_allow_html=True,
            )
            if st.button(f"Confirmar check-in da reserva #{r.id_reserva}", key=f"checkin_{r.id_reserva}", width="stretch"):
                try:
                    with SessionLocal() as db:
                        _, aviso = ReservaService(db).fazer_checkin(r.id_reserva, usuario=st.user.email)
                    if aviso:
                        st.warning(f"Check-in realizado, mas: {aviso}")
                    else:
                        st.success(f"Check-in da reserva #{r.id_reserva} realizado!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Erro: {e}")

# ── Fazer Check-out ───────────────────────────────────────────────────────────
with tab_checkout:
    st.subheader("Hóspedes atualmente no resort")

    with SessionLocal() as db:
        service = ReservaService(db)
        reservas = [r for r in service.listar_reservas() if r.status == "Hospedado"]
        info_extra = {r.id_reserva: _suites_vinculadas_texto(db, r.id_reserva) for r in reservas}
        nomes = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in reservas}

    if not reservas:
        st.info("Nenhum hóspede hospedado no momento.")
    else:
        for r in reservas:
            detalhes = f"""
            <strong>Hóspede:</strong> {nomes[r.id_reserva]}<br>
            <strong>Check-out previsto:</strong> {r.checkout_previsto}<br>
            <strong>Suítes:</strong> {info_extra[r.id_reserva]}<br>
            <strong>Check-in feito:</strong> {r.checkin_realizado} por {r.checkin_por or '—'}
            """
            st.markdown(
                card_item(f"Reserva #{r.id_reserva}", "Hóspede no Resort", detalhes, status=r.status),
                unsafe_allow_html=True,
            )
            if st.button(f"Confirmar check-out da reserva #{r.id_reserva}", key=f"checkout_{r.id_reserva}", width="stretch"):
                try:
                    with SessionLocal() as db:
                        ReservaService(db).fazer_checkout(r.id_reserva, usuario=st.user.email)
                    st.success(f"Check-out da reserva #{r.id_reserva} realizado! Suíte(s) liberada(s).")
                    st.caption("Lembre-se de registrar a limpeza na página **Suítes** quando o quarto estiver pronto.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Erro: {e}")

# ── Consultar por Hóspede (Nome ou CPF) ──────────────────────────────────────────
with tab_consulta:
    st.subheader("Histórico de check-in / check-out por hóspede")

    with SessionLocal() as db:
        hospedes = HospedeService(db).listar_hospedes()

    if not hospedes:
        st.info("Nenhum hóspede cadastrado no sistema.")
    else:
        hospede_sel = st.selectbox(
            "Selecione o hóspede",
            hospedes,
            format_func=lambda h: f"{h.nome} (CPF: {h.cpf[:3]}.***.***-{h.cpf[-2:]})",
            index=None,
            placeholder="Digite o nome ou CPF do hóspede..."
        )

        if hospede_sel:
            cpf_alvo = hospede_sel.cpf
            with SessionLocal() as db:
                service = ReservaService(db)
                reservas = service.buscar_por_cpf(cpf_alvo)
                vinculo_service = ReservaSuiteService(db)

                if not reservas:
                    st.info(f"Nenhuma reserva encontrada para **{hospede_sel.nome}**.")
                else:
                    st.markdown(f"**{len(reservas)} reserva(s) encontrada(s) para {hospede_sel.nome}**")

                reservas_ordenadas = sorted(reservas, key=lambda r: r.data_reserva, reverse=True)

                for r in reservas_ordenadas:
                    vinculos = vinculo_service.listar_por_reserva(r.id_reserva)
                    hoje = date.today()
                    if vinculos:
                        suites_texto = ", ".join(
                            f"nº {v.suite.numero}"
                            + (" (ativa)" if (v.data_saida is None or v.data_saida >= hoje) else f" (saiu {v.data_saida})")
                            for v in vinculos
                        )
                    else:
                        suites_texto = "nenhuma suíte vinculada"

                    checkin_txt = f"{r.checkin_realizado} (por {r.checkin_por})" if r.checkin_realizado else "ainda não realizado"
                    checkout_txt = f"{r.checkout_realizado} (por {r.checkout_por})" if r.checkout_realizado else "ainda não realizado"

                    detalhes = f"""
                    <strong>Previsto:</strong> {r.checkin_previsto} → {r.checkout_previsto}<br>
                    <strong>Check-in real:</strong> {checkin_txt}<br>
                    <strong>Check-out real:</strong> {checkout_txt}<br>
                    <strong>Suíte(s):</strong> {suites_texto}
                    """

                    st.markdown(
                        card_item(f"Reserva #{r.id_reserva}", f"Hóspede: {hospede_sel.nome}", detalhes, status=r.status),
                        unsafe_allow_html=True,
                    )