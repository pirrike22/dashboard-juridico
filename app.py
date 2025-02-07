import streamlit as st
import pandas as pd

# Função para carregar os dados do arquivo Excel
def load_data(file):
    xls = pd.ExcelFile(file)

    # Ajustar os nomes das abas e colunas conforme necessário
    prazos_data = xls.parse('Prazos', header=None)  # Sem cabeçalho
    audiencias_data = xls.parse('Audiências')
    compliance_data = xls.parse('Compliance')
    iniciais_data = xls.parse('Iniciais')

    # Renomear colunas para padronizar
    prazos_data.columns = [f'Coluna_{i}' for i in range(prazos_data.shape[1])]
    audiencias_data.columns = audiencias_data.columns.str.strip().str.lower()
    compliance_data.columns = compliance_data.columns.str.strip().str.lower()
    iniciais_data.columns = iniciais_data.columns.str.strip().str.lower()

    return prazos_data, audiencias_data, compliance_data, iniciais_data

# Carregando o arquivo Excel
st.title('Dashboard Jurídico')
file = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

if file:
    prazos, audiencias, compliance, iniciais = load_data(file)
    st.success('Dados carregados com sucesso!')

    # Tela principal com filtros e contadores
    st.header("Resumo Geral")

    # Filtros para Prazos
    st.subheader("Filtros para Prazos")
    prazo_periodo = st.selectbox("Filtrar por período dos prazos:", ["Todos", "Próximos 7 dias", "Próximos 15 dias", "Próximos 30 dias"])
    complexidade = st.multiselect("Filtrar por complexidade:", options=prazos['Coluna_2'].unique())
    responsavel_prazos = st.multiselect("Filtrar por responsável:", options=prazos['Coluna_3'].unique())
    protocolo_status = st.multiselect("Filtrar por status de protocolo:", options=prazos['Coluna_4'].unique())
    cliente_prazos = st.multiselect("Filtrar por cliente:", options=prazos['Coluna_5'].unique())

    # Aplicar filtros em Prazos
    if prazo_periodo != "Todos":
        days = int(prazo_periodo.split()[1])
        prazos = prazos[prazos['Coluna_1'] <= pd.Timestamp.now() + pd.Timedelta(days=days)]
    if complexidade:
        prazos = prazos[prazos['Coluna_2'].isin(complexidade)]
    if responsavel_prazos:
        prazos = prazos[prazos['Coluna_3'].isin(responsavel_prazos)]
    if protocolo_status:
        prazos = prazos[prazos['Coluna_4'].isin(protocolo_status)]
    if cliente_prazos:
        prazos = prazos[prazos['Coluna_5'].isin(cliente_prazos)]

    st.write(f"Número de Prazos: {len(prazos)}")

    # Filtros para Audiências
    st.subheader("Filtros para Audiências")
    audiencia_data = st.date_input("Filtrar por data de audiências:")
    cliente_audiencia = st.multiselect("Filtrar por cliente:", options=audiencias['razão social'].unique())
    tipo_audiencia = st.multiselect("Filtrar por tipo de audiência:", options=audiencias['tipo de audiência'].unique())
    responsavel_audiencias = st.multiselect("Filtrar por responsável:", options=audiencias['responsável'].unique())
    parte_adversa = st.multiselect("Filtrar por parte adversa:", options=audiencias['parte adversa'].unique())
    testemunhas = st.selectbox("Testemunha na agenda:", ["Todos", "Confirmada", "Pendente"])

    # Aplicar filtros em Audiências
    if audiencia_data:
        audiencias = audiencias[audiencias['data'] == pd.Timestamp(audiencia_data)]
    if cliente_audiencia:
        audiencias = audiencias[audiencias['razão social'].isin(cliente_audiencia)]
    if tipo_audiencia:
        audiencias = audiencias[audiencias['tipo de audiência'].isin(tipo_audiencia)]
    if responsavel_audiencias:
        audiencias = audiencias[audiencias['responsável'].isin(responsavel_audiencias)]
    if parte_adversa:
        audiencias = audiencias[audiencias['parte adversa'].isin(parte_adversa)]
    if testemunhas != "Todos":
        audiencias = audiencias[audiencias['testemunha'] == testemunhas]

    st.write(f"Número de Audiências: {len(audiencias)}")

    # Exibir tabelas filtradas
    st.header("Dados Filtrados")
    st.subheader("Prazos")
    st.dataframe(prazos)

    st.subheader("Audiências")
    st.dataframe(audiencias)
