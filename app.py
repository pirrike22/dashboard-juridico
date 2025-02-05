import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Configuração da página
st.set_page_config(
    page_title="Dashboard Jurídica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def carregar_dados(uploaded_file):
    try:
        excel_file = io.BytesIO(uploaded_file.getvalue())
        
        # Carregar apenas as abas necessárias
        audiencias_df = pd.read_excel(excel_file, sheet_name='Audiências')
        iniciais_df = pd.read_excel(excel_file, sheet_name='Iniciais')
        
        # Converter colunas de data
        audiencias_df['DATA'] = pd.to_datetime(audiencias_df['DATA'], errors='coerce')
        iniciais_df['DATA'] = pd.to_datetime(iniciais_df['DATA'], errors='coerce')
        
        return audiencias_df, iniciais_df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None, None

def filtrar_por_periodo(df):
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
    
    return df[df['DATA'].between(inicio, fim)]

# Interface principal
st.title("🔍 Dashboard Jurídica")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=['xlsx'])

if not uploaded_file:
    st.info("👆 Por favor, faça o upload do arquivo Excel para começar.")
    st.stop()

# Carregar dados
audiencias_df, iniciais_df = carregar_dados(uploaded_file)

if audiencias_df is None or iniciais_df is None:
    st.stop()

# Menu lateral
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
    
    # Audiências
    with col1:
        total_audiencias = len(audiencias_df)
        audiencias_futuras = len(audiencias_df[audiencias_df['DATA'] >= pd.Timestamp.now()])
        st.metric(
            "Total de Audiências",
            total_audiencias,
            f"{audiencias_futuras} pendentes"
        )
    
    # Processos
    with col2:
        total_processos = len(iniciais_df)
        protocolados = len(iniciais_df[iniciais_df['PROTOCOLADO'] == 'Sim'])
        st.metric(
            "Total de Processos",
            total_processos,
            f"{protocolados} protocolados"
        )
    
    # Matérias
    with col3:
        total_materias = iniciais_df['MATÉRIA'].nunique()
        st.metric("Tipos de Matéria", total_materias)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Tipos de Audiência
        fig_tipos = px.pie(
            audiencias_df,
            names='TIPO DE AUDIÊNCIA',
            title='Distribuição por Tipo de Audiência'
        )
        st.plotly_chart(fig_tipos, use_container_width=True)
    
    with col2:
        # Matérias
        fig_materias = px.bar(
            iniciais_df['MATÉRIA'].value_counts(),
            title='Distribuição por Matéria'
        )
        st.plotly_chart(fig_materias, use_container_width=True)

# Página: Audiências
elif pagina == "Audiências":
    st.header("👥 Gestão de Audiências")
    
    # Filtros
    audiencias_filtradas = filtrar_por_periodo(audiencias_df)
    
    # Filtro por tipo de audiência
    tipos_audiencia = st.sidebar.multiselect(
        "Filtrar por Tipo de Audiência",
        options=sorted(audiencias_df['TIPO DE AUDIÊNCIA'].unique())
    )
    if tipos_audiencia:
        audiencias_filtradas = audiencias_filtradas[
            audiencias_filtradas['TIPO DE AUDIÊNCIA'].isin(tipos_audiencia)
        ]
    
    # Filtro por responsável
    responsaveis = st.sidebar.multiselect(
        "Filtrar por Responsável",
        options=sorted(audiencias_df['RESPONSÁVEL'].unique())
    )
    if responsaveis:
        audiencias_filtradas = audiencias_filtradas[
            audiencias_filtradas['RESPONSÁVEL'].isin(responsaveis)
        ]
    
    # Preparar dados para exibição
    audiencias_display = audiencias_filtradas.copy()
    audiencias_display['DATA'] = audiencias_display['DATA'].dt.strftime('%d/%m/%Y')
    audiencias_display['HORÁRIO'] = pd.to_datetime(
        audiencias_display['HORÁRIO'], format='mixed', errors='coerce'
    ).dt.strftime('%H:%M')
    
    # Exibir tabela
    st.dataframe(
        audiencias_display,
        hide_index=True,
        use_container_width=True
    )
    
    # Calendário de audiências
    if not audiencias_filtradas.empty:
        st.subheader("📅 Calendário de Audiências")
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=audiencias_filtradas['DATA'],
            y=audiencias_filtradas['Nº DO PROCESSO'],
            mode='markers+text',
            marker=dict(
                size=12,
                symbol='circle',
                color=audiencias_filtradas['TIPO DE AUDIÊNCIA'].astype('category').cat.codes,
                colorscale='Viridis'
            ),
            text=audiencias_filtradas['TIPO DE AUDIÊNCIA'],
            textposition='top center'
        ))
        
        fig.update_layout(
            height=max(400, len(audiencias_filtradas) * 30),
            showlegend=False,
            xaxis_title="Data",
            yaxis_title="Processo",
            xaxis=dict(
                type='date',
                tickformat='%d/%m/%Y'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Página: Iniciais
else:
    st.header("📝 Gestão de Processos Iniciais")
    
    # Filtros
    processos_filtrados = filtrar_por_periodo(iniciais_df)
    
    # Filtro por matéria
    materias = st.sidebar.multiselect(
        "Filtrar por Matéria",
        options=sorted(iniciais_df['MATÉRIA'].unique())
    )
    if materias:
        processos_filtrados = processos_filtrados[
            processos_filtrados['MATÉRIA'].isin(materias)
        ]
    
    # Filtro por responsável
    responsaveis = st.sidebar.multiselect(
        "Filtrar por Responsável",
        options=sorted(iniciais_df['RESPONSÁVEL'].unique())
    )
    if responsaveis:
        processos_filtrados = processos_filtrados[
            processos_filtrados['RESPONSÁVEL'].isin(responsaveis)
        ]
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(processos_filtrados)
        st.metric("Total de Processos", total)
    
    with col2:
        distribuidos = len(processos_filtrados[processos_filtrados['DISTRIBUÍDO'] == 'Sim'])
        st.metric("Processos Distribuídos", distribuidos)
    
    with col3:
        protocolados = len(processos_filtrados[processos_filtrados['PROTOCOLADO'] == 'Sim'])
        st.metric("Processos Protocolados", protocolados)
    
    # Preparar dados para exibição
    processos_display = processos_filtrados.copy()
    processos_display['DATA'] = processos_display['DATA'].dt.strftime('%d/%m/%Y')
    processos_display['DATA DA ENTREGA'] = pd.to_datetime(
        processos_display['DATA DA ENTREGA'], errors='coerce'
    ).dt.strftime('%d/%m/%Y')
    processos_display['DATA DO PROTOCOLO'] = pd.to_datetime(
        processos_display['DATA DO PROTOCOLO'], errors='coerce'
    ).dt.strftime('%d/%m/%Y')
    
    # Exibir tabela
    st.dataframe(
        processos_display,
        hide_index=True,
        use_container_width=True
    )

# Estilo personalizado
st.markdown("""
    <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stDataFrame {
            margin-top: 25px;
            margin-bottom: 25px;
        }
        .stRadio > label {
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)
