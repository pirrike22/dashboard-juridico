import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração inicial
st.set_page_config(page_title="Gestão Jurídica", layout="wide")

# URLs das abas publicadas
URL_PRAZOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1719876081&single=true&output=csv"
URL_AUDIENCIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1604483895&single=true&output=csv"
URL_INICIAIS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1311683775&single=true&output=csv"

# Função para carregar dados com verificação
@st.cache_data(ttl=600)
def load_data(url, expected_columns=None):
    try:
        df = pd.read_csv(url)
        
        # Verificar colunas esperadas
        if expected_columns:
            missing = [col for col in expected_columns if col not in df.columns]
            if missing:
                st.error(f"Colunas faltantes: {', '.join(missing)}")
                return None
                
        # Converter colunas de data
        date_columns = [col for col in df.columns if 'data' in col.lower() or 'prazo' in col.lower()]
        
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Carregar dados com verificação de colunas
df_prazos = load_data(URL_PRAZOS, expected_columns=['Prazo', 'Status', 'Responsável', 'Tipo'])
df_audiencias = load_data(URL_AUDIENCIAS, expected_columns=['Data', 'Processo', 'Tribunal', 'Status'])
df_iniciais = load_data(URL_INICIAIS, expected_columns=['Cliente', 'Área', 'Status', 'Prioridade'])

# Verificar se todos os dados foram carregados
if df_prazos is None or df_audiencias is None or df_iniciais is None:
    st.error("Falha crítica no carregamento de dados. Verifique a conexão e os links.")
    st.stop()

# Sidebar - Filtros temporais
st.sidebar.header("Filtros Temporais")
today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

# Função para filtro de datas
def date_filter(df, date_column, days):
    if date_column not in df.columns:
        st.error(f"Coluna {date_column} não encontrada")
        return pd.DataFrame()
    
    return df[
        (df[date_column] >= today) & 
        (df[date_column] <= today + timedelta(days=days))
    ]

# Seleção de período
periodo = st.sidebar.selectbox(
    "Selecione o período para Prazos e Audiências:",
    ["Esta Semana (7 dias)", "Próxima Semana (14 dias)", "Próximos 15 dias"],
    index=0
)

days = 7 if "7" in periodo else 14 if "14" in periodo else 15

# Layout principal
st.title("Dashboard Gestão Jurídica")

# Abas principais
tab1, tab2, tab3 = st.tabs(["🗓️ Prazos Processuais", "👨⚖️ Audiências", "📁 Processos Iniciais"])

with tab1:
    st.header("Controle de Prazos Processuais")
    
    # Aplicar filtro
    filtered_prazos = date_filter(df_prazos, 'Prazo', days)
    
    if not filtered_prazos.empty:
        # Filtros adicionais
        col1, col2, col3 = st.columns(3)
        with col1:
            status_options = filtered_prazos['Status'].unique()
            status = st.multiselect("Status do Prazo", options=status_options, default=status_options)
            
        with col2:
            responsaveis_options = filtered_prazos['Responsável'].unique()
            responsaveis = st.multiselect("Responsáveis", options=responsaveis_options, default=responsaveis_options)
            
        with col3:
            tipos_options = filtered_prazos['Tipo'].unique()
            tipos = st.multiselect("Tipo de Prazo", options=tipos_options, default=tipos_options)
        
        # Aplicar filtros
        filtered_prazos = filtered_prazos[
            filtered_prazos['Status'].isin(status) &
            filtered_prazos['Responsável'].isin(responsaveis) &
            filtered_prazos['Tipo'].isin(tipos)
        ]
        
        # Exibir dados
        st.dataframe(filtered_prazos, height=500, use_container_width=True)
    else:
        st.warning("Nenhum prazo encontrado para o período selecionado")

with tab2:
    st.header("Agenda de Audiências")
    
    # Aplicar filtro
    filtered_audiencias = date_filter(df_audiencias, 'Data', days)
    
    if not filtered_audiencias.empty:
        # Filtros rápidos
        col1, col2 = st.columns(2)
        with col1:
            tribunal_options = filtered_audiencias['Tribunal'].unique()
            tribunal = st.multiselect("Tribunal", options=tribunal_options, default=tribunal_options)
            
        with col2:
            status_options = filtered_audiencias['Status'].unique()
            status_aud = st.multiselect("Status da Audiência", options=status_options, default=status_options)
        
        # Aplicar filtros
        filtered_audiencias = filtered_audiencias[
            filtered_audiencias['Tribunal'].isin(tribunal) &
            filtered_audiencias['Status'].isin(status_aud)
        ]
        
        # Exibir dados
        st.dataframe(filtered_audiencias, height=500, use_container_width=True)
    else:
        st.warning("Nenhuma audiência encontrada para o período selecionado")

with tab3:
    st.header("Processos Iniciais")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        clientes_options = df_iniciais['Cliente'].unique()
        clientes = st.multiselect("Clientes", options=clientes_options, default=clientes_options)
        
    with col2:
        areas_options = df_iniciais['Área'].unique()
        areas = st.multiselect("Área Jurídica", options=areas_options, default=areas_options)
        
    with col3:
        status_options = df_iniciais['Status'].unique()
        status_inic = st.multiselect("Status do Processo", options=status_options, default=status_options)
    
    # Aplicar filtros
    filtered_iniciais = df_iniciais[
        df_iniciais['Cliente'].isin(clientes) &
        df_iniciais['Área'].isin(areas) &
        df_iniciais['Status'].isin(status_inic)
    ]
    
    # Exibir dados
    st.dataframe(filtered_iniciais, height=500, use_container_width=True)
    st.caption(f"Total de processos: {len(filtered_iniciais)}")

# Rodapé
st.markdown("---")
st.caption(f"Dados atualizados em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
