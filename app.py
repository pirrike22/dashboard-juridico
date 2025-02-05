import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO

st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

# URLs das planilhas publicadas
URLS = {
    'prazos': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1719876081&single=true&output=csv',
    'audiencias': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1604483895&single=true&output=csv',
    'iniciais': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1311683775&single=true&output=csv'
}

@st.cache_data(ttl=300)
def load_data():
    try:
        # Carregar Prazos
        response = requests.get(URLS['prazos'])
        response.raise_for_status()
        
        # Debug - mostrar conteúdo bruto
        st.write("Conteúdo bruto dos prazos:")
        st.text(response.text[:500])
        
        # Ler CSV ignorando linhas vazias
        df_prazos = pd.read_csv(
            StringIO(response.text),
            encoding='utf-8',
            skiprows=lambda x: x == 0,  # Pular primeira linha se estiver vazia
            on_bad_lines='skip'  # Ignorar linhas problemáticas
        )
        
        # Debug - mostrar DataFrame após leitura inicial
        st.write("DataFrame após leitura inicial:")
        st.write(df_prazos.head())
        st.write("Colunas:", df_prazos.columns.tolist())
        
        # Remover colunas completamente vazias
        df_prazos = df_prazos.dropna(axis=1, how='all')
        
        # Debug - mostrar DataFrame após remover colunas vazias
        st.write("DataFrame após remover colunas vazias:")
        st.write(df_prazos.head())
        st.write("Colunas:", df_prazos.columns.tolist())
        
        # Carregar Audiências
        response = requests.get(URLS['audiencias'])
        response.raise_for_status()
        df_audiencias = pd.read_csv(StringIO(response.text), encoding='utf-8')
        
        # Debug - mostrar estrutura de audiências
        st.write("DataFrame de audiências:")
        st.write(df_audiencias.head())
        st.write("Colunas de audiências:", df_audiencias.columns.tolist())
        
        # Carregar Iniciais
        response = requests.get(URLS['iniciais'])
        response.raise_for_status()
        df_iniciais = pd.read_csv(StringIO(response.text), encoding='utf-8')
        
        # Debug - mostrar estrutura de iniciais
        st.write("DataFrame de iniciais:")
        st.write(df_iniciais.head())
        st.write("Colunas de iniciais:", df_iniciais.columns.tolist())
        
        return df_prazos, df_audiencias, df_iniciais
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.write("Detalhes completos do erro:", str(e))
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados e mostrar debug
df_prazos, df_audiencias, df_iniciais = load_data()

# Parar aqui para verificar os dados
st.stop()
