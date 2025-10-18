import pandas as pd
import plotly.express as px
import streamlit as st

#### Calories
# tab 1
def calorie_distribution_per_product_chart(chart_data):
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
def total_calories_consumed_each_month_chart(chart_data):
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
def distribution_of_money_spent_per_product_chart(chart_data):
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

def total_money_spend_each_month_chart(chart_data):
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
