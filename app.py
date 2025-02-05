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
            response.raise_for_status()  # Verificar se houve erro no download
            
            # Ler CSV da resposta
            df = pd.read_csv(StringIO(response.text))
            
            # Converter colunas de data
            if name == 'prazos':
                df['Data'] = pd.to_datetime(df['Data'])
            elif name == 'audiencias':
                df['Data'] = pd.to_datetime(df['Data'])
            elif name == 'iniciais':
                df['Data Distribuição'] = pd.to_datetime(df['Data Distribuição'])
            
            dfs[name] = df
        
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Título do Dashboard
st.title("Dashboard Jurídico")

try:
    # Carregar dados
    df_prazos, df_audiencias, df_iniciais = load_data()

    # Verificar se os dados foram carregados corretamente
    if df_prazos.empty or df_audiencias.empty or df_iniciais.empty:
        st.error("""
        Erro ao carregar os dados. Verifique se:
        1. Os links das planilhas estão corretos
        2. As planilhas foram publicadas corretamente
        3. O formato de download está como CSV
        """)
        st.stop()

    # Debug info - mostrar as primeiras linhas de cada DataFrame
    if st.checkbox("Mostrar dados brutos"):
        st.write("### Dados de Prazos")
        st.write(df_prazos.head())
        st.write("### Dados de Audiências")
        st.write(df_audiencias.head())
        st.write("### Dados de Processos Iniciais")
        st.write(df_iniciais.head())

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
                options=sorted(df_prazos['Tipo'].unique()),
                default=sorted(df_prazos['Tipo'].unique())
            )
        
        with col_prazos2:
            responsavel_prazo = st.multiselect(
                "Responsável",
                options=sorted(df_prazos['Responsável'].unique()),
                default=sorted(df_prazos['Responsável'].unique())
            )
        
        # Filtrar dados de prazos
        mask_prazos = (
            df_prazos_filtrado['Tipo'].isin(tipo_prazo) &
            df_prazos_filtrado['Responsável'].isin(responsavel_prazo)
        )
        df_prazos_filtrado = df_prazos_filtrado[mask_prazos]
        
        # Gráfico de prazos por tipo
        if not df_prazos_filtrado.empty:
            fig_prazos_tipo = px.bar(
                df_prazos_filtrado['Tipo'].value_counts(),
                title="Prazos por Tipo"
            )
            st.plotly_chart(fig_prazos_tipo, use_container_width=True)
        
            # Tabela de prazos
            st.dataframe(
                df_prazos_filtrado.sort_values('Data'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Nenhum prazo encontrado para os filtros selecionados.")

    with tab2:
        st.header("Audiências")
        
        # Filtros específicos para audiências
        col_aud1, col_aud2 = st.columns(2)
        
        with col_aud1:
            tipo_audiencia = st.multiselect(
                "Tipo de Audiência",
                options=sorted(df_audiencias['Tipo'].unique()),
                default=sorted(df_audiencias['Tipo'].unique())
            )
        
        with col_aud2:
            vara_audiencia = st.multiselect(
                "Vara",
                options=sorted(df_audiencias['Vara'].unique()),
                default=sorted(df_audiencias['Vara'].unique())
            )
        
        # Filtrar dados de audiências
        mask_audiencias = (
            df_audiencias_filtrado['Tipo'].isin(tipo_audiencia) &
            df_audiencias_filtrado['Vara'].isin(vara_audiencia)
        )
        df_audiencias_filtrado = df_audiencias_filtrado[mask_audiencias]
        
        # Gráfico de audiências por tipo
        if not df_audiencias_filtrado.empty:
            fig_aud_tipo = px.bar(
                df_audiencias_filtrado['Tipo'].value_counts(),
                title="Audiências por Tipo"
            )
            st.plotly_chart(fig_aud_tipo, use_container_width=True)
        
            # Tabela de audiências
            st.dataframe(
                df_audiencias_filtrado.sort_values('Data'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Nenhuma audiência encontrada para os filtros selecionados.")

    with tab3:
        st.header("Processos Iniciais")
        
        # Filtros específicos para processos iniciais
        col_ini1, col_ini2 = st.columns(2)
        
        with col_ini1:
            tipo_acao = st.multiselect(
                "Tipo de Ação",
                options=sorted(df_iniciais['Tipo de Ação'].unique()),
                default=sorted(df_iniciais['Tipo de Ação'].unique())
            )
        
        with col_ini2:
            status = st.multiselect(
                "Status",
                options=sorted(df_iniciais['Status'].unique()),
                default=sorted(df_iniciais['Status'].unique())
            )
        
        # Filtrar dados de processos iniciais
        mask_iniciais = (
            df_iniciais['Tipo de Ação'].isin(tipo_acao) &
            df_iniciais['Status'].isin(status)
        )
        df_iniciais_filtrado = df_iniciais[mask_iniciais]
        
        if not df_iniciais_filtrado.empty:
            # Gráfico de processos por tipo de ação
            fig_ini_tipo = px.bar(
                df_iniciais_filtrado['Tipo de Ação'].value_counts(),
                title="Processos por Tipo de Ação"
            )
            st.plotly_chart(fig_ini_tipo, use_container_width=True)
            
            # Gráfico de processos por status
            fig_ini_status = px.pie(
                df_iniciais_filtrado,
                names='Status',
                title="Distribuição por Status"
            )
            st.plotly_chart(fig_ini_status, use_container_width=True)
            
            # Tabela de processos iniciais
            st.dataframe(
                df_iniciais_filtrado.sort_values('Data Distribuição', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Nenhum processo encontrado para os filtros selecionados.")

    # Adicionar footer com informações de última atualização
    st.markdown("---")
    st.markdown(f"*Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")

except Exception as e:
    st.error(f"Ocorreu um erro inesperado: {str(e)}")
    st.write("Por favor, verifique se todas as colunas necessárias estão presentes nas planilhas e se os formatos estão corretos.")
