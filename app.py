import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Dashboard Jurídica", layout="wide")

# Função para carregar dados
def load_excel(uploaded_file):
    try:
        # Criar buffer do arquivo
        excel_file = io.BytesIO(uploaded_file.getvalue())
        
        # Ler todas as abas
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        # Mostrar informações sobre as abas encontradas
        st.write("Abas encontradas no arquivo:")
        for sheet_name, df in excel_data.items():
            st.write(f"\nAba: {sheet_name}")
            st.write("Colunas:", df.columns.tolist())
        
        return excel_data
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# Interface de upload
st.title("Dashboard Jurídica")
uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=['xlsx'])

if uploaded_file:
    # Carregar dados
    data = load_excel(uploaded_file)
    
    if data is not None:
        st.write("Arquivo carregado com sucesso!")
        
        # Mostrar dados básicos de cada aba
        for sheet_name, df in data.items():
            st.subheader(f"Dados da aba {sheet_name}")
            st.dataframe(df.head())
else:
    st.info("Por favor, faça upload do arquivo Excel.")
