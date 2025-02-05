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

# Função para identificar a coluna de data em um DataFrame
def find_date_column(df):
    """
    Identifica a coluna que contém datas no DataFrame.
    Retorna o nome da coluna e o DataFrame com a coluna convertida.
    """
    possible_date_columns = ['Data', 'DATA', 'Data do Prazo', 'DATA DO PRAZO', 
                           'Data da Audiência', 'DATA DA AUDIÊNCIA',
                           'Data Distribuição', 'DATA DISTRIBUIÇÃO', 
                           'Data de Distribuição', 'data']
    
    # Primeiro, procura por colunas com nomes conhecidos
    for col in possible_date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')
                return col, df
            except:
                continue
    
    # Se não encontrar, tenta identificar qualquer coluna que possa ser convertida para data
    for col in df.columns:
        try:
            test_conversion = pd.to_datetime(df[col], format='mixed', errors='coerce')
            if not test_conversion.isna().all():  # Se conseguiu converter pelo menos alguns valores
                df[col] = test_conversion
                return col, df
        except:
            continue
    
    return None, df

def load_data(uploaded_file):
    """
    Carrega e processa os dados do arquivo Excel.
    """
    try:
        # Leitura inicial do arquivo
        excel_file = io.BytesIO(uploaded_file.getvalue())
        
        # Tenta ler todas as abas do arquivo
        with pd.ExcelFile(excel_file) as xls:
            sheet_names = xls.sheet_names
            
            # Dicionário para armazenar os DataFrames
            dfs = {}
            
            # Tenta carregar cada aba
            for sheet in sheet_names:
                try:
                    df = pd.read_excel(xls, sheet)
                    date_col, df = find_date_column(df)
                    
                    if date_col:
                        # Padroniza o nome da coluna de data
                        df = df.rename(columns={date_col: 'Data'})
                        dfs[sheet.lower()] = df
                    else:
                        st.warning(f"Não foi possível identificar a coluna de data na aba {sheet}")
                except Exception as e:
                    st.error(f"Erro ao processar a aba {sheet}: {str(e)}")
            
            # Verifica se encontrou as abas necessárias
            required_sheets = ['prazos', 'audiências', 'audiencias', 'iniciais']
            found_sheets = [sheet.lower() for sheet in dfs.keys()]
            
            prazos_df = None
            audiencias_df = None
            iniciais_df = None
            
            # Atribui os DataFrames encontrados
            if 'prazos' in found_sheets:
                prazos_df = dfs['prazos']
            
            if 'audiências' in found_sheets or 'audiencias' in found_sheets:
                audiencias_df = next((dfs[k] for k in found_sheets if k in ['audiências', 'audiencias']), None)
            
            if 'iniciais' in found_sheets:
                iniciais_df = dfs['iniciais']
            
            # Verifica se todos os DataFrames necessários foram encontrados
            if not all([prazos_df is not None, audiencias_df is not None, iniciais_df is not None]):
                missing_sheets = []
                if prazos_df is None: missing_sheets.append('Prazos')
                if audiencias_df is None: missing_sheets.append('Audiências')
                if iniciais_df is None: missing_sheets.append('Iniciais')
                st.error(f"Abas não encontradas: {', '.join(missing_sheets)}")
                return None, None, None
            
            return prazos_df, audiencias_df, iniciais_df
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        return None, None, None

# Função para filtrar dados por período
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
    else:  # Próximos 15 dias
        inicio = hoje
        fim = hoje + timedelta(days=15)
    
    return df[df['Data'].between(inicio, fim)]

# Interface principal
st.title("🔍 Dashboard Jurídica")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Faça o upload do arquivo Excel com os dados",
    type=['xlsx', 'xls'],
    help="O arquivo deve conter as abas: Prazos, Audiências e Iniciais"
)

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

# Carrega os dados
with st.spinner("Processando o arquivo..."):
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if any(df is None for df in [prazos_df, audiencias_df, iniciais_df]):
    st.stop()

