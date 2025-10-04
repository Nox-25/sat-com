# weather-prediction-system/frontend/dashboard.py

import streamlit as st
import pandas as pd
import sys
import os
import altair as alt
from datetime import date, timedelta

# Add the project root to the Python path to allow for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_historical_weather_data
from data_preprocessing.data_cleaning import preprocess_historical_data
from ml_models.weather_predictor import train_time_series_model, make_time_series_prediction

def plot_historical_and_prediction(df_hist, prediction, prediction_date):
    """
    Plots the historical temperature data and the new prediction.
    """
    # Reset index to make 'date' a column for Altair
    df_hist_chart = df_hist.reset_index()

    # Create the historical data line chart
    line = alt.Chart(df_hist_chart).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('temperature:Q', title='Temperature (°C)'),
        tooltip=['date:T', 'temperature:Q']
    ).properties(
        title="Historical Temperature Trend"
    ).interactive()

    # Create a DataFrame for the prediction point
    df_pred = pd.DataFrame({
        'date': [pd.to_datetime(prediction_date)],
        'temperature': [prediction],
        'label': ['Prediction']
    })

    # Create the prediction point chart
    point = alt.Chart(df_pred).mark_point(
        size=100,
        color='red',
        filled=True
    ).encode(
        x='date:T',
        y='temperature:Q',
        tooltip=['date:T', 'temperature:Q', 'label:N']
    )

    # Combine the line chart and the prediction point
    chart = (line + point).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

def main():
    st.title("Weather Prediction System")
    st.markdown("Powered by NASA POWER API")

    # --- User Input ---
    city_name = st.text_input("Enter a city name:", "London")

    st.subheader("Select Date Range for Historical Data")
    today = date.today()
    col1, col2 = st.columns(2)
    # Default to a shorter range to speed up API calls
    start_date = col1.date_input("Start Date", today - timedelta(days=90))
    end_date = col2.date_input("End Date", today - timedelta(days=1))

    st.subheader("Select Date for Prediction")
    prediction_date = st.date_input("Future Date to Predict", today + timedelta(days=1))

    if st.button("Get Historical Data and Predict"):
        if city_name and start_date and end_date and prediction_date:
            if start_date >= end_date:
                st.error("Error: The start date must be before the end date.")
                return
            if prediction_date <= end_date:
                st.error("Error: The prediction date must be after the historical data's end date.")
                return

            # --- 1. Data Collection & Preprocessing ---
            st.header("1. Historical Weather Data Summary")
            with st.spinner(f"Fetching and processing historical data for {city_name}..."):
                historical_data = get_historical_weather_data(
                    city_name,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )

                if historical_data:
                    df_hist = preprocess_historical_data(historical_data)
                    if df_hist is not None and not df_hist.empty:
                        st.dataframe(df_hist.head())
                    else:
                        st.error("Data processing failed. The fetched data might be empty or in an unexpected format.")
                        st.stop()
                else:
                    st.error(f"Could not fetch historical weather data for '{city_name}'. Please check the city name and date range.")
                    st.stop()

            # --- 2. Model Training and Prediction ---
            st.header("2. Weather Prediction")
            with st.spinner("Training model and making prediction..."):
                model = train_time_series_model(df_hist)
                if model:
                    prediction = make_time_series_prediction(model, prediction_date, df_hist)
                    st.metric(
                        label=f"Predicted Temperature for {prediction_date.strftime('%Y-%m-%d')}",
                        value=f"{prediction:.2f}°C"
                    )
                else:
                    st.error("Failed to train the prediction model.")
                    st.stop()

            # --- 3. Visualization ---
            st.header("3. Historical Data and Prediction Visualization")
            plot_historical_and_prediction(df_hist, prediction, prediction_date)

        else:
            st.warning("Please fill in all fields: city name, start date, end date, and prediction date.")

if __name__ == "__main__":
    main()