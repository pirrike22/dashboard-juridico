import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def sanitizar_dataframe(df):
    """
    Sanitiza o DataFrame para evitar erros de JSON no Streamlit.
    """
    df = df.copy()
    
    # Substitui NaN por string vazia em todas as colunas não-data
    for col in df.columns:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = df[col].fillna('').astype(str)
            # Remove caracteres que podem causar problemas no JSON
            df[col] = df[col].replace({
                'NaN': '',
                'nan': '',
                'NaT': '',
                'None': ''
            })
    
    return df

def identificar_colunas(df):
    """
    Identifica as colunas do DataFrame e retorna um dicionário com seus nomes.
    """
    colunas = {}
    for col in df.columns:
        col_upper = str(col).upper()
        # Procura por padrões de data
        if 'DATA' in col_upper:
            colunas['data'] = col
        # Adicione outros padrões conforme necessário
    return colunas

def processar_aba(df, nome_aba):
    """
    Processa uma aba do Excel e retorna o DataFrame limpo.
    """
    if df.empty:
        return pd.DataFrame()
    
    # Encontra a linha do cabeçalho
    header_row = None
    for idx, row in df.iterrows():
        row_str = [str(cell).upper() for cell in row]
        if any('DATA' in cell for cell in row_str):
            header_row = idx
            break
    
    if header_row is not None:
        # Define o cabeçalho e remove linhas anteriores
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    # Sanitiza o DataFrame
    df = sanitizar_dataframe(df)
    
    return df

def carregar_dados(arquivo):
    """
    Carrega os dados do Excel e processa cada aba.
    """
    try:
        dados = {}
        excel_file = pd.ExcelFile(arquivo)
        
        # Debug: mostrar todas as abas encontradas
        st.write("Abas encontradas:", excel_file.sheet_names)
        
        for nome_aba in ['Prazos', 'Audiências', 'Iniciais']:
            try:
                df = pd.read_excel(excel_file, sheet_name=nome_aba, header=None)
                df_processado = processar_aba(df, nome_aba)
                
                # Debug: mostrar colunas encontradas
                st.write(f"Colunas na aba {nome_aba}:", list(df_processado.columns))
                
                dados[nome_aba] = df_processado
            except Exception as e:
                st.error(f"Erro ao processar aba {nome_aba}: {str(e)}")
                dados[nome_aba] = pd.DataFrame()
        
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def aplicar_filtros(df, coluna_data, periodo, filtros_adicionais):
    """
    Aplica os filtros selecionados ao DataFrame.
    """
    if df.empty or coluna_data not in df.columns:
        return df
    
    # Converte a coluna de data
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    df = df.dropna(subset=[coluna_data])
    
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    
    # Aplica filtro de período
    if periodo == 'Esta semana':
        df = df[df[coluna_data].between(
            inicio_semana,
            inicio_semana + timedelta(days=6)
        )]
    elif periodo == 'Próxima semana':
        df = df[df[coluna_data].between(
            inicio_semana + timedelta(days=7),
            inicio_semana + timedelta(days=13)
        )]
    elif periodo == 'Próximos 15 dias':
        df = df[df[coluna_data].between(
            hoje,
            hoje + timedelta(days=15)
        )]
    
    # Aplica filtros adicionais
    if filtros_adicionais:
        if 'Apenas urgentes' in filtros_adicionais:
            df = df[df[coluna_data] <= hoje + timedelta(days=3)]
        if 'Apenas atrasados' in filtros_adicionais:
            df = df[df[coluna_data] < hoje]
        if 'Ordenar por data' in filtros_adicionais:
            df = df.sort_values(coluna_data)
    
    return sanitizar_dataframe(df)

def exibir_aba(dados, nome_aba, periodo, filtros_adicionais):
    """
    Exibe os dados de uma aba com tratamento de erros.
    """
    if dados[nome_aba].empty:
        st.warning(f"Nenhum dado encontrado na aba {nome_aba}")
        return
    
    # Identifica a coluna de data
    colunas = identificar_colunas(dados[nome_aba])
    if 'data' not in colunas:
        st.error(f"Não foi possível identificar a coluna de data na aba {nome_aba}")
        st.write("Colunas disponíveis:", list(dados[nome_aba].columns))
        return
    
    # Aplica os filtros
    df_filtrado = aplicar_filtros(
        dados[nome_aba],
        colunas['data'],
        periodo,
        filtros_adicionais
    )
    
    # Exibe métricas
    col1, col2, col3 = st.columns(3)
    hoje = pd.Timestamp.now()
    
    with col1:
        st.metric("Total", len(df_filtrado))
    with col2:
        urgentes = len(df_filtrado[df_filtrado[colunas['data']] <= hoje + timedelta(days=3)])
        st.metric("Urgentes", urgentes)
    with col3:
        atrasados = len(df_filtrado[df_filtrado[colunas['data']] < hoje])
        st.metric("Atrasados", atrasados)
    
    # Exibe a tabela
    if not df_filtrado.empty:
        try:
            # Primeira tentativa: com configuração de coluna de data
            st.dataframe(
                df_filtrado,
                column_config={
                    colunas['data']: st.column_config.DateColumn(
                        "Data",
                        format="DD/MM/YYYY"
                    )
                },
                hide_index=True
            )
        except Exception as e:
            # Segunda tentativa: exibição simples
            st.error(f"Erro ao formatar tabela: {str(e)}")
            st.dataframe(df_filtrado, hide_index=True)
    else:
        st.info("Nenhum registro encontrado para os filtros selecionados")

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
            
            # Exibe cada aba
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
