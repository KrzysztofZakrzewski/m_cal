# import json
from openai import OpenAI
# from dotenv import load_dotenv
import os
from dirs import DIRS

# load_dotenv()

def get_openai_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def loading_data_from_receipt_into_json(prepared_receipt):
    
    response = get_openai_client().chat.completions.create(
        # model="gpt-4o",
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
    Wyciągnij informacje zawarte na paragonie z Restauracji w McDonald's w Polsce.
    Dane przedstaw w formacie JSON.
    Oczekuję informacji dotyczących nazw produtków, ilości, kwoty za poszczególne produkty oraz łącznej kwoty za cały paragon.
    Niektóre produkty w systemie fiskalnym mogą mieć niekonwencjonalne nazwy.
    Pod napisem "PARAGON FISKALNY" znajdują się produkty jeden pod drugim.
    Od lewej jest jego nazwa, po prawej ilość i należność.
    „Jeśli w nazwie produktu występuje liczba (np. Tenders 3, Tenders 5), traktuj ją jako część nazwy np: "Nuggets 6", "Tenders 3", etc. traktuj je jako 1 produkt.
    Dodatkowo potrzebuję informacji o:
    - dacie: rok, misiąć i dzień oraz godzinę zakupu.
    - Miejscu zakupu: miasto, ulica.
    Usuń z wszystkich kluczy i wartości dokładnie te znaki: kropkę (.), gwiazdkę (*), podłogę (_).
    Jeżeli podłoga (_) jest między literami zastą spacją ( )
    Nie zostawiaj żadnego z nich.
    Przykładowa struktura (na paragonie będą się znajdować różne produkty to przykład):
    {
    {
    "lody w wafelku z polewą karmelową": {
        "ilość": ...,
        "kwota": ...
    },
    "cheeseburger": {
        "ilość": ...,
        "kwota": ...
    },
    "lody w kubku z polewą truskawkową": {
        "ilość": ...,
        "kwota": ...
    },
    "Big Mac": {
        "ilość": ...,
        "kwota": ...
    },
    "łączna kwota za paragon": ...,
    "data": "yyyy-mm-dd",
    "godzina": "hh:mm",
    "miasto": "...",
    "ulica": "..."
    }

    tylko dane jako JSON, bez żadnych komentarzy
    """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": prepared_receipt,
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
    )

        # saving the calorie table as json
        # temporary_json_from_receipt_PATH
    json_from_receipt = response.choices[0].message.content.replace('```json','').replace('```','').strip()
    with open(DIRS['temporary_json_from_receipt']/f'receipt_raw.json', 'w') as f:
            f.write(json_from_receipt)