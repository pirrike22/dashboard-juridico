import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(page_title="Dashboard Jurídica", layout="wide")

def format_date_column(df, date_col):
    """Formata coluna de data"""
    try:
        df[date_col] = pd.to_datetime(df[date_col], format='mixed', errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao formatar coluna de data {date_col}: {str(e)}")
        return df

def load_data(uploaded_file):
    try:
        excel_file = io.BytesIO(uploaded_file.getvalue())
        
        # Carregar cada aba
        prazos_df = pd.read_excel(excel_file, sheet_name='Prazos', header=0)
        audiencias_df = pd.read_excel(excel_file, sheet_name='Audiências')
        iniciais_df = pd.read_excel(excel_file, sheet_name='Iniciais')
        
        # Formatar colunas de data
        audiencias_df = format_date_column(audiencias_df, 'DATA')
        iniciais_df = format_date_column(iniciais_df, 'DATA')
        
        return prazos_df, audiencias_df, iniciais_df
        
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None, None, None

def filter_by_period(df, date_col='DATA'):
    """Filtra DataFrame por período"""
    if date_col not in df.columns:
        return df
    
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
    
    return df[df[date_col].between(inicio, fim)]

# Interface principal
st.title("🔍 Dashboard Jurídica")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Carregue o arquivo Excel",
    type=['xlsx'],
    help="Selecione o arquivo Excel com as abas: Prazos, Audiências e Iniciais"
)

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

# Carregar dados
with st.spinner("Processando arquivo..."):
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.stop()

# Menu de navegação
st.sidebar.title("Navegação")
pagina = st.sidebar.radio(
    "Selecione a página",
    ["Dashboard Geral", "Audiências", "Iniciais"]
)

# Página: Dashboard Geral
if pagina == "Dashboard Geral":
    st.header("📊 Visão Geral")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_audiencias = len(audiencias_df)
        st.metric("Total de Audiências", total_audiencias)
        
    with col2:
        audiencias_pendentes = len(audiencias_df[audiencias_df['DATA'] >= pd.Timestamp.now()])
        st.metric("Audiências Pendentes", audiencias_pendentes)
        
    with col3:
        total_iniciais = len(iniciais_df)
        st.metric("Total de Processos Iniciais", total_iniciais)
    
    # Análises
    col1, col2 = st.columns(2)
    
    with col1:
        if 'TIPO DE AUDIÊNCIA' in audiencias_df.columns:
            fig = px.pie(audiencias_df, names='TIPO DE AUDIÊNCIA', 
                        title='Distribuição por Tipo de Audiência')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'MATÉRIA' in iniciais_df.columns:
            fig = px.bar(iniciais_df['MATÉRIA'].value_counts(),
                        title='Distribuição por Matéria')
            st.plotly_chart(fig, use_container_width=True)

# Página: Audiências
elif pagina == "Audiências":
    st.header("👥 Gestão de Audiências")
    
    # Filtros
    audiencias_filtradas = filter_by_period(audiencias_df)
    
    if 'TIPO DE AUDIÊNCIA' in audiencias_df.columns:
        tipos = st.sidebar.multiselect(
            "Filtrar por Tipo de Audiência",
            options=sorted(audiencias_df['TIPO DE AUDIÊNCIA'].unique())
        )
        if tipos:
            audiencias_filtradas = audiencias_filtradas[
                audiencias_filtradas['TIPO DE AUDIÊNCIA'].isin(tipos)
            ]
    
    # Preparar dados para exibição
    audiencias_display = audiencias_filtradas.copy()
    
    # Formatar data e hora para exibição
    audiencias_display['DATA'] = audiencias_display['DATA'].dt.strftime('%d/%m/%Y')
    if 'HORÁRIO' in audiencias_display.columns:
        audiencias_display['HORÁRIO'] = pd.to_datetime(
            audiencias_display['HORÁRIO'], format='mixed', errors='coerce'
        ).dt.strftime('%H:%M')
    
    # Exibir tabela de audiências
    st.dataframe(
        audiencias_display,
        hide_index=True,
        use_container_width=True
    )
    
    # Calendário de audiências
    if not audiencias_filtradas.empty:
        st.subheader("📅 Calendário de Audiências")
        fig = go.Figure()
        
        # Adicionar eventos ao calendário
        fig.add_trace(go.Scatter(
            x=audiencias_filtradas['DATA'],
            y=audiencias_filtradas['Nº DO PROCESSO'],
            mode='markers+text',
            marker=dict(size=12, symbol='circle'),
            text=audiencias_filtradas['TIPO DE AUDIÊNCIA'],
            textposition='top center'
        ))
        
        # Configurar layout
        fig.update_layout(
            height=max(400, len(audiencias_filtradas) * 30),
            showlegend=False,
            xaxis=dict(title='Data', tickformat='%d/%m/%Y'),
            yaxis=dict(title='Processo')
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Página: Iniciais
else:
    st.header("📝 Processos Iniciais")
    
    # Filtros
    if 'MATÉRIA' in iniciais_df.columns:
        materias = st.sidebar.multiselect(
            "Filtrar por Matéria",
            options=sorted(iniciais_df['MATÉRIA'].unique())
        )
        if materias:
            iniciais_df = iniciais_df[iniciais_df['MATÉRIA'].isin(materias)]
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Processos", len(iniciais_df))
    
    with col2:
        processos_distribuidos = len(iniciais_df[iniciais_df['DISTRIBUÍDO'] == 'Sim'])
        st.metric("Processos Distribuídos", processos_distribuidos)
    
    with col3:
        processos_protocolados = len(iniciais_df[iniciais_df['PROTOCOLADO'] == 'Sim'])
        st.metric("Processos Protocolados", processos_protocolados)
    
    # Exibição dos dados
    st.dataframe(iniciais_df, hide_index=True, use_container_width=True)

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
    </style>
""", unsafe_allow_html=True
