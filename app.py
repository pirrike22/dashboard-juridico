import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def limpar_valores(val):
    """Limpa valores problemáticos."""
    if pd.isna(val) or val is None:
        return ""
    return str(val).replace('nan', '').replace('NaN', '').replace('NaT', '')

def processar_dataframe(df):
    """Processa o DataFrame removendo valores problemáticos."""
    # Criar uma cópia do DataFrame
    df = df.copy()
    
    # Remover linhas totalmente vazias
    df = df.dropna(how='all')
    
    # Para cada coluna que não é data, limpar valores
    for col in df.columns:
        if df[col].dtype != 'datetime64[ns]':
            df[col] = df[col].apply(limpar_valores)
    
    return df

def carregar_dados(arquivo):
    """Carrega dados do Excel com tratamento específico para cada aba."""
    try:
        # Carregar cada aba
        df_prazos = pd.read_excel(arquivo, sheet_name='Prazos')
        df_audiencias = pd.read_excel(arquivo, sheet_name='Audiências')
        df_iniciais = pd.read_excel(arquivo, sheet_name='Iniciais')
        
        # Debug: mostrar colunas de cada aba
        st.write("Colunas encontradas em Prazos:", df_prazos.columns.tolist())
        st.write("Colunas encontradas em Audiências:", df_audiencias.columns.tolist())
        st.write("Colunas encontradas em Iniciais:", df_iniciais.columns.tolist())
        
        return {
            'Prazos': processar_dataframe(df_prazos),
            'Audiências': processar_dataframe(df_audiencias),
            'Iniciais': processar_dataframe(df_iniciais)
        }
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

def aplicar_filtros(df, coluna_data, periodo):
    """Aplica filtros de data ao DataFrame."""
    try:
        # Converter coluna de data
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
        # Processar o DataFrame para exibição
        df_display = df.copy()
        
        # Converter datas para o formato correto
        df_display[coluna_data] = pd.to_datetime(df_display[coluna_data], errors='coerce')
        
        # Remover valores NaN
        df_display = df_display.fillna('')
        
        # Tentar exibir com configuração de coluna de data
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
        # Fallback para exibição simples
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
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, coluna_data, periodo)
    
    # Aplicar filtros adicionais
    hoje = pd.Timestamp.now()
    if 'Apenas urgentes' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
    if 'Apenas atrasados' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
    if 'Ordenar por data' in filtros_adicionais:
        df_filtrado = df_filtrado.sort_values(coluna_data)
    
    # Exibir métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Total de {nome_aba}", len(df_filtrado))
    with col2:
        urgentes = len(df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)])
        st.metric(f"{nome_aba} Urgentes", urgentes)
    with col3:
        atrasados = len(df_filtrado[df_filtrado[coluna_data] < hoje])
        st.metric(f"{nome_aba} Atrasados", atrasados)
    
    # Exibir dados
    if not df_filtrado.empty:
        exibir_dataframe(df_filtrado, coluna_data)
    else:
        st.info(f"Nenhum registro encontrado em {nome_aba} para os filtros selecionados")

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
