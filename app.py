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

    # Converter colunas que possuem datas para o formato dia/mês/ano
    for df in [prazos_data, audiencias_data, compliance_data, iniciais_data]:
        for col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y')
            except Exception:
                pass

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
    prazo_periodo = st.selectbox("Filtrar por período dos prazos:", ["Todos", "Próximos 7 dias", "Próximos 15 dias", "Próximos 30 dias"], key="prazo_periodo")
    complexidade = st.multiselect("Filtrar por complexidade:", options=prazos['Coluna_2'].unique(), key="complexidade")
    responsavel_prazos = st.multiselect("Filtrar por responsável:", options=prazos['Coluna_3'].unique(), key="responsavel_prazos")
    protocolo_status = st.multiselect("Filtrar por status de protocolo:", options=prazos['Coluna_4'].unique(), key="protocolo_status")
    cliente_prazos = st.multiselect("Filtrar por cliente:", options=prazos['Coluna_5'].unique(), key="cliente_prazos")

    # Aplicar filtros em Prazos
    if prazo_periodo != "Todos":
        days = int(prazo_periodo.split()[1])
        prazos['Coluna_1'] = pd.to_datetime(prazos['Coluna_1'], format='%d/%m/%Y', errors='coerce')
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
    audiencia_data = st.date_input("Filtrar por data de audiências:", key="audiencia_data")
    cliente_audiencia = st.multiselect("Filtrar por cliente:", options=audiencias['razão social'].unique(), key="cliente_audiencia")
    tipo_audiencia = st.multiselect("Filtrar por tipo de audiência:", options=audiencias['tipo de audiência'].unique(), key="tipo_audiencia")
    responsavel_audiencias = st.multiselect("Filtrar por responsável:", options=audiencias['responsável'].unique(), key="responsavel_audiencias")
    parte_adversa = st.multiselect("Filtrar por parte adversa:", options=audiencias['parte adversa'].unique(), key="parte_adversa")
    testemunhas = st.selectbox("Testemunha na agenda:", ["Todos", "Confirmada", "Pendente"], key="testemunhas")

    # Aplicar filtros em Audiências
    if audiencia_data:
        audiencias['data'] = pd.to_datetime(audiencias['data'], format='%d/%m/%Y', errors='coerce')
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
