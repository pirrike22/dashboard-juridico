import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

# Função para carregar os dados
@st.cache_data
def load_data():
    # URLs das abas da planilha
    url_base = "https://docs.google.com/spreadsheets/d/1fM5Oq6McjWFTDbUTbimMJfcnB2J1Oiy-_UY-VnDcnxE/export?format=csv&gid="
    
    # IDs das abas (você precisará substituir pelos IDs corretos)
    prazos_gid = "0"  # Substitua pelo ID correto da aba prazos
    audiencias_gid = "1"  # Substitua pelo ID correto da aba audiências
    iniciais_gid = "2"  # Substitua pelo ID correto da aba iniciais
    
    # Carregar os dataframes
    df_prazos = pd.read_csv(f"{url_base}{prazos_gid}")
    df_audiencias = pd.read_csv(f"{url_base}{audiencias_gid}")
    df_iniciais = pd.read_csv(f"{url_base}{iniciais_gid}")
    
    # Converter colunas de data
    df_prazos['Data'] = pd.to_datetime(df_prazos['Data'])
    df_audiencias['Data'] = pd.to_datetime(df_audiencias['Data'])
    df_iniciais['Data Distribuição'] = pd.to_datetime(df_iniciais['Data Distribuição'])
    
    return df_prazos, df_audiencias, df_iniciais

# Carregar dados
df_prazos, df_audiencias, df_iniciais = load_data()

# Título do Dashboard
st.title("Dashboard Jurídico")

# Sidebar para filtros
st.sidebar.header("Filtros")

# Filtro de período
periodo_options = [
    "Esta semana",
    "Próxima semana",
    "Próximos 15 dias",
    "Todos"
]
periodo_selecionado = st.sidebar.selectbox("Período", periodo_options)

# Função para filtrar por período
def filtrar_por_periodo(df, coluna_data):
    hoje = pd.Timestamp.today()
    
    if periodo_selecionado == "Esta semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        return df[(df[coluna_data] >= inicio_semana) & (df[coluna_data] <= fim_semana)]
    
    elif periodo_selecionado == "Próxima semana":
        inicio_prox_semana = hoje - timedelta(days=hoje.weekday()) + timedelta(days=7)
        fim_prox_semana = inicio_prox_semana + timedelta(days=6)
        return df[(df[coluna_data] >= inicio_prox_semana) & (df[coluna_data] <= fim_prox_semana)]
    
    elif periodo_selecionado == "Próximos 15 dias":
        fim_periodo = hoje + timedelta(days=15)
        return df[(df[coluna_data] >= hoje) & (df[coluna_data] <= fim_periodo)]
    
    return df

# Aplicar filtros
df_prazos_filtrado = filtrar_por_periodo(df_prazos, 'Data')
df_audiencias_filtrado = filtrar_por_periodo(df_audiencias, 'Data')

# Layout em três colunas para métricas principais
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Prazos", len(df_prazos_filtrado))
    
with col2:
    st.metric("Total de Audiências", len(df_audiencias_filtrado))
    
with col3:
    st.metric("Total de Processos Iniciais", len(df_iniciais))

# Tabs para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])

with tab1:
    st.header("Prazos")
    
    # Filtros específicos para prazos
    col_prazos1, col_prazos2 = st.columns(2)
    
    with col_prazos1:
        tipo_prazo = st.multiselect(
            "Tipo de Prazo",
            options=df_prazos['Tipo'].unique(),
            default=df_prazos['Tipo'].unique()
        )
    
    with col_prazos2:
        responsavel_prazo = st.multiselect(
            "Responsável",
            options=df_prazos['Responsável'].unique(),
            default=df_prazos['Responsável'].unique()
        )
    
    # Filtrar dados de prazos
    df_prazos_filtrado = df_prazos_filtrado[
        (df_prazos_filtrado['Tipo'].isin(tipo_prazo)) &
        (df_prazos_filtrado['Responsável'].isin(responsavel_prazo))
    ]
    
    # Gráfico de prazos por tipo
    fig_prazos_tipo = px.bar(
        df_prazos_filtrado['Tipo'].value_counts(),
        title="Prazos por Tipo"
    )
    st.plotly_chart(fig_prazos_tipo)
    
    # Tabela de prazos
    st.dataframe(df_prazos_filtrado)

with tab2:
    st.header("Audiências")
    
    # Filtros específicos para audiências
    col_aud1, col_aud2 = st.columns(2)
    
    with col_aud1:
        tipo_audiencia = st.multiselect(
            "Tipo de Audiência",
            options=df_audiencias['Tipo'].unique(),
            default=df_audiencias['Tipo'].unique()
        )
    
    with col_aud2:
        vara_audiencia = st.multiselect(
            "Vara",
            options=df_audiencias['Vara'].unique(),
            default=df_audiencias['Vara'].unique()
        )
    
    # Filtrar dados de audiências
    df_audiencias_filtrado = df_audiencias_filtrado[
        (df_audiencias_filtrado['Tipo'].isin(tipo_audiencia)) &
        (df_audiencias_filtrado['Vara'].isin(vara_audiencia))
    ]
    
    # Gráfico de audiências por tipo
    fig_aud_tipo = px.bar(
        df_audiencias_filtrado['Tipo'].value_counts(),
        title="Audiências por Tipo"
    )
    st.plotly_chart(fig_aud_tipo)
    
    # Tabela de audiências
    st.dataframe(df_audiencias_filtrado)

with tab3:
    st.header("Processos Iniciais")
    
    # Filtros específicos para processos iniciais
    col_ini1, col_ini2 = st.columns(2)
    
    with col_ini1:
        tipo_acao = st.multiselect(
            "Tipo de Ação",
            options=df_iniciais['Tipo de Ação'].unique(),
            default=df_iniciais['Tipo de Ação'].unique()
        )
    
    with col_ini2:
        status = st.multiselect(
            "Status",
            options=df_iniciais['Status'].unique(),
            default=df_iniciais['Status'].unique()
        )
    
    # Filtrar dados de processos iniciais
    df_iniciais_filtrado = df_iniciais[
        (df_iniciais['Tipo de Ação'].isin(tipo_acao)) &
        (df_iniciais['Status'].isin(status))
    ]
    
    # Gráfico de processos por tipo de ação
    fig_ini_tipo = px.bar(
        df_iniciais_filtrado['Tipo de Ação'].value_counts(),
        title="Processos por Tipo de Ação"
    )
    st.plotly_chart(fig_ini_tipo)
    
    # Gráfico de processos por status
    fig_ini_status = px.pie(
        df_iniciais_filtrado,
        names='Status',
        title="Distribuição por Status"
    )
    st.plotly_chart(fig_ini_status)
    
    # Tabela de processos iniciais
    st.dataframe(df_iniciais_filtrado)

# Adicionar footer com informações de última atualização
st.markdown("---")
st.markdown(f"*Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
