import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import plotly.express as px

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def processar_aba(df, nome_aba):
    """Processa uma aba do Excel, identificando o cabeçalho correto."""
    if df is None or df.empty:
        return pd.DataFrame()
        
    # Procurar a linha que contém o cabeçalho
    header_row = 0
    for idx, row in df.iterrows():
        # Converte todos os valores da linha para string e maiúsculas para comparação
        row_values = [str(val).upper() for val in row]
        # Verifica se a linha contém palavras-chave específicas para cada aba
        if nome_aba == 'Prazos' and any('DATA (D-1)' in val for val in row_values):
            header_row = idx
            break
        elif nome_aba == 'Audiências' and any('DATA AUDIÊNCIA' in val for val in row_values):
            header_row = idx
            break
        elif nome_aba == 'Iniciais' and any('DATA DISTRIBUIÇÃO' in val for val in row_values):
            header_row = idx
            break

    # Usar a linha identificada como cabeçalho
    if header_row > 0:
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    return df

def carregar_dados(arquivo):
    """Carrega todas as abas do arquivo Excel."""
    try:
        with st.spinner('Carregando dados...'):
            # Carregar todas as abas sem definir cabeçalho
            df_prazos = pd.read_excel(arquivo, sheet_name='Prazos', header=None)
            df_audiencias = pd.read_excel(arquivo, sheet_name='Audiências', header=None)
            df_iniciais = pd.read_excel(arquivo, sheet_name='Iniciais', header=None)
            
            # Processar cada aba
            prazos = processar_aba(df_prazos, 'Prazos')
            audiencias = processar_aba(df_audiencias, 'Audiências')
            iniciais = processar_aba(df_iniciais, 'Iniciais')
            
            # Debug: Mostrar colunas encontradas em cada aba
            st.write("Colunas na aba Prazos:", prazos.columns.tolist())
            st.write("Colunas na aba Audiências:", audiencias.columns.tolist())
            st.write("Colunas na aba Iniciais:", iniciais.columns.tolist())
            
            return {
                'Prazos': prazos,
                'Audiências': audiencias,
                'Iniciais': iniciais
            }
            
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def encontrar_coluna_data(df, tipo_aba):
    """Encontra a coluna de data baseada no tipo da aba."""
    colunas_data = {
        'Prazos': ['DATA (D-1)'],
        'Audiências': ['DATA AUDIÊNCIA', 'DATA DA AUDIÊNCIA', 'DATA'],
        'Iniciais': ['DATA DISTRIBUIÇÃO', 'DATA DA DISTRIBUIÇÃO', 'DATA']
    }
    
    possiveis_colunas = colunas_data.get(tipo_aba, [])
    for col in df.columns:
        if any(nome.upper() in str(col).upper() for nome in possiveis_colunas):
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
        st.write("Colunas disponíveis:", dados[nome_aba].columns.tolist())
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
        st.dataframe(
            df_filtrado,
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
