import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Dashboard Jurídica", layout="wide")

def load_data(uploaded_file):
    try:
        # Criar buffer do arquivo
        excel_file = io.BytesIO(uploaded_file.getvalue())
        
        # Lista de todas as abas
        all_sheets = pd.read_excel(excel_file, sheet_name=None)
        
        # Mostrar estrutura do arquivo
        st.write("### Estrutura do arquivo:")
        for sheet_name, df in all_sheets.items():
            st.write(f"\n**Aba:** {sheet_name}")
            st.write("Colunas:", df.columns.tolist())
            st.write("Primeiras linhas:")
            st.dataframe(df.head(2))
            st.write("---")
        
        # Retornar os dataframes necessários
        prazos_df = None
        audiencias_df = None
        iniciais_df = None
        
        # Buscar as abas corretas
        for sheet_name, df in all_sheets.items():
            sheet_lower = sheet_name.lower()
            if "prazo" in sheet_lower:
                prazos_df = df
            elif "audi" in sheet_lower:
                audiencias_df = df
            elif "inici" in sheet_lower:
                iniciais_df = df
        
        return prazos_df, audiencias_df, iniciais_df
        
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None, None, None

# Interface principal
st.title("🔍 Dashboard Jurídica v0.1 (Debug)")
st.write("Esta é uma versão de debug para identificar a estrutura dos dados.")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=['xlsx'])

if uploaded_file:
    # Carregar dados
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)
    
    # Verificar se os dados foram carregados
    if prazos_df is not None:
        st.write("### Dados de Prazos")
        st.write("Colunas encontradas:", prazos_df.columns.tolist())
        st.dataframe(prazos_df)
    
    if audiencias_df is not None:
        st.write("### Dados de Audiências")
        st.write("Colunas encontradas:", audiencias_df.columns.tolist())
        st.dataframe(audiencias_df)
    
    if iniciais_df is not None:
        st.write("### Dados de Iniciais")
        st.write("Colunas encontradas:", iniciais_df.columns.tolist())
        st.dataframe(iniciais_df)
        
else:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
