import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Criar o app
st.title("Dashboard Jurídico")

# Solicitar upload do arquivo
uploaded_file = st.file_uploader("Faça upload da planilha .xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Função para carregar os dados
    def load_data(file):
        xls = pd.ExcelFile(file)
        prazos_df = pd.read_excel(xls, sheet_name="Prazos")
        audiencias_df = pd.read_excel(xls, sheet_name="Audiências")
        iniciais_df = pd.read_excel(xls, sheet_name="Iniciais")
        return prazos_df, audiencias_df, iniciais_df

    # Carregar os dados
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    # Converter colunas de data para datetime
    prazos_df.iloc[:, 0] = pd.to_datetime(prazos_df.iloc[:, 0], errors='coerce').dt.strftime("%d/%m/%Y")
    audiencias_df.iloc[:, 0] = pd.to_datetime(audiencias_df.iloc[:, 0], errors='coerce').dt.strftime("%d/%m/%Y")
    audiencias_df.iloc[:, 1] = pd.to_datetime(audiencias_df.iloc[:, 1], errors='coerce').dt.strftime("%H:%M")
    iniciais_df.iloc[:, 0] = pd.to_datetime(iniciais_df.iloc[:, 0], errors='coerce').dt.strftime("%d/%m/%Y")

    # Definir período de filtragem
    hoje = datetime.today()
    semana_atual = (hoje, hoje + timedelta(days=7))
    semana_seguinte = (hoje + timedelta(days=7), hoje + timedelta(days=14))
    quinze_dias = (hoje, hoje + timedelta(days=15))

    # Filtros estratégicos
    st.sidebar.header("Filtros Estratégicos")
    responsavel = st.sidebar.multiselect("Filtrar por responsável", prazos_df.iloc[:, 4].dropna().unique())
    complexidade = st.sidebar.multiselect("Filtrar por complexidade", prazos_df.iloc[:, 9].dropna().unique())
    status = st.sidebar.multiselect("Filtrar por status", prazos_df.iloc[:, 11].dropna().unique())
    tipo_audiencia = st.sidebar.multiselect("Filtrar por tipo de audiência", audiencias_df.iloc[:, 7].dropna().unique())
    cliente = st.sidebar.text_input("Buscar por cliente")

    # Filtro de prazos e audiências por período
    periodo = st.sidebar.radio("Filtrar por período", ["Esta semana", "Semana seguinte", "Próximos 15 dias", "Todos"])

    # Aplicar filtros
    def filter_by_period(df, column, period):
        df[column] = pd.to_datetime(df[column], errors='coerce')
        if period == "Esta semana":
            return df[(df[column] >= semana_atual[0]) & (df[column] <= semana_atual[1])]
        elif period == "Semana seguinte":
            return df[(df[column] >= semana_seguinte[0]) & (df[column] <= semana_seguinte[1])]
        elif period == "Próximos 15 dias":
            return df[(df[column] >= quinze_dias[0]) & (df[column] <= quinze_dias[1])]
        return df

    prazos_df = filter_by_period(prazos_df, prazos_df.columns[0], periodo)
    audiencias_df = filter_by_period(audiencias_df, audiencias_df.columns[0], periodo)

    if not prazos_df.empty and responsavel:
        prazos_df = prazos_df[prazos_df.iloc[:, 4].isin(responsavel)]
    if not prazos_df.empty and complexidade:
        prazos_df = prazos_df[prazos_df.iloc[:, 9].isin(complexidade)]
    if not prazos_df.empty and status:
        prazos_df = prazos_df[prazos_df.iloc[:, 11].isin(status)]
    if not audiencias_df.empty and tipo_audiencia:
        audiencias_df = audiencias_df[audiencias_df.iloc[:, 7].isin(tipo_audiencia)]
    if cliente:
        prazos_df = prazos_df[prazos_df.iloc[:, 1].astype(str).str.contains(cliente, na=False, case=False)]
        audiencias_df = audiencias_df[audiencias_df.iloc[:, 2].astype(str).str.contains(cliente, na=False, case=False)]
        iniciais_df = iniciais_df[iniciais_df.iloc[:, 1].astype(str).str.contains(cliente, na=False, case=False)]

    # Exibir contadores
    st.metric("Total de Prazos", len(prazos_df))
    st.metric("Total de Audiências", len(audiencias_df))

    # Exibir tabelas
    st.subheader("Prazos")
    st.dataframe(prazos_df)

    st.subheader("Audiências")
    st.dataframe(audiencias_df)

    st.subheader("Iniciais")
    st.dataframe(iniciais_df)

    st.sidebar.markdown("**Atualize a planilha para visualizar novos dados**")

