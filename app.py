import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("Dashboard Jurídico")

uploaded_file = st.file_uploader("Faça upload da planilha .xlsx", type=["xlsx"])

if uploaded_file is not None:
    def load_data(file):
        xls = pd.ExcelFile(file)
        prazos_df = pd.read_excel(xls, sheet_name="Prazos", dtype=str, header=0)
        audiencias_df = pd.read_excel(xls, sheet_name="Audiências", dtype=str, header=0)
        iniciais_df = pd.read_excel(xls, sheet_name="Iniciais", dtype=str, header=0)
        
        prazos_df = prazos_df.dropna(axis=1, how='all')
        audiencias_df = audiencias_df.dropna(axis=1, how='all')
        iniciais_df = iniciais_df.dropna(axis=1, how='all')
        
        return prazos_df, audiencias_df, iniciais_df

    prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

    # Função para normalizar horários
    def normalize_time(time_str):
        if pd.isna(time_str) or str(time_str).strip() in ['', 'NaT']:
            return "00:00"
        
        time_str = str(time_str).strip().upper()
        
        # Converter formato '14h00' para '14:00'
        time_str = time_str.replace('H', ':').replace('h', ':')
        
        # Remover segundos se existirem
        if len(time_str.split(':')) > 2:
            time_str = ":".join(time_str.split(':')[:2])
            
        return time_str

    # Processar coluna de horários
    if "HORÁRIO" in audiencias_df.columns:
        audiencias_df["HORÁRIO"] = audiencias_df["HORÁRIO"].apply(normalize_time)
        audiencias_df["HORÁRIO"] = pd.to_datetime(
            audiencias_df["HORÁRIO"], 
            format='%H:%M', 
            errors='coerce'
        ).dt.strftime("%H:%M")

    # Converter outras colunas de data
    date_columns = {
        'prazos_df': ['DATA', 'DATA DE CIÊNCIA', 'DATA DA DELEGAÇÃO', 'PRAZO INTERNO (DEL.+5)', 'DATA DA ENTREGA'],
        'audiencias_df': ['DATA'],
        'iniciais_df': ['DATA']
    }

    for df_name, cols in date_columns.items():
        df = locals()[df_name]
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%d/%m/%Y")

    # Restante do código mantido...
    # [Manter o restante da lógica de filtros e exibição igual ao código original]

    st.metric("Total de Prazos", len(prazos_df))
    st.metric("Total de Audiências", len(audiencias_df))

    st.subheader("Prazos")
    st.dataframe(prazos_df)

    st.subheader("Audiências")
    st.dataframe(audiencias_df)

    st.subheader("Iniciais")
    st.dataframe(iniciais_df)

    st.sidebar.markdown("**Atualize a planilha para visualizar novos dados**")
