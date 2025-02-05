import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração inicial
st.set_page_config(page_title="Gestão Jurídica", layout="wide")

# URLs das abas publicadas
URL_PRAZOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1719876081&single=true&output=csv"
URL_AUDIENCIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1604483895&single=true&output=csv"
URL_INICIAIS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1311683775&single=true&output=csv"

# Função para carregar dados
@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url)
    
    # Converter colunas de data (ajuste os nomes conforme necessário)
    date_columns = [col for col in df.columns if 'data' in col.lower() or 'prazo' in col.lower()]
    
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        except Exception as e:
            st.error(f"Erro ao converter coluna {col}: {str(e)}")
    
    return df

# Carregar todos os dados
try:
    df_prazos = load_data(URL_PRAZOS)
    df_audiencias = load_data(URL_AUDIENCIAS)
    df_iniciais = load_data(URL_INICIAIS)
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.stop()

# Sidebar - Filtros temporais
st.sidebar.header("Filtros Temporais")
today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

# Função para filtro de datas
def date_filter(df, date_column, days):
    if date_column in df.columns:
        end_date = today + timedelta(days=days)
        return df[(df[date_column] >= today) & (df[date_column] <= end_date)]
    return df

# ... (o restante do código permanece igual a partir daqui)
