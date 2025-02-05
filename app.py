import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração inicial
st.set_page_config(page_title="Gestão Jurídica", layout="wide")

# URLs das abas publicadas
URL_PRAZOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1719876081&single=true&output=csv"
URL_AUDIENCIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1604483895&single=true&output=csv"
URL_INICIAIS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJjDmlGNdybLnCLRZ1GpeJN8cuDWnGH59BiNJ2U0rklQR8BD3wQKbjgVFX0HvT7-Syk5cIJVzebrwk/pub?gid=1311683775&single=true&output=csv"

# Função para carregar dados
@st.cache_data(ttl=600)
def load_data(url):
    df = pd.read_csv(url)
    
    # Detectar automaticamente colunas de data (ajuste conforme necessário)
    date_columns = [col for col in df.columns if 'data' in col.lower() or 'prazo' in col.lower()]
    
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
        except:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

# Carregar todos os dados
df_prazos = load_data(URL_PRAZOS)
df_audiencias = load_data(URL_AUDIENCIAS)
df_iniciais = load_data(URL_INICIAIS)

# Sidebar - Filtros temporais
st.sidebar.header("Filtros Temporais")
today = datetime.today().normalize()

# Função para filtro de datas
def date_filter(df, date_column, days):
    if date_column in df.columns:
        end_date = today + timedelta(days=days)
        return df[(df[date_column] >= today) & (df[date_column] <= end_date)]
    return df

# Seleção de período
periodo = st.sidebar.selectbox(
    "Selecione o período para Prazos e Audiências:",
    ["Esta Semana (7 dias)", "Próxima Semana (14 dias)", "Próximos 15 dias"],
    index=0
)

# Mapeamento de dias
days = 7 if "7" in periodo else 14 if "14" in periodo else 15

# Layout principal
st.title("Dashboard Gestão Jurídica")

# Abas principais
tab1, tab2, tab3 = st.tabs(["🗓️ Prazos Processuais", "👨⚖️ Audiências", "📁 Processos Iniciais"])

with tab1:
    st.header("Controle de Prazos Processuais")
    
    # Aplicar filtro
    filtered_prazos = date_filter(df_prazos, 'Prazo', days)  # Ajustar nome da coluna
    
    # Filtros adicionais
    col1, col2, col3 = st.columns(3)
    with col1:
        status = st.multiselect(
            "Status do Prazo",
            options=filtered_prazos['Status'].unique(),
            default=filtered_prazos['Status'].unique()
        )
    with col2:
        responsaveis = st.multiselect(
            "Responsáveis",
            options=filtered_prazos['Responsável'].unique(),
            default=filtered_prazos['Responsável'].unique()
        )
    with col3:
        tipos = st.multiselect(
            "Tipo de Prazo",
            options=filtered_prazos['Tipo'].unique(),
            default=filtered_prazos['Tipo'].unique()
        )
    
    # Aplicar filtros
    filtered_prazos = filtered_prazos[
        filtered_prazos['Status'].isin(status) &
        filtered_prazos['Responsável'].isin(responsaveis) &
        filtered_prazos['Tipo'].isin(tipos)
    ]
    
    # Exibir dados
    st.dataframe(
        filtered_prazos.style.highlight_between(
            subset='Prazo', 
            left=today, 
            right=today+timedelta(days=3),
            color='#ff9999'
        ),
        use_container_width=True,
        height=600
    )

with tab2:
    st.header("Agenda de Audiências")
    
    # Aplicar filtro
    filtered_audiencias = date_filter(df_audiencias, 'Data', days)  # Ajustar nome da coluna
    
    # Filtros rápidos
    col1, col2 = st.columns(2)
    with col1:
        tribunal = st.multiselect(
            "Tribunal",
            options=filtered_audiencias['Tribunal'].unique(),
            default=filtered_audiencias['Tribunal'].unique()
        )
    with col2:
        status_aud = st.multiselect(
            "Status da Audiência",
            options=filtered_audiencias['Status'].unique(),
            default=filtered_audiencias['Status'].unique()
        )
    
    # Aplicar filtros
    filtered_audiencias = filtered_audiencias[
        filtered_audiencias['Tribunal'].isin(tribunal) &
        filtered_audiencias['Status'].isin(status_aud)
    ]
    
    # Visualização em calendário
    if not filtered_audiencias.empty:
        st.subheader("Linha do Tempo")
        timeline_data = filtered_audiencias[['Data', 'Processo', 'Horário']].sort_values('Data')
        st.write(timeline_data.set_index('Data'))
    else:
        st.warning("Nenhuma audiência encontrada para o período selecionado")

with tab3:
    st.header("Processos Iniciais")
    
    # Filtros estáticos
    col1, col2, col3 = st.columns(3)
    with col1:
        clientes = st.multiselect(
            "Clientes",
            options=df_iniciais['Cliente'].unique(),
            default=df_iniciais['Cliente'].unique()
        )
    with col2:
        areas = st.multiselect(
            "Área Jurídica",
            options=df_iniciais['Área'].unique(),
            default=df_iniciais['Área'].unique()
        )
    with col3:
        status_inic = st.multiselect(
            "Status do Processo",
            options=df_iniciais['Status'].unique(),
            default=df_iniciais['Status'].unique()
        )
    
    # Aplicar filtros
    filtered_iniciais = df_iniciais[
        df_iniciais['Cliente'].isin(clientes) &
        df_iniciais['Área'].isin(areas) &
        df_iniciais['Status'].isin(status_inic)
    ]
    
    # Métricas
    st.subheader("Estatísticas")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Processos", len(filtered_iniciais))
    col2.metric("Ativos", len(filtered_iniciais[filtered_iniciais['Status'] == 'Ativo']))
    col3.metric("Urgentes", len(filtered_iniciais[filtered_iniciais['Prioridade'] == 'Alta']))
    col4.metric("Em Atraso", len(filtered_iniciais[filtered_iniciais['Prazo'] < today]))
    
    # Exibir dados
    st.dataframe(filtered_iniciais, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption("Dados atualizados automaticamente da planilha pública - Atualizado em " + datetime.now().strftime("%d/%m/%Y %H:%M"))
