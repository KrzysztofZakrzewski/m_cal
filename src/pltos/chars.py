import pandas as pd
import plotly.express as px
import streamlit as st
from typing import Optional
    # if chart_data is None:
        # return

# ===============================================================
# 📦 Calories
# ===============================================================
# tab 1
def calorie_distribution_per_product_chart(chart_data: pd.DataFrame) -> None:
    '''
    Generate a histogram of calories per product if there is data:
    1. Check if 'chart_data' DataFrame is not empty.
    2. Create a Plotly histogram with:
       - X-axis: product names
       - Y-axis: total calories ('kcal_razem')
       - Color: city ('miasto')
       - Automatic text labels and 10 bins
    3. Update layout with descriptive titles and axis labels, and set bar gap.
    4. Display the chart in Streamlit with 'st.plotly_chart'.
    5. If 'chart_data' is empty, show a warning indicating no data to display.
    '''
    chart_data
    if not chart_data.empty:
        fig_kalc = px.histogram(
            chart_data,
            x="produkt",
            y="kcal_razem",
            title="Rozkład kalorii na produkt",
            color="miasto",
            nbins=10,
            text_auto=True
        )

        fig_kalc.update_layout(
            title="📊 Kalorie w zależności od produktu w podanym zakresie",
            xaxis_title="Produkt",
            yaxis_title="Łączna liczba kcal",
            bargap=0.2
        )

        st.plotly_chart(fig_kalc, use_container_width=True, key="plot_kcal")
    else:
        st.warning("Brak danych do wyświetlenia na wykresie.")

#tab 2
def total_calories_consumed_each_month_chart(chart_data: pd.DataFrame) -> None:
    '''
    Display a histogram of total calories per product by city.
    
    Args:
        chart_data (pd.DataFrame): DataFrame containing columns 'produkt', 'kcal_razem', and 'miasto'.
    
    Returns:
        None. Shows the chart in Streamlit or a warning if DataFrame is empty.
    '''
    if not chart_data.empty and "data" in chart_data.columns:
        # We make sure that the 'date' column has the correct format
        chart_data["data"] = pd.to_datetime(chart_data["data"], errors="coerce")

        # We create a column with the month
        chart_data["miesiąc"] = chart_data["data"].dt.to_period("M").astype(str)

        # Group by month and add up the calories
        monthly_kcal = chart_data.groupby("miesiąc", as_index=False)["kcal_razem"].sum()

        # Chart
        fig_monthly = px.bar(
            monthly_kcal,
            x="miesiąc",
            y="kcal_razem",
            title="📅 Suma kalorii spożytych w każdym miesiącu",
            text_auto=True
        )

        fig_monthly.update_layout(
            xaxis_title="Miesiąc",
            yaxis_title="Łączna liczba kcal",
            bargap=0.2
        )

        st.plotly_chart(fig_monthly, use_container_width=True, key="plot_monthly_kcal")

    else:
        st.warning("Brak danych z kolumną 'data' do stworzenia wykresu miesięcznego.")


#tab 4
def distribution_of_money_spent_per_product_chart(chart_data: pd.DataFrame) -> None:
    '''# Generate and display a histogram of money spent per product by city:
    1. Check if 'chart_data' is not empty.
    2. Create a Plotly histogram with:
       - X-axis: product names ('produkt')
       - Y-axis: total money spent ('cena_razem')
       - Color grouping by city ('miasto')
       - 10 bins and automatic text labels
    3. Update layout with descriptive titles and axis labels, and set bar gap.
    4. Display the chart in Streamlit.
    5. If 'chart_data' is empty, show a warning.
    '''
    if not chart_data.empty:
        fig_price = px.histogram(
            chart_data,
            x="produkt",             # nazwa kolumny na osi X
            y="cena_razem",          # (opcjonalnie) co ma być na osi Y
            title="Rozkład wydanych pieniedży na produkt",
            color="miasto",          # (opcjonalnie) grupowanie kolorami
            nbins=10,                # liczba przedziałów histogramu
            text_auto=True           # liczby nad słupkami
        )

        fig_price.update_layout(
            title="💸 Pieniądze wydane na poszczególne produkty",
            xaxis_title="Produkt",
            yaxis_title="Łączna wydana kwota",
            bargap=0.2
        )

        st.plotly_chart(fig_price, use_container_width=True, key="plot_price")
    else:
        st.warning("Brak danych do wyświetlenia na wykresie.")

def total_money_spend_each_month_chart(chart_data: pd.DataFrame) -> None:
    '''
    Display a bar chart showing total money spent per month.

    - Checks that 'chart_data' is not empty and contains a 'data' column.
    - Converts 'data' to datetime format and extracts the month.
    - Groups data by month and sums 'cena_razem' (total money spent).
    - Plots the monthly totals as a bar chart in Streamlit.
    - Shows a warning if data is missing or the 'data' column is not present.
    '''
    if not chart_data.empty and "data" in chart_data.columns:
        # We make sure that the 'date' column has the correct format
        chart_data["data"] = pd.to_datetime(chart_data["data"], errors="coerce")

        # We create a column with the month
        chart_data["miesiąc"] = chart_data["data"].dt.to_period("M").astype(str)

        # Group by month and add up the calories
        monthly_kcal = chart_data.groupby("miesiąc", as_index=False)["cena_razem"].sum()

        # Chart
        fig_monthly = px.bar(
            monthly_kcal,
            x="miesiąc",
            y="cena_razem",
            title="💸 Suma łączna pieniędzy wydanych w kazdym miesiącu miesiąc",
            text_auto=True
        )

        fig_monthly.update_layout(
            xaxis_title="Miesiąc",
            yaxis_title="Suma",
            bargap=0.2
        )

        st.plotly_chart(fig_monthly, use_container_width=True, key="plot_monthly_amount")

    else:
        st.warning("Brak danych z kolumną 'data' do stworzenia wykresu miesięcznego.")
