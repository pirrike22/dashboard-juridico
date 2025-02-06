import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Dashboard Jurídico")

uploaded_file = st.file_uploader("Faça upload da planilha .xlsx", type=["xlsx"])

if uploaded_file is not None:
    def load_data(file):
        xls = pd.ExcelFile(file)
        prazos_df = pd.read_excel(xls, sheet_name="Prazos", dtype=str, header=1)
        audiencias_df = pd.read_excel(xls, sheet_name="Audiências", dtype=str, header=0)
        iniciais_df = pd.read_excel(xls, sheet_name="Iniciais", dtype=str, header=0)
        
        prazos_df = prazos_df.dropna(axis=1, how='all')
        audiencias_df = audiencias_df.dropna(axis=1, how='all')
        iniciais_df = iniciais_df.dropna(axis=1, how='all')
        
        return prazos_df, audiencias_df, iniciais_df

    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    # Ajustar as colunas de data para garantir que os filtros funcionem corretamente
    def adjust_date_columns(df, columns):
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    adjust_date_columns(prazos_df, ['DATA', 'DATA DE CIÊNCIA', 'DATA DA DELEGAÇÃO', 'PRAZO INTERNO (DEL.+5)', 'DATA DA ENTREGA'])
    adjust_date_columns(audiencias_df, ['DATA'])

    # Criar os intervalos de data para os filtros
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    next_week_start = end_of_week + timedelta(days=1)
    next_week_end = next_week_start + timedelta(days=6)
    next_15_days = now + timedelta(days=15)
    last_week_start = start_of_week - timedelta(days=7)
    last_week_end = start_of_week - timedelta(days=1)

    # Revisar os filtros para prazos
    def filter_prazos(df, filter_option):
        if filter_option == "Semana Passada":
            return df[(df['DATA'] >= last_week_start) & (df['DATA'] <= last_week_end)]
        elif filter_option == "Esta Semana":
            return df[(df['DATA'] >= start_of_week) & (df['DATA'] <= end_of_week)]
        elif filter_option == "Semana Seguinte":
            return df[(df['DATA'] >= next_week_start) & (df['DATA'] <= next_week_end)]
        elif filter_option == "Próximos 15 Dias":
            return df[(df['DATA'] <= next_15_days)]
        else:
            return df

    # Revisar os filtros para audiências
    def filter_audiencias(df, filter_option):
        if filter_option == "Semana Passada":
            return df[(df['DATA'] >= last_week_start) & (df['DATA'] <= last_week_end)]
        elif filter_option == "Esta Semana":
            return df[(df['DATA'] >= start_of_week) & (df['DATA'] <= end_of_week)]
        elif filter_option == "Semana Seguinte":
            return df[(df['DATA'] >= next_week_start) & (df['DATA'] <= next_week_end)]
        elif filter_option == "Próximos 15 Dias":
            return df[(df['DATA'] <= next_15_days)]
        else:
            return df

    # Adicionar filtro para tipo de audiência
    def filter_tipo_audiencia(df, tipo):
        if "TIPO DE AUDIÊNCIA" in df.columns:
            return df[df["TIPO DE AUDIÊNCIA"].str.contains(tipo, case=False, na=False)]
        return df

    # Filtros estratégicos
    st.sidebar.subheader("Filtros para Prazos")
    prazos_filter = st.sidebar.selectbox("Selecione o filtro para Prazos", ["Todos", "Semana Passada", "Esta Semana", "Semana Seguinte", "Próximos 15 Dias"])
    prazos_df = filter_prazos(prazos_df, prazos_filter)

    st.sidebar.subheader("Filtros para Audiências")
    audiencias_filter = st.sidebar.selectbox("Selecione o filtro para Audiências", ["Todos", "Semana Passada", "Esta Semana", "Semana Seguinte", "Próximos 15 Dias"])
    audiencias_df = filter_audiencias(audiencias_df, audiencias_filter)

    tipo_audiencia_filter = st.sidebar.text_input("Filtrar por Tipo de Audiência")
    if tipo_audiencia_filter:
        audiencias_df = filter_tipo_audiencia(audiencias_df, tipo_audiencia_filter)

    # Filtro de busca por cliente
    st.sidebar.subheader("Busca por Cliente")
    cliente_filter = st.sidebar.text_input("Digite o nome do cliente")
    if cliente_filter:
        if "CLIENTE" in prazos_df.columns:
            prazos_df = prazos_df[prazos_df["CLIENTE"].str.contains(cliente_filter, case=False, na=False)]
        if "RAZÃO SOCIAL" in audiencias_df.columns:
            audiencias_df = audiencias_df[audiencias_df["RAZÃO SOCIAL"].str.contains(cliente_filter, case=False, na=False)]

    # Exibição dos dados
    st.metric("Total de Prazos", len(prazos_df))
    st.metric("Total de Audiências", len(audiencias_df))

    st.subheader("Prazos")
    st.dataframe(prazos_df)

    st.subheader("Audiências")
    st.dataframe(audiencias_df)

    st.subheader("Iniciais")
    st.dataframe(iniciais_df)

    st.sidebar.markdown("**Atualize a planilha para visualizar novos dados**")
