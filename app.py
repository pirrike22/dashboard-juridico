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

def debug_csv_content(name, response_text):
    st.write(f"### Conteúdo bruto do CSV - {name}")
    st.text(response_text[:500])  # Mostrar os primeiros 500 caracteres

@st.cache_data(ttl=300)
def load_data():
    try:
        dfs = {}
        
        # Tentar carregar cada planilha
        for name, url in URLS.items():
            st.write(f"Tentando carregar {name}...")
            
            # Fazer o request
            response = requests.get(url)
            response.raise_for_status()
            
            # Debug do conteúdo bruto
            debug_csv_content(name, response.text)
            
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    st.write(f"Tentando encoding {encoding}...")
                    df = pd.read_csv(StringIO(response.text), encoding=encoding)
                    st.write(f"Sucesso com encoding {encoding}")
                    st.write("Colunas encontradas:", df.columns.tolist())
                    st.write("Primeiras linhas:")
                    st.write(df.head())
                    dfs[name] = df
                    break
                except Exception as e:
                    st.write(f"Erro com encoding {encoding}: {str(e)}")
                    continue
            
            if name not in dfs:
                st.error(f"Não foi possível ler os dados de {name} com nenhum encoding")
                dfs[name] = pd.DataFrame()
        
        return dfs.get('prazos', pd.DataFrame()), dfs.get('audiencias', pd.DataFrame()), dfs.get('iniciais', pd.DataFrame())
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.write("Detalhes completos do erro:", str(e))
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Parar aqui para verificar os dados
st.stop()
