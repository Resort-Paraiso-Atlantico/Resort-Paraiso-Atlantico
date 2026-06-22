import streamlit as st
import pandas as pd  # Se não tiver instalado, rode 'pip install pandas' no terminal
from app.services.SuiteService import criar_suite
from app.database import SessionLocal  # Importe a sua sessão do banco de dados
from app.models.Suite import Suite     # Importe o modelo da Suite

def listar_suites_do_banco():
    """Busca todas as suítes direto no banco de dados para checar se foram salvas"""
    db = SessionLocal()
    try:
        # Busca todas as suítes cadastradas
        suites = db.query(Suite).all()
        
        # Converte os dados em uma lista de dicionários para o Streamlit exibir bonito
        dados = []
        for s in suites:
            dados.append({
                "ID": s.id_suite,
                "Número": s.numero,
                "Tipo": s.tipo,
                "Capacidade": s.capacidade,
                "Diária (R$)": s.valor_diaria,
                "Status": s.status
            })
        return dados
    finally:
        db.close()

def form_criar_suite():
    st.subheader("Cadastrar Suite")

    numero = st.number_input("Número", min_value=1, step=1)
    tipo = st.selectbox("Tipo", ["Standard", "Luxo", "Master"])
    capacidade = st.number_input("Capacidade", min_value=1, step=1)
    valor_diaria = st.number_input("Valor da Diária (R$)", min_value=0.0, format="%.2f")
    status = st.selectbox("Status", ["Disponível", "Ocupada", "Manutenção"])

    if st.button("Cadastrar"):
        try:
            suite = criar_suite(
                numero=int(numero),
                tipo=tipo,
                capacidade=int(capacidade),
                valor_diaria=valor_diaria,
                status=status,
            )
            st.success(f"Suite #{suite.numero} cadastrada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao cadastrar suite: {e}")
            
    # --- O TESTE EM TEMPO REAL APARECE AQUI ---
    st.markdown("---")
    st.subheader("Suítes Atualmente no Banco de Dados")
    
    lista_suites = listar_suites_do_banco()
    
    if lista_suites:
        # Mostra uma tabela interativa com tudo o que está salvo no PostgreSQL
        st.dataframe(pd.DataFrame(lista_suites), use_container_width=True)
    else:
        st.info("Nenhuma suíte encontrada no banco de dados.")

if __name__ == "__main__":
    form_criar_suite()