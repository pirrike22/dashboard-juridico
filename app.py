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
        # Carregar dados brutos primeiro para análise
        dfs = {}
        for name, url in URLS.items():
            response = requests.get(url)
            response.raise_for_status()
            
            # Tentar diferentes encodings
            for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(StringIO(response.text), encoding=encoding)
                    st.write(f"DataFrame {name} - usando encoding {encoding}")
                    st.write("Colunas originais:", df.columns.tolist())
                    st.write("Número de colunas:", len(df.columns))
                    st.write("Primeiras linhas:")
                    st.write(df.head())
                    dfs[name] = df
                    break
                except Exception as e:
                    st.write(f"Erro com encoding {encoding}: {str(e)}")
                    continue
        
        # Se não conseguiu carregar algum DataFrame, retornar erro
        if len(dfs) != 3:
            raise Exception("Não foi possível carregar todos os DataFrames")
        
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.write("Detalhes completos do erro:", str(e))
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Debug - Mostrar informações dos DataFrames processados
st.write("### Dados Processados - Estrutura Detalhada")

st.write("#### Prazos")
if not df_prazos.empty:
    st.write("Número de colunas:", len(df_prazos.columns))
    st.write("Nomes das colunas:", df_prazos.columns.tolist())
    st.write("Tipos de dados das colunas:")
    st.write(df_prazos.dtypes)
    st.write("Primeiras linhas:")
    st.write(df_prazos.head())

st.write("#### Audiências")
if not df_audiencias.empty:
    st.write("Número de colunas:", len(df_audiencias.columns))
    st.write("Nomes das colunas:", df_audiencias.columns.tolist())
    st.write("Tipos de dados das colunas:")
    st.write(df_audiencias.dtypes)
    st.write("Primeiras linhas:")
    st.write(df_audiencias.head())

st.write("#### Iniciais")
if not df_iniciais.empty:
    st.write("Número de colunas:", len(df_iniciais.columns))
    st.write("Nomes das colunas:", df_iniciais.columns.tolist())
    st.write("Tipos de dados das colunas:")
    st.write(df_iniciais.dtypes)
    st.write("Primeiras linhas:")
    st.write(df_iniciais.head())

# Parar aqui para verificar a estrutura detalhada dos dados
st.stop()
