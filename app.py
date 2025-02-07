import streamlit as st
import pandas as pd

# Função para carregar os dados do arquivo Excel
def load_data(file):
    xls = pd.ExcelFile(file)

    # Ajustar os nomes das abas e colunas conforme necessário
    prazos_data = xls.parse('Prazos', header=None)  # Sem cabeçalho
    audiencias_data = xls.parse('Audiências')
    compliance_data = xls.parse('Compliance')
    iniciais_data = xls.parse('Iniciais')

    # Renomear colunas para padronizar
    prazos_data.columns = [f'Coluna_{i}' for i in range(prazos_data.shape[1])]
    audiencias_data.columns = audiencias_data.columns.str.strip().str.lower()
    compliance_data.columns = compliance_data.columns.str.strip().str.lower()
    iniciais_data.columns = iniciais_data.columns.str.strip().str.lower()

    return prazos_data, audiencias_data, compliance_data, iniciais_data

# Carregando o arquivo Excel
st.title('Dashboard Jurídico')
file = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

if file:
    prazos, audiencias, compliance, iniciais = load_data(file)
    st.success('Dados carregados com sucesso!')

    # Exibir as primeiras linhas de cada aba para validação
    st.header("Prazos")
    st.dataframe(prazos)

    st.header("Audiências")
    st.dataframe(audiencias)

    st.header("Compliance")
    st.dataframe(compliance)

    st.header("Iniciais")
    st.dataframe(iniciais)
