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


# PDF
if "pdf_path" not in st.session_state:
    pdf_path = Path("./pdf")
    pdf_path.mkdir(parents=True, exist_ok=True)
    st.session_state["pdf_path"] = pdf_path


# Logs
os.makedirs("logs", exist_ok=True)
LOGS_PATH = Path("logs")
LOGS_FILE = LOGS_PATH / 'logs.log'





url = "https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf"

parsed_url = urlparse(url)
filename = os.path.basename(parsed_url.path)  # wyciągnie "352978-tabela-wo-8-11-2023-mop.pdf"

# print(filename)

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