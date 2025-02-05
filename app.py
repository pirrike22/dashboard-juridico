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

# Função para carregar os dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    try:
        # Carregar dados de cada URL
        dfs = {}
        
        # Carregar Prazos
        response = requests.get(URLS['prazos'])
        response.raise_for_status()
        df_prazos = pd.read_csv(StringIO(response.text), encoding='utf-8')
        # Renomear a coluna de data
        df_prazos = df_prazos.rename(columns={'Unnamed: 12': 'Data'})
        df_prazos['Data'] = pd.to_datetime(df_prazos['Data'], format='%d/%m/%y', errors='coerce')
        dfs['prazos'] = df_prazos
        
        # Carregar Audiências
        response = requests.get(URLS['audiencias'])
        response.raise_for_status()
        df_audiencias = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_audiencias['DATA'] = pd.to_datetime(df_audiencias['DATA'], format='%d/%m/%y', errors='coerce')
        df_audiencias = df_audiencias.rename(columns={
            'DATA': 'Data',
            'TIPO DE AUDIÃNCIA': 'Tipo',
            'VARA/TURMA': 'Vara',
            'RESPONSÃVEL': 'Responsavel'
        })
        dfs['audiencias'] = df_audiencias
        
        # Carregar Iniciais
        response = requests.get(URLS['iniciais'])
        response.raise_for_status()
        df_iniciais = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_iniciais['DATA'] = pd.to_datetime(df_iniciais['DATA'], format='%d/%m/%y', errors='coerce')
        df_iniciais = df_iniciais.rename(columns={
            'DATA': 'Data',
            'MATÃRIA': 'Tipo de Ação',
            'DISTRIBUÃDO': 'Status'
        })
        dfs['iniciais'] = df_iniciais
        
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Debug - Mostrar informações dos DataFrames
st.write("### Debug - Estrutura dos Dados")

st.write("#### Prazos")
st.write("Colunas:", df_prazos.columns.tolist())
st.write("Amostra:", df_prazos.head())

st.write("#### Audiências")
st.write("Colunas:", df_audiencias.columns.tolist())
st.write("Amostra:", df_audiencias.head())

st.write("#### Iniciais")
st.write("Colunas:", df_iniciais.columns.tolist())
st.write("Amostra:", df_iniciais.head())

# Parar aqui para verificar os dados
st.stop()

[... resto do código ...]
