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
        sheet_names = [s.lower() for s in xls.sheet_names]
        
        # Função auxiliar para encontrar a aba correta
        def find_sheet(possible_names, available_sheets):
            for name in possible_names:
                for sheet in available_sheets:
                    if name.lower() == sheet.lower():
                        return sheet
            return None

        # Definir possíveis nomes para cada aba
        prazo_names = ['Prazos', 'PRAZOS', 'prazos', 'Prazo', 'PRAZO']
        audiencia_names = ['Audiências', 'AUDIÊNCIAS', 'Audiencias', 'AUDIENCIAS', 'audiencias', 'Audiência', 'AUDIÊNCIA']
        inicial_names = ['Iniciais', 'INICIAIS', 'iniciais', 'Inicial', 'INICIAL']

        # Encontrar as abas corretas
        prazo_sheet = find_sheet(prazo_names, xls.sheet_names)
        audiencia_sheet = find_sheet(audiencia_names, xls.sheet_names)
        inicial_sheet = find_sheet(inicial_names, xls.sheet_names)

        # Carregar aba Prazos
        if prazo_sheet:
            dfs['prazos'] = pd.read_excel(xls, prazo_sheet)
            if 'Data' in dfs['prazos'].columns:
                dfs['prazos']['Data'] = pd.to_datetime(dfs['prazos']['Data'], errors='coerce')
        
        # Carregar aba Audiências
        if audiencia_sheet:
            dfs['audiencias'] = pd.read_excel(xls, audiencia_sheet)
            if 'Data' in dfs['audiencias'].columns:
                dfs['audiencias']['Data'] = pd.to_datetime(dfs['audiencias']['Data'], errors='coerce')
            if 'Horário' in dfs['audiencias'].columns:
                dfs['audiencias']['Horário'] = pd.to_datetime(dfs['audiencias']['Horário'], format='mixed', errors='coerce')
        
        # Carregar aba Iniciais
        if inicial_sheet:
            dfs['iniciais'] = pd.read_excel(xls, inicial_sheet)
            if 'Data' in dfs['iniciais'].columns:
                dfs['iniciais']['Data'] = pd.to_datetime(dfs['iniciais']['Data'], errors='coerce')
        
        # Verificar se todas as abas necessárias foram carregadas
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
    # Debug: mostrar as colunas disponíveis
    st.write("Colunas disponíveis:", df.columns.tolist())
    
    # Encontrar a coluna de data (pode ter variações no nome)
    date_cols = [col for col in df.columns if any(date_term in col.lower() 
                 for date_term in ['data', 'date', 'dt', 'data audiência', 'data prazo'])]
    
    if not date_cols:
        st.warning("Não foi encontrada coluna de data. Mostrando todos os registros.")
        return df
        
    date_col = date_cols[0]
    st.write(f"Usando coluna de data: {date_col}")
    
    # Converter a coluna de data para datetime se ainda não estiver
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    except Exception as e:
        st.error(f"Erro ao converter datas: {str(e)}")
        return df
    
    periodo = st.sidebar.selectbox(
        "Filtrar por período",
        ["Todos", "Esta semana", "Próxima semana", "Próximos 15 dias"]
    )
    
    if periodo == "Todos":
        return df
    
    hoje = pd.Timestamp.now().normalize()
    
    try:
        if periodo == "Esta semana":
            inicio = hoje - timedelta(days=hoje.weekday())
            fim = inicio + timedelta(days=6)
        elif periodo == "Próxima semana":
            inicio = hoje - timedelta(days=hoje.weekday()) + timedelta(days=7)
            fim = inicio + timedelta(days=6)
        else:  # Próximos 15 dias
            inicio = hoje
            fim = hoje + timedelta(days=15)
        
        # Debug: mostrar datas do filtro
        st.write(f"Filtrando de {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}")
        
        # Aplicar filtro com tratamento de erro
        filtered_df = df[df[date_col].notna() & df[date_col].between(inicio, fim)]
        return filtered_df
        
    except Exception as e:
        st.error(f"Erro ao aplicar filtro: {str(e)}")
        return df

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
    st.dataframe(prazos_filtrados, hide_index=True)

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
    
    # Formatação das colunas de data e horário para exibição
    audiencias_display = audiencias_filtradas.copy()
    
    # Identificar a coluna de data (pode ter variações no nome)
    date_columns = [col for col in audiencias_display.columns if 'data' in col.lower()]
    horario_columns = [col for col in audiencias_display.columns if 'hor' in col.lower()]
    
    # Formatar a coluna de data
    if date_columns:
        date_col = date_columns[0]
        audiencias_display[date_col] = pd.to_datetime(audiencias_display[date_col], errors='coerce').dt.strftime('%d/%m/%Y')
    
    # Formatar a coluna de horário
    if horario_columns:
        horario_col = horario_columns[0]
        audiencias_display[horario_col] = pd.to_datetime(audiencias_display[horario_col], format='mixed', errors='coerce').dt.strftime('%H:%M')
    
    # Exibição dos dados formatados
    st.dataframe(audiencias_display, hide_index=True)
    
    # Calendário de audiências
    if len(audiencias_filtradas) > 0:
        # Verificar e usar o nome correto da coluna para processos
        processo_column = next((col for col in audiencias_filtradas.columns 
                              if col.lower() in ['processo', 'nº processo', 'numero processo', 'núm. processo']), 
                             audiencias_filtradas.columns[0])
        
        # Criar figura base
        fig = go.Figure()
        
        # Encontrar a coluna de data
        date_columns = [col for col in audiencias_filtradas.columns if 'data' in col.lower()]
        if date_columns:
            date_col = date_columns[0]
            # Adicionar as audiências como pontos
            fig.add_trace(go.Scatter(
                x=audiencias_filtradas[date_col],
                y=audiencias_filtradas[processo_column],
                mode='markers+text',
                marker=dict(size=12, symbol='circle'),
                text=audiencias_filtradas['Tipo'] if 'Tipo' in audiencias_filtradas.columns else None,
                textposition='top center'
            ))
        
        # Configurar o layout
        fig.update_layout(
            title='Calendário de Audiências',
            xaxis_title='Data',
            yaxis_title='Processo',
            height=max(400, len(audiencias_filtradas) * 30),
            showlegend=False,
            xaxis=dict(
                type='date',
                tickformat='%d/%m/%Y'
            )
        )
        
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
    st.dataframe(iniciais_df, hide_index=True)

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
