import base64
import pandas as pd
import json
from typing import Dict, Union
from pathlib import Path

def change_receipt_for_binary(receipt_path: str) -> str:
    """
    Convert a receipt image file to a Base64-encoded string suitable for
    embedding in HTML or displaying in Streamlit as an image.

    Args:
        receipt_path (str): Path to the receipt image file.

    Returns:
        str: Base64-encoded string with the 'data:image/jpg;base64,' prefix.
    """
    with open(receipt_path, "rb") as f:
        receipt_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:image/jpg;base64,{receipt_data}"


def reading_calories_table(path_for_calories_table: str) -> Dict[str, Union[int, float]]:
    """
    Read a JSON file containing a calories table and return it as a dictionary.

    Args:
        path_for_calories_table (str): Path to the JSON file with calorie data.

    Returns:
        Dict[str, Union[int, float]]: Dictionary mapping product names to their calorie values.
    """
    with open(path_for_calories_table, 'r', encoding='utf-8') as f:
        calories = json.load(f)
        return calories
    
# ===============================================================
# 📦 Cleanig recepit folder from img
# ===============================================================

def delete_recipt_img(file_path: Path) -> None:
    """
    Delete a file at the given path if it exists.
    
    Parameters
    ----------
    file_path : Path
        Path to the file to be deleted.
    """
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

# ===============================================================
# 📦 Cleanig json files folder temporarty json files
# ===============================================================

def delete_temporary_jsons(folder_path: Path):
    """
    Delete all JSON files in the given folder.
    """
    if folder_path.exists() and folder_path.is_dir():
        for file in folder_path.iterdir():
            if file.is_file() and file.suffix == ".json":
                file.unlink()