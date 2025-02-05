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
        df_prazos = pd.read_csv(StringIO(response.text), encoding='utf-8')
        # Debug prazos
        st.write("Colunas originais de prazos:", df_prazos.columns.tolist())
        st.write("Primeiras linhas de prazos:", df_prazos.head())
        
        # Encontrar a coluna que contém 'DATA' no nome
        data_col = next((col for col in df_prazos.columns if 'DATA' in str(col).upper()), None)
        if data_col:
            st.write(f"Coluna de data encontrada: {data_col}")
            df_prazos['Data'] = pd.to_datetime(df_prazos[data_col], format='%d/%m/%Y', errors='coerce')
        
        # Carregar Audiências
        response = requests.get(URLS['audiencias'])
        response.raise_for_status()
        df_audiencias = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_audiencias = df_audiencias.rename(columns={
            'DATA': 'Data',
            'HORÃRIO': 'Horario',
            'RAZÃO SOCIAL': 'Cliente',
            'TIPO DE AUDIÃNCIA': 'Tipo',
            'VARA/TURMA': 'Vara',
            'MATÃRIA': 'Materia',
            'RESPONSÃVEL': 'Responsavel',
            'NÂº DO PROCESSO': 'Processo'
        })
        df_audiencias['Data'] = pd.to_datetime(df_audiencias['Data'].str.replace('.', '/') + '/2024', 
                                             format='%d/%m/%Y', errors='coerce')
        
        # Carregar Iniciais
        response = requests.get(URLS['iniciais'])
        response.raise_for_status()
        df_iniciais = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_iniciais = df_iniciais.rename(columns={
            'DATA': 'Data',
            'MATÃRIA': 'Tipo_Acao',
            'DISTRIBUÃDO': 'Status',
            'RESPONSÃVEL': 'Responsavel',
            'NÂº DO PROCESSO': 'Processo'
        })
        df_iniciais['Data'] = pd.to_datetime(df_iniciais['Data'], format='%d/%m/%y', errors='coerce')
        
        # Remover linhas com datas ausentes
        df_prazos = df_prazos.dropna(subset=['Data'])
        df_audiencias = df_audiencias.dropna(subset=['Data'])
        df_iniciais = df_iniciais.dropna(subset=['Data'])
        
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
