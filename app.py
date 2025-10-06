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
from openai import OpenAI

import pdfplumber
import streamlit as st



###################
### MAKE DISR
from dirs import DIRS
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
temporary_json_from_receipt_PATH = Path('temporary_json_from_receipt')
temporary_json_parsed_PATH = Path('temporary_json_parsed')



# url = "https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf"

# parsed_url = urlparse(url)
# filename = os.path.basename(parsed_url.path)  # wyciągnie "352978-tabela-wo-8-11-2023-mop.pdf"

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
    
# scrape_pdf(BASE_URL)