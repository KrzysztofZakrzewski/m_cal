import pandas as pd
from dirs import DIRS
import json

def create_main_df(save: bool = True) -> pd.DataFrame:
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


def receipt_of_user_to_dataframe(path_for_receipt_parsed, calories):
    # read jsona
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
            
            # wyciągamy cenę z podklucza "kwota za ..."
            price = None
            for k, v in info.items():
                if "kwota" in k:
                    price = v
            
            if price is None:
                price = 0.0
            
            # price jednostkowa = price / ilość
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
    main_df = pd.concat([main_df, new_df], ignore_index=True)
    main_df = main_df.drop_duplicates()
    main_df = main_df.sort_values(by="data", ascending=False)
    return main_df