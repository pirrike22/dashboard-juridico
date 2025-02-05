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
        excel_file = io.BytesIO(uploaded_file.getvalue())
        xls = pd.ExcelFile(excel_file)
        
        dfs = {}
        sheet_names = [s.lower() for s in xls.sheet_names]

        def find_sheet(possible_names, available_sheets):
            for name in possible_names:
                for sheet in available_sheets:
                    if name.lower() == sheet.lower():
                        return sheet
            return None

        prazo_names = ['Prazos', 'Prazo']
        audiencia_names = ['Audiências', 'Audiencias']
        inicial_names = ['Iniciais', 'Inicial']

        prazo_sheet = find_sheet(prazo_names, xls.sheet_names)
        audiencia_sheet = find_sheet(audiencia_names, xls.sheet_names)
        inicial_sheet = find_sheet(inicial_names, xls.sheet_names)

        if prazo_sheet:
            dfs['prazos'] = pd.read_excel(xls, prazo_sheet)
            if 'Data' in dfs['prazos'].columns:
                dfs['prazos']['Data'] = pd.to_datetime(dfs['prazos']['Data'], errors='coerce')
        
        if audiencia_sheet:
            dfs['audiencias'] = pd.read_excel(xls, audiencia_sheet)
            if 'Data' in dfs['audiencias'].columns:
                dfs['audiencias']['Data'] = pd.to_datetime(dfs['audiencias']['Data'], errors='coerce')
            if 'Horário' in dfs['audiencias'].columns:
                dfs['audiencias']['Horário'] = pd.to_datetime(dfs['audiencias']['Horário'], errors='coerce').dt.strftime('%H:%M')
        
        if inicial_sheet:
            dfs['iniciais'] = pd.read_excel(xls, inicial_sheet)
            if 'Data' in dfs['iniciais'].columns:
                dfs['iniciais']['Data'] = pd.to_datetime(dfs['iniciais']['Data'], errors='coerce')

        required_sheets = ['prazos', 'audiencias', 'iniciais']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in dfs]
        
        if missing_sheets:
            st.error(f"Abas não encontradas: {', '.join(missing_sheets)}")
            return None, None, None
            
        return dfs['prazos'], dfs['audiencias'], dfs['iniciais']
        
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
    else:  # Próximos 15 dias
        inicio = hoje
        fim = hoje + timedelta(days=15)
    
    return df[df['Data'].between(inicio, fim)]

st.title("🔍 Dashboard Jurídica")

uploaded_file = st.file_uploader(
    "Faça o upload do arquivo Excel com os dados",
    type=['xlsx', 'xls'],
    help="O arquivo deve conter as abas: Prazos, Audiências e Iniciais"
)

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

with st.spinner("Processando o arquivo..."):
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.stop()

st.sidebar.title("Filtros")
view = st.sidebar.radio(
    "Selecione a visualização",
    ["Dashboard Geral", "Prazos", "Audiências", "Processos Iniciais"]
)

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
            fig = px.bar(iniciais_df['Status'].value_counts(), title='Status dos Processos')
            st.plotly_chart(fig, use_container_width=True)

elif view == "Audiências":
    st.header("👥 Gestão de Audiências")
    
    audiencias_filtradas = filter_by_period(audiencias_df)
    
    audiencias_display = audiencias_filtradas.copy()
    audiencias_display['Data'] = audiencias_display['Data'].dt.strftime('%d/%m/%Y')
    
    if 'Horário' in audiencias_display.columns:
        audiencias_display['Horário'] = pd.to_datetime(audiencias_display['Horário'], errors='coerce').dt.strftime('%H:%M')
    
    st.dataframe(audiencias_display.reset_index(drop=True))

    if len(audiencias_filtradas) > 0:
        processo_column = next((col for col in audiencias_filtradas.columns 
                              if col.lower() in ['processo', 'nº processo', 'numero processo', 'núm. processo']), 
                             None)

        if processo_column:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=audiencias_filtradas['Data'],
                y=audiencias_filtradas[processo_column],
                mode='markers+text',
                marker=dict(size=12, symbol='circle'),
                text=audiencias_filtradas['Tipo'] if 'Tipo' in audiencias_filtradas.columns else None,
                textposition='top center'
            ))
            fig.update_layout(
                title='Calendário de Audiências',
                xaxis_title='Data',
                yaxis_title='Processo',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
