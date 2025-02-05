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

# Dicionário de mapeamento de colunas
COLUNAS_MAPEADAS = {
    'data': ['DATA (D-1)', 'data', 'Data', 'DATA', 'data_prazo', 'data_audiencia', 'data_audiência', 'data_distribuicao'],
    'responsavel': ['RESPONSÁVEL', 'Responsável', 'responsavel', 'RESPONSAVEL', 'advogado'],
    'tipo': ['TIPO', 'Tipo', 'tipo', 'tipo_processo', 'TIPO PROCESSO'],
    'valor': ['VALOR', 'Valor', 'valor', 'valor_causa', 'VALOR DA CAUSA'],
    'cliente': ['CLIENTE', 'Cliente', 'cliente', 'PARTE', 'parte'],
    'status': ['STATUS', 'Status', 'status', 'SITUAÇÃO', 'situacao'],
    'complexidade': ['COMPLEXIDADE', 'Complexidade', 'complexidade', 'DIFICULDADE']
}

def encontrar_coluna(df, tipo_coluna):
    """Encontra a coluna correta baseada no mapeamento."""
    possiveis_nomes = COLUNAS_MAPEADAS.get(tipo_coluna, [])
    for nome in possiveis_nomes:
        if nome in df.columns:
            return nome
    return None

def carregar_dados(arquivo):
    """Carrega os dados do arquivo Excel com tratamento de erros."""
    try:
        with st.spinner('Carregando dados...'):
            excel_file = pd.ExcelFile(arquivo)
            dados = {}
            
            # Mapeia os nomes das abas esperadas
            mapeamento_abas = {
                'Prazos': ['prazos', 'prazo', 'PRAZOS', 'deadline'],
                'Audiências': ['audiencias', 'audiência', 'AUDIÊNCIAS', 'AUDIENCIAS'],
                'Iniciais': ['iniciais', 'inicial', 'INICIAIS', 'PETIÇÕES']
            }
            
            for aba_padrao, variacoes in mapeamento_abas.items():
                for sheet_name in excel_file.sheet_names:
                    if sheet_name.lower() in [v.lower() for v in variacoes]:
                        df = pd.read_excel(arquivo, sheet_name=sheet_name)
                        
                        # Identifica a coluna de data
                        coluna_data = encontrar_coluna(df, 'data')
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

def aplicar_filtros_estrategicos(df, filtros, coluna_data):
    """Aplica filtros estratégicos ao DataFrame."""
    df_filtrado = df.copy()
    
    if df_filtrado.empty:
        return df_filtrado

    hoje = pd.Timestamp.now()
    
    # Filtros de prazo
    if "Apenas urgentes (3 dias)" in filtros:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] <= hoje + timedelta(days=3)]
    if "Vencidos" in filtros:
        df_filtrado = df_filtrado[df_filtrado[coluna_data] < hoje]
        
    # Filtros por responsável
    coluna_responsavel = encontrar_coluna(df_filtrado, 'responsavel')
    if coluna_responsavel and "Agrupar por responsável" in filtros:
        st.subheader("Distribuição por Responsável")
        contagem_resp = df_filtrado[coluna_responsavel].value_counts()
        st.bar_chart(contagem_resp)
        
    # Filtros por complexidade
    coluna_complexidade = encontrar_coluna(df_filtrado, 'complexidade')
    if coluna_complexidade and "Filtrar por complexidade" in filtros:
        complexidade = st.selectbox("Selecione a complexidade", 
                                  df_filtrado[coluna_complexidade].unique())
        df_filtrado = df_filtrado[df_filtrado[coluna_complexidade] == complexidade]
        
    # Filtros por cliente
    coluna_cliente = encontrar_coluna(df_filtrado, 'cliente')
    if coluna_cliente and "Agrupar por cliente" in filtros:
        st.subheader("Distribuição por Cliente")
        contagem_cliente = df_filtrado[coluna_cliente].value_counts().head(10)
        st.bar_chart(contagem_cliente)
        
    # Análise de valor
    coluna_valor = encontrar_coluna(df_filtrado, 'valor')
    if coluna_valor and "Análise de valor" in filtros:
        st.subheader("Análise de Valor")
        valor_total = df_filtrado[coluna_valor].sum()
        media_valor = df_filtrado[coluna_valor].mean()
        col1, col2 = st.columns(2)
        col1.metric("Valor Total", f"R$ {valor_total:,.2f}")
        col2.metric("Valor Médio", f"R$ {media_valor:,.2f}")
        
    # KPIs
    if "Mostrar KPIs" in filtros:
        st.subheader("KPIs")
        col1, col2, col3 = st.columns(3)
        
        # KPI 1: Cumprimento de Prazo
        if coluna_data:
            total_prazos = len(df_filtrado)
            prazos_vencidos = len(df_filtrado[df_filtrado[coluna_data] < hoje])
            taxa_cumprimento = ((total_prazos - prazos_vencidos) / total_prazos * 100) if total_prazos > 0 else 0
            col1.metric("Taxa de Cumprimento de Prazo", f"{taxa_cumprimento:.1f}%")
        
        # KPI 2: Distribuição de Carga
        if coluna_responsavel:
            carga_media = df_filtrado[coluna_responsavel].value_counts().mean()
            col2.metric("Média de Processos por Responsável", f"{carga_media:.1f}")
        
        # KPI 3: Valor Médio por Processo
        if coluna_valor:
            valor_medio = df_filtrado[coluna_valor].mean()
            col3.metric("Valor Médio por Processo", f"R$ {valor_medio:,.2f}")
            
    return df_filtrado

