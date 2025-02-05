import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def limpar_dataframe(df):
    """Limpa o DataFrame removendo valores nulos e formatando corretamente."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Remove linhas completamente vazias
    df = df.dropna(how='all')
    
    # Converte todas as colunas para string, exceto datas
    for col in df.columns:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = df[col].fillna('').astype(str)
    
    return df

def processar_aba(df, nome_aba):
    """Processa uma aba do Excel identificando o cabeçalho correto."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Procurar a linha do cabeçalho
    header_row = None
    for idx, row in df.iterrows():
        row_str = row.astype(str).str.upper()
        
        # Critérios específicos para cada aba
        if nome_aba == 'Prazos' and any('DATA' in str(cell).upper() for cell in row):
            header_row = idx
            break
        elif nome_aba == 'Audiências' and any('AUDIÊNCIA' in str(cell).upper() or 'AUDIENCIA' in str(cell).upper() for cell in row):
            header_row = idx
            break
        elif nome_aba == 'Iniciais' and any('DISTRIBUIÇÃO' in str(cell).upper() or 'DISTRIBUICAO' in str(cell).upper() for cell in row):
            header_row = idx
            break
    
    if header_row is not None:
        # Usar a linha encontrada como cabeçalho
        headers = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        df.columns = headers
        
        # Limpar o DataFrame
        df = limpar_dataframe(df)
        
        return df
    
    return df

def carregar_dados(arquivo):
    """Carrega todas as abas do arquivo Excel."""
    try:
        with st.spinner('Carregando dados...'):
            # Carregar cada aba
            excel_file = pd.ExcelFile(arquivo)
            
            dados = {}
            for nome_aba in ['Prazos', 'Audiências', 'Iniciais']:
                try:
                    df = pd.read_excel(excel_file, sheet_name=nome_aba, header=None)
                    df_processado = processar_aba(df, nome_aba)
                    dados[nome_aba] = df_processado
                    
                    # Debug: mostrar colunas encontradas
                    if not df_processado.empty:
                        st.write(f"Colunas encontradas na aba {nome_aba}:", 
                               [str(col) for col in df_processado.columns])
                except Exception as e:
                    st.error(f"Erro ao processar aba {nome_aba}: {str(e)}")
                    dados[nome_aba] = pd.DataFrame()
            
            return dados
            
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def encontrar_coluna_data(df, tipo_aba):
    """Encontra a coluna de data no DataFrame."""
    if df.empty:
        return None
        
    padroes = {
        'Prazos': ['DATA (D-1)', 'DATA', 'PRAZO'],
        'Audiências': ['DATA AUDIÊNCIA', 'AUDIENCIA', 'DATA'],
        'Iniciais': ['DATA DISTRIBUIÇÃO', 'DISTRIBUICAO', 'DATA INICIAL', 'DATA']
    }
    
    # Primeiro, tenta encontrar correspondência exata
    for col in df.columns:
        col_str = str(col).upper()
        if col_str in [p.upper() for p in padroes[tipo_aba]]:
            return col
    
    # Se não encontrar, procura por correspondência parcial
    for col in df.columns:
        col_str = str(col).upper()
        if any(padrao.upper() in col_str for padrao in padroes[tipo_aba]):
            return col
    
    return None

def filtrar_dados(df, coluna_data, periodo):
    """Filtra os dados por período."""
    if df.empty or coluna_data not in df.columns:
        return df
    
    # Converter coluna para datetime de forma segura
    try:
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    except:
        st.error(f"Erro ao converter datas da coluna {coluna_data}")
        return df
    
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Remover linhas com datas inválidas
    df = df[df[coluna_data].notna()]
    
    if periodo == 'Esta semana':
        return df[(df[coluna_data] >= inicio_semana) & (df[coluna_data] <= fim_semana)]
    elif periodo == 'Próxima semana':
        inicio_prox = inicio_semana + timedelta(days=7)
        fim_prox = fim_semana + timedelta(days=7)
        return df[(df[coluna_data] >= inicio_prox) & (df[coluna_data] <= fim_prox)]
    elif periodo == 'Próximos 15 dias':
        return df[(df[coluna_data] >= hoje) & (df[coluna_data] <= hoje + timedelta(days=15))]
    return df

def exibir_aba(dados, nome_aba, periodo, filtros_adicionais):
    """Exibe os dados de uma aba específica."""
    if dados[nome_aba].empty:
        st.warning(f"Nenhum dado encontrado na aba {nome_aba}")
        return
    
    coluna_data = encontrar_coluna_data(dados[nome_aba], nome_aba)
    if not coluna_data:
        st.error(f"Não foi possível identificar a coluna de data na aba {nome_aba}")
        st.write("Colunas disponíveis:", [str(col) for col in dados[nome_aba].columns])
        return
    
    df_filtrado = filtrar_dados(dados[nome_aba].copy(), coluna_data, periodo)
    
    # Aplicar filtros adicionais
    hoje = pd.Timestamp.now()
    if 'Apenas urgentes' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
    if 'Apenas atrasados' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
    if 'Ordenar por data' in filtros_adicionais:
        df_filtrado = df_filtrado.sort_values(coluna_data)
    
    # Garantir que todos os dados estão limpos antes de exibir
    df_filtrado = limpar_dataframe(df_filtrado)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Total de {nome_aba}", len(df_filtrado))
    with col2:
        urgentes = len(df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)])
        st.metric(f"{nome_aba} Urgentes", urgentes)
    with col3:
        atrasados = len(df_filtrado[df_filtrado[coluna_data] < hoje])
        st.metric(f"{nome_aba} Atrasados/Vencidos", atrasados)
    
    # Exibir tabela
    if not df_filtrado.empty:
        try:
            st.dataframe(
                df_filtrado,
                column_config={
                    coluna_data: st.column_config.DateColumn(
                        "Data",
                        format="DD/MM/YYYY"
                    )
                },
                hide_index=True
            )
        except Exception as e:
            st.error(f"Erro ao exibir tabela: {str(e)}")
            st.write("Tentando exibir sem configuração especial de coluna...")
            st.dataframe(df_filtrado, hide_index=True)
    else:
        st.info(f"Nenhum registro encontrado em {nome_aba} para os filtros selecionados.")

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
            
            # Exibir cada aba
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
