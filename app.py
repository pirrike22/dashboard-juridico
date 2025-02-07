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
    prazo_periodo = st.selectbox("Filtrar por período dos prazos:", ["Todos", "Próximos 7 dias", "Próximos 15 dias", "Próximos 30 dias"], key="prazo_periodo")
    cliente_prazos = st.multiselect("Filtrar por cliente:", options=prazos['cliente'].unique(), key="cliente_prazos")

    # Aplicar filtros em Prazos
    if prazo_periodo != "Todos":
        days = int(prazo_periodo.split()[1])
        prazos['data'] = pd.to_datetime(prazos['data'], errors='coerce')
        prazos = prazos[prazos['data'] <= pd.Timestamp.now() + pd.Timedelta(days=days)]
    if cliente_prazos:
        prazos = prazos[prazos['cliente'].isin(cliente_prazos)]

    st.dataframe(prazos)

    # Filtros para Audiências
    st.header("Filtros para Audiências")
    audiencia_data = st.date_input("Filtrar por data de audiências:", key="audiencia_data")
    cliente_audiencia = st.multiselect("Filtrar por cliente:", options=audiencias['razão social'].unique(), key="cliente_audiencia")

    # Aplicar filtros em Audiências
    if audiencia_data:
        audiencias['data'] = pd.to_datetime(audiencias['data'], errors='coerce')
        audiencias = audiencias[audiencias['data'] == pd.Timestamp(audiencia_data)]
    if cliente_audiencia:
        audiencias = audiencias[audiencias['razão social'].isin(cliente_audiencia)]

    st.dataframe(audiencias)

    # Exibir abas para Compliance e Iniciais
    st.header("Compliance")
    st.dataframe(compliance)

    st.header("Iniciais")
    st.dataframe(iniciais)
