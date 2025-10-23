import pandas as pd
from pathlib import Path
import numpy as np
import logging
import os
from io import StringIO
from urllib.parse import urlparse # scraper
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
load_dotenv()



# Ensure the OpenAI API key is available in environment variables before proceeding.
# If missing, display an error message and stop the Streamlit app to prevent further execution.
if "OPENAI_API_KEY" not in os.environ:
    st.error("Nie znaleziono klucza API OpenAI.")
    st.stop()


# Helper function to initialize and return an OpenAI client using the stored API key.
def get_openai_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ===============================================================
# Local module imports — core project components and helper functions
# ===============================================================

# Imports from custom project modules:
# - dirs: paths and directory management
# - base_dataframe: main dataframe creation and merging logic
# - utils: general-purpose helpers (file conversion, calorie table loading)
# - receipt_processing: OCR and JSON parsing of receipts
# - chars: visualization utilities (Plotly charts
from src.dirs import DIRS
from src.scraper.scaper import (
    scrape_pdf
)
from src.data.base_dataframe import (
    create_main_df,
    receipt_of_user_to_dataframe,
    append_user_df_to_main_df
)
from src.utils.utils import (
    change_receipt_for_binary,
    reading_calories_table, delete_recipt_img, 
    delete_temporary_jsons
) 
from src.receipt_processing.receipt_processing import (
    loading_data_from_receipt_into_json,
    parsing_data_from_receipt_raw_into_json
)
from src.pltos.chars import (
    calorie_distribution_per_product_chart,
    total_calories_consumed_each_month_chart,
    distribution_of_money_spent_per_product_chart,
    total_money_spend_each_month_chart
)
from src.pdf_parser.pdf_parser import (
    
    extracting_text_from_pdf, 
    new_caloris_table_from_pdf_json,
    merge_json_files
)
from src.data.data_export import (
    download_csv_button,
    to_excel
)
from src.ai_trainer.ai_calorie_trainer import (
    ask_ai
)
# ===============================================================
# 📦 PATHS
# ===============================================================

# LOGS
LOGS_PATH = Path("logs")
LOGS_FILE = LOGS_PATH / 'logs.log'

# PDF
pdf_path_to_create_text = DIRS['pdf']/'352978-tabela-wo-8-11-2023-mop.pdf'

# DataFrame
main_dataframe_PATH = Path("main_dataframe")

# Calories Table in json
json_calories_table_PATH = Path('json_calories_table')

# Receipt
img_receipt_PATH = Path("./receipt")
temporary_json_from_receipt_PATH = Path('temporary_json_from_receipt')
temporary_json_parsed_PATH = Path('temporary_json_parsed')

# ===============================================================
# 📦 SESSION STATE MANAGEMENT — prevent data loss between reruns
# ===============================================================

if 'user_receipt' not in st.session_state:
    st.session_state['user_receipt'] = None

st.title("Dodawanie zdjęć")
if 'img_receipt_PATH' not in st.session_state:
    st.session_state['img_receipt_PATH'] = None

if "path_for_calories_table" not in st.session_state:
    st.session_state["path_for_calories_table"] = None

if "calories" not in st.session_state:
    st.session_state["calories"] = None

if "path_for_receipt_parsed" not in st.session_state:
    st.session_state["path_for_receipt_parsed"] = None

if "main_df" not in st.session_state:
    # st.session_state["main_df"] = None
    st.session_state["main_df"] = create_main_df()

if "df" not in st.session_state:
    st.session_state["df"] = None

# name of csv uploded by user
if "name_of_uloded_df" not in st.session_state:
    st.session_state["name_of_uloded_df"] = None

# user_main_df_name
if "user_main_df_name" not in st.session_state:
    st.session_state["user_main_df_name"] = "moja_baza"

# Wyświetlaj ramkę danych POZA blokiem przycisku
if "data_ready" not in st.session_state:
    st.session_state["data_ready"] = False

if 'uploaded_file_for_csv' not in st.session_state:
    st.session_state['uploaded_file_for_csv'] = None

if "url_input" not in st.session_state:
    st.session_state["url_input"] = None

if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None 

