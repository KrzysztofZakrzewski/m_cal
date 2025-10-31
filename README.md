# FitTrack AI 🏋️‍♂️
## An app for measuring calories consumed at McDonald's
( Proof of concept )

# This application is intended for educational purposes only.

- Inteligentna aplikacja do analizy danych żywieniowych i generowania planów treningowych na podstawie paragonów i plików PDF.

## Features
- 📄 Ability to download a PDF file containing the “Nutritional Values Table” from the McDonald’s website

- ✍🏻 Creation of a JSON file with calorie and nutritional values for individual products extracted from the nutritional table PDF, or adding new entries to an existing file

- 📷 Reading information from receipt images and automatically generating a DataFrame using AI

- 📄 Loading an existing user DataFrame and adding new data from scanned receipts

- 📄 Parsing receipt data and merging it with nutritional information extracted from the PDF using AI

- 📊 Filtering of user data based on selected parameters

- 📊 Visualization of data through interactive charts

- 💾 Export of filtered data to CSV or Excel formats

- 💾 Option to rename filtered datasets before export

- 🤖 Generation of a personalized AI-based training plan

- 💾 Saving the generated training plan as a PDF

## Requirements / Dependencies
- python 3.11
- environment.yaml
- pip install -r requirements.txt

## Installation and Setup

1. Create the main project folder
cd m_cal

2. Clone the repository
git clone https://github.com/twoj-nick/fittrack-ai.git

3. Or using Conda:
conda env create -f environment.yml
conda activate m_cal

5. Using terminal type
streamlit run app.py

Alternative dependencies
pip install -r requirements.txt

## Project Structure

```
m_cal/
├── app.py # Main Streamlit application file
├── src/
│ ├── pdf_parser/ # Modules for PDF parsing
│ ├── data/ # Data export (CSV, Excel, PDF)
│ ├── ai_trainer/ # AI-powered training plan generation
│ ├── pltos/ # Visualizations and charts
│ └── utils/ # Utility and helper functions
│
├── json_calories_table/ # Static calorie table in JSON format
├── logs/ # Application logs
├── main_dataframe/ # Template for base dataframe
├── pdf/ # Nutrition table PDFs
├── receipt/ # Dynamic receipt image storage
├── temporary_json_from_receipt/ # Temporary JSONs generated from receipts
├── parsed_json_for_user_dataframe/ # Final parsed JSONs for dataframe creation
│
└── requirements.txt # Python dependencies
```

# How it works

1. The user uploads a photo of a receipt.

2. The application extracts product names and prices using AI-based OCR.

3. Product names are parsed and matched with the calorie table from the JSON file.

4. The application generates interactive charts showing calorie intake and total spending — per product or by month.

5. The user can rename and export the filtered DataFrame to CSV or Excel.

6. The exported DataFrame can later be re-uploaded to add new receipts and update the data.

7. Based on the filtered data and the user’s personal information, the app generates a personalized AI training plan.

8. The generated plan can be saved as a PDF file for download.

# Technologies
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
- plotly.express
- requests

## 🔒 Security

Create a .env file and add your OpenAI API key:

OPENAI_API_KEY=twój_klucz_api

## 👨‍💻 Autor
Made by [Krzysztof Zakrzewski](https://github.com/KrzysztofZakrzewski).

## ⚖️ License
This project is intended **for educational and non-commercial use only**.  
All trademarks and brand names are the property of their respective owners.  
This app is not affiliated with or endorsed by McDonald’s or any other company.