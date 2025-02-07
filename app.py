import streamlit as st
import pandas as pd
import numpy as np

# Função para carregar os dados do arquivo Excel
def load_data(file):
    xls = pd.ExcelFile(file)
    
    prazos_data = xls.parse('Prazos')
    audiencias_data = xls.parse('Audiências')
    compliance_data = xls.parse('Compliance')
    iniciais_data = xls.parse('Iniciais')
    
    return prazos_data, audiencias_data, compliance_data, iniciais_data

# Carregando o arquivo Excel
st.title('Dashboard Jurídico')
file = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

if file:
    prazos, audiencias, compliance, iniciais = load_data(file)
    st.success('Dados carregados com sucesso!')

    # Verificar se as colunas necessárias existem antes de aplicar filtros
    required_columns_prazos = ['Data do Prazo', 'Complexidade', 'Responsável', 'Status de Protocolo', 'Cliente']
    required_columns_audiencias = ['Cliente', 'Data', 'Tipo de Audiência', 'Responsável', 'Parte Adversa', 'Testemunha']
    required_columns_compliance = ['Cliente', 'Status do Checklist', 'Data de Entrada', 'Status de Resolução']
    required_columns_iniciais = ['Cliente', 'Data da Entrega', 'Responsável', 'Status']

    # Aba Prazos
    st.header("Prazos")
    if all(col in prazos.columns for col in required_columns_prazos):
        cliente_selecionado = st.text_input("Buscar por cliente:", "")
        if cliente_selecionado:
            prazos = prazos[prazos['Cliente'].str.contains(cliente_selecionado, na=False, case=False)]

        prazo_periodo = st.selectbox("Filtrar por período dos prazos:", ["Próximos 7 dias", "Próximos 15 dias", "Próximos 30 dias"])
        if prazo_periodo == "Próximos 7 dias":
            prazos = prazos[prazos['Data do Prazo'] <= pd.Timestamp.now() + pd.Timedelta(days=7)]
        elif prazo_periodo == "Próximos 15 dias":
            prazos = prazos[prazos['Data do Prazo'] <= pd.Timestamp.now() + pd.Timedelta(days=15)]
        elif prazo_periodo == "Próximos 30 dias":
            prazos = prazos[prazos['Data do Prazo'] <= pd.Timestamp.now() + pd.Timedelta(days=30)]

        complexidade = st.multiselect("Filtrar por complexidade:", options=prazos['Complexidade'].unique())
        if complexidade:
            prazos = prazos[prazos['Complexidade'].isin(complexidade)]

        responsavel_prazos = st.multiselect("Filtrar por responsável:", options=prazos['Responsável'].unique())
        if responsavel_prazos:
            prazos = prazos[prazos['Responsável'].isin(responsavel_prazos)]

        protocolo_status = st.multiselect("Filtrar por status de protocolo:", options=prazos['Status de Protocolo'].unique())
        if protocolo_status:
            prazos = prazos[prazos['Status de Protocolo'].isin(protocolo_status)]

        cliente_prazos = st.multiselect("Filtrar por cliente:", options=prazos['Cliente'].unique())
        if cliente_prazos:
            prazos = prazos[prazos['Cliente'].isin(cliente_prazos)]

        st.dataframe(prazos)
    else:
        st.error("A aba 'Prazos' não possui as colunas necessárias.")

    # Aba Audiências
    st.header("Audiências")
    if all(col in audiencias.columns for col in required_columns_audiencias):
        if cliente_selecionado:
            audiencias = audiencias[audiencias['Cliente'].str.contains(cliente_selecionado, na=False, case=False)]

        audiencia_data = st.date_input("Filtrar por data de audiências:")
        if audiencia_data:
            audiencias = audiencias[audiencias['Data'] == pd.Timestamp(audiencia_data)]

        cliente_audiencia = st.multiselect("Filtrar por cliente:", options=audiencias['Cliente'].unique())
        if cliente_audiencia:
            audiencias = audiencias[audiencias['Cliente'].isin(cliente_audiencia)]

        tipo_audiencia = st.multiselect("Filtrar por tipo de audiência:", options=audiencias['Tipo de Audiência'].unique())
        if tipo_audiencia:
            audiencias = audiencias[audiencias['Tipo de Audiência'].isin(tipo_audiencia)]

        responsavel_audiencias = st.multiselect("Filtrar por responsável:", options=audiencias['Responsável'].unique())
        if responsavel_audiencias:
            audiencias = audiencias[audiencias['Responsável'].isin(responsavel_audiencias)]

        parte_adversa = st.multiselect("Filtrar por parte adversa:", options=audiencias['Parte Adversa'].unique())
        if parte_adversa:
            audiencias = audiencias[audiencias['Parte Adversa'].isin(parte_adversa)]

        testemunhas = st.selectbox("Testemunha na agenda:", ["Confirmada", "Pendente"])
        if testemunhas:
            audiencias = audiencias[audiencias['Testemunha'] == testemunhas]

        st.dataframe(audiencias)
    else:
        st.error("A aba 'Audiências' não possui as colunas necessárias.")

    # Aba Compliance
    st.header("Compliance")
    if all(col in compliance.columns for col in required_columns_compliance):
        if cliente_selecionado:
            compliance = compliance[compliance['Cliente'].str.contains(cliente_selecionado, na=False, case=False)]

        checklist_status = st.multiselect("Filtrar por status do checklist:", options=compliance['Status do Checklist'].unique())
        if checklist_status:
            compliance = compliance[compliance['Status do Checklist'].isin(checklist_status)]

        data_entrada = st.date_input("Filtrar por data de entrada:")
        if data_entrada:
            compliance = compliance[compliance['Data de Entrada'] == pd.Timestamp(data_entrada)]

        resolucao_status = st.multiselect("Filtrar por status de resolução:", options=compliance['Status de Resolução'].unique())
        if resolucao_status:
            compliance = compliance[compliance['Status de Resolução'].isin(resolucao_status)]

        cliente_compliance = st.multiselect("Filtrar por cliente:", options=compliance['Cliente'].unique())
        if cliente_compliance:
            compliance = compliance[compliance['Cliente'].isin(cliente_compliance)]

        st.dataframe(compliance)
    else:
        st.error("A aba 'Compliance' não possui as colunas necessárias.")

    # Aba Iniciais
    st.header("Iniciais")
    if all(col in iniciais.columns for col in required_columns_iniciais):
        if cliente_selecionado:
            iniciais = iniciais[iniciais['Cliente'].str.contains(cliente_selecionado, na=False, case=False)]

        data_entrega = st.date_input("Filtrar por data da entrega:")
        if data_entrega:
            iniciais = iniciais[iniciais['Data da Entrega'] == pd.Timestamp(data_entrega)]

        responsavel_iniciais = st.multiselect("Filtrar por responsável:", options=iniciais['Responsável'].unique())
        if responsavel_iniciais:
            iniciais = iniciais[iniciais['Responsável'].isin(responsavel_iniciais)]

        status_iniciais = st.multiselect("Filtrar por status:", options=iniciais['Status'].unique())
        if status_iniciais:
            iniciais = iniciais[iniciais['Status'].isin(status_iniciais)]

        cliente_iniciais = st.multiselect("Filtrar por cliente:", options=iniciais['Cliente'].unique())
        if cliente_iniciais:
            iniciais = iniciais[iniciais['Cliente'].isin(cliente_iniciais)]

        st.dataframe(iniciais)
    else:
        st.error("A aba 'Iniciais' não possui as colunas necessárias.")
