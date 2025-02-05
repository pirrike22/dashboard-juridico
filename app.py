import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import locale
from dateutil.relativedelta import relativedelta
import plotly.express as px

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

def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel."""
    try:
        prazos = pd.read_excel(arquivo, sheet_name='Prazos')
        audiencias = pd.read_excel(arquivo, sheet_name='Audiências')
        iniciais = pd.read_excel(arquivo, sheet_name='Iniciais')
        
        # Convertendo colunas de data
        colunas_data = {
            'prazos': 'data_prazo',
            'audiencias': 'data_audiencia',
            'iniciais': 'data_distribuicao'
        }
        
        for df, col in zip([prazos, audiencias, iniciais], colunas_data.values()):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return prazos, audiencias, iniciais
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None, None, None

def filtrar_por_periodo(df, coluna_data, periodo):
    """Filtra o DataFrame com base no período selecionado."""
    hoje = pd.Timestamp.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    fim_semana = inicio_semana + timedelta(days=6)
    
    if periodo == 'Esta semana':
        mask = (df[coluna_data] >= inicio_semana) & (df[coluna_data] <= fim_semana)
    elif periodo == 'Próxima semana':
        inicio_prox = inicio_semana + timedelta(days=7)
        fim_prox = fim_semana + timedelta(days=7)
        mask = (df[coluna_data] >= inicio_prox) & (df[coluna_data] <= fim_prox)
    elif periodo == 'Próximos 15 dias':
        mask = (df[coluna_data] >= hoje) & (df[coluna_data] <= hoje + timedelta(days=15))
    else:
        return df
    
    return df[mask]

def criar_grafico_status(df, coluna_data, titulo):
    """Cria um gráfico de barras com a contagem por status."""
    if 'status' in df.columns:
        contagem = df['status'].value_counts()
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
        prazos, audiencias, iniciais = carregar_dados(uploaded_file)
        
        if prazos is not None and audiencias is not None and iniciais is not None:
            # Sidebar com filtros
            st.sidebar.title("Filtros")
            periodo = st.sidebar.selectbox(
                "Selecione o período",
                ["Esta semana", "Próxima semana", "Próximos 15 dias"]
            )
            
            # Criando abas
            tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])
            
            # Aba de Prazos
            with tab1:
                st.header("Prazos")
                prazos_filtrados = filtrar_por_periodo(prazos, 'data_prazo', periodo)
                
                # Removendo prazos da semana anterior
                hoje = pd.Timestamp.now()
                inicio_semana_anterior = hoje - timedelta(days=hoje.weekday() + 7)
                prazos_filtrados = prazos_filtrados[prazos_filtrados['data_prazo'] >= inicio_semana_anterior]
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Prazos", len(prazos_filtrados))
                with col2:
                    prazos_urgentes = len(prazos_filtrados[prazos_filtrados['data_prazo'] <= hoje + timedelta(days=3)])
                    st.metric("Prazos Urgentes", prazos_urgentes)
                with col3:
                    prazos_vencidos = len(prazos_filtrados[prazos_filtrados['data_prazo'] < hoje])
                    st.metric("Prazos Vencidos", prazos_vencidos)
                
                # Gráfico de status (se existir)
                grafico_prazos = criar_grafico_status(prazos_filtrados, 'data_prazo', 'Distribuição por Status')
                if grafico_prazos:
                    st.plotly_chart(grafico_prazos)
                
                # Tabela de prazos
                if not prazos_filtrados.empty:
                    st.dataframe(
                        prazos_filtrados.sort_values('data_prazo'),
                        column_config={
                            "data_prazo": st.column_config.DateColumn(
                                "Data do Prazo",
                                format="DD/MM/YYYY"
                            )
                        }
                    )
                else:
                    st.info("Nenhum prazo encontrado para o período selecionado.")
            
            # Aba de Audiências
            with tab2:
                st.header("Audiências")
                audiencias_filtradas = filtrar_por_periodo(audiencias, 'data_audiencia', periodo)
                
                # Métricas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Audiências", len(audiencias_filtradas))
                with col2:
                    audiencias_proximas = len(audiencias_filtradas[audiencias_filtradas['data_audiencia'] <= hoje + timedelta(days=3)])
                    st.metric("Audiências Próximas", audiencias_proximas)
                
                # Tabela de audiências
                if not audiencias_filtradas.empty:
                    st.dataframe(
                        audiencias_filtradas.sort_values('data_audiencia'),
                        column_config={
                            "data_audiencia": st.column_config.DateColumn(
                                "Data da Audiência",
                                format="DD/MM/YYYY"
                            )
                        }
                    )
                else:
                    st.info("Nenhuma audiência encontrada para o período selecionado.")
            
            # Aba de Iniciais
            with tab3:
                st.header("Iniciais")
                iniciais_filtradas = filtrar_por_periodo(iniciais, 'data_distribuicao', periodo)
                
                # Métricas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Iniciais", len(iniciais_filtradas))
                with col2:
                    valor_total = iniciais_filtradas['valor_causa'].sum() if 'valor_causa' in iniciais_filtradas.columns else 0
                    st.metric("Valor Total", f"R$ {valor_total:,.2f}")
                
                # Tabela de iniciais
                if not iniciais_filtradas.empty:
                    st.dataframe(
                        iniciais_filtradas.sort_values('data_distribuicao'),
                        column_config={
                            "data_distribuicao": st.column_config.DateColumn(
                                "Data de Distribuição",
                                format="DD/MM/YYYY"
                            )
                        }
                    )
                else:
                    st.info("Nenhuma inicial encontrada para o período selecionado.")

if __name__ == "__main__":
    main()
