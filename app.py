import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

# URL da planilha
SHEET_ID = "1fM5Oq6McjWFTDbUTbimMJfcnB2J1Oiy-_UY-VnDcnxE"
SHEET_NAMES = {
    'Prazos': 'Prazos',
    'Audiências': 'Audiências',
    'Iniciais': 'Iniciais'
}

def limpar_valores(val):
    """Limpa valores problemáticos."""
    if pd.isna(val) or val is None:
        return ""
    return str(val).replace('nan', '').replace('NaN', '').replace('NaT', '')

def processar_dataframe(df):
    """Processa o DataFrame removendo valores problemáticos."""
    df = df.copy()
    df = df.dropna(how='all')
    
    for col in df.columns:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = df[col].apply(limpar_valores)
    
    return df

def carregar_dados_sheets():
    """Carrega dados diretamente do Google Sheets usando URL pública."""
    try:
        dados = {}
        for nome_aba, sheet_name in SHEET_NAMES.items():
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            
            try:
                df = pd.read_csv(url)
                dados[nome_aba] = processar_dataframe(df)
                st.write(f"Colunas encontradas em {nome_aba}:", df.columns.tolist())
            except Exception as e:
                st.error(f"Erro ao carregar aba {nome_aba}: {str(e)}")
                dados[nome_aba] = pd.DataFrame()
        
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Sheets: {str(e)}")
        return None

def aplicar_filtros(df, coluna_data, periodo):
    """Aplica filtros de data ao DataFrame."""
    try:
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
        df = df.dropna(subset=[coluna_data])
        
        hoje = pd.Timestamp.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        if periodo == 'Esta semana':
            mask = (df[coluna_data] >= inicio_semana) & (df[coluna_data] <= inicio_semana + timedelta(days=6))
            return df[mask].copy()
        elif periodo == 'Próxima semana':
            inicio_prox = inicio_semana + timedelta(days=7)
            mask = (df[coluna_data] >= inicio_prox) & (df[coluna_data] <= inicio_prox + timedelta(days=6))
            return df[mask].copy()
        elif periodo == 'Próximos 15 dias':
            mask = (df[coluna_data] >= hoje) & (df[coluna_data] <= hoje + timedelta(days=15))
            return df[mask].copy()
        return df.copy()
    except Exception as e:
        st.error(f"Erro ao aplicar filtros: {str(e)}")
        return df.copy()

def exibir_dataframe(df, coluna_data):
    """Exibe o DataFrame de forma segura."""
    try:
        df_display = df.copy()
        df_display[coluna_data] = pd.to_datetime(df_display[coluna_data], errors='coerce')
        df_display = df_display.fillna('')
        
        st.dataframe(
            df_display,
            column_config={
                coluna_data: st.column_config.DateColumn(
                    "Data",
                    format="DD/MM/YYYY"
                )
            },
            hide_index=True
        )
    except Exception as e:
        st.error(f"Erro ao exibir dados: {str(e)}")
        st.dataframe(df_display, hide_index=True)

def exibir_aba(dados, nome_aba, periodo, filtros_adicionais):
    """Exibe dados de uma aba específica."""
    df = dados[nome_aba]
    if df.empty:
        st.warning(f"Nenhum dado encontrado na aba {nome_aba}")
        return
        
    # Identificar coluna de data baseada na aba
    if nome_aba == 'Prazos':
        coluna_data = 'DATA (D-1)'
    elif nome_aba == 'Audiências':
        coluna_data = 'DATA AUDIÊNCIA'
    elif nome_aba == 'Iniciais':
        coluna_data = 'DATA DISTRIBUIÇÃO'
    else:
        st.error(f"Aba não reconhecida: {nome_aba}")
        return
    
    if coluna_data not in df.columns:
        st.error(f"Coluna de data '{coluna_data}' não encontrada na aba {nome_aba}")
        st.write("Colunas disponíveis:", df.columns.tolist())
        return
    
    df_filtrado = aplicar_filtros(df, coluna_data, periodo)
    
    hoje = pd.Timestamp.now()
    if 'Apenas urgentes' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
    if 'Apenas atrasados' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
    if 'Ordenar por data' in filtros_adicionais:
        df_filtrado = df_filtrado.sort_values(coluna_data)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Total de {nome_aba}", len(df_filtrado))
    with col2:
        urgentes = len(df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)])
        st.metric(f"{nome_aba} Urgentes", urgentes)
    with col3:
        atrasados = len(df_filtrado[df_filtrado[coluna_data] < hoje])
        st.metric(f"{nome_aba} Atrasados", atrasados)
    
    if not df_filtrado.empty:
        exibir_dataframe(df_filtrado, coluna_data)
    else:
        st.info(f"Nenhum registro encontrado em {nome_aba} para os filtros selecionados")

def main():
    st.title("Dashboard Jurídico")
    
    # Carregar dados do Google Sheets
    with st.spinner('Carregando dados do Google Sheets...'):
        dados = carregar_dados_sheets()
    
    if dados:
        # Sidebar com filtros
        st.sidebar.title("Filtros")
        periodo = st.sidebar.selectbox(
            "Período",
            ["Esta semana", "Próxima semana", "Próximos 15 dias", "Todos"]
        )
        
        filtros_adicionais = st.sidebar.multiselect(
            "Filtros adicionais",
            ["Apenas urgentes", "Apenas atrasados", "Ordenar por data"]
        )
        
        # Botão para atualizar dados
        if st.sidebar.button("Atualizar Dados"):
            st.experimental_rerun()
        
        # Abas
        tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])
        
        with tab1:
            st.header("Prazos")
            exibir_aba(dados, 'Prazos', periodo, filtros_adicionais)
        
        with tab2:
            st.header("Audiências")
            exibir_aba(dados, 'Audiências', periodo, filtros_adicionais)
        
        with tab3:
            st.header("Iniciais")
            exibir_aba(dados, 'Iniciais', periodo, filtros_adicionais)

if __name__ == "__main__":
    main()
