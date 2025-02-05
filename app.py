import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import io

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Dashboard Jurídica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data(uploaded_file):
    try:
        # Leitura inicial do arquivo
        excel_file = io.BytesIO(uploaded_file.getvalue())
        xls = pd.ExcelFile(excel_file)
        
        # Carregar as abas necessárias
        dfs = {}
        
        # Carregar aba Prazos
        if "Prazos" in xls.sheet_names:
            df_prazos = pd.read_excel(xls, "Prazos", header=0)
            df_prazos.columns = df_prazos.columns.str.strip()
            if 'DATA (D-1)' in df_prazos.columns:
                df_prazos.rename(columns={'DATA (D-1)': 'Data'}, inplace=True)
                df_prazos['Data'] = pd.to_datetime(df_prazos['Data'], errors='coerce')
            dfs['prazos'] = df_prazos
        
        # Carregar aba Audiências
        if "Audiências" in xls.sheet_names:
            df_audiencias = pd.read_excel(xls, "Audiências", header=0)
            df_audiencias.columns = df_audiencias.columns.str.strip()
            if 'DATA' in df_audiencias.columns:
                df_audiencias['Data'] = pd.to_datetime(df_audiencias['DATA'], errors='coerce')
            if 'HORÁRIO' in df_audiencias.columns:
                df_audiencias['Horário'] = pd.to_datetime(df_audiencias['HORÁRIO'], format='mixed', errors='coerce').dt.time
            dfs['audiencias'] = df_audiencias
        
        # Carregar aba Iniciais
        if "Iniciais" in xls.sheet_names:
            df_iniciais = pd.read_excel(xls, "Iniciais", header=0)
            df_iniciais.columns = df_iniciais.columns.str.strip()
            if 'DATA' in df_iniciais.columns:
                df_iniciais['Data'] = pd.to_datetime(df_iniciais['DATA'], errors='coerce')
            dfs['iniciais'] = df_iniciais
        
        return dfs.get('prazos'), dfs.get('audiencias'), dfs.get('iniciais')
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        return None, None, None

def filter_by_period(df):
    periodo = st.sidebar.selectbox(
        "Filtrar por período",
        ["Todos", "Esta semana", "Próxima semana", "Próximos 15 dias"]
    )
    
    if periodo == "Todos":
        return df
    
    hoje = pd.Timestamp.now().normalize()
    
    if periodo == "Esta semana":
        inicio = hoje - timedelta(days=hoje.weekday())
        fim = inicio + timedelta(days=6)
    elif periodo == "Próxima semana":
        inicio = hoje - timedelta(days=hoje.weekday()) + timedelta(days=7)
        fim = inicio + timedelta(days=6)
    else:
        inicio = hoje
        fim = hoje + timedelta(days=15)
    
    return df[df['Data'].between(inicio, fim)]

# Interface principal
st.title("🔍 Dashboard Jurídica")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Faça o upload do arquivo Excel com os dados",
    type=['xlsx', 'xls'],
    help="O arquivo deve conter as abas: Prazos, Audiências e Iniciais"")

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

# Carrega os dados
with st.spinner("Processando o arquivo..."):
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.stop()

# Exibição das tabelas corrigidas
st.subheader("📋 Dados Corrigidos")
st.dataframe(prazos_df, hide_index=True)
st.dataframe(audiencias_df, hide_index=True)
st.dataframe(iniciais_df, hide_index=True)
