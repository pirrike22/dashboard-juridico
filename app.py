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
        prazos_df = pd.read_excel(xls, sheet_name="Prazos", dtype=str)
        audiencias_df = pd.read_excel(xls, sheet_name="Audiências", dtype=str)
        iniciais_df = pd.read_excel(xls, sheet_name="Iniciais", dtype=str)
        
        # Ajustar colunas para a aba 'Prazos'
        prazos_df.columns = prazos_df.iloc[0]
        prazos_df = prazos_df[1:].reset_index(drop=True)
        
        return prazos_df, audiencias_df, iniciais_df

    # Carregar os dados
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    # Remover valores NaN e espaços extras
    prazos_df = prazos_df.applymap(lambda x: x.strip() if isinstance(x, str) else x).fillna("")
    audiencias_df = audiencias_df.applymap(lambda x: x.strip() if isinstance(x, str) else x).fillna("")
    iniciais_df = iniciais_df.applymap(lambda x: x.strip() if isinstance(x, str) else x).fillna("")

    # Converter colunas de data corretamente
    if "DATA" in prazos_df.columns:
        prazos_df["DATA"] = pd.to_datetime(prazos_df["DATA"], errors='coerce').dt.strftime("%d/%m/%Y")
    if "DATA" in audiencias_df.columns:
        audiencias_df["DATA"] = pd.to_datetime(audiencias_df["DATA"], errors='coerce').dt.strftime("%d/%m/%Y")
    if "HORÁRIO" in audiencias_df.columns:
        audiencias_df["HORÁRIO"] = pd.to_datetime(audiencias_df["HORÁRIO"], errors='coerce').dt.strftime("%H:%M").fillna('00:00')
    if "DATA" in iniciais_df.columns:
        iniciais_df["DATA"] = pd.to_datetime(iniciais_df["DATA"], errors='coerce').dt.strftime("%d/%m/%Y")

    # Definir período de filtragem
    hoje = datetime.today()
    semana_atual = (hoje, hoje + timedelta(days=7))
    semana_seguinte = (hoje + timedelta(days=7), hoje + timedelta(days=14))
    quinze_dias = (hoje, hoje + timedelta(days=15))

    # Filtros estratégicos
    st.sidebar.header("Filtros Estratégicos")
    responsavel = st.sidebar.multiselect("Filtrar por responsável", prazos_df.get("RESPONSÁVEL", pd.Series()).unique())
    complexidade = st.sidebar.multiselect("Filtrar por complexidade", prazos_df.get("COMPLEXIDADE", pd.Series()).unique())
    status = st.sidebar.multiselect("Filtrar por status", prazos_df.get("PROTOCOLADO?", pd.Series()).unique())
    tipo_audiencia = st.sidebar.multiselect("Filtrar por tipo de audiência", audiencias_df.get("TIPO DE AUDIÊNCIA", pd.Series()).unique())
    cliente = st.sidebar.text_input("Buscar por cliente")

    # Filtro de prazos e audiências por período
    periodo = st.sidebar.radio("Filtrar por período", ["Esta semana", "Semana seguinte", "Próximos 15 dias", "Todos"])

    def filter_by_period(df, column, period):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
            if period == "Esta semana":
                return df[(df[column] >= semana_atual[0]) & (df[column] <= semana_atual[1])]
            elif period == "Semana seguinte":
                return df[(df[column] >= semana_seguinte[0]) & (df[column] <= semana_seguinte[1])]
            elif period == "Próximos 15 dias":
                return df[(df[column] >= quinze_dias[0]) & (df[column] <= quinze_dias[1])]
        return df

    if "DATA" in prazos_df.columns:
        prazos_df = filter_by_period(prazos_df, "DATA", periodo)
    if "DATA" in audiencias_df.columns:
        audiencias_df = filter_by_period(audiencias_df, "DATA", periodo)

    if responsavel:
        prazos_df = prazos_df[prazos_df["RESPONSÁVEL"].isin(responsavel)]
    if complexidade:
        prazos_df = prazos_df[prazos_df["COMPLEXIDADE"].isin(complexidade)]
    if status:
        prazos_df = prazos_df[prazos_df["PROTOCOLADO?"].isin(status)]
    if tipo_audiencia:
        audiencias_df = audiencias_df[audiencias_df["TIPO DE AUDIÊNCIA"].isin(tipo_audiencia)]
    if cliente:
        prazos_df = prazos_df[prazos_df["CLIENTE"].astype(str).str.contains(cliente, na=False, case=False)]
        audiencias_df = audiencias_df[audiencias_df["RAZÃO SOCIAL"].astype(str).str.contains(cliente, na=False, case=False)]
        iniciais_df = iniciais_df[iniciais_df["Cliente"].astype(str).str.contains(cliente, na=False, case=False)]

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
