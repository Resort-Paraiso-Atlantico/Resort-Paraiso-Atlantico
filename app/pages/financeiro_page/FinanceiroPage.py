import streamlit as st
import pandas as pd
from datetime import date

from app.database import SessionLocal
from app.services.financeiro_service.FinanceiroService import FinanceiroService
from app.theme import aplicar_tema, cabecalho, badge_status, card_item, PRIMARY_TEAL, ACCENT_CORAL, PRIMARY_DARK

if not st.user.is_logged_in:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

aplicar_tema()

# ── Cabeçalho Principal ───────────────────────────────────────────────────────
cabecalho("Painel Financeiro Executivo", "Demonstrativo de Resultados, Fluxo de Caixa e DRE do Resort", "💰")

with SessionLocal() as db:
    financeiro = FinanceiroService(db)
    resumo = financeiro.obter_resumo()
    receitas = financeiro.listar_receitas()
    despesas = financeiro.listar_despesas()

    nomes_hospede = {r.id_reserva: (r.hospede.nome if r.hospede else r.cpf_hospede) for r in receitas}
    nomes_fornecedor = {p.id_pedido: (p.fornecedor.nome if p.fornecedor else p.cnpj_fornecedor) for p in despesas}

# ── KPIs Executivos Principais ────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="🟢 RECEITA BRUTA",
        value=f"R$ {resumo.total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"{resumo.qtd_reservas_receita} reservas"
    )

with kpi2:
    st.metric(
        label="🔴 DESPESAS OPERACIONAIS",
        value=f"R$ {resumo.total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"{resumo.qtd_pedidos_despesa} compras",
        delta_color="inverse"
    )

with kpi3:
    cor_saldo = "normal" if resumo.saldo >= 0 else "inverse"
    st.metric(
        label="💵 SALDO LÍQUIDO",
        value=f"R$ {resumo.saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta=f"Margem {resumo.margem_lucro:.1f}%",
        delta_color=cor_saldo
    )

with kpi4:
    st.metric(
        label="🎟️ TICKET MÉDIO",
        value=f"R$ {resumo.ticket_medio_reserva:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        delta="por reserva"
    )

# ── KPIs Secundários / Pendências ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
p1, p2 = st.columns(2)

with p1:
    st.info(
        f"⏳ **Receitas Pendentes (A Confirmar):** R$ {resumo.receitas_pendentes:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with p2:
    st.warning(
        f"🚚 **Despesas Pendentes (A Pagar):** R$ {resumo.despesas_pendentes:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

st.divider()

# ── DRE Simplificado & Análise Gráfica ─────────────────────────────────────────
col_dre, col_grafico = st.columns([1, 1.4])

with col_dre:
    st.subheader("📑 DRE Simplificado")
    st.caption("Demonstrativo do Resultado do Exercício")

    dre_html = f"""
    <div style="background-color: #FFFFFF; padding: 1.2rem; border-radius: 14px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding: 8px 0;">
            <span style="font-weight: 600; color: #1E293B;">(+) Receita Bruta de Hospedagem</span>
            <span style="font-weight: 700; color: #047857;">R$ {resumo.total_receitas:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding: 8px 0;">
            <span style="font-weight: 600; color: #1E293B;">(-) Custos com Insumos & Pedidos</span>
            <span style="font-weight: 700; color: #B91C1C;">(R$ {resumo.total_despesas:,.2f})</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #CBD5E1; padding: 10px 0; margin-top: 4px;">
            <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">(=) Resultado Líquido Operacional</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: {'#047857' if resumo.saldo >= 0 else '#B91C1C'};">R$ {resumo.saldo:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 8px 0; margin-top: 4px; font-size: 0.88rem; color: #64748B;">
            <span>Margem Operacional Líquida</span>
            <span style="font-weight: 700; color: #0D9488;">{resumo.margem_lucro:.1f}%</span>
        </div>
    </div>
    """
    st.markdown(dre_html.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

with col_grafico:
    st.subheader("📈 Fluxo Financeiro Mensal")
    meses = sorted(set(resumo.receitas_por_mes) | set(resumo.despesas_por_mes))
    if meses:
        df_chart = pd.DataFrame({
            "Mês": meses,
            "Receitas (R$)": [resumo.receitas_por_mes.get(m, 0.0) for m in meses],
            "Despesas (R$)": [resumo.despesas_por_mes.get(m, 0.0) for m in meses]
        }).set_index("Mês")

        st.bar_chart(df_chart, height=280)
    else:
        st.info("Ainda não há registros financeiros com data para exibição no gráfico.")

st.divider()

# ── Detalhamento de Lançamentos com Filtro e Exportação CSV ────────────────────
st.subheader("📊 Relatórios Detalhados de Lançamentos")

aba_receitas, aba_despesas = st.tabs(["📋 Receitas de Hospedagem", "🚚 Despesas de Suprimentos"])

with aba_receitas:
    if not receitas:
        st.info("Nenhuma receita registrada até o momento.")
    else:
        busca_rec = st.text_input("🔍 Buscar receita por cliente ou CPF:", "", key="busca_rec")
        
        dados_rec = []
        for r in receitas:
            cliente = nomes_hospede.get(r.id_reserva, r.cpf_hospede)
            if busca_rec.lower() in cliente.lower() or busca_rec in r.cpf_hospede:
                dados_rec.append({
                    "Reserva #": r.id_reserva,
                    "Cliente / Hóspede": cliente,
                    "CPF": r.cpf_hospede,
                    "Data": r.data_reserva.strftime("%d/%m/%Y") if r.data_reserva else "—",
                    "Status": r.status,
                    "Valor Total (R$)": f"R$ {(r.valor_total or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })

        if dados_rec:
            df_rec = pd.DataFrame(dados_rec)
            st.dataframe(df_rec, use_container_width=True, hide_index=True)

            # Botão de Exportação CSV
            csv_rec = df_rec.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Receitas em CSV",
                data=csv_rec,
                file_name=f"relatorio_receitas_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhuma receita encontrada para os termos da busca.")

with aba_despesas:
    if not despesas:
        st.info("Nenhuma despesa registrada até o momento.")
    else:
        busca_desp = st.text_input("🔍 Buscar despesa por fornecedor ou CNPJ:", "", key="busca_desp")

        dados_desp = []
        for p in despesas:
            fornec = nomes_fornecedor.get(p.id_pedido, p.cnpj_fornecedor)
            if busca_desp.lower() in fornec.lower() or busca_desp in p.cnpj_fornecedor:
                dados_desp.append({
                    "Pedido #": p.id_pedido,
                    "Fornecedor": fornec,
                    "CNPJ": p.cnpj_fornecedor,
                    "Data do Pedido": p.data_pedido.strftime("%d/%m/%Y") if p.data_pedido else "—",
                    "Status": p.status,
                    "Valor Total (R$)": f"R$ {(p.valor_total or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                })

        if dados_desp:
            df_desp = pd.DataFrame(dados_desp)
            st.dataframe(df_desp, use_container_width=True, hide_index=True)

            # Botão de Exportação CSV
            csv_desp = df_desp.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Despesas em CSV",
                data=csv_desp,
                file_name=f"relatorio_despesas_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhuma despesa encontrada para os termos da busca.")