# Mostra informações sobre os dados carregados
with st.expander("ℹ️ Informações sobre os dados carregados"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Prazos:**")
        st.write(f"- Total de registros: {len(prazos_df)}")
        st.write(f"- Colunas: {', '.join(prazos_df.columns)}")
    with col2:
        st.write("**Audiências:**")
        st.write(f"- Total de registros: {len(audiencias_df)}")
        st.write(f"- Colunas: {', '.join(audiencias_df.columns)}")
    with col3:
        st.write("**Iniciais:**")
        st.write(f"- Total de registros: {len(iniciais_df)}")
        st.write(f"- Colunas: {', '.join(iniciais_df.columns)}")

# Seleção da visão
st.sidebar.title("Filtros")
view = st.sidebar.radio(
    "Selecione a visão",
    ["Dashboard Geral", "Prazos", "Audiências", "Processos Iniciais"]
)

# Dashboard Geral
if view == "Dashboard Geral":
    st.header("📊 Dashboard Geral")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Prazos", len(prazos_df))
    with col2:
        st.metric("Total de Audiências", len(audiencias_df))
    with col3:
        st.metric("Total de Processos", len(iniciais_df))
    
    # Gráficos gerais
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Tipo' in prazos_df.columns:
            fig = px.pie(prazos_df, names='Tipo', title='Distribuição de Tipos de Prazo')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Status' in iniciais_df.columns:
            fig = px.bar(iniciais_df['Status'].value_counts(), title='Status dos Processos')
            st.plotly_chart(fig, use_container_width=True)

# Visão de Prazos
elif view == "Prazos":
    st.header("⏰ Gestão de Prazos")
    
    # Filtros
    prazos_filtrados = filter_by_period(prazos_df)
    
    if 'Responsável' in prazos_df.columns:
        responsaveis = st.sidebar.multiselect(
            "Filtrar por Responsável",
            options=sorted(prazos_df['Responsável'].unique())
        )
        if responsaveis:
            prazos_filtrados = prazos_filtrados[prazos_filtrados['Responsável'].isin(responsaveis)]
    
    # Exibição dos dados
    st.dataframe(prazos_filtrados)

# Visão de Audiências
elif view == "Audiências":
    st.header("👥 Gestão de Audiências")
    
    # Filtros
    audiencias_filtradas = filter_by_period(audiencias_df)
    
    if 'Tipo' in audiencias_df.columns:
        tipos = st.sidebar.multiselect(
            "Filtrar por Tipo de Audiência",
            options=sorted(audiencias_df['Tipo'].unique())
        )
        if tipos:
            audiencias_filtradas = audiencias_filtradas[audiencias_filtradas['Tipo'].isin(tipos)]
    
    # Exibição dos dados
    st.dataframe(audiencias_filtradas)
    
    # Calendário de audiências
    if not audiencias_filtradas.empty:
        fig = px.timeline(audiencias_filtradas, x_start='Data', y='Processo',
                         title='Calendário de Audiências')
        st.plotly_chart(fig, use_container_width=True)

# Visão de Processos Iniciais
else:
    st.header("📝 Gestão de Processos Iniciais")
    
    # Filtros
    if 'Status' in iniciais_df.columns:
        status = st.sidebar.multiselect(
            "Filtrar por Status",
            options=sorted(iniciais_df['Status'].unique())
        )
        if status:
            iniciais_df = iniciais_df[iniciais_df['Status'].isin(status)]
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Processos", len(iniciais_df))
    with col2:
        if 'Valor da Causa' in iniciais_df.columns:
            valor_total = iniciais_df['Valor da Causa'].sum()
            st.metric("Valor Total", f"R$ {valor_total:,.2f}")
    with col3:
        if 'Status' in iniciais_df.columns:
            ativos = len(iniciais_df[iniciais_df['Status'] == 'Ativo'])
            st.metric("Processos Ativos", ativos)
    
    # Exibição dos dados
    st.dataframe(iniciais_df)

# Estilo personalizado
st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .stDataFrame {
            margin-top: 20px;
        }
        .stRadio > label {
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)
