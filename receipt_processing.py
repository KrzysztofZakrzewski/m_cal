import json
from openai import OpenAI
# from dotenv import load_dotenv
import os
import re
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


### PARSIN JSON_RAW

def parsing_data_from_receipt_raw_into_json():

        # Ścieżka do pliku raw JSON
    receipt_raw_path = DIRS['temporary_json_from_receipt'] / "receipt_raw.json"

    # 🔹 Jeśli plik nie istnieje — kończymy funkcję bez błędu
    if not receipt_raw_path.exists():
        return None

    # 🔹 Próba wczytania JSON-a — pierwszy raz (do przygotowania stringa)
    try:
        with open(receipt_raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Jeśli plik jest pusty lub uszkodzony — kończymy
        return None

    # 🔹 Zamiana na string dla prompta
    data_str_for_AI_maping = json.dumps(data, indent=2, ensure_ascii=False)

    # 🔹 Drugi raz wczytujemy (zgodnie z Twoim kodem)
    with open(receipt_raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Prepering receipt_raw.json for reading
    # with open(DIRS['temporary_json_from_receipt']/"receipt_raw.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # # zamiana na string, który możesz wstawić do prompt
    # data_str_for_AI_maping = json.dumps(data, indent=2, ensure_ascii=False)


    # # Read Json as VARIABLE
    # receipt_raw = DIRS['temporary_json_from_receipt']/ "receipt_raw.json"
    # with open(receipt_raw, "r", encoding="utf-8") as f:
    #     data = json.load(f)

    
    prompt = f"""
    Masz poniższy JSON z danymi pochodzącymi z paragonu z restauracji McDonald's Polska:
    {data_str_for_AI_maping}

    Twoim zadaniem jest:
    1. Zamienić TYLKO nazwy produktów (klucze na najwyższym poziomie) na ich czytelne odpowiedniki w języku polskim.
    2. Nie zmieniaj żadnych podstruktur:
    - Klucze "ilość" i "kwota" muszą pozostać takie same.
    - Wartości tych kluczy pozostają bez zmian.
    3. Nie zmieniaj ani nie ruszaj pól: "łączna kwota za paragon", "data", "godzina", "miasto", "ulica".
    4. Jeżeli w nazwie produktu występują litery "HM" — usuń ten produkt z wynikowego JSON-a.
    5. Nie twórz nowych produktów ani nie poprawiaj nazw istniejących (np. NIE zmieniaj "Cheeseburger" → "McCheeseburger").
    6. Zwróć TYLKO poprawiony JSON, bez żadnych komentarzy ani tekstu opisu.

    Mapowanie nazw produktów:
    "FL Wan Lio Czek": "McFlurry waniliowe Lion z polewą o smaku czekoladowym",
    "WrapChrup Klas": "McWrap Chrupiący Klasyczny",
    "Frytki Mal Pol": "Frytki Małe",
    "FrytkiMala Por.": "Frytki Małe",
    "Frytki M": "Frytki Średnie",
    "Frytki Srednie": "Frytki Średnie",
    "Sos Smietanowy": "Sos Śmietanowy",
    "Tenders 3": "Chicken Tenders 3 szt.",
    "Sos Siri Mayo": "Sos Sriracha Mayo",
    "Kanapka Chikker": "Chikker",
    "Ketchup Platny": "Ketchup",
    "Kaj Wie Wiel": "Wieloziarnista Kajzerka Kurczak Premium",
    "MuffinWiepJajko": "McMuffin Wieprzowy z Jajkiem",
    "Wafel Czekolada": "Lody o smaku waniliowym z polewą o smaku czekoladowym",
    "Kubek Czekolada": "Lody o smaku waniliowym z polewą o smaku czekoladowym",
    "Kubek Karmel": "Lody o smaku waniliowym z polewą karmelową",
    "Wafel Karmel": "Lody o smaku waniliowym z polewą karmelową",
    "Jalapeno Burger": "Jalapeño Burger"

    Zwróć poprawiony JSON.
    """

    response = get_openai_client().chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    )
    new_json_text = response.choices[0].message.content

    match = re.search(r'(\{.*\})', new_json_text, re.DOTALL)
    if match:
        json_only = match.group(1)
        new_data = json.loads(json_only)
    else:
        raise ValueError("Nie znaleziono poprawnego JSON-a w odpowiedzi modelu")

    # zapis do pliku
    with open(DIRS['temporary_json_parsed']/"receipt_parsed.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)