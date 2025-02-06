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

# Função para carregar e processar os dados
def load_data(uploaded_file):
    try:
        excel_file = io.BytesIO(uploaded_file.getvalue())
        xls = pd.ExcelFile(excel_file)
        
        required_sheets = {'prazos': 'Prazos', 'audiencias': 'Audiências', 'iniciais': 'Iniciais'}
        dfs = {}
        
        for key, sheet in required_sheets.items():
            if sheet in xls.sheet_names:
                dfs[key] = pd.read_excel(xls, sheet, header=0)
                dfs[key].columns = dfs[key].columns.str.strip()
                if 'Data' in dfs[key].columns:
                    dfs[key]['Data'] = pd.to_datetime(dfs[key]['Data'], errors='coerce')
                if key == 'audiencias' and 'Horário' in dfs[key].columns:
                    dfs[key]['Horário'] = pd.to_datetime(dfs[key]['Horário'], errors='coerce').dt.time
            else:
                st.error(f"A aba '{sheet}' não foi encontrada no arquivo.")
                return None, None, None
        
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        return None, None, None

# Interface principal
st.title("🔍 Dashboard Jurídica")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Faça o upload do arquivo Excel com os dados",
    type=['xlsx', 'xls']
)

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

# Carrega os dados
with st.spinner("Processando o arquivo..."):
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.stop()

# Seleção da visão
st.sidebar.title("Filtros")
view = st.sidebar.radio(
    "Selecione a visualização",
    ["Dashboard Geral", "Prazos", "Audiências", "Processos Iniciais"]
)

# Dashboard Geral
if view == "Dashboard Geral":
    st.header("📊 Dashboard Geral")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Prazos", len(prazos_df))
    with col2:
        st.metric("Total de Audiências", len(audiencias_df))
    with col3:
        st.metric("Total de Processos", len(iniciais_df))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Tipo' in prazos_df.columns:
            fig = px.pie(prazos_df, names='Tipo', title='Distribuição de Tipos de Prazo')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Status' in iniciais_df.columns:
            fig = px.bar(iniciais_df, x='Status', title='Status dos Processos')
            st.plotly_chart(fig, use_container_width=True)

# Visão de Prazos
elif view == "Prazos":
    st.header("⏰ Gestão de Prazos")
    st.dataframe(prazos_df)

# Visão de Audiências
elif view == "Audiências":
    st.header("👥 Gestão de Audiências")
    st.dataframe(audiencias_df)

# Visão de Processos Iniciais
else:
    st.header("📝 Gestão de Processos Iniciais")
    st.dataframe(iniciais_df)

