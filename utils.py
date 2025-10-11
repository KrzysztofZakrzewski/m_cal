import base64
import pandas as pd
import json

def change_receipt_for_binary(receipt_path):
    with open(receipt_path, "rb") as f:
        receipt_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:image/jpg;base64,{receipt_data}"



# path_for_calories_table = json_calories_table_PATH/'calories_table_352978-tabela-wo-8-11-2023-mop.json'

def reading_calories_table(path_for_calories_table):
    with open(path_for_calories_table, 'r', encoding='utf-8') as f:
        calories = json.load(f)
        return calories
    
# calories = reading_calories_table(path_for_calories_table)



