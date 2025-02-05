import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Dashboard Jurídica", layout="wide")

# Função para verificar e converter colunas de data
def convert_date_columns(df, possible_date_columns):
    for col in possible_date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
            except:
                st.error(f"Erro ao converter a coluna {col} para data")
    return df

# Função para carregar os dados do arquivo uploadado
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            # Carregando as abas específicas
            excel_file = io.BytesIO(uploaded_file.getvalue())
            
            # Tentativa de leitura com diferentes nomes de abas possíveis
            try:
                prazos_df = pd.read_excel(excel_file, sheet_name='Prazos')
            except:
                try:
                    prazos_df = pd.read_excel(excel_file, sheet_name='PRAZOS')
                except:
                    st.error("Não foi possível encontrar a aba 'Prazos'")
                    return None, None, None
            
            try:
                audiencias_df = pd.read_excel(excel_file, sheet_name='Audiências')
            except:
                try:
                    audiencias_df = pd.read_excel(excel_file, sheet_name='AUDIÊNCIAS')
                except:
                    try:
                        audiencias_df = pd.read_excel(excel_file, sheet_name='Audiencias')
                    except:
                        st.error("Não foi possível encontrar a aba 'Audiências'")
                        return None, None, None
            
            try:
                iniciais_df = pd.read_excel(excel_file, sheet_name='Iniciais')
            except:
                try:
                    iniciais_df = pd.read_excel(excel_file, sheet_name='INICIAIS')
                except:
                    st.error("Não foi possível encontrar a aba 'Iniciais'")
                    return None, None, None
            
            # Lista de possíveis nomes de colunas de data
            date_columns_prazos = ['Data', 'DATA', 'Data do Prazo', 'DATA DO PRAZO']
            date_columns_audiencias = ['Data', 'DATA', 'Data da Audiência', 'DATA DA AUDIÊNCIA']
            date_columns_iniciais = ['Data Distribuição', 'DATA DISTRIBUIÇÃO', 'Data de Distribuição']
            
            # Convertendo colunas de data
            prazos_df = convert_date_columns(prazos_df, date_columns_prazos)
            audiencias_df = convert_date_columns(audiencias_df, date_columns_audiencias)
            iniciais_df = convert_date_columns(iniciais_df, date_columns_iniciais)
            
            # Verificar se as colunas de data foram encontradas e convertidas
            if not any(col in prazos_df.columns for col in date_columns_prazos):
                st.error("Não foi encontrada uma coluna de data válida na aba Prazos")
                return None, None, None
                
            if not any(col in audiencias_df.columns for col in date_columns_audiencias):
                st.error("Não foi encontrada uma coluna de data válida na aba Audiências")
                return None, None, None
                
            if not any(col in iniciais_df.columns for col in date_columns_iniciais):
                st.error("Não foi encontrada uma coluna de data válida na aba Iniciais")
                return None, None, None
            
            # Padronizar os nomes das colunas de data
            for col in prazos_df.columns:
                if col.upper() in [c.upper() for c in date_columns_prazos]:
                    prazos_df = prazos_df.rename(columns={col: 'Data'})
                    
            for col in audiencias_df.columns:
                if col.upper() in [c.upper() for c in date_columns_audiencias]:
                    audiencias_df = audiencias_df.rename(columns={col: 'Data'})
                    
            for col in iniciais_df.columns:
                if col.upper() in [c.upper() for c in date_columns_iniciais]:
                    iniciais_df = iniciais_df.rename(columns={col: 'Data Distribuição'})
            
            return prazos_df, audiencias_df, iniciais_df
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            return None, None, None
    return None, None, None

# Interface para upload do arquivo
st.title("Dashboard Jurídica")
st.write("Para começar, faça o upload do arquivo Excel com os dados atualizados:")

uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])

if uploaded_file is None:
    st.warning("Por favor, faça o upload do arquivo Excel para visualizar a dashboard.")
    st.stop()

# Carregando os dados após o upload
prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo está no formato correto.")
    st.stop()

# Mostrar informações sobre as colunas encontradas
with st.expander("Informações sobre as colunas carregadas"):
    st.write("Colunas da aba Prazos:", list(prazos_df.columns))
    st.write("Colunas da aba Audiências:", list(audiencias_df.columns))
    st.write("Colunas da aba Iniciais:", list(iniciais_df.columns))

# Configuração da sidebar
st.sidebar.title("Filtros")
selected_view = st.sidebar.selectbox(
    "Selecione a visualização",
    ["Visão Geral", "Prazos", "Audiências", "Iniciais"]
)

# Função para filtrar por período
def filter_by_period(df, date_column):
    periodo = st.sidebar.selectbox(
        "Selecione o período",
        ["Esta semana", "Próxima semana", "Próximos 15 dias", "Todos"]
    )
    
    hoje = pd.Timestamp.now()
    if periodo == "Esta semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        return df[df[date_column].between(inicio_semana, fim_semana)]
    elif periodo == "Próxima semana":
        inicio_prox_semana = hoje - timedelta(days=hoje.weekday()) + timedelta(days=7)
        fim_prox_semana = inicio_prox_semana + timedelta(days=6)
        return df[df[date_column].between(inicio_prox_semana, fim_prox_semana)]
    elif periodo == "Próximos 15 dias":
        return df[df[date_column].between(hoje, hoje + timedelta(days=15))]
    else:
        return df

