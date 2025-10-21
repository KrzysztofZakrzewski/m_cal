import io
import streamlit as st
from openpyxl import Workbook
import pandas as pd

# ===============================================================
# 💾 CSV Dowland functions
# ===============================================================
def download_csv_button(df, file_name, label="💾 Pobierz dane jako CSV"):
    """
    Helper function to generate a CSV download button in Streamlit.
    - df: DataFrame to export
    - file_name: output file name (with or without .csv)
    - label: button label
    """
    if not file_name.endswith(".csv"):
        file_name += ".csv"

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    csv_data = buffer.getvalue()

    st.download_button(
        label=label,
        data=csv_data,
        file_name=file_name,
        mime="text/csv"
    )

# ===============================================================
# 💾 Exel Dowland functions
# ===============================================================
def to_excel(df: pd.DataFrame) -> bytes:
    """
    Convert a pandas DataFrame into an Excel file stored in memory as bytes.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to export. Must not be None or empty.

    Returns
    -------
    bytes
        The Excel file content in bytes, ready for download or saving to disk.

    Raises
    ------
    ValueError
        If the DataFrame is None or empty.
    
    Notes
    -----
    - Uses 'openpyxl' engine to write Excel.
    - Index column is excluded.
    - Sheet is named 'Dane'.
    """
    if df is None or df.empty:
        raise ValueError("❌ DataFrame is empty — nothing to export to Excel.")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Dane")
    processed_data = output.getvalue()
    return processed_data
