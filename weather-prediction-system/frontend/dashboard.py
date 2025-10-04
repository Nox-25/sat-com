# weather-prediction-system/frontend/dashboard.py

import streamlit as st
import pandas as pd
import sys
import os
import altair as alt

# Add the project root to the Python path to allow for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_weather_data
from data_preprocessing.data_cleaning import preprocess_weather_data
from ml_models.weather_predictor import train_weather_model, make_prediction

def display_raw_data(data):
    """Displays the raw weather data in a structured and clean UI."""
    st.subheader("Current Weather Conditions")

    # --- Main Metrics ---
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather_desc = data.get("weather", [{}])[0].get("description", "N/A")

    # Convert temperatures from Kelvin to Celsius
    temp_c = main.get("temp", 273.15) - 273.15
    feels_like_c = main.get("feels_like", 273.15) - 273.15

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{temp_c:.2f}°C", f"Feels like {feels_like_c:.2f}°C")
    col2.metric("Humidity", f"{main.get('humidity', 'N/A')}%")
    col3.metric("Pressure", f"{main.get('pressure', 'N/A')} hPa")

    st.markdown(f"**Description:** `{weather_desc.capitalize()}`")

    # --- Detailed Metrics ---
    with st.expander("See More Details"):
        col1_detail, col2_detail, col3_detail = st.columns(3)
        col1_detail.metric("Wind Speed", f"{wind.get('speed', 'N/A')} m/s")
        col2_detail.metric("Cloudiness", f"{data.get('clouds', {}).get('all', 'N/A')}%")
        col3_detail.metric("Visibility", f"{data.get('visibility', 'N/A')} m")

        # Display min/max temperatures
        temp_min_c = main.get("temp_min", 273.15) - 273.15
        temp_max_c = main.get("temp_max", 273.15) - 273.15
        col1_detail.metric("Min Temperature", f"{temp_min_c:.2f}°C")
        col2_detail.metric("Max Temperature", f"{temp_max_c:.2f}°C")

def main():
    st.title("Weather Prediction System")

    # --- User Input ---
    city_name = st.text_input("Enter a city name:", "London")

    if st.button("Get Weather and Predict"):
        if city_name:
            # --- 1. Data Collection ---
            with st.spinner(f"Fetching weather data for {city_name}..."):
                raw_data = get_weather_data(city_name)

            if raw_data and raw_data.get("cod") == 200:
                display_raw_data(raw_data)

                # --- 2. Data Preprocessing & Visualization ---
                st.subheader("2. Normalized Weather Metrics")
                with st.spinner("Preprocessing data..."):
                    preprocessed_data = preprocess_weather_data(raw_data)

                if preprocessed_data is not None:
                    # Create a clean DataFrame for the chart
                    chart_data = pd.DataFrame({
                        'Metric': ['Temperature', 'Pressure', 'Humidity'],
                        'Normalized Value': [
                            preprocessed_data['temp'].iloc[0],
                            preprocessed_data['pressure'].iloc[0],
                            preprocessed_data['humidity'].iloc[0]
                        ]
                    })

                    chart = alt.Chart(chart_data).mark_bar().encode(
                        x=alt.X('Metric:N', title='Weather Metric'),
                        y=alt.Y('Normalized Value:Q', title='Normalized Value (0 to 1)'),
                        color='Metric:N',
                        tooltip=['Metric', 'Normalized Value']
                    ).properties(
                        title="Normalized Weather Metrics"
                    )
                    st.altair_chart(chart, use_container_width=True)
                    st.write("This chart shows the normalized values (scaled between 0 and 1) of the key weather metrics.")

                    # --- 3. Prediction ---
                    st.subheader("3. Weather Prediction")
                    with st.spinner("Training model and making prediction..."):
                        training_df = pd.concat([preprocessed_data.copy() for _ in range(10)], ignore_index=True)
                        model = train_weather_model(training_df)

                        if model:
                            prediction = make_prediction(model, preprocessed_data)
                            st.metric("Predicted Future Condition (Normalized)", f"{prediction[0]:.4f}")
                            st.info("Note: This is a simulated prediction using a placeholder model.")
                        else:
                            st.error("Failed to train the prediction model.")
                else:
                    st.error("Failed to preprocess the data.")
            else:
                st.error(f"Could not fetch weather data for '{city_name}'. Please check the city name or API key.")
        else:
            st.warning("Please enter a city name.")

if __name__ == "__main__":
    main()