# Visão Geral
if selected_view == "Visão Geral":
    st.header("Visão Geral")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Prazos", len(prazos_df))
    with col2:
        st.metric("Total de Audiências", len(audiencias_df))
    with col3:
        st.metric("Total de Processos Iniciais", len(iniciais_df))
    
    # Gráficos da visão geral
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de prazos por tipo
        if 'Tipo' in prazos_df.columns:
            fig_tipos = px.pie(prazos_df, names='Tipo', title='Distribuição de Prazos por Tipo')
            st.plotly_chart(fig_tipos, use_container_width=True)
    
    with col2:
        # Timeline de audiências
        fig_timeline = px.timeline(audiencias_df, x_start='Data', y='Processo',
                                 title='Timeline de Audiências')
        st.plotly_chart(fig_timeline, use_container_width=True)

# Visão de Prazos
elif selected_view == "Prazos":
    st.header("Gestão de Prazos")
    
    # Filtros específicos para prazos
    prazos_filtrados = filter_by_period(prazos_df, 'Data')
    
    if 'Responsável' in prazos_df.columns:
        responsavel = st.sidebar.multiselect(
            "Filtrar por Responsável",
            options=sorted(prazos_df['Responsável'].unique())
        )
        if responsavel:
            prazos_filtrados = prazos_filtrados[prazos_filtrados['Responsável'].isin(responsavel)]
    
    # Exibição dos prazos em tabela
    st.dataframe(prazos_filtrados, use_container_width=True)
    
    # Gráficos de prazos
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Status' in prazos_filtrados.columns:
            fig_status = px.bar(prazos_filtrados['Status'].value_counts(), 
                              title='Distribuição por Status')
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        if 'Tipo' in prazos_filtrados.columns:
            fig_tipo = px.pie(prazos_filtrados, names='Tipo', 
                            title='Distribuição por Tipo de Prazo')
            st.plotly_chart(fig_tipo, use_container_width=True)

# Visão de Audiências
elif selected_view == "Audiências":
    st.header("Gestão de Audiências")
    
    # Filtros específicos para audiências
    audiencias_filtradas = filter_by_period(audiencias_df, 'Data')
    
    if 'Tipo' in audiencias_df.columns:
        tipo_audiencia = st.sidebar.multiselect(
            "Filtrar por Tipo de Audiência",
            options=sorted(audiencias_df['Tipo'].unique())
        )
        if tipo_audiencia:
            audiencias_filtradas = audiencias_filtradas[audiencias_filtradas['Tipo'].isin(tipo_audiencia)]
    
    # Exibição das audiências em tabela
    st.dataframe(audiencias_filtradas, use_container_width=True)
    
    # Calendário de audiências
    if not audiencias_filtradas.empty:
        fig_calendar = go.Figure(data=[go.Scatter(
            x=audiencias_filtradas['Data'],
            y=audiencias_filtradas['Processo'],
            mode='markers+text',
            text=audiencias_filtradas['Tipo'],
            textposition='top center'
        )])
        fig_calendar.update_layout(title='Calendário de Audiências')
        st.plotly_chart(fig_calendar, use_container_width=True)

# Visão de Iniciais
elif selected_view == "Iniciais":
    st.header("Gestão de Processos Iniciais")
    
    # Filtros específicos para processos iniciais
    if 'Status' in iniciais_df.columns:
        status_inicial = st.sidebar.multiselect(
            "Filtrar por Status",
            options=sorted(iniciais_df['Status'].unique())
        )
        if status_inicial:
            iniciais_df = iniciais_df[iniciais_df['Status'].isin(status_inicial)]
    
    # Métricas importantes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Processos", len(iniciais_df))
    with col2:
        if 'Valor da Causa' in iniciais_df.columns:
            valor_total = iniciais_df['Valor da Causa'].sum()
            st.metric("Valor Total das Causas", f"R$ {valor_total:,.2f}")
    with col3:
        if 'Status' in iniciais_df.columns:
            processos_ativos = len(iniciais_df[iniciais_df['Status'] == 'Ativo'])
            st.metric("Processos Ativos", processos_ativos)
    
    # Exibição dos processos em tabela
    st.dataframe(iniciais_df, use_container_width=True)
    
    # Gráficos de análise
    if 'Valor da Causa' in iniciais_df.columns and 'Data Distribuição' in iniciais_df.columns:
        fig_evolucao = px.line(iniciais_df.sort_values('Data Distribuição'),
                             x='Data Distribuição',
                             y='Valor da Causa',
                             title='Evolução do Valor das Causas ao Longo do Tempo')
        st.plotly_chart(fig_evolucao, use_container_width=True)

# Adicionar CSS personalizado
st.markdown("""
    <style>
        .stSelectbox {
            margin-bottom: 20px;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .uploadedFile {
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
