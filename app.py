import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
import plotly.express as px
import numpy as np

# Configurando o locale para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")

def identificar_colunas_data(df):
    """Identifica automaticamente as colunas de data no DataFrame."""
    colunas_data = []
    for coluna in df.columns:
        # Verifica se o nome da coluna contém palavras-chave relacionadas a datas
        if any(palavra in coluna.lower() for palavra in ['data', 'prazo', 'audiencia', 'audiência', 'distribuicao', 'distribuição']):
            try:
                # Tenta converter a coluna para datetime
                pd.to_datetime(df[coluna], errors='coerce')
                colunas_data.append(coluna)
            except:
                continue
    return colunas_data[0] if colunas_data else None

def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel com tratamento de erros."""
    try:
        with st.spinner('Carregando dados...'):
            excel_file = pd.ExcelFile(arquivo)
            dados = {}
            
            # Mapeia os nomes das abas esperadas para possíveis variações
            mapeamento_abas = {
                'Prazos': ['prazos', 'prazo', 'deadline', 'deadlines'],
                'Audiências': ['audiencias', 'audiência', 'audiências', 'audiencia', 'hearings'],
                'Iniciais': ['iniciais', 'inicial', 'petições', 'peticoes', 'initials']
            }
            
            # Tenta encontrar as abas corretas
            for aba_padrao, variacoes in mapeamento_abas.items():
                for sheet_name in excel_file.sheet_names:
                    if sheet_name.lower() in [v.lower() for v in variacoes]:
                        df = pd.read_excel(arquivo, sheet_name=sheet_name)
                        
                        # Identifica a coluna de data automaticamente
                        coluna_data = identificar_colunas_data(df)
                        if coluna_data:
                            df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
                        
                        dados[aba_padrao] = df
                        break
                else:
                    st.warning(f"Aba '{aba_padrao}' não encontrada no arquivo.")
                    dados[aba_padrao] = pd.DataFrame()
            
            return dados
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

def filtrar_por_periodo(df, coluna_data, periodo, filtros_adicionais=None):
    """Filtra o DataFrame com base no período e filtros adicionais selecionados."""
    if df.empty or coluna_data not in df.columns:
        return df
        
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    # Filtro principal de período
    periodo_base = periodo.split(' - ')[0] if ' - ' in periodo else periodo
    
    if periodo_base == 'Esta semana':
        df_filtrado = df[(df[coluna_data] >= inicio_semana) & (df[coluna_data] <= fim_semana)]
    elif periodo_base == 'Próxima semana':
        inicio_prox = inicio_semana + timedelta(days=7)
        fim_prox = fim_semana + timedelta(days=7)
        df_filtrado = df[(df[coluna_data] >= inicio_prox) & (df[coluna_data] <= fim_prox)]
    elif periodo_base == 'Próximos 15 dias':
        df_filtrado = df[(df[coluna_data] >= hoje) & (df[coluna_data] <= hoje + timedelta(days=15))]
    else:
        df_filtrado = df
    
    # Aplicar filtros adicionais se especificados
    if filtros_adicionais and not df_filtrado.empty:
        if 'Apenas urgentes' in filtros_adicionais:
            df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
        if 'Apenas vencidos' in filtros_adicionais:
            df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
        if 'Apenas em andamento' in filtros_adicionais and 'status' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['status'].str.lower() == 'em andamento']
    
    return df_filtrado

def criar_grafico_status(df, titulo):
    """Cria um gráfico de barras com a contagem por status."""
    if df.empty:
        return None
        
    for coluna in ['status', 'Status', 'STATUS']:
        if coluna in df.columns:
            contagem = df[coluna].value_counts()
            fig = px.bar(
                x=contagem.index,
                y=contagem.values,
                title=titulo,
                labels={'x': 'Status', 'y': 'Quantidade'}
            )
            return fig
    return None

def main():
    st.title("Dashboard Jurídico")
    
    # Upload do arquivo
    uploaded_file = st.file_uploader("Carregar arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        dados = carregar_dados(uploaded_file)
        
        if dados:
            # Sidebar com filtros
            st.sidebar.title("Filtros")
            
            # Filtro de período principal
            periodo_base = st.sidebar.selectbox(
                "Selecione o período base",
                ["Esta semana", "Próxima semana", "Próximos 15 dias"]
            )
            
            # Filtros adicionais por checkbox
            st.sidebar.subheader("Filtros adicionais")
            filtros_adicionais = st.sidebar.multiselect(
                "Selecione os filtros",
                [
                    "Apenas urgentes",
                    "Apenas vencidos",
                    "Apenas em andamento",
                    "Ordenar por data",
                    "Mostrar valor da causa"
                ]
            )
            
            # Criando abas
            tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])
            
            # Aba de Prazos
            with tab1:
                st.header("Prazos")
                if not dados['Prazos'].empty:
                    coluna_data = identificar_colunas_data(dados['Prazos'])
                    if coluna_data:
                        prazos_filtrados = filtrar_por_periodo(
                            dados['Prazos'],
                            coluna_data,
                            periodo_base,
                            filtros_adicionais
                        )
                        
                        # Métricas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de Prazos", len(prazos_filtrados))
                        with col2:
                            prazos_urgentes = len(prazos_filtrados[prazos_filtrados[coluna_data] <= pd.Timestamp.now() + timedelta(days=3)])
                            st.metric("Prazos Urgentes", prazos_urgentes)
                        with col3:
                            prazos_vencidos = len(prazos_filtrados[prazos_filtrados[coluna_data] < pd.Timestamp.now()])
                            st.metric("Prazos Vencidos", prazos_vencidos)
                        
                        # Gráfico de status
                        grafico_prazos = criar_grafico_status(prazos_filtrados, 'Distribuição por Status')
                        if grafico_prazos:
                            st.plotly_chart(grafico_prazos, use_container_width=True)
                        
                        # Tabela de prazos
                        if not prazos_filtrados.empty:
                            if "Ordenar por data" in filtros_adicionais:
                                prazos_filtrados = prazos_filtrados.sort_values(coluna_data)
                            
                            st.dataframe(
                                prazos_filtrados,
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
                        st.error("Não foi possível identificar a coluna de data na aba de Prazos.")
                else:
                    st.warning("Nenhum dado encontrado na aba de Prazos.")
            
            # Aba de Audiências (similar à aba de Prazos)
            with tab2:
                st.header("Audiências")
                if not dados['Audiências'].empty:
                    coluna_data = identificar_colunas_data(dados['Audiências'])
                    if coluna_data:
                        audiencias_filtradas = filtrar_por_periodo(
                            dados['Audiências'],
                            coluna_data,
                            periodo_base,
                            filtros_adicionais
                        )
                        
                        # Métricas para audiências
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total de Audiências", len(audiencias_filtradas))
                        with col2:
                            audiencias_proximas = len(audiencias_filtradas[audiencias_filtradas[coluna_data] <= pd.Timestamp.now() + timedelta(days=3)])
                            st.metric("Audiências Próximas", audiencias_proximas)
                        
                        # Tabela de audiências
                        if not audiencias_filtradas.empty:
                            if "Ordenar por data" in filtros_adicionais:
                                audiencias_filtradas = audiencias_filtradas.sort_values(coluna_data)
                            
                            st.dataframe(
                                audiencias_filtradas,
                                column_config={
                                    coluna_data: st.column_config.DateColumn(
                                        "Data da Audiência",
                                        format="DD/MM/YYYY"
                                    )
                                }
                            )
                        else:
                            st.info("Nenhuma audiência encontrada para os filtros selecionados.")
                    else:
                        st.error("Não foi possível identificar a coluna de data na aba de Audiências.")
                else:
                    st.warning("Nenhum dado encontrado na aba de Audiências.")
            
            # Aba de Iniciais
            with tab3:
                st.header("Iniciais")
                if not dados['Iniciais'].empty:
                    coluna_data = identificar_colunas_data(dados['Iniciais'])
                    if coluna_data:
                        iniciais_filtradas = filtrar_por_periodo(
                            dados['Iniciais'],
                            coluna_data,
                            periodo_base,
                            filtros_adicionais
                        )
                        
                        # Métricas para iniciais
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total de Iniciais", len(iniciais_filtradas))
                        with col2:
                            if "Mostrar valor da causa" in filtros_adicionais:
                                for coluna in ['valor_causa', 'valor', 'Valor da Causa', 'VALOR']:
                                    if coluna in iniciais_filtradas.columns:
                                        valor_total = iniciais_filtradas[coluna].sum()
                                        st.metric("Valor Total", f"R$ {valor_total:,.2f}")
                                        break
                        
                        # Tabela de iniciais
                        if not iniciais_filtradas.empty:
                            if "Ordenar por data" in filtros_adicionais:
                                iniciais_filtradas = iniciais_filtradas.sort_values(coluna_data)
                            
                            st.dataframe(
                                iniciais_filtradas,
                                column_config={
                                    coluna_data: st.column_config.DateColumn(
                                        "Data de Distribuição",
                                        format="DD/MM/YYYY"
                                    )
                                }
                            )
                        else:
                            st.info("Nenhuma inicial encontrada para os filtros selecionados.")
                    else:
                        st.error("Não foi possível identificar a coluna de data na aba de Iniciais.")
                else:
                    st.warning("Nenhum dado encontrado na aba de Iniciais.")

if __name__ == "__main__":
    main()
