# Configuração da Página DEVE ser o primeiro comando
import streamlit as st
st.set_page_config(
    page_title="Telemarketing Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# Tema do Seaborn para melhorar o visual dos gráficos
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)


# Função para ler os dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=";")
    except:
        return pd.read_excel(file_data)


# Função para multiseleção
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if "all" in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


# Função para converter DataFrame para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()


# Função principal
def main():
    # Título principal
    st.write("# Telemarketing Analysis")
    st.markdown("---")

    # Imagem na barra lateral
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image, use_container_width=True)

    # Upload do arquivo
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=["csv", "xlsx"])

    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        # Tabela antes dos filtros
        st.write("## Antes dos filtros")
        st.dataframe(bank_raw.head())

        with st.sidebar.form(key="filter_form"):
            # Opções de filtros
            graph_type = st.radio("Tipo de gráfico:", ("Barras", "Pizza"))

            # Idades
            min_age, max_age = int(bank.age.min()), int(bank.age.max())
            idades = st.slider("Idade", min_age, max_age, (min_age, max_age))

            # Profissões
            jobs_list = bank.job.unique().tolist() + ["all"]
            jobs_selected = st.multiselect("Profissão", jobs_list, ["all"])

            # Estado civil
            marital_list = bank.marital.unique().tolist() + ["all"]
            marital_selected = st.multiselect("Estado civil", marital_list, ["all"])

            # Outros filtros
            filters = {
                "default": bank.default.unique().tolist() + ["all"],
                "housing": bank.housing.unique().tolist() + ["all"],
                "loan": bank.loan.unique().tolist() + ["all"],
                "contact": bank.contact.unique().tolist() + ["all"],
                "month": bank.month.unique().tolist() + ["all"],
                "day_of_week": bank.day_of_week.unique().tolist() + ["all"],
            }

            filter_selections = {}
            for key, values in filters.items():
                filter_selections[key] = st.multiselect(f"{key.capitalize()}?", values, ["all"])

            # Aplicação dos filtros
            submit_button = st.form_submit_button("Aplicar")
            if submit_button:
                bank = (
                    bank.query("age >= @idades[0] and age <= @idades[1]")
                    .pipe(multiselect_filter, "job", jobs_selected)
                    .pipe(multiselect_filter, "marital", marital_selected)
                )
                for col, selected in filter_selections.items():
                    bank = bank.pipe(multiselect_filter, col, selected)

        # Tabela após os filtros
        st.write("## Após os filtros")
        st.dataframe(bank.head())

        # Download do Excel
        df_xlsx = to_excel(bank)
        st.download_button(
            label="📥 Download tabela filtrada em EXCEL",
            data=df_xlsx,
            file_name="bank_filtered.xlsx",
            mime="application/vnd.ms-excel",
        )

        # Gráficos
        st.markdown("---")
        st.write("## Proporção de aceite")

        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True) * 100
        bank_target_perc = bank.y.value_counts(normalize=True) * 100

        if graph_type == "Barras":
            sns.barplot(x=bank_raw_target_perc.index, y=bank_raw_target_perc.values, ax=ax[0])
            ax[0].set_title("Dados Brutos")
            sns.barplot(x=bank_target_perc.index, y=bank_target_perc.values, ax=ax[1])
            ax[1].set_title("Dados Filtrados")
        else:
            bank_raw_target_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[0])
            ax[0].set_title("Dados Brutos")
            bank_target_perc.plot(kind="pie", autopct="%.2f%%", ax=ax[1])
            ax[1].set_title("Dados Filtrados")

        st.pyplot(fig)


if __name__ == "__main__":
    main()
