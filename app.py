import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Dashboard Jurídico")

uploaded_file = st.file_uploader("Faça upload da planilha .xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Função para carregar as planilhas
    def load_data(file):
        xls = pd.ExcelFile(file)
        prazos_df = pd.read_excel(xls, sheet_name="Prazos", dtype=str, header=0)
        audiencias_df = pd.read_excel(xls, sheet_name="Audiências", dtype=str, header=0)
        iniciais_df = pd.read_excel(xls, sheet_name="Iniciais", dtype=str, header=0)
        
        # Remover colunas completamente vazias
        prazos_df = prazos_df.dropna(axis=1, how='all')
        audiencias_df = audiencias_df.dropna(axis=1, how='all')
        iniciais_df = iniciais_df.dropna(axis=1, how='all')
        
        return prazos_df, audiencias_df, iniciais_df

    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    #####################################
    # Correção da aba Prazos
    # Converter o campo "Unnamed: 0" para data (sem horário) no formato dd/mm/aaaa
    if "Unnamed: 0" in prazos_df.columns:
        prazos_df["Unnamed: 0"] = pd.to_datetime(
            prazos_df["Unnamed: 0"], 
            errors='coerce',
            dayfirst=True
        ).dt.strftime("%d/%m/%Y")
    
    #####################################
    # Processar coluna de horários na aba Audiências
    def normalize_time(time_str):
        if pd.isna(time_str) or str(time_str).strip() in ['', 'NaT']:
            return "00:00"
        time_str = str(time_str).strip().upper()
        # Converter formatos do tipo '14h00' para '14:00'
        time_str = time_str.replace('H', ':').replace('h', ':')
        # Se houver segundos, mantemos apenas horas e minutos
        if len(time_str.split(':')) > 2:
            time_str = ":".join(time_str.split(':')[:2])
        return time_str

    if "HORÁRIO" in audiencias_df.columns:
        audiencias_df["HORÁRIO"] = audiencias_df["HORÁRIO"].apply(normalize_time)
        audiencias_df["HORÁRIO"] = pd.to_datetime(
            audiencias_df["HORÁRIO"], 
            format='%H:%M', 
            errors='coerce'
        ).dt.strftime("%H:%M")

    #####################################
    # Converter outras colunas de data nas abas (exceto Prazos, que já foi tratado)
    date_columns = {
        'audiencias_df': ['DATA'],
        'iniciais_df': ['DATA']
    }

    for df_name, cols in date_columns.items():
        df = locals()[df_name]
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_datetime(
                    df[col], 
                    errors='coerce',
                    dayfirst=True
                ).dt.strftime("%d/%m/%Y")

    #####################################
    # Filtros Estratégicos no Sidebar

    st.sidebar.header("Filtros Estratégicos")

    # Filtros para a aba Prazos
    if "RESPONSÁVEL" in prazos_df.columns:
        responsavel_selecionado = st.sidebar.multiselect(
            "Responsável (Prazos)",
            options=prazos_df["RESPONSÁVEL"].unique()
        )
        if responsavel_selecionado:
            prazos_df = prazos_df[prazos_df["RESPONSÁVEL"].isin(responsavel_selecionado)]
    
    if "CLIENTE" in prazos_df.columns:
        cliente_prazos = st.sidebar.text_input("Buscar Cliente (Prazos)")
        if cliente_prazos:
            prazos_df = prazos_df[prazos_df["CLIENTE"].str.contains(cliente_prazos, case=False, na=False)]

    # Filtros para a aba Audiências
    if "TIPO DE AUDIÊNCIA" in audiencias_df.columns:
        tipo_audiencia = st.sidebar.multiselect(
            "Tipo de Audiência",
            options=audiencias_df["TIPO DE AUDIÊNCIA"].unique()
        )
        if tipo_audiencia:
            audiencias_df = audiencias_df[audiencias_df["TIPO DE AUDIÊNCIA"].isin(tipo_audiencia)]
    
    if "RAZÃO SOCIAL" in audiencias_df.columns:
        cliente_audiencias = st.sidebar.text_input("Buscar Cliente (Audiências)")
        if cliente_audiencias:
            audiencias_df = audiencias_df[audiencias_df["RAZÃO SOCIAL"].str.contains(cliente_audiencias, case=False, na=False)]
    
    # Filtro de período para Prazos e Audiências
    periodo = st.sidebar.radio(
        "Filtrar por período",
        options=["Todos", "Esta semana", "Semana seguinte", "Próximos 15 dias"]
    )

    def filter_by_period(df, date_column, period):
        """
        Filtra um DataFrame de acordo com o período em relação à data atual.
        O parâmetro date_column deve conter datas no formato que permita conversão via pd.to_datetime.
        """
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], dayfirst=True, errors='coerce')
            hoje = datetime.today()
            if period == "Esta semana":
                start = hoje
                end = hoje + timedelta(days=7)
                return df[(df[date_column] >= start) & (df[date_column] < end)]
            elif period == "Semana seguinte":
                start = hoje + timedelta(days=7)
                end = hoje + timedelta(days=14)
                return df[(df[date_column] >= start) & (df[date_column] < end)]
            elif period == "Próximos 15 dias":
                start = hoje
                end = hoje + timedelta(days=15)
                return df[(df[date_column] >= start) & (df[date_column] < end)]
        return df

    if periodo != "Todos":
        # Para Prazos, utiliza-se o campo "Unnamed: 0"
        prazos_df = filter_by_period(prazos_df, "Unnamed: 0", periodo)
        # Para Audiências, utiliza-se o campo "DATA"
        audiencias_df = filter_by_period(audiencias_df, "DATA", periodo)

    #####################################
    # Exibir métricas e tabelas

    st.metric("Total de Prazos", len(prazos_df))
    st.metric("Total de Audiências", len(audiencias_df))

    st.subheader("Prazos")
    st.dataframe(prazos_df)

    st.subheader("Audiências")
    st.dataframe(audiencias_df)

    st.subheader("Iniciais")
    st.dataframe(iniciais_df)

    st.sidebar.markdown("**Atualize a planilha para visualizar novos dados**")