def main():
    st.title("Dashboard Jurídico Estratégico")
    
    uploaded_file = st.file_uploader("Carregar arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        dados = carregar_dados(uploaded_file)
        
        if dados:
            # Filtros principais
            st.sidebar.title("Filtros")
            
            # Período
            periodo = st.sidebar.selectbox(
                "Período",
                ["Esta semana", "Próxima semana", "Próximos 15 dias", "Próximos 30 dias", "Todos"]
            )
            
            # Filtros estratégicos
            st.sidebar.subheader("Filtros Estratégicos")
            filtros_estrategicos = st.sidebar.multiselect(
                "Selecione os filtros",
                [
                    "Apenas urgentes (3 dias)",
                    "Vencidos",
                    "Agrupar por responsável",
                    "Agrupar por cliente",
                    "Filtrar por complexidade",
                    "Análise de valor",
                    "Mostrar KPIs",
                    "Ordenar por data",
                    "Ordenar por valor"
                ]
            )
            
            # Abas principais
            tab1, tab2, tab3 = st.tabs(["Prazos", "Audiências", "Iniciais"])
            
            # Processamento de cada aba
            for tab, nome_aba in zip([tab1, tab2, tab3], ['Prazos', 'Audiências', 'Iniciais']):
                with tab:
                    st.header(nome_aba)
                    if not dados[nome_aba].empty:
                        coluna_data = encontrar_coluna(dados[nome_aba], 'data')
                        
                        if coluna_data:
                            df_filtrado = aplicar_filtros_estrategicos(
                                dados[nome_aba],
                                filtros_estrategicos,
                                coluna_data
                            )
                            
                            if not df_filtrado.empty:
                                # Ordenação
                                if "Ordenar por data" in filtros_estrategicos:
                                    df_filtrado = df_filtrado.sort_values(coluna_data)
                                elif "Ordenar por valor" in filtros_estrategicos:
                                    coluna_valor = encontrar_coluna(df_filtrado, 'valor')
                                    if coluna_valor:
                                        df_filtrado = df_filtrado.sort_values(coluna_valor, ascending=False)
                                
                                # Exibição da tabela
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
                        else:
                            st.error(f"Não foi possível identificar a coluna de data em {nome_aba}")
                    else:
                        st.warning(f"Nenhum dado encontrado em {nome_aba}")

if __name__ == "__main__":
    main()
