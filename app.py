import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Função para carregar dados
def load_data(file):
    df = pd.read_excel(file)
    return df

# Configuração do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")
st.title("📊 Dashboard Jurídico Interativo")

# Upload de arquivo
uploaded_file = st.file_uploader("Carregue a planilha Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.success("Dados carregados com sucesso!")
    
    # Exibir preview da planilha
    st.subheader("Visualização da Tabela")
    st.dataframe(df)
    
    # Criar filtros dinâmicos
    st.sidebar.header("Filtros")
    columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    filters = {}
    for col in columns:
        unique_values = df[col].dropna().unique().tolist()
        filters[col] = st.sidebar.multiselect(f"Filtrar {col}", unique_values, default=unique_values)
    
    # Aplicar filtros
    filtered_df = df.copy()
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    # Exibir dados filtrados
    st.subheader("Dados Filtrados")
    st.dataframe(filtered_df)
    
    # Criar gráficos dinâmicos
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_columns:
        st.subheader("Gráficos Interativos")
        x_axis = st.selectbox("Escolha a variável X", numeric_columns)
        y_axis = st.selectbox("Escolha a variável Y", numeric_columns)
        
        fig, ax = plt.subplots()
        ax.scatter(filtered_df[x_axis], filtered_df[y_axis])
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        ax.set_title(f"Relação entre {x_axis} e {y_axis}")
        st.pyplot(fig)
    
    # Botão para exportar dados filtrados
    st.download_button(
        label="Baixar dados filtrados",
        data=filtered_df.to_csv(index=False),
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )
