import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import plotly.express as px
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def identificar_coluna_data(df):
    """Identifica a coluna de data no DataFrame."""
    # Lista de possíveis nomes de coluna de data
    possiveis_nomes = [
        'DATA (D-1)',
        'DATA(D-1)',
        'DATA D-1',
        'DATA',
        'Data',
        'data'
    ]
    
    # Primeiro, procura pelo nome exato
    for col in df.columns:
        if any(nome.upper() == str(col).upper().strip() for nome in possiveis_nomes):
            return col
    
    # Se não encontrar, procura por colunas que contenham 'DATA'
    for col in df.columns:
        if 'DATA' in str(col).upper():
            return col
    
    return None

def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel com tratamento de erros aprimorado."""
    try:
        with st.spinner('Carregando dados...'):
            # Carregar todas as abas
            todas_abas = pd.read_excel(arquivo, sheet_name=None)
            
            # Debug: Mostrar todas as abas encontradas
            st.write("Abas encontradas:", list(todas_abas.keys()))
            
            dados = {}
            
            # Processar aba de Prazos
            if 'Prazos' in todas_abas:
                df_prazos = todas_abas['Prazos']
                # Debug: Mostrar colunas encontradas
                st.write("Colunas na aba Prazos:", list(df_prazos.columns))
                
                # Identificar coluna de data
                coluna_data = identificar_coluna_data(df_prazos)
                if coluna_data:
                    st.success(f"Coluna de data identificada: '{coluna_data}'")
                    df_prazos[coluna_data] = pd.to_datetime(df_prazos[coluna_data], errors='coerce')
                    dados['Prazos'] = df_prazos
                else:
                    st.error("Não foi possível identificar a coluna de data na aba Prazos")
                    dados['Prazos'] = df_prazos
            
            # Processar outras abas
            for aba in ['Audiências', 'Iniciais']:
                if aba in todas_abas:
                    dados[aba] = todas_abas[aba]
                else:
                    dados[aba] = pd.DataFrame()
            
            return dados
            
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def filtrar_dados(df, coluna_data, periodo, filtros_adicionais=None):
    """Filtra os dados por período e filtros adicionais."""
    if df.empty or coluna_data not in df.columns:
        return df
    
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Filtro de período
    if periodo == 'Esta semana':
        df = df[(df[coluna_data] >= inicio_semana) & (df[coluna_data] <= fim_semana)]
    elif periodo == 'Próxima semana':
        inicio_prox = inicio_semana + timedelta(days=7)
        fim_prox = fim_semana + timedelta(days=7)
        df = df[(df[coluna_data] >= inicio_prox) & (df[coluna_data] <= fim_prox)]
    elif periodo == 'Próximos 15 dias':
        df = df[(df[coluna_data] >= hoje) & (df[coluna_data] <= hoje + timedelta(days=15))]
    
    # Filtros adicionais
    if filtros_adicionais:
        if 'Apenas urgentes' in filtros_adicionais:
            df = df[df[coluna_data] <= hoje + timedelta(days=3)]
        if 'Apenas atrasados' in filtros_adicionais:
            df = df[df[coluna_data] < hoje]
    
    return df

def main():
    st.title("Dashboard Jurídico")
    
    uploaded_file = st.file_uploader("Carregar arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        dados = carregar_dados(uploaded_file)
        
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
            
            # Abas
            tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])
            
            # Aba de Prazos
            with tab1:
                st.header("Prazos")
                if not dados['Prazos'].empty:
                    coluna_data = identificar_coluna_data(dados['Prazos'])
                    if coluna_data:
                        df_filtrado = filtrar_dados(dados['Prazos'], coluna_data, periodo, filtros_adicionais)
                        
                        # Métricas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Prazos", len(df_filtrado))
                        with col2:
                            urgentes = len(df_filtrado[df_filtrado[coluna_data] <= pd.Timestamp.now() + timedelta(days=3)])
                            st.metric("Prazos Urgentes", urgentes)
                        with col3:
                            atrasados = len(df_filtrado[df_filtrado[coluna_data] < pd.Timestamp.now()])
                            st.metric("Prazos Atrasados", atrasados)
                        
                        # Exibir dados
                        if not df_filtrado.empty:
                            if "Ordenar por data" in filtros_adicionais:
                                df_filtrado = df_filtrado.sort_values(coluna_data)
                            
                            st.dataframe(
                                df_filtrado,
                                column_config={
                                    coluna_data: st.column_config.DateColumn(
                                        "Data do Prazo",
                                        format="DD/MM/YYYY"
                                    )
                                }
                            )
                        else:
                            st.info("Nenhum prazo encontrado para os filtros selecionados.")
                    else:
                        st.error("Não foi possível identificar a coluna de data")
                else:
                    st.warning("Nenhum dado encontrado na aba de Prazos")

if __name__ == "__main__":
    main()
