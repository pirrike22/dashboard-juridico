import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Função para carregar dados e garantir formatação correta de datas
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
    
    data = {matched_sheets[sheet]: pd.read_excel(file, sheet_name=matched_sheets[sheet], parse_dates=True) for sheet in matched_sheets}
    
    # Ajustar formatação de datas e ordená-las corretamente
    for sheet in data:
        for col in data[sheet].columns:
            if "data" in col.lower() or data[sheet][col].dtype == 'datetime64[ns]':
                data[sheet][col] = pd.to_datetime(data[sheet][col], errors='coerce')
                data[sheet] = data[sheet].sort_values(by=[col], ascending=True)
                
                if sheet == "Audiência":
                    data[sheet][col] = data[sheet][col].dt.strftime('%d/%m/%Y %H:%M')
                else:
                    data[sheet][col] = data[sheet][col].dt.strftime('%d/%m/%Y')
    
    return data, valid_sheets

# Função para filtrar por período
def filter_by_period(df):
    today = datetime.date.today()
    start_week = today - datetime.timedelta(days=today.weekday())
    end_week = start_week + datetime.timedelta(days=6)
    next_week_start = end_week + datetime.timedelta(days=1)
    next_week_end = next_week_start + datetime.timedelta(days=6)
    next_15_days = today + datetime.timedelta(days=15)
    
    date_columns = [col for col in df.columns if "data" in col.lower()]
    if not date_columns:
        return df  # Retorna o DataFrame sem filtro se não encontrar colunas de data
    
    date_column = date_columns[0]
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce', format='%d/%m/%Y')
    
    period_filter = st.sidebar.radio("Filtrar por período:", ["Todos", "Essa semana", "Semana seguinte", "Próximos 15 dias"], key=f"{date_column}_filter")
    
    if period_filter == "Essa semana":
        df = df[(df[date_column] >= pd.to_datetime(start_week)) & (df[date_column] <= pd.to_datetime(end_week))]
    elif period_filter == "Semana seguinte":
        df = df[(df[date_column] >= pd.to_datetime(next_week_start)) & (df[date_column] <= pd.to_datetime(next_week_end))]
    elif period_filter == "Próximos 15 dias":
        df = df[(df[date_column] >= pd.to_datetime(today)) & (df[date_column] <= pd.to_datetime(next_15_days))]
    
    df[date_column] = df[date_column].dt.strftime('%d/%m/%Y')
    return df

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
        if sheet not in data:
            st.warning(f"A aba '{sheet}' não pôde ser carregada corretamente.")
            continue
        
        with tab_names[i]:
            df = data[sheet]
            st.subheader(f"Visualização da Tabela - {sheet}")
            
            df = filter_by_period(df)
            
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
