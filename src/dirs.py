# modules.py
from pathlib import Path
import os
from typing import Dict

def init_dirs()-> Dict[str, Path]:
    """
    Initialize project directories relative to this file.

    Creates necessary folders if they do not exist yet.

    Returns:
        dirs (Dict[str, Path]): A dictionary mapping folder names to their Path objects.
    """
    BASE_DIR = Path(__file__).resolve().parent
    dirs = {
        # "test1": BASE_DIR / "test1",
        # "test2": BASE_DIR / "test2",
        "pdf": BASE_DIR / "pdf",
        "logs": BASE_DIR / "logs",
        "receipt": BASE_DIR / "receipt",
        "main_dataframe": BASE_DIR / "main_dataframe",
        'json_calories_table': BASE_DIR / 'json_calories_table',
        'temporary_json_from_receipt': BASE_DIR / 'temporary_json_from_receipt',
        'temporary_json_parsed': BASE_DIR / 'temporary_json_parsed'
        # "json": Path("json_temp")
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs

DIRS = init_dirs()
