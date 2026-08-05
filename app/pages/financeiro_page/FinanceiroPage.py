import streamlit as st
from datetime import date

from app.database import SessionLocal
from app.services.financeiro_service.FinanceiroService import FinanceiroService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()
cabecalho("Financeiro", "Visão geral de receitas, despesas e balanço do resort", "💰")

with SessionLocal() as db:
    financeiro = FinanceiroService(db)
    resumo = financeiro.obter_resumo()
    receitas = financeiro.listar_receitas()
    despesas = financeiro.listar_despesas()

    nomes_hospede = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in receitas}
    nomes_fornecedor = {p.id_pedido: (p.fornecedor.nome if p.fornecedor else p.cnpj_fornecedor) for p in despesas}

# ── KPIs principais ─────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Receitas (reservas)", f"R$ {resumo.total_receitas:,.2f}")
c2.metric("Despesas (compras)", f"R$ {resumo.total_despesas:,.2f}")
c3.metric("Saldo Líquido", f"R$ {resumo.saldo:,.2f}")

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
        cols = st.columns(2)
        for i, r in enumerate(receitas):
            cliente = nomes_hospede.get(r.id_reserva, r.cpf_hospede)
            dt = r.data_reserva.strftime("%d/%m/%Y") if r.data_reserva else "—"
            detalhes = f"""
            <strong>Cliente:</strong> {cliente}<br>
            <strong>Data:</strong> {dt}<br>
            <strong>Valor Total:</strong> R$ {(r.valor_total or 0):,.2f}
            """
            with cols[i % 2]:
                st.markdown(
                    card_item(f"Reserva #{r.id_reserva}", "Receita de Hospedagem", detalhes, status=r.status),
                    unsafe_allow_html=True
                )

with aba_despesas:
    if not despesas:
        st.info("Nenhuma despesa registrada ainda.")
    else:
        cols = st.columns(2)
        for i, p in enumerate(despesas):
            fornec = nomes_fornecedor.get(p.id_pedido, p.cnpj_fornecedor)
            dt = p.data_pedido.strftime("%d/%m/%Y") if p.data_pedido else "—"
            detalhes = f"""
            <strong>Fornecedor:</strong> {fornec}<br>
            <strong>Data do Pedido:</strong> {dt}<br>
            <strong>Valor Total:</strong> R$ {(p.valor_total or 0):,.2f}
            """
            status_fmt = p.status.capitalize() if p.status else "Pendente"
            with cols[i % 2]:
                st.markdown(
                    card_item(f"Pedido #{p.id_pedido}", "Despesa de Insumos", detalhes, status=status_fmt),
                    unsafe_allow_html=True
                )
