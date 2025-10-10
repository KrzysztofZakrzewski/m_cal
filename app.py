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
import logging
import os
from urllib.parse import urlparse

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

if "OPENAI_API_KEY" not in os.environ:
    st.error("Nie znaleziono klucza API OpenAI.")
    st.stop()

def get_openai_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])



###################
### MAKE DISR
from dirs import DIRS
from utils import change_receipt_for_binary
from receipt_processing import loading_data_from_receipt_into_json, parsing_data_from_receipt_raw_into_json
# from paths import PATHS

##############
## PATHS

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
# if 'img_receipt_PATH' not in st.session_state:
#     st.session_state['img_receipt_PATH'] = None
img_receipt_PATH = Path("./receipt")
temporary_json_from_receipt_PATH = Path('temporary_json_from_receipt')
temporary_json_parsed_PATH = Path('temporary_json_parsed')


# Session State Dynamic path
if 'user_receipt' not in st.session_state:
    st.session_state['user_receipt'] = None



url = "https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf"

parsed_url = urlparse(url)
filename = os.path.basename(parsed_url.path)  # wyciągnie "352978-tabela-wo-8-11-2023-mop.pdf"

# LOGS_FILE = DIRS["logs"] / "logs.log"
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

def scrape_pdf(url):
    try:
        url = BASE_URL
        response = requests.get(
            url,
            # params=params,
            headers={"version":"2"},

            #timeout for 5 sek
            timeout=5
        )


        response.raise_for_status()

        # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pdf_name=filename

        with open(raw_pdf_PATH/pdf_name, 'wb') as f:
            f.write(response.content)
        logger.info(f'💚 udało się pobrać plik pfd {pdf_name}')
    except HTTPError as e:
        if 400 <= response.status_code < 500:
            logger.error(f'❌Błąd klienta {response.status_code}:{response.reason} dla strony..')
            return
        elif 500 <= response.status_code < 600:
            logger.warning(f'⚠️Błąd serwera {response.status_code}:{response.reason}')
        else:
            reason = getattr(response, 'reason', "brak opisu")
            logger.error(f'❌ Inny błąt HTTP {response.status_code}:{reason}')

    except (ConnectionAbortedError, Timeout) as e:
        logger.warning(f'🌐 Problem z połączeniem/timeout na stronie: {e}')
    
    except OSError as e:
        logger.error(f'❓ Niespodziewany wyjątek przy stronie, {e.__class__.__name__}: {e}')

    else:
    
        return None
    

# # Converting receipt img to bytes

# def change_receipt_for_binary(receipt_path):
#     with open(receipt_path, "rb") as f:
#         receipt_data = base64.b64encode(f.read()).decode('utf-8')

#     return f"data:image/jpg;base64,{receipt_data}"
    
# scrape_pdf(BASE_URL)

st.title("Dodawanie zdjęć")
if 'img_receipt_PATH' not in st.session_state:
    st.session_state['img_receipt_PATH'] = None
# IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Field for uploading a photo
uploaded_file = st.file_uploader("Wybierz zdjęcie", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Delete all old files in the folder
    for old_file in img_receipt_PATH.iterdir():
        if old_file.is_file():
            old_file.unlink()

    # Saving a photo to a directory
        if 'user_receipt' not in st.session_state:
            st.session_state['user_receipt'] = None

    save_path = img_receipt_PATH / "user_receipt.jpg"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state['user_receipt'] = save_path
    
    st.success(f"wybrano zdjęcie: {uploaded_file.name}")
    st.image(save_path, caption=uploaded_file.name, width=150)
    # st.image(save_path, caption="Twoje zdjęcie", use_container_width=True)

    # prepared_receipt = prepare_receipt_for_openai(user_receipt)
    # st.json(prepared_receipt)
    if st.button("Proceduj"):
        if 'user_receipt' in st.session_state and st.session_state['user_receipt']:
            
            st.session_state['prepared_receipt'] = change_receipt_for_binary(st.session_state['user_receipt'])
            st.success("Obraz przetworzony na bajty i zapisany w session_state")
            loading_data_from_receipt_into_json(st.session_state['prepared_receipt'])
            parsing_data_from_receipt_raw_into_json()
            # st.json(prepared_receipt) 
        else:
            st.warning("Najpierw wgraj zdjęcie!")