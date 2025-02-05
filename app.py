import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Dashboard Jurídica", layout="wide")

# Função para verificar e converter colunas de data
def convert_date_columns(df, possible_date_columns):
    for col in possible_date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
            except:
                st.error(f"Erro ao converter a coluna {col} para data")
    return df

# Função para carregar os dados do arquivo uploadado
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            # Carregando as abas específicas
            excel_file = io.BytesIO(uploaded_file.getvalue())
            
            # Tentativa de leitura com diferentes nomes de abas possíveis
            try:
                prazos_df = pd.read_excel(excel_file, sheet_name='Prazos')
            except:
                try:
                    prazos_df = pd.read_excel(excel_file, sheet_name='PRAZOS')
                except:
                    st.error("Não foi possível encontrar a aba 'Prazos'")
                    return None, None, None
            
            try:
                audiencias_df = pd.read_excel(excel_file, sheet_name='Audiências')
            except:
                try:
                    audiencias_df = pd.read_excel(excel_file, sheet_name='AUDIÊNCIAS')
                except:
                    try:
                        audiencias_df = pd.read_excel(excel_file, sheet_name='Audiencias')
                    except:
                        st.error("Não foi possível encontrar a aba 'Audiências'")
                        return None, None, None
            
            try:
                iniciais_df = pd.read_excel(excel_file, sheet_name='Iniciais')
            except:
                try:
                    iniciais_df = pd.read_excel(excel_file, sheet_name='INICIAIS')
                except:
                    st.error("Não foi possível encontrar a aba 'Iniciais'")
                    return None, None, None
            
            # Lista de possíveis nomes de colunas de data
            date_columns_prazos = ['Data', 'DATA', 'Data do Prazo', 'DATA DO PRAZO']
            date_columns_audiencias = ['Data', 'DATA', 'Data da Audiência', 'DATA DA AUDIÊNCIA']
            date_columns_iniciais = ['Data Distribuição', 'DATA DISTRIBUIÇÃO', 'Data de Distribuição']
            
            # Convertendo colunas de data
            prazos_df = convert_date_columns(prazos_df, date_columns_prazos)
            audiencias_df = convert_date_columns(audiencias_df, date_columns_audiencias)
            iniciais_df = convert_date_columns(iniciais_df, date_columns_iniciais)
            
            # Verificar se as colunas de data foram encontradas e convertidas
            if not any(col in prazos_df.columns for col in date_columns_prazos):
                st.error("Não foi encontrada uma coluna de data válida na aba Prazos")
                return None, None, None
                
            if not any(col in audiencias_df.columns for col in date_columns_audiencias):
                st.error("Não foi encontrada uma coluna de data válida na aba Audiências")
                return None, None, None
                
            if not any(col in iniciais_df.columns for col in date_columns_iniciais):
                st.error("Não foi encontrada uma coluna de data válida na aba Iniciais")
                return None, None, None
            
            # Padronizar os nomes das colunas de data
            for col in prazos_df.columns:
                if col.upper() in [c.upper() for c in date_columns_prazos]:
                    prazos_df = prazos_df.rename(columns={col: 'Data'})
                    
            for col in audiencias_df.columns:
                if col.upper() in [c.upper() for c in date_columns_audiencias]:
                    audiencias_df = audiencias_df.rename(columns={col: 'Data'})
                    
            for col in iniciais_df.columns:
                if col.upper() in [c.upper() for c in date_columns_iniciais]:
                    iniciais_df = iniciais_df.rename(columns={col: 'Data Distribuição'})
            
            return prazos_df, audiencias_df, iniciais_df
            
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            return None, None, None
    return None, None, None

# Interface para upload do arquivo
st.title("Dashboard Jurídica")
st.write("Para começar, faça o upload do arquivo Excel com os dados atualizados:")

uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])

if uploaded_file is None:
    st.warning("Por favor, faça o upload do arquivo Excel para visualizar a dashboard.")
    st.stop()

# Carregando os dados após o upload
prazos_df, audiencias_df, iniciais_df = load_data(uploaded_file)

if prazos_df is None or audiencias_df is None or iniciais_df is None:
    st.error("Não foi possível carregar os dados. Verifique se o arquivo está no formato correto.")
    st.stop()

# Mostrar informações sobre as colunas encontradas
with st.expander("Informações sobre as colunas carregadas"):
    st.write("Colunas da aba Prazos:", list(prazos_df.columns))
    st.write("Colunas da aba Audiências:", list(audiencias_df.columns))
    st.write("Colunas da aba Iniciais:", list(iniciais_df.columns))

[... resto do código continua igual ...]
