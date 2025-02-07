import streamlit as st
import pandas as pd

# Função para carregar os dados do arquivo Excel
def load_data(file):
    xls = pd.ExcelFile(file)

    # Ajustar os nomes das abas e colunas conforme necessário
    prazos_data = xls.parse('Prazos', header=1)  # Cabeçalho na segunda linha
    audiencias_data = xls.parse('Audiências', header=0)
    compliance_data = xls.parse('Compliance', header=0)
    iniciais_data = xls.parse('Iniciais', header=0)

    # Renomear colunas para padronizar
    prazos_data.columns = prazos_data.columns.str.strip().str.lower()
    audiencias_data.columns = audiencias_data.columns.str.strip().str.lower()
    compliance_data.columns = compliance_data.columns.str.strip().str.lower()
    iniciais_data.columns = iniciais_data.columns.str.strip().str.lower()

    # Converter colunas que possuem datas para o formato dia/mês/ano
    for df in [prazos_data, audiencias_data, compliance_data, iniciais_data]:
        for col in df.columns:
            if 'data' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y')

    return prazos_data, audiencias_data, compliance_data, iniciais_data

# Carregando o arquivo Excel
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")
st.title('Dashboard Jurídico')
file = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

if file:
    prazos, audiencias, compliance, iniciais = load_data(file)
    st.success('Dados carregados com sucesso!')

    # Layout do dashboard
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Número de Prazos")
        st.metric(label="Total de Prazos", value=len(prazos))

    with col2:
        st.subheader("Número de Audiências")
        st.metric(label="Total de Audiências", value=len(audiencias))

    # Filtros para Prazos
    st.header("Filtros para Prazos")
    prazo_periodo = st.selectbox("Filtrar por período dos prazos:", ["Todos", "Semana Passada", "Essa Semana", "Próximos 7 dias", "Próximos 15 dias", "Esse Mês"], key="prazo_periodo")
    cliente_prazos = st.multiselect("Filtrar por cliente:", options=prazos['cliente'].unique(), key="cliente_prazos")

    # Aplicar filtros em Prazos
    if prazo_periodo != "Todos":
        prazos['data'] = pd.to_datetime(prazos['data'], format='%d/%m/%Y', errors='coerce')
        today = pd.Timestamp.now()
        start_of_week = today - pd.Timedelta(days=today.weekday())
        end_of_week = start_of_week + pd.Timedelta(days=4)

        if prazo_periodo == "Semana Passada":
            start = start_of_week - pd.Timedelta(days=7)
            end = start_of_week - pd.Timedelta(days=1)
            prazos = prazos[(prazos['data'] >= start) & (prazos['data'] <= end)]
        elif prazo_periodo == "Essa Semana":
            prazos = prazos[(prazos['data'] >= start_of_week) & (prazos['data'] <= end_of_week)]
        elif prazo_periodo == "Próximos 7 dias":
            prazos = prazos[(prazos['data'] >= today) & (prazos['data'] <= today + pd.Timedelta(days=7))]
        elif prazo_periodo == "Próximos 15 dias":
            prazos = prazos[(prazos['data'] >= today) & (prazos['data'] <= today + pd.Timedelta(days=15))]
        elif prazo_periodo == "Esse Mês":
            prazos = prazos[prazos['data'].dt.month == today.month]

    if cliente_prazos:
        prazos = prazos[prazos['cliente'].isin(cliente_prazos)]

    st.dataframe(prazos)

    # Filtros para Audiências
    st.header("Filtros para Audiências")
    audiencia_periodo = st.selectbox("Filtrar por período das audiências:", ["Todos", "Semana Passada", "Essa Semana", "Próximos 7 dias", "Próximos 15 dias", "Esse Mês"], key="audiencia_periodo")
    cliente_audiencia = st.multiselect("Filtrar por cliente:", options=audiencias['razão social'].unique(), key="cliente_audiencia")

    # Aplicar filtros em Audiências
    if audiencia_periodo != "Todos":
        audiencias['data'] = pd.to_datetime(audiencias['data'], format='%d/%m/%Y', errors='coerce')

        if audiencia_periodo == "Semana Passada":
            start = start_of_week - pd.Timedelta(days=7)
            end = start_of_week - pd.Timedelta(days=1)
            audiencias = audiencias[(audiencias['data'] >= start) & (audiencias['data'] <= end)]
        elif audiencia_periodo == "Essa Semana":
            audiencias = audiencias[(audiencias['data'] >= start_of_week) & (audiencias['data'] <= end_of_week)]
        elif audiencia_periodo == "Próximos 7 dias":
            audiencias = audiencias[(audiencias['data'] >= today) & (audiencias['data'] <= today + pd.Timedelta(days=7))]
        elif audiencia_periodo == "Próximos 15 dias":
            audiencias = audiencias[(audiencias['data'] >= today) & (audiencias['data'] <= today + pd.Timedelta(days=15))]
        elif audiencia_periodo == "Esse Mês":
            audiencias = audiencias[audiencias['data'].dt.month == today.month]

    if cliente_audiencia:
        audiencias = audiencias[audiencias['razão social'].isin(cliente_audiencia)]

    st.dataframe(audiencias)

    # Exibir abas para Compliance e Iniciais
    st.header("Compliance")
    st.dataframe(compliance)

    st.header("Iniciais")
    st.dataframe(iniciais)
