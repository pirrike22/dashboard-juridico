import streamlit as st
import pandas as pd
import datetime

def load_data(sheet_url):
    csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv")
    return pd.read_csv(csv_url)

# URL pública do Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM5Oq6McjWFTDbUTbimMJfcnB2J1Oiy-_UY-VnDcnxE/edit?usp=sharing"

# Carregar dados
prazos_df = load_data(SHEET_URL)
audiencias_df = load_data(SHEET_URL)
iniciais_df = load_data(SHEET_URL)

# Converter datas para datetime
prazos_df['Data'] = pd.to_datetime(prazos_df['Data'], errors='coerce')
audiencias_df['Data'] = pd.to_datetime(audiencias_df['Data'], errors='coerce')

# Criar filtros de tempo
hoje = datetime.date.today()
semana_atual = hoje + datetime.timedelta(days=(6-hoje.weekday()))
semana_seguinte = semana_atual + datetime.timedelta(days=7)
quinze_dias = hoje + datetime.timedelta(days=15)

# Filtros estratégicos
st.sidebar.header("Filtros Estratégicos")
filtro_tipo = st.sidebar.multiselect("Tipo de Demanda", prazos_df['Tipo'].unique())
filtro_cliente = st.sidebar.multiselect("Cliente", prazos_df['Cliente'].unique())
filtro_advogado = st.sidebar.multiselect("Advogado", prazos_df['Advogado'].unique())
filtro_status = st.sidebar.multiselect("Status", prazos_df['Status'].unique())
filtro_prioridade = st.sidebar.multiselect("Prioridade", prazos_df['Prioridade'].unique())

# Aplicando os filtros aos DataFrames
if filtro_tipo:
    prazos_df = prazos_df[prazos_df['Tipo'].isin(filtro_tipo)]
if filtro_cliente:
    prazos_df = prazos_df[prazos_df['Cliente'].isin(filtro_cliente)]
if filtro_advogado:
    prazos_df = prazos_df[prazos_df['Advogado'].isin(filtro_advogado)]
if filtro_status:
    prazos_df = prazos_df[prazos_df['Status'].isin(filtro_status)]
if filtro_prioridade:
    prazos_df = prazos_df[prazos_df['Prioridade'].isin(filtro_prioridade)]

# Filtros de tempo
st.sidebar.header("Filtrar por Data")
opcao_tempo = st.sidebar.radio("Selecione um período", ["Esta Semana", "Próxima Semana", "Próximos 15 Dias", "Todos"])

if opcao_tempo == "Esta Semana":
    prazos_df = prazos_df[prazos_df['Data'] <= pd.to_datetime(semana_atual)]
    audiencias_df = audiencias_df[audiencias_df['Data'] <= pd.to_datetime(semana_atual)]
elif opcao_tempo == "Próxima Semana":
    prazos_df = prazos_df[(prazos_df['Data'] > pd.to_datetime(semana_atual)) & (prazos_df['Data'] <= pd.to_datetime(semana_seguinte))]
    audiencias_df = audiencias_df[(audiencias_df['Data'] > pd.to_datetime(semana_atual)) & (audiencias_df['Data'] <= pd.to_datetime(semana_seguinte))]
elif opcao_tempo == "Próximos 15 Dias":
    prazos_df = prazos_df[prazos_df['Data'] <= pd.to_datetime(quinze_dias)]
    audiencias_df = audiencias_df[audiencias_df['Data'] <= pd.to_datetime(quinze_dias)]

# Exibir tabelas filtradas
st.header("Prazos")
st.dataframe(prazos_df)

st.header("Audiências")
st.dataframe(audiencias_df)

st.header("Iniciais")
st.dataframe(iniciais_df)
