from src.dirs import DIRS
import pdfplumber
import re
import json
import os

def extracting_text_from_pdf(pdf_path_to_create_text):
    with pdfplumber.open(pdf_path_to_create_text) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        return text



def new_caloris_table_from_pdf_json(text: str, sections=None) -> dict:
    """
    Parse PDF text into a JSON dictionary {product_name: fifth_number}.
    - Keeps products with digits in names
    - Removes '*' from product names
    - Ignores lines with certain end markers
    - Stops after processing 'Syrop karmelowy' as the last product
    - Fifth number is rounded to int
    """
    if sections is None:
        sections = [
            "OFERTA KLASYCZNA",
            "SAŁATKI",
            "SOSY DO SAŁATEK",
            "EKSTRAKĄSKI",
            "OFERTA ŚNIADANIOWA",
            "FRYTKI",
            "DODATKI",
            "PRODUKTY PROMOCYJNE",
            "DESERY",
            "NAPOJE",
        ]
    
    result = {}

    # normalize text: remove special chars ® ™
    text = re.sub(r"[®™]", "", text)

    # markers to ignore
    ignore_markers = [
        "* Produkt jest dostępny w wybranych",
        "** Zawiera źródło fenyloalaniny."
    ]

    # iterate over sections
    for i, section in enumerate(sections):
        # find start of section
        pattern = re.compile(rf"{section}", re.IGNORECASE)
        match = pattern.search(text)
        if not match:
            continue  # section not found

        start_idx = match.end()
        end_idx = len(text)

        # if not last section, find start of next section
        for next_section in sections[i+1:]:
            next_match = re.search(next_section, text[start_idx:], re.IGNORECASE)
            if next_match:
                end_idx = start_idx + next_match.start()
                break

        section_text = text[start_idx:end_idx].strip()

        # process each line
        for line in section_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # skip lines with ignore markers
            if any(marker in line for marker in ignore_markers):
                continue

            # split tokens
            tokens = line.split()
            if not tokens:
                continue

            # find first numeric value -> everything before it is product name
            product_tokens = []
            numbers_tokens = []
            number_found = False

            for t in tokens:
                t_clean = t.replace(",", ".")
                # consider numeric values (float/int)
                if re.match(r"^\d+(\.\d+)?$", t_clean) and not number_found:
                    number_found = True
                    numbers_tokens.append(t_clean)
                elif number_found:
                    numbers_tokens.append(t_clean)
                else:
                    product_tokens.append(t)

            if not numbers_tokens:
                continue  # no numeric values, skip line

            # assemble product name and remove '*'
            product_name = re.sub(r"\*", "", " ".join(product_tokens)).strip()

            # take 5th number if exists
            if len(numbers_tokens) >= 5:
                try:
                    fifth_number = int(round(float(numbers_tokens[4])))
                    result[product_name] = fifth_number
                except ValueError:
                    # skip products where 5th value is invalid
                    continue

            # stop processing after 'Syrop karmelowy'
            if "Syrop karmelowy" in product_name:
                # ensure Syrop karmelowy is last
                result["Syrop karmelowy"] = int(round(float(numbers_tokens[4])))
                return result

            with open(DIRS['json_calories_table']/"offer_classic_temporary.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

    # ✅ if not ended earlier, save at the end anyway
    with open(DIRS['json_calories_table'] / "offer_classic_temporary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


import json
import os
from pathlib import Path

def merge_json_files(tablica_a_path: Path, tablica_b_path: Path) -> None:
    """
    Merge TablicaB.json into TablicaA.json.
    - Adds only missing keys or updates existing ones from B.
    - After merge, TablicaB.json is deleted.
    """
    # read A
    if tablica_a_path.exists():
        with open(tablica_a_path, "r", encoding="utf-8") as f:
            data_a = json.load(f)
    else:
        data_a = {}

    # read B
    if not tablica_b_path.exists():
        print("⚠️ File TablicaB.json not found.")
        return
    
    with open(tablica_b_path, "r", encoding="utf-8") as f:
        data_b = json.load(f)

    # merge
    data_a.update(data_b)

    # save merged A
    with open(tablica_a_path, "w", encoding="utf-8") as f:
        json.dump(data_a, f, ensure_ascii=False, indent=2)

    # delete B
    os.remove(tablica_b_path)
    print(f"✅ Merged and updated {tablica_a_path.name}, deleted {tablica_b_path.name}")