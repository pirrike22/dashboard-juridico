import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import plotly.express as px

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel com tratamento especial para cabeçalhos."""
    try:
        with st.spinner('Carregando dados...'):
            # Primeiro, vamos ler a aba de Prazos sem definir cabeçalho
            df_prazos = pd.read_excel(arquivo, sheet_name='Prazos', header=None)
            
            # Debug: Mostrar as primeiras linhas para identificar onde está o cabeçalho
            st.write("Primeiras linhas dos dados brutos:")
            st.write(df_prazos.head())
            
            # Encontrar a linha que contém "DATA (D-1)"
            for idx, row in df_prazos.iterrows():
                if any('DATA (D-1)' in str(cell).upper() for cell in row):
                    header_row = idx
                    # Recarregar o DataFrame usando esta linha como cabeçalho
                    df_prazos = pd.read_excel(arquivo, sheet_name='Prazos', header=header_row)
                    break
            
            # Debug: Mostrar as colunas após processar o cabeçalho
            st.write("Colunas encontradas após processamento:", df_prazos.columns.tolist())
            
            # Carregar outras abas
            try:
                df_audiencias = pd.read_excel(arquivo, sheet_name='Audiências')
            except:
                df_audiencias = pd.DataFrame()
            
            try:
                df_iniciais = pd.read_excel(arquivo, sheet_name='Iniciais')
            except:
                df_iniciais = pd.DataFrame()
            
            return {
                'Prazos': df_prazos,
                'Audiências': df_audiencias,
                'Iniciais': df_iniciais
            }
            
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        st.error("Detalhes do erro para debug:")
        st.write(e)
        return None

def encontrar_coluna_data(df):
    """Encontra a coluna de data no DataFrame."""
    for col in df.columns:
        if 'DATA (D-1)' in str(col).upper():
            return col
    return None

def filtrar_dados(df, coluna_data, periodo, filtros_adicionais=None):
    """Filtra os dados por período e filtros adicionais."""
    if df.empty or coluna_data not in df.columns:
        return df
    
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Converter coluna para datetime se ainda não for
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    
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
                    coluna_data = encontrar_coluna_data(dados['Prazos'])
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
                        st.write("Colunas disponíveis:", dados['Prazos'].columns.tolist())
                else:
                    st.warning("Nenhum dado encontrado na aba de Prazos")

if __name__ == "__main__":
    main()
