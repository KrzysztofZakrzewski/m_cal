import json
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
#add Path
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime
import re
import time
import random
import plotly.express as px
import logging
import os
import io
from io import StringIO
from urllib.parse import urlparse # scraper
import matplotlib.pyplot as plt

import base64
from getpass import getpass

from IPython.display import Image, display, FileLink,IFrame
import instructor
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

import pdfplumber
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
from dirs import DIRS
from scaper import scrape_pdf
from base_dataframe import create_main_df, receipt_of_user_to_dataframe, append_user_df_to_main_df
from utils import change_receipt_for_binary, reading_calories_table
from receipt_processing import loading_data_from_receipt_into_json, parsing_data_from_receipt_raw_into_json
from chars import calorie_distribution_per_product_chart, total_calories_consumed_each_month_chart, distribution_of_money_spent_per_product_chart, total_money_spend_each_month_chart

# ===============================================================
# 📦 PATHS
# ===============================================================

# LOGS
LOGS_PATH = Path("logs")
LOGS_FILE = LOGS_PATH / 'logs.log'

# PDF
raw_pdf_PATH = Path("./pdf")
raw_pdf_PATH.mkdir(parents=True, exist_ok=True)
pdf_path_to_create_text = raw_pdf_PATH/'352978-tabela-wo-8-11-2023-mop.pdf'

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

if "analyze_mode" not in st.session_state:
    st.session_state["analyze_mode"] = False



url = "https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf"

parsed_url = urlparse(url)
filename = os.path.basename(parsed_url.path)  # take the name "352978-tabela-wo-8-11-2023-mop.pdf"

LOGS_PATH = Path("logs")
LOGS_FILE = LOGS_PATH / 'logs.log'

logging.basicConfig(
    filename=str(LOGS_FILE),  # will create the logs folder (if it doesn't exist) and the errors.log file | str ensures compatibility with older Python
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


BASE_URL = 'https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf'

#######
##Functions
if st.button('Pobierz pdf'):
    scrape_pdf(url)


# def scrape_pdf(url):
#     try:
#         url = BASE_URL
#         response = requests.get(
#             url,
#             # params=params,
#             headers={"version":"2"},

#             #timeout for 5 sek
#             timeout=5
#         )


#         response.raise_for_status()

#         # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         pdf_name=filename

#         with open(raw_pdf_PATH/pdf_name, 'wb') as f:
#             f.write(response.content)
#         logger.info(f'💚 udało się pobrać plik pfd {pdf_name}')
#     except HTTPError as e:
#         if 400 <= response.status_code < 500:
#             logger.error(f'❌Błąd klienta {response.status_code}:{response.reason} dla strony..')
#             return
#         elif 500 <= response.status_code < 600:
#             logger.warning(f'⚠️Błąd serwera {response.status_code}:{response.reason}')
#         else:
#             reason = getattr(response, 'reason', "brak opisu")
#             logger.error(f'❌ Inny błąt HTTP {response.status_code}:{reason}')

#     except (ConnectionAbortedError, Timeout) as e:
#         logger.warning(f'🌐 Problem z połączeniem/timeout na stronie: {e}')
    
#     except OSError as e:
#         logger.error(f'❓ Niespodziewany wyjątek przy stronie, {e.__class__.__name__}: {e}')

#     else:
    
#         return None

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
            st.session_state["path_for_calories_table"] = DIRS['json_calories_table']/'calories_table_352978-tabela-wo-8-11-2023-mop.json'
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
        st.success("Dodano nowe dane")

# Always show master database
st.text('')
st.dataframe(st.session_state["main_df"], height=200)

# Prepare the current DataFrame for CSV export:
# 1. Retrieve the main DataFrame from Streamlit's session state.
# 2. If the user has uploaded a CSV, display a text input to allow them
#    to specify a name for their dataset, and overdrive the name it in session state.
# 3. Convert the DataFrame to a CSV string in memory using io.StringIO,
#    without including the index column, and store the CSV content in csv_data.
csv_to_save = st.session_state["main_df"]

# Input to file name (only if user has not uploaded CSV)
if st.session_state['uploaded_file_for_csv']:
    st.session_state["user_main_df_name"] = st.text_input(
        "Podaj nazwę dla swojego zestawu danych:",
        value=st.session_state["user_main_df_name"]
        # key="user_main_df_name_input"
    )
buffer = io.StringIO()
csv_to_save.to_csv(buffer, index=False)
csv_data = buffer.getvalue()

#Download dataframe with new data
st.download_button(
    label="💾 Pobierz dane jako CSV",
    data=csv_data,
    file_name=f"{st.session_state['user_main_df_name']}.csv",
    mime="text/csv"
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
st.dataframe(filtered_df, use_container_width=True)
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