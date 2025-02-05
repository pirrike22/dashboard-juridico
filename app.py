import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Função para carregar dados
def load_data(file):
    expected_sheets = ["Prazos", "Audiência", "Iniciais"]
    excel_file = pd.ExcelFile(file)
    available_sheets = excel_file.sheet_names
    
    # Exibir as abas disponíveis no arquivo
    st.sidebar.write("📌 Abas disponíveis no arquivo:")
    st.sidebar.write(available_sheets)
    
    # Ajustar para variações de nome
    matched_sheets = {}
    for sheet in expected_sheets:
        for available_sheet in available_sheets:
            if sheet.lower().strip() in available_sheet.lower().strip():
                matched_sheets[sheet] = available_sheet
                break
    
    valid_sheets = list(matched_sheets.values())
    
    if not valid_sheets:
        st.error("Nenhuma das abas esperadas ('Prazos', 'Audiência', 'Iniciais') foi encontrada no arquivo.")
        return None, None
    
    data = {sheet: pd.read_excel(file, sheet_name=matched_sheets[sheet]) for sheet in matched_sheets}
    
    # Ajustar formatação de datas
    for sheet in data:
        for col in data[sheet].select_dtypes(include=['datetime']):
            data[sheet][col] = data[sheet][col].dt.strftime('%d/%m/%Y')
    
    return data, valid_sheets

# Configuração do Streamlit
st.set_page_config(page_title="Dashboard Jurídico", layout="wide")
st.title("📊 Dashboard Jurídico Interativo")

# Upload de arquivo
uploaded_file = st.file_uploader("Carregue a planilha Excel", type=["xlsx"])

if uploaded_file:
    data, sheets = load_data(uploaded_file)
    
    if data is None:
        st.stop()
    
    st.success("Dados carregados com sucesso!")
    
    # Criar abas para cada planilha disponível
    tab_names = st.tabs(sheets)
    
    for i, sheet in enumerate(sheets):
        with tab_names[i]:
            df = data[sheet]
            st.subheader(f"Visualização da Tabela - {sheet}")
            st.dataframe(df)
            
            # Criar filtros dinâmicos sem pré-seleção
            st.sidebar.header(f"Filtros - {sheet}")
            columns = df.columns.tolist()
            filters = {}
            for col in columns:
                unique_values = df[col].dropna().unique().tolist()
                filters[col] = st.sidebar.multiselect(f"Filtrar {col}", unique_values, key=f"{sheet}_{col}")
            
            # Aplicar filtros apenas se houver seleção
            filtered_df = df.copy()
            for col, values in filters.items():
                if values:
                    filtered_df = filtered_df[filtered_df[col].isin(values)]
            
            # Exibir dados filtrados
            st.subheader("Dados Filtrados")
            st.dataframe(filtered_df)
            
            # Criar gráficos dinâmicos
            numeric_columns = filtered_df.select_dtypes(include=['number']).columns.tolist()
            if numeric_columns:
                st.subheader("Gráficos Interativos")
                x_axis = st.selectbox("Escolha a variável X", numeric_columns, key=f"{sheet}_x")
                y_axis = st.selectbox("Escolha a variável Y", numeric_columns, key=f"{sheet}_y")
                
                fig, ax = plt.subplots()
                ax.scatter(filtered_df[x_axis], filtered_df[y_axis])
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                ax.set_title(f"Relação entre {x_axis} e {y_axis} - {sheet}")
                st.pyplot(fig)
            
            # Botão para exportar dados filtrados
            st.download_button(
                label="Baixar dados filtrados",
                data=filtered_df.to_csv(index=False),
                file_name=f"dados_filtrados_{sheet}.csv",
                mime="text/csv"
            )
