# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date() if isinstance(date_str, str) else date_str
    except:
        return None

def process_sheet(sheet_name, upload_file):
    try:
        df = pd.read_excel(upload_file, sheet_name=sheet_name)
        
        # Converter datas para o formato dd/mm/yyyy
        date_columns = []
        if sheet_name == 'Prazos':
            date_columns = ['DATA (D-1)', 'DATA DE CIÊNCIA', 'DATA DA DELEGAÇÃO', 'PRAZO INTERNO (DEL.+5)', 'DATA DA ENTREGA']
        elif sheet_name == 'Audiências':
            date_columns = ['DATA']
        elif sheet_name == 'Iniciais':
            date_columns = ['DATA', 'DATA  DA ENTREGA', 'DATA DO PROTOCOLO']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba {sheet_name}: {str(e)}")
        return pd.DataFrame()

def filter_dates(df, date_column, start_date, end_date):
    try:
        mask = (
            (pd.to_datetime(df[date_column], dayfirst=True) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(df[date_column], dayfirst=True) <= pd.to_datetime(end_date))
        )
        return df[mask].copy()
    except:
        return df

def main():
    st.set_page_config(page_title="Dashboard Jurídico", layout="wide")
    st.title("Dashboard Jurídico - Acompanhamento de Processos")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader("Carregar planilha atualizada", type=["xlsx"])
    
    if uploaded_file:
        # Processar abas
        prazos = process_sheet('Prazos', uploaded_file)
        audiencias = process_sheet('Audiências', uploaded_file)
        iniciais = process_sheet('Iniciais', uploaded_file)
        
        # Filtros de data
        st.sidebar.header("Filtros")
        date_filter = st.sidebar.selectbox(
            "Período",
            ["Esta Semana", "Próxima Semana", "Próximos 15 Dias"]
        )
        
        # Calcular datas
        today = datetime.today().date()
        if date_filter == "Esta Semana":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_filter == "Próxima Semana":
            start_date = today + timedelta(days=(7 - today.weekday()))
            end_date = start_date + timedelta(days=6)
        else:
            start_date = today
            end_date = today + timedelta(days=15)
            
        # Aplicar filtros
        if not prazos.empty:
            filtered_prazos = filter_dates(prazos, 'DATA (D-1)', start_date, end_date)
            if date_filter == "Esta Semana":
                segunda_passada = today - timedelta(days=today.weekday() + 7)
                filtered_prazos = filtered_prazos[
                    pd.to_datetime(filtered_prazos['DATA (D-1)'], dayfirst=True) >= pd.to_datetime(segunda_passada)
                ]
            
            st.subheader("Prazos")
            st.dataframe(filtered_prazos, use_container_width=True)
        
        if not audiencias.empty:
            filtered_audiencias = filter_dates(audiencias, 'DATA', start_date, end_date)
            st.subheader("Audiências")
            st.dataframe(filtered_audiencias, use_container_width=True)
        
        if not iniciais.empty:
            filtered_iniciais = filter_dates(iniciais, 'DATA', start_date, end_date)
            st.subheader("Iniciais")
            st.dataframe(filtered_iniciais, use_container_width=True)

if __name__ == "__main__":
    main()
