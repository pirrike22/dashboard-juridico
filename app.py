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

def converter_data(data_str):
    """Converte string de data para datetime."""
    if pd.isna(data_str):
        return None
    
    try:
        data_str = str(data_str).strip()
        if 'nov' in data_str.lower():
            data_str = data_str.lower().replace('nov.', '11')
            return pd.to_datetime(data_str + '/2024', format='%d/%m/%Y')
        elif '/' in data_str:
            if len(data_str.split('/')[2]) == 2:  # Formato dd/mm/yy
                return pd.to_datetime(data_str, format='%d/%m/%y')
            return pd.to_datetime(data_str, format='%d/%m/%Y')
    except:
        return None
    return None

@st.cache_data(ttl=300)
def load_data():
    try:
        # Mapeamento correto das colunas para cada DataFrame
        colunas_prazos = {
            'DATA (D-1)': 'data',
            'CLIENTE': 'cliente',
            'PROCESSO': 'processo',
            'TAREFA': 'tarefa',
            'RESPONSÃVEL': 'responsavel',
            'DATA DE CIÃNCIA': 'data_ciencia',
            'DATA DA DELEGAÃÃO': 'data_delegacao',
            'PRAZO INTERNO (DEL.+5)': 'prazo_interno',
            'DATA DA ENTREGA': 'data_entrega',
            'COMPLEXIDADE': 'complexidade',
            'PRONTO PARA PROTOCOLO': 'pronto_protocolo',
            'PROTOCOLADO?': 'protocolado'
        }
        
        colunas_audiencias = {
            'DATA': 'data',
            'HORÃRIO': 'horario',
            'RAZÃO SOCIAL': 'cliente',
            'CLIENTE AVISADO? (1 semana antes)': 'cliente_avisado',
            'LEMBRETE ENVIADO? (1 dia antes)': 'lembrete_enviado',
            'TESTEMUNHA': 'testemunha',
            'NA AGENDA': 'na_agenda',
            'RESPONSÃVEL': 'responsavel',
            'NÂº DO PROCESSO': 'processo',
            'VARA/TURMA': 'vara',
            'TIPO DE AUDIÃNCIA': 'tipo',
            'MATÃRIA': 'materia',
            'PARTE ADVERSA': 'parte_adversa',
            'LINK/OBSERVAÃÃES': 'observacoes'
        }
        
        colunas_iniciais = {
            'DATA': 'data',
            'Cliente': 'cliente',
            'CNPJ/CPF': 'documento',
            'MATÃRIA': 'tipo_acao',
            'OBSERVAÃÃO': 'observacoes',
            'RESPONSÃVEL': 'responsavel',
            'DATA DA ENTREGA': 'data_entrega',
            'LIBERADO PARA PROTOCOLO': 'liberado_protocolo',
            'DISTRIBUÃDO': 'status',
            'PROTOCOLADO': 'protocolado',
            'DATA DO PROTOCOLO': 'data_protocolo',
            'NÂº DO PROCESSO': 'processo'
        }
        
        # Carregar e processar Prazos
        response = requests.get(URLS['prazos'])
        response.raise_for_status()
        df_prazos = pd.read_csv(StringIO(response.text), encoding='utf-8', skiprows=lambda x: x == 0)
        df_prazos = df_prazos.dropna(axis=1, how='all')
        df_prazos = df_prazos.rename(columns=colunas_prazos)
        
        # Carregar e processar Audiências
        response = requests.get(URLS['audiencias'])
        response.raise_for_status()
        df_audiencias = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_audiencias = df_audiencias.rename(columns=colunas_audiencias)
        
        # Carregar e processar Iniciais
        response = requests.get(URLS['iniciais'])
        response.raise_for_status()
        df_iniciais = pd.read_csv(StringIO(response.text), encoding='utf-8')
        df_iniciais = df_iniciais.rename(columns=colunas_iniciais)
        
        # Converter datas em todos os DataFrames
        for df in [df_prazos, df_audiencias, df_iniciais]:
            date_columns = [col for col in df.columns if 'data' in col.lower()]
            for col in date_columns:
                df[col] = df[col].apply(converter_data)
        
        # Remover linhas com datas ausentes na coluna principal de data
        df_prazos = df_prazos.dropna(subset=['data'])
        df_audiencias = df_audiencias.dropna(subset=['data'])
        df_iniciais = df_iniciais.dropna(subset=['data'])
        
        return df_prazos, df_audiencias, df_iniciais
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        st.write("Detalhes completos do erro:", str(e))
        st.write("Traceback:", st.exception)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Debug - Mostrar informações dos DataFrames processados
st.write("### Dados Processados")

st.write("#### Prazos")
st.write("Colunas:", sorted(df_prazos.columns.tolist()))
st.write("Primeiras linhas:")
st.write(df_prazos.head())

st.write("#### Audiências")
st.write("Colunas:", sorted(df_audiencias.columns.tolist()))
st.write("Primeiras linhas:")
st.write(df_audiencias.head())

st.write("#### Iniciais")
st.write("Colunas:", sorted(df_iniciais.columns.tolist()))
st.write("Primeiras linhas:")
st.write(df_iniciais.head())

# Parar aqui para verificar os dados processados
st.stop()
