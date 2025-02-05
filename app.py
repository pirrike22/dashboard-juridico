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
        
        for name, url in URLS.items():
            response = requests.get(url)
            response.raise_for_status()
            
            # Debug: Mostrar os primeiros caracteres da resposta
            st.write(f"Primeiros caracteres da resposta de {name}:")
            st.write(response.text[:200])
            
            # Ler CSV da resposta
            df = pd.read_csv(StringIO(response.text))
            
            # Debug: Mostrar colunas disponíveis
            st.write(f"Colunas disponíveis em {name}:")
            st.write(df.columns.tolist())
            
            # Debug: Mostrar primeiras linhas
            st.write(f"Primeiras linhas de {name}:")
            st.write(df.head())
            
            dfs[name] = df
        
        # Tentar identificar a coluna de data em cada DataFrame
        for name, df in dfs.items():
            st.write(f"Tentando identificar coluna de data em {name}")
            for col in df.columns:
                st.write(f"Coluna: {col}")
                try:
                    # Tentar converter para datetime
                    pd.to_datetime(df[col])
                    st.write(f"✓ Coluna {col} pode ser convertida para data")
                except:
                    st.write(f"✗ Coluna {col} não é uma data")
        
        # Converter colunas de data com base nas colunas identificadas
        if 'data' in dfs['prazos'].columns:
            dfs['prazos']['data'] = pd.to_datetime(dfs['prazos']['data'])
        elif 'Data' in dfs['prazos'].columns:
            dfs['prazos']['Data'] = pd.to_datetime(dfs['prazos']['Data'])
            
        if 'data' in dfs['audiencias'].columns:
            dfs['audiencias']['data'] = pd.to_datetime(dfs['audiencias']['data'])
        elif 'Data' in dfs['audiencias'].columns:
            dfs['audiencias']['Data'] = pd.to_datetime(dfs['audiencias']['Data'])
            
        if 'data_distribuicao' in dfs['iniciais'].columns:
            dfs['iniciais']['data_distribuicao'] = pd.to_datetime(dfs['iniciais']['data_distribuicao'])
        elif 'Data Distribuição' in dfs['iniciais'].columns:
            dfs['iniciais']['Data Distribuição'] = pd.to_datetime(dfs['iniciais']['Data Distribuição'])
        
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.write("Detalhes do erro:", str(e))
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Parar aqui para debug
st.stop()

# Resto do código ...
