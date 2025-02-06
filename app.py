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
        
        # Ajustar colunas para a aba 'Prazos'
        prazos_df.columns = prazos_df.iloc[0]  # Definir a primeira linha como cabeçalho
        prazos_df = prazos_df[1:].reset_index(drop=True)  # Remover a linha de cabeçalho duplicada
        
        return prazos_df, audiencias_df, iniciais_df

    # Carregar os dados
    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    # Garantir que colunas de data sejam convertidas corretamente
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
    responsavel = st.sidebar.multiselect("Filtrar por responsável", prazos_df["RESPONSÁVEL"].dropna().unique() if "RESPONSÁVEL" in prazos_df.columns else [])
    complexidade = st.sidebar.multiselect("Filtrar por complexidade", prazos_df["COMPLEXIDADE"].dropna().unique() if "COMPLEXIDADE" in prazos_df.columns else [])
    status = st.sidebar.multiselect("Filtrar por status", prazos_df["PROTOCOLADO?"].dropna().unique() if "PROTOCOLADO?" in prazos_df.columns else [])
    tipo_audiencia = st.sidebar.multiselect("Filtrar por tipo de audiência", audiencias_df["TIPO DE AUDIÊNCIA"].dropna().unique() if "TIPO DE AUDIÊNCIA" in audiencias_df.columns else [])
    cliente = st.sidebar.text_input("Buscar por cliente")

    # Filtro de prazos e audiências por período
    periodo = st.sidebar.radio("Filtrar por período", ["Esta semana", "Semana seguinte", "Próximos 15 dias", "Todos"])

    # Aplicar filtros
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

    if "RESPONSÁVEL" in prazos_df.columns and responsavel:
        prazos_df = prazos_df[prazos_df["RESPONSÁVEL"].isin(responsavel)]
    if "COMPLEXIDADE" in prazos_df.columns and complexidade:
        prazos_df = prazos_df[prazos_df["COMPLEXIDADE"].isin(complexidade)]
    if "PROTOCOLADO?" in prazos_df.columns and status:
        prazos_df = prazos_df[prazos_df["PROTOCOLADO?"].isin(status)]
    if "TIPO DE AUDIÊNCIA" in audiencias_df.columns and tipo_audiencia:
        audiencias_df = audiencias_df[audiencias_df["TIPO DE AUDIÊNCIA"].isin(tipo_audiencia)]
    if cliente:
        if "CLIENTE" in prazos_df.columns:
            prazos_df = prazos_df[prazos_df["CLIENTE"].astype(str).str.contains(cliente, na=False, case=False)]
        if "RAZÃO SOCIAL" in audiencias_df.columns:
            audiencias_df = audiencias_df[audiencias_df["RAZÃO SOCIAL"].astype(str).str.contains(cliente, na=False, case=False)]
        if "Cliente" in iniciais_df.columns:
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