# Hardcore the url adres for pdf
url = "https://cdn.mcdonalds.pl/uploads/20251021094322/352978-tabela-wo-8-11-2023-mop.pdf?openOutsideMcd=true"

# The user can add a new calorie table if necessary.
url_x= st.text_input("Podaj adres nowej tabeli kalorycznej", value=url)

parsed_url = urlparse(url_x)
filename = os.path.basename(parsed_url.path)  # take the name "352978-tabela-wo-8-11-2023-mop.pdf"

LOGS_PATH = Path("logs")
LOGS_FILE = LOGS_PATH / 'logs.log'

logging.basicConfig(
    filename=str(LOGS_FILE),  # will create the logs folder (if it doesn't exist) and the errors.log file | str ensures compatibility with older Python
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


BASE_URL = 'https://cdn.mcdonalds.pl/uploads/20251020194126/352978-tabela-wo-8-11-2023-mop.pdf?openOutsideMcd=true'

#######
##Functions

constant_cal_table = DIRS['json_calories_table']/'offer_classic.json'
temporary_cal_table = DIRS['json_calories_table']/'offer_classic_temporary.json'

if st.button('Pobierz pdf'):
    scrape_pdf(url_x, filename)

if st.button('Sparsuj PDF'):
    text = extracting_text_from_pdf(pdf_path_to_create_text)
    new_cal_table = new_caloris_table_from_pdf_json(text)
    merge_json_files(constant_cal_table, temporary_cal_table)

# ===============================================================
# 📦 LOAD data frame
# If the user already has a saved dataset (CSV), 
# they can upload it here for further analysis.
# ===============================================================
st.session_state['uploaded_file_for_csv'] = st.file_uploader("⬇️ Wybierz plik CSV, jeśli już posiadasz", type=["csv"])


if st.session_state['uploaded_file_for_csv'] is not None:
    # 1️⃣ Loading CSV into DataFrame directly into session_state
    st.session_state["main_df"] = pd.read_csv(StringIO(st.session_state['uploaded_file_for_csv'].getvalue().decode("utf-8")))

    # 2️⃣ File name preservation
    base_name = Path(st.session_state['uploaded_file_for_csv'].name).stem
    st.session_state["user_main_df_name"] = base_name

    # 3️⃣ Converting columns to the appropriate types
    df = st.session_state["main_df"]

    df["produkt"] = df["produkt"].astype("string")
    df["ilość"] = df["ilość"].astype("Int64")
    df["kcal_na_szt"] = df["kcal_na_szt"].astype("Int64")
    df["kcal_razem"] = df["kcal_razem"].astype("Int64")
    df["cena_na_szt"] = df["cena_na_szt"].astype("float")
    df["cena_razem"] = df["cena_razem"].astype("float")
    df["łączna kwota za paragon"] = df["łączna kwota za paragon"].astype("float")
    df["miasto"] = df["miasto"].astype("string")
    df["ulica"] = df["ulica"].astype("string")

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # 4️⃣ Assigning back to session_state
    st.session_state["main_df"] = df

    st.success(f"✅ Wczytano plik {base_name} i przypisano odpowiednie typy kolumn")

# ===============================================================
# 📦 Uploading a photo of the prescription
# ===============================================================
uploaded_receipt_image = st.file_uploader("Wybierz zdjęcie paragonu aby dodać nowe dane", type=["png", "jpg", "jpeg"])

# ===============================================================
# 📦 PROCESING THE IMAGE IN DATAFRAME
# ===============================================================
if uploaded_receipt_image is not None:
    # Delete all old files in the folder
    for old_file in img_receipt_PATH.iterdir():
        if old_file.is_file():
            old_file.unlink()

    # Saving a photo to a directory
        if 'user_receipt' not in st.session_state:
            st.session_state['user_receipt'] = None

    save_path = img_receipt_PATH / "user_receipt.jpg"
    with open(save_path, "wb") as f:
        f.write(uploaded_receipt_image.getbuffer())
    st.session_state['user_receipt'] = save_path
    
    st.success(f"wybrano zdjęcie: {uploaded_receipt_image.name}")
    st.image(save_path, caption=uploaded_receipt_image.name, width=150)
    # st.image(save_path, caption="Twoje zdjęcie", use_container_width=True)

    # PROCESING
    if st.button("Proceduj"):
        if 'user_receipt' in st.session_state and st.session_state['user_receipt']:
            
            st.session_state['prepared_receipt'] = change_receipt_for_binary(st.session_state['user_receipt'])
            # st.info("Przetwarzam obraz")
            # Loading data from recitp
            loading_data_from_receipt_into_json(st.session_state['prepared_receipt'])

            # Parsing to proper json base
            parsing_data_from_receipt_raw_into_json()

            # Reading calories table
            st.session_state["path_for_calories_table"] = DIRS['json_calories_table']/'offer_classic.json'
            st.session_state["calories"] = reading_calories_table(st.session_state["path_for_calories_table"])

            # Add data to dataframe
            st.session_state["path_for_receipt_parsed"] = DIRS["temporary_json_parsed"] / "receipt_parsed.json"
            st.session_state["df"] = receipt_of_user_to_dataframe(st.session_state['path_for_receipt_parsed'], st.session_state["calories"])
            st.success("Obraz przetworzony")


            st.session_state["data_ready"] = True

        else:
            st.warning("Najpierw wgraj zdjęcie!")

# ===============================================================
# 📦 Add dataframe from user do main_df
# ===============================================================
if st.session_state.get("data_ready", False):
    st.dataframe(st.session_state["df"])

    if st.button("Dodaj do swojej bazy danych"):
        st.session_state["main_df"] = append_user_df_to_main_df(
            st.session_state["main_df"],
            st.session_state["df"]
        )

        # ------ Cleanig recipt folder after procesing
        delete_recipt_img(st.session_state['user_receipt'])
        delete_temporary_jsons(DIRS['temporary_json_from_receipt'])
        delete_temporary_jsons(DIRS['temporary_json_parsed'])
        st.success("Dodano nowe dane")


# Always show master database
st.text('')
st.dataframe(st.session_state["main_df"], height=200)

# ===============================================================
# 💾 Dowland as CSV
# ===============================================================

# Prepare and export the current DataFrame as a CSV file:
# 1. Display a text input that allows the user to specify or update the dataset name.
#    The entered name is stored in Streamlit's session state under 'user_main_df_name'.
# 2. Call the `download_csv_button` utility function to create a Streamlit download button.
#    The function handles converting the DataFrame to CSV in memory and triggers file download
#    using the provided dataset name as the file name.

# Input to file name
st.session_state["user_main_df_name"] = st.text_input(
    "Podaj nazwę dla swojego zestawu danych:",
    value=st.session_state["user_main_df_name"])

# Download dataframe with new data

download_csv_button(
    df=st.session_state["main_df"],
    file_name=st.session_state["user_main_df_name"],
    label="💾 Pobierz dane jako CSV"
)

# ===============================================================
# 💾 Dowland as Exel
# ===============================================================

# Render a Streamlit download button for exporting a DataFrame as a CSV file:
# - `df`: the DataFrame to export (here, the main DataFrame from session state).
# - `file_name`: the name that will be suggested for the downloaded CSV file.
# - `label`: the text shown on the Streamlit button.
# 
# When the user clicks the button, the DataFrame is converted to a CSV in memory
# and offered for download without writing a file to disk.

if st.button("💾 Zapisz jako Excel"):
    excel_data = to_excel(st.session_state['main_df'])
    st.download_button(
        label="⬇️ Pobierz plik Excel",
        data=excel_data,
        file_name=st.session_state['user_main_df_name'],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ===============================================================
# 🔍 FILTERS
# ===============================================================

# Copying modified main_df
DATA = st.session_state['main_df']

# ===============================================================
# 🔍 SIDEBAR SELECTOR
# Creating arguments only for foltered_df BASE ON main_df
filtered_df = DATA.copy()

with st.sidebar:
    st.header('🔍 Filtry')
    # Products
    product = st.sidebar.multiselect("Produkt", ["(Wszystkie)"] + list(DATA["produkt"].dropna().unique()))
    if "(Wszystkie)" not in product and product:
        filtered_df = DATA[filtered_df["produkt"].isin(product)]

    # Mulitiple amount of one product
    amount_of_products = st.multiselect('Ilość pojedyńczego produktu', ["(Wszystkie)"] + list(DATA["ilość"].dropna().unique()))
    if "(Wszystkie)" not in amount_of_products and amount_of_products:
        filtered_df = filtered_df[filtered_df["ilość"].isin(amount_of_products)]

    # Kalories of one product
    single_kalc = st.sidebar.multiselect('Pojedyńcze kaloriw', ["(Wszystkie)"] + list(DATA["kcal_na_szt"].dropna().unique()))
    if "(Wszystkie)" not in single_kalc and single_kalc:
        filtered_df = filtered_df[filtered_df["kcal_na_szt"].isin(single_kalc)]

    # Kcal for one type of product per receipt
    kcal_for_one_type_of_product_per_receipt = st.sidebar.multiselect("Kalorie razem",["(Wszystkie)"] + list(DATA["kcal_razem"].dropna().unique()))
    if "(Wszystkie)" not in kcal_for_one_type_of_product_per_receipt and kcal_for_one_type_of_product_per_receipt:
        filtered_df = filtered_df[filtered_df["kcal_razem"].isin(kcal_for_one_type_of_product_per_receipt)]

    # Price for one product
    price_for_pice = st.sidebar.multiselect("Cena za sztukę",["(Wszystkie)"] + list(DATA["cena_na_szt"].dropna().unique()))
    if "(Wszystkie)" not in price_for_pice and price_for_pice:
        filtered_df = filtered_df[filtered_df["cena_na_szt"].isin(price_for_pice)]

    # # Total price for this same products
    total_price_for_this_same_products_in_one_recepit = filtered_df["cena_razem"].dropna()

    if not total_price_for_this_same_products_in_one_recepit.empty:
        min_price = float(total_price_for_this_same_products_in_one_recepit.min())
        max_price = float(total_price_for_this_same_products_in_one_recepit.max())

        if min_price == max_price:
            selected_range = (min_price, max_price)
        else:
            selected_range = st.slider(
                "Zakres cen za te same produkty na jednym paragonie",
                min_value=round(min_price, 2),
                max_value=round(max_price, 2),
                value=(round(min_price, 2), round(max_price, 2)),
                step=0.5,
            )
        filtered_df = filtered_df[
            (filtered_df["cena_razem"] >= selected_range[0]) &
            (filtered_df["cena_razem"] <= selected_range[1])
        ]
    else:
        st.warning("Brak danych w kolumnie 'cena_razem'.")


    # Total amount for receipt
    total_amount_for_receipt = filtered_df["łączna kwota za paragon"].dropna()

    if not total_amount_for_receipt.empty:
        min_amount = float(total_amount_for_receipt.min())
        max_amount = float(total_amount_for_receipt.max())

        if min_amount < max_amount:
            selected_range = st.slider(
                "Zakres łącznej kwoty za paragon (zł)",
                min_value=round(min_amount, 2),
                max_value=round(max_amount, 2),
                value=(round(min_amount, 2), round(max_amount, 2)),
                step=0.5,
            )
        else:
            st.write(f"📊 Wszystkie paragony mają tę samą kwotę: {min_amount} zł")
            selected_range = (min_amount, max_amount)

        filtered_df = filtered_df[
            (filtered_df["łączna kwota za paragon"] >= selected_range[0]) &
            (filtered_df["łączna kwota za paragon"] <= selected_range[1])
            ]

    else:
        st.warning("Brak danych w kolumnie 'łączna kwota za paragon'.")

    # City
    city = st.sidebar.multiselect('Miasto', ["(Wszystkie)"] + list(DATA["miasto"].dropna().unique()))
    if "(Wszystkie)" not in city and city:
        filtered_df = filtered_df[filtered_df["miasto"].isin(city)]

    # Street
    stret = st.sidebar.multiselect('Ulica', DATA['ulica'].unique())
    if "(Wszystkie)" not in stret and stret:
        filtered_df = filtered_df[filtered_df["ulica"].isin(stret)]

    # Date
    st.header("📅 Zakres dat")
    date = DATA["data"].dropna()

    if not date.empty:
        # convert to datetime (just in case)
        date = pd.to_datetime(date)

        min_data = date.min().date()
        max_data = date.max().date()

        selected_date_range = st.date_input(
            "Wybierz zakres dat",
            value=(min_data, max_data),
            min_value=min_data,
            max_value=max_data,
            format="YYYY-MM-DD"
        )

        if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            filtered_df = filtered_df[
                (filtered_df["data"].dt.date >= start_date) &
                (filtered_df["data"].dt.date <= end_date)
            ]
            st.write(f"📊 Wybrany zakres: **{start_date} – {end_date}**")
        else:
            st.warning("Wybierz poprawny zakres dat (od – do).")
    else:
        st.warning("Brak danych w kolumnie 'data'.")

# ===============================================================
# 📦 Display after filters
# ===============================================================
st.markdown("### 📊 Wyniki filtrowania po produkcie")
st.dataframe(filtered_df, use_container_width=True, height=200)
st.write(f"🔹 Liczba rekordów: {len(filtered_df)}")

# Creating arguments only for charts BASE ON filtered_df BASE ON main_df
bars_df = filtered_df

st.markdown("<h2>🍗Podsumowanie kalori</h2>", unsafe_allow_html=True)

# ===============================================================
# 📦 Tabs for barcharts
# ===============================================================
# Organize charts into tabs by category to facilitate comparison:
# - The first set of tabs (tab1, tab2, tab3) displays calorie-related charts
#   grouped by Products, Months, and Cities.
# - The second set of tabs (tab4, tab5, tab6) displays financial charts
#   grouped by the same categories.
# This tabbed layout allows users to quickly compare calorie intake and 
# spending patterns using the same filters for consistency.

tab1, tab2, tab3 = st.tabs(["Produkty", "Mieiące", "Miasta"])

with tab1:
    calorie_distribution_per_product_chart(bars_df)
with tab2:
    total_calories_consumed_each_month_chart(bars_df)


st.markdown("<h2>💰Podsumowanie finansów</h2>", unsafe_allow_html=True)

tab4, tab5, tab6 = st.tabs(["Produkty", "Mieiące", "Miasta"])
with tab4:
    distribution_of_money_spent_per_product_chart(bars_df)
with tab5:
    total_money_spend_each_month_chart(bars_df)

# ===============================================================
# 💾 Dowland filtered data as CSV
# ===============================================================

# Name of the filtred file, defolt with "przefiltrowany"
filtered_name = st.text_input("Podaj nazwę dla przefiltrowanego zestawu danych:", st.session_state["user_main_df_name"]+" przefiltrowany")

# Dowland to csv button
download_csv_button(
    df=filtered_df,
    file_name=filtered_name,
    label="⬇️ Pobierz przefiltrowane dane jako CSV"
)

# ===============================================================
# 💾 Dowland filtered data as EXEL
# ===============================================================

# Dowland to exel button
if st.button("💾 Zapisz przefiltorane dane jako Excel"):
    excel_data = to_excel(filtered_df)
    st.download_button(
        label="⬇️ Pobierz plik Excel",
        data=excel_data,
        file_name=filtered_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

total_calories_for_pumps = filtered_df["kcal_razem"].sum()
st.session_state["total_calories_for_pumps"] = total_calories_for_pumps  # zapis do session_state

# Wyświetlenie metryki
st.metric("Łączna liczba zjedzonych kalorii", f"{st.session_state['total_calories_for_pumps']:.0f} kcal")

# --- Dane użytkownika ---
# jeśli pole jeszcze nie istnieje, utwórz je w session_state
if "user_info" not in st.session_state:
    st.session_state["user_info"] = ""

# input do wpisania np. "mężczyzna, 80kg, 30 lat"
st.session_state["user_info"] = st.text_input(
    "Podaj: płeć, wagę, wiek, wzrost",
    value=st.session_state["user_info"]
)

st.write("👤 Dane użytkownika:", st.session_state["user_info"])



if st.button('Podaj plan treningowy'):
    answer = ask_ai(st.session_state["user_info"],total_calories_for_pumps)
    st.write(answer)