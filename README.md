# FitTrack AI 🏋️‍♂️
## Aplikacja do mierzenia kalorii nabytych w McDonaldzie
( Proof of concept )

# Aplikacja stworzona do użycia tylko w celach edukacyjnych twórcy

- Inteligentna aplikacja do analizy danych żywieniowych i generowania planów treningowych na podstawie paragonów i plików PDF.

## Features
- 📄 Mozliwość pobrania pliku PDF z "tabelą wartości odżywczych" ze strony McDonalds  
- ✍🏻 Stworzenie pliku json z wartościami kalorycznymi dla poszczególnych produktów ze PDF z "tabelą wartości odżywczych" lub dodanie nowych do istniejących  
- 📷 Zczytanie informacji i utworzenia dataframe ze zdjęć paragonów użyciu AI
- 📄 Wczytanie istniejącego już datframe użytkonika i dodawanie nowych danych z paragonów
- 📄 Parsowanie informacji uzyskanych z zdjęć paragonów z z wartościami kalorycznymi pozyskanymi z pdf użyciu AI
- 📊 Możliwość filtracji danych
- 📊 Wizualizacja danych w postaci wykresów
- 💾 Eksport sfiltrowanych danych do CSV, Excel
- 💾 Mozliwośc zmiany nazwy sfiltrowanych danych
- 🤖 Generowanie spersonalizowanego planu treningowego przy użyciu AI
- 💾 Zapisanie planu treningowego do PDF

## Requirements / Dependencies
- python 3.11
- pip install -r requirements.txt
- environment.yaml

## Instalacja i uruchomienie

1. Scopiuj repozytorium
git clone https://github.com/twoj-nick/fittrack-ai.git

2. Idz do
cd m_cal

3. Zainstaluj requirements
pip install -r requirements.txt

4. Wpisz
streamlit run app.py


## Project Structure

m_cal/
├── app.py                               # Streamlit Main File
├── src/             
│   ├── pdf_parser/                      # PDF parsing modules
│   ├── data/                            # Data export (CSV, Excel, PDF)
│   ├── ai_trainer/                      # AI plan generation
│   ├── pltos/                           # Visualizations and charts
│   └── utils/                           # Auxiliary functions
├── json_calories_table                  # Calories table
├── logs                                 # Logs
├── logs                                 # Logs
├── main_dataframe                       # Dataframe template
├── pdf                                  # PDF with nutrion table
├── receipt                              # Dynamic receipt img holder
├── temporary_json_from_receipt          # Dynamic json from img
├── temporary_json_from_receipt          # Parsed dynamic json for user dataframe
│
└── requirements.txt
# How it works
Aplikacja posiada wbudowany plik json z warościami kalorycznymi na 1 porcję prdouktu.
W razie potrzeby jeżeli pojawią sie nowe produkty uzytkownik może pobrać nowy PDF z "tabelą warości odzywczych" i dodac nowe protuky do jsona z warościami kalorycznymi.
Użytkownik może wgrywa zdjęcie paragonu -> ze zdjęcia wyciągane są informacji dotyczące produktów -> nazwy produktów sa parsowane aby zgadzały się z tabelą kaloryczną -> wyswietlane są wykresy dotyczące kalori oraz wydanych pieniędzy z każdego produktu lub z danego miesiąca -> uzytkownik może zmienić nazwę dataframeu i zapisac do csv lub exel -> tak uzyskany dataframe można wgrać spowrotem i dodać następne dane z paragonów aktualizując swój dataframe -> Na podstawie przefiltrowanego dataframe i podanych informacjach o użytkowniku tworzy przy pomocy AI plan treningowy -> plan mozna zapisac do PDF

# Technologie
- python 3.11
- pandas
- pathlib
- numpy
- logging
- urllib.parse
- dotenv
- openai
- streamlit
- openpyxl
- fpdf2
- pdfplumber
- re
- plotly.express
- requests
- urllib.parse

## 🔒 Bezpieczeństwo
Utwórz plik `.env` i dodaj swój klucz OpenAI:

OPENAI_API_KEY=twój_klucz_api

## 👨‍💻 Autor
Projekt stworzony przez [Twoje Imię](https://github.com/twoj-github).

## 📜 Licencja
MIT License