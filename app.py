import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import numpy as np

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def limpar_dados(df):
    """Limpa os dados do DataFrame, removendo linhas vazias e valores NaN."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Remover linhas onde todas as colunas são NaN
    df = df.dropna(how='all')
    
    # Substituir NaN por strings vazias em colunas de texto
    df = df.fillna('')
    
    return df

def processar_aba(df, nome_aba):
    """Processa uma aba do Excel identificando o cabeçalho correto."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Procurar a linha do cabeçalho
    header_row = None
    for idx, row in df.iterrows():
        row_str = row.astype(str).str.upper()
        
        # Definir critérios de busca para cada aba
        if nome_aba == 'Prazos' and row_str.str.contains('DATA').any():
            header_row = idx
            break
        elif nome_aba == 'Audiências' and (
            row_str.str.contains('AUDIÊNCIA').any() or 
            row_str.str.contains('AUDIENCIA').any()
        ):
            header_row = idx
            break
        elif nome_aba == 'Iniciais' and row_str.str.contains('DISTRIBUIÇÃO').any():
            header_row = idx
            break
    
    if header_row is not None:
        # Usar a linha encontrada como cabeçalho
        headers = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        df.columns = headers
        
        # Limpar os dados
        df = limpar_dados(df)
        
        return df
    
    return df

def carregar_dados(arquivo):
    """Carrega todas as abas do arquivo Excel."""
    try:
        with st.spinner('Carregando dados...'):
            # Ler todas as abas
            try:
                df_prazos = pd.read_excel(arquivo, sheet_name='Prazos', header=None)
            except:
                st.error("Erro ao ler aba Prazos")
                df_prazos = pd.DataFrame()
            
            try:
                df_audiencias = pd.read_excel(arquivo, sheet_name='Audiências', header=None)
            except:
                st.error("Erro ao ler aba Audiências")
                df_audiencias = pd.DataFrame()
            
            try:
                df_iniciais = pd.read_excel(arquivo, sheet_name='Iniciais', header=None)
            except:
                st.error("Erro ao ler aba Iniciais")
                df_iniciais = pd.DataFrame()
            
            # Processar cada aba
            prazos = processar_aba(df_prazos, 'Prazos')
            audiencias = processar_aba(df_audiencias, 'Audiências')
            iniciais = processar_aba(df_iniciais, 'Iniciais')
            
            # Debug: Mostrar as colunas encontradas
            if not prazos.empty:
                st.write("Colunas na aba Prazos:", list(prazos.columns))
            if not audiencias.empty:
                st.write("Colunas na aba Audiências:", list(audiencias.columns))
            if not iniciais.empty:
                st.write("Colunas na aba Iniciais:", list(iniciais.columns))
            
            return {
                'Prazos': prazos,
                'Audiências': audiencias,
                'Iniciais': iniciais
            }
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def encontrar_coluna_data(df, tipo_aba):
    """Encontra a coluna de data no DataFrame."""
    if df.empty:
        return None
        
    padroes = {
        'Prazos': ['DATA', 'D-1', 'PRAZO'],
        'Audiências': ['DATA', 'AUDIÊNCIA', 'AUDIENCIA'],
        'Iniciais': ['DATA', 'DISTRIBUIÇÃO', 'DISTRIBUICAO']
    }
    
    for col in df.columns:
        col_upper = str(col).upper()
        if any(padrao in col_upper for padrao in padroes.get(tipo_aba, [])):
            return col
    return None

def filtrar_dados(df, coluna_data, periodo):
    """Filtra os dados por período."""
    if df.empty or coluna_data not in df.columns:
        return df
    
    # Converter coluna para datetime
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
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
        st.write("Colunas disponíveis:", list(dados[nome_aba].columns))
        return
    
    df_filtrado = filtrar_dados(dados[nome_aba], coluna_data, periodo)
    
    # Aplicar filtros adicionais
    hoje = pd.Timestamp.now()
    if 'Apenas urgentes' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
    if 'Apenas atrasados' in filtros_adicionais:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
    if 'Ordenar por data' in filtros_adicionais:
        df_filtrado = df_filtrado.sort_values(coluna_data)
    
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
        # Garantir que não há valores NaN antes de exibir
        df_display = df_filtrado.fillna('')
        st.dataframe(
            df_display,
            column_config={
                coluna_data: st.column_config.DateColumn(
                    "Data",
                    format="DD/MM/YYYY"
                )
            }
        )
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
