import streamlit as st
from datetime import date

from app.database import SessionLocal
from app.services.financeiro_service.FinanceiroService import FinanceiroService
from app.theme import aplicar_tema, cabecalho, badge_status

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Financeiro", "Visão geral de receitas e despesas do resort", "💰")

with SessionLocal() as db:
    financeiro = FinanceiroService(db)
    resumo = financeiro.obter_resumo()
    receitas = financeiro.listar_receitas()
    despesas = financeiro.listar_despesas()

    # Resolve os nomes relacionados (hóspede / fornecedor) ainda com a
    # sessão aberta, para não disparar lazy load depois que ela fechar.
    nomes_hospede = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in receitas}
    nomes_fornecedor = {p.id_pedido: (p.fornecedor.nome if p.fornecedor else p.cnpj_fornecedor) for p in despesas}

# ── KPIs principais ─────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Receitas (reservas)", f"R$ {resumo.total_receitas:,.2f}")
c2.metric("Despesas (compras)", f"R$ {resumo.total_despesas:,.2f}")
c3.metric("Saldo", f"R$ {resumo.saldo:,.2f}")

c4, c5 = st.columns(2)
c4.metric("Receitas pendentes de confirmação", f"R$ {resumo.receitas_pendentes:,.2f}")
c5.metric("Despesas pendentes de recebimento", f"R$ {resumo.despesas_pendentes:,.2f}")

st.caption(
    f"Considerando {resumo.qtd_reservas_receita} reserva(s) com pagamento confirmado "
    f"e {resumo.qtd_pedidos_despesa} pedido(s) de compra não cancelado(s)."
)

st.divider()

# ── Receitas x Despesas por mês ─────────────────────────────────────────────
st.subheader("📈 Receitas x Despesas por mês")
meses = sorted(set(resumo.receitas_por_mes) | set(resumo.despesas_por_mes))
if meses:
    dados_grafico = {
        "Receitas": [resumo.receitas_por_mes.get(m, 0.0) for m in meses],
        "Despesas": [resumo.despesas_por_mes.get(m, 0.0) for m in meses],
    }
    st.bar_chart(dados_grafico, x_label="Mês", y_label="R$")
else:
    st.info("Ainda não há receitas ou despesas registradas para exibir no gráfico.")

st.divider()

# ── Detalhamento ─────────────────────────────────────────────────────────────
aba_receitas, aba_despesas = st.tabs(["📋 Receitas (Reservas)", "🚚 Despesas (Pedidos de Compra)"])

with aba_receitas:
    if not receitas:
        st.info("Nenhuma receita registrada ainda.")
    else:
        for r in receitas:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            col1.write(f"**Reserva #{r.id_reserva}**")
            col2.write(nomes_hospede.get(r.id_reserva, r.cpf_hospede))
            col3.write(r.data_reserva.strftime("%d/%m/%Y") if r.data_reserva else "—")
            col4.markdown(badge_status(r.status), unsafe_allow_html=True)
            st.write(f"💵 R$ {(r.valor_total or 0):,.2f}")
            st.divider()

with aba_despesas:
    if not despesas:
        st.info("Nenhuma despesa registrada ainda.")
    else:
        for p in despesas:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            col1.write(f"**Pedido #{p.id_pedido}**")
            col2.write(nomes_fornecedor.get(p.id_pedido, p.cnpj_fornecedor))
            col3.write(p.data_pedido.strftime("%d/%m/%Y") if p.data_pedido else "—")
            col4.markdown(badge_status(p.status.capitalize()), unsafe_allow_html=True)
            st.write(f"💸 R$ {(p.valor_total or 0):,.2f}")
            st.divider()
