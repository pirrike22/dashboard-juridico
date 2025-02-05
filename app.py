import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração inicial
st.set_page_config(page_title="Gestão Jurídica", layout="wide")

# Função para carregar dados
@st.cache_data
def load_data():
    # Substitua pela URL raw do seu arquivo no GitHub
    url = "URL_DO_SEU_ARQUIVO_XLSX_NO_GITHUB_RAW"
    
    sheets = {
        'Prazos': {'sheet_name': 'Prazos', 'usecols': 'A:N'},
        'Audiências': {'sheet_name': 'Audiências', 'usecols': 'A:N'},
        'Iniciais': {'sheet_name': 'Iniciais', 'usecols': 'A:L'}
    }
    
    dfs = {}
    for name, params in sheets.items():
        dfs[name] = pd.read_excel(url, **params)
        dfs[name]['DATA'] = pd.to_datetime(dfs[name]['DATA'], errors='coerce')
    
    return dfs

dfs = load_data()

# Sidebar com filtros globais
st.sidebar.header("Filtros Globais")

# Filtros comuns
selected_responsavel = st.sidebar.multiselect(
    'Selecione o Responsável:',
    options=pd.concat([dfs['Prazos']['RESPONSÁVEL'], dfs['Audiências']['RESPONSÁVEL']]).unique()
)

# Filtros de período
periodo_options = ['Esta semana', 'Próxima semana', 'Próximos 15 dias']
selected_period = st.sidebar.selectbox('Selecione o período:', periodo_options)

# Funções de filtragem
def filter_by_period(df, date_column):
    today = datetime.today()
    
    if selected_period == 'Esta semana':
        start_date = today
        end_date = today + timedelta(days=7)
    elif selected_period == 'Próxima semana':
        start_date = today + timedelta(days=7)
        end_date = today + timedelta(days=14)
    else:
        start_date = today
        end_date = today + timedelta(days=15)
        
    return df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

# Página principal
st.title("Dashboard de Gestão Jurídica")

# Abas para diferentes seções
tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Processos Iniciais"])

with tab1:
    st.header("Gestão de Prazos")
    
    # Filtros específicos
    col1, col2 = st.columns(2)
    with col1:
        selected_cliente_prazos = st.multiselect(
            'Clientes (Prazos):',
            options=dfs['Prazos']['CLIENTE'].unique()
        )
    
    with col2:
        selected_status = st.multiselect(
            'Status do Protocolo:',
            options=dfs['Prazos']['PROTOCOLADO?'].unique()
        )
    
    # Aplicar filtros
    filtered_prazos = dfs['Prazos']
    if selected_responsavel:
        filtered_prazos = filtered_prazos[filtered_prazos['RESPONSÁVEL'].isin(selected_responsavel)]
    if selected_cliente_prazos:
        filtered_prazos = filtered_prazos[filtered_prazos['CLIENTE'].isin(selected_cliente_prazos)]
    if selected_status:
        filtered_prazos = filtered_prazos[filtered_prazos['PROTOCOLADO?'].isin(selected_status)]
    
    filtered_prazos = filter_by_period(filtered_prazos, 'DATA (D-1)')
    
    # Exibir dados
    st.dataframe(
        filtered_prazos.sort_values('DATA (D-1)'),
        use_container_width=True,
        column_config={
            "DATA (D-1)": "Data Limite",
            "PROCESSO": "Nº Processo",
            "TAREFA": "Tipo de Tarefa"
        }
    )

with tab2:
    st.header("Gestão de Audiências")
    
    # Filtros específicos
    col1, col2 = st.columns(2)
    with col1:
        selected_tipo = st.multiselect(
            'Tipo de Audiência:',
            options=dfs['Audiências']['TIPO DE AUDIÊNCIA'].unique()
        )
    
    # Aplicar filtros
    filtered_audiencias = dfs['Audiências']
    if selected_responsavel:
        filtered_audiencias = filtered_audiencias[filtered_audiencias['RESPONSÁVEL'].isin(selected_responsavel)]
    if selected_tipo:
        filtered_audiencias = filtered_audiencias[filtered_audiencias['TIPO DE AUDIÊNCIA'].isin(selected_tipo)]
    
    filtered_audiencias = filter_by_period(filtered_audiencias, 'DATA')
    
    # Exibir dados
    st.dataframe(
        filtered_audiencias.sort_values('DATA'),
        use_container_width=True,
        column_config={
            "DATA": "Data",
            "HORÁRIO": "Horário",
            "Nº DO PROCESSO": "Processo",
            "PARTE ADVERSA": "Parte Adversa"
        }
    )

with tab3:
    st.header("Processos Iniciais")
    
    # Filtros específicos
    col1, col2 = st.columns(2)
    with col1:
        selected_status_inicial = st.multiselect(
            'Status do Processo:',
            options=dfs['Iniciais']['LIBERADO PARA PROTOCOLO'].unique()
        )
    
    # Aplicar filtros
    filtered_iniciais = dfs['Iniciais']
    if selected_responsavel:
        filtered_iniciais = filtered_iniciais[filtered_iniciais['RESPONSÁVEL'].isin(selected_responsavel)]
    if selected_status_inicial:
        filtered_iniciais = filtered_iniciais[filtered_iniciais['LIBERADO PARA PROTOCOLO'].isin(selected_status_inicial)]
    
    # Exibir dados
    st.dataframe(
        filtered_iniciais,
        use_container_width=True,
        column_config={
            "DATA": "Data de Abertura",
            "CLIENTE": "Cliente",
            "MATÉRIA": "Matéria Jurídica"
        }
    )

# Rodapé com estatísticas
st.sidebar.markdown("---")
st.sidebar.subheader("Estatísticas Gerais")
st.sidebar.metric("Total de Prazos", len(dfs['Prazos']))
st.sidebar.metric("Audiências Agendadas", len(dfs['Audiências']))
st.sidebar.metric("Processos Iniciais", len(dfs['Iniciais']))
