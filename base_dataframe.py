import pandas as pd
from dirs import DIRS
import json
from typing import Dict, Any, Union

def create_main_df(save: bool = True) -> pd.DataFrame:
    '''
    Create the base "main_df" DataFrame template at the start of the application.

    Args:
        save (bool): If True, save the DataFrame as a CSV file in DIRS['main_dataframe'].

    Returns:
        pd.DataFrame: An empty DataFrame with predefined columns and types.
    '''
    main_df = pd.DataFrame({
        "produkt": pd.Series(dtype="str"),
        "ilość": pd.Series(dtype="int"),
        "kcal_na_szt": pd.Series(dtype="int"),
        "kcal_razem": pd.Series(dtype="int"),
        "cena_na_szt": pd.Series(dtype="float"),
        "cena_razem": pd.Series(dtype="float"),
        "łączna kwota za paragon": pd.Series(dtype="float"),
        "data": pd.Series(dtype="datetime64[ns]"),
        "miasto": pd.Series(dtype="str"),
        "ulica": pd.Series(dtype="str"),
    })

    
    if save:
        main_df.to_csv(DIRS['main_dataframe']/"main.csv", index=False, encoding="utf-8-sig")

    return main_df


def receipt_of_user_to_dataframe(path_for_receipt_parsed: str, calories: Dict[str, Union[int, float]]) -> pd.DataFrame:
    """
    Convert a parsed receipt JSON file into a structured DataFrame with nutritional 
    and financial information for each product.

    Args:
        path_for_receipt_parsed (str): Path to the JSON file containing the parsed receipt.
        calories (Dict[str, Union[int, float]]): Dictionary mapping product names to calories per unit.

    Returns:
        pd.DataFrame: DataFrame containing columns for product name, quantity, calories per unit,
                      total calories, price per unit, total price, date, time, city, and street.
    """
    # read json
    with open(path_for_receipt_parsed, "r", encoding="utf-8") as f:
        receipt = json.load(f)
    # dataholder
    data = []

    meta = {
    "łączna kwota za paragon": receipt.get("łączna kwota za paragon"),
    "data": receipt.get("data"),
    "godzina": receipt.get("godzina"),
    "miasto": receipt.get("miasto"),
    "ulica": receipt.get("ulica")
}
    for product, info in receipt.items():
        if isinstance(info, dict) and "ilość" in info:
            amount = info["ilość"]
            kcal = calories.get(product, 0)
            
            price = None
            for k, v in info.items():
                if "kwota" in k:
                    price = v
            
            if price is None:
                price = 0.0
            
            cena_na_szt = price / amount if amount else 0
            
            data.append({
                "produkt": product,
                "ilość": amount,
                "kcal_na_szt": kcal,
                "kcal_razem": amount * kcal,
                "cena_na_szt": cena_na_szt,
                "cena_razem": price,
                **meta
            })

    df = pd.DataFrame(data)
    df['data'] = pd.to_datetime(df['data'] + ' ' + df['godzina'])

        # opcjonalnie usuń kolumnę 'godzina', jeśli niepotrzebna
        # df = df.drop(columns=['godzina'])
    return df


def append_user_df_to_main_df(main_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Append a new user DataFrame to the main DataFrame, remove duplicates,
    and sort by the 'data' column in descending order.

    Args:
        main_df (pd.DataFrame): The main DataFrame containing existing records.
        new_df (pd.DataFrame): The new DataFrame to append to the main DataFrame.

    Returns:
        pd.DataFrame: Updated DataFrame containing all records, without duplicates,
                      sorted by 'data' in descending order.
    """
    main_df = pd.concat([main_df, new_df], ignore_index=True)
    main_df = main_df.drop_duplicates()
    main_df = main_df.sort_values(by="data", ascending=False)
    return main_df