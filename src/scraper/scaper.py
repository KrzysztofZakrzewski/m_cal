import os
import logging
import requests
from urllib.parse import urlparse
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from src.dirs import DIRS

raw_pdf_PATH = DIRS["pdf"]
pdf_path_to_create_text = raw_pdf_PATH/'352978-tabela-wo-8-11-2023-mop.pdf'

# url = "https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf"

# parsed_url = urlparse(url)
# filename = os.path.basename(parsed_url.path)  # take the name "352978-tabela-wo-8-11-2023-mop.pdf"

LOGS_PATH = DIRS["logs"]
LOGS_FILE = LOGS_PATH / 'logs.log'

logging.basicConfig(
    filename=str(LOGS_FILE),  # will create the logs folder (if it doesn't exist) and the errors.log file | str ensures compatibility with older Python
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# BASE_URL = 'https://cdn.mcdonalds.pl/uploads/20250910144011/352978-tabela-wo-8-11-2023-mop.pdf'

def scrape_pdf(url, filename):
    try:
        url
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