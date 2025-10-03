# weather-prediction-system/frontend/dashboard.py

import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the Python path to allow for module imports
# This is a common pattern when running a script from a subdirectory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_weather_data
from data_preprocessing.data_cleaning import preprocess_weather_data
from ml_models.weather_predictor import train_weather_model, make_prediction

def main():
    st.title("Weather Prediction System")

    st.info("""
    **Note:** To use this application, you must first add your free OpenWeatherMap API key.
    1. Open the file: `weather-prediction-system/data_collection/satellite_api_handler.py`
    2. Replace `"Your_API_Key"` with your actual key.
    """)

    # --- User Input ---
    city_name = st.text_input("Enter a city name:", "London")

    if st.button("Get Weather and Predict"):
        if city_name:
            # --- 1. Data Collection ---
            st.subheader("1. Raw Weather Data")
            with st.spinner(f"Fetching weather data for {city_name}..."):
                raw_data = get_weather_data(city_name)

            if raw_data:
                st.json(raw_data)

                # --- 2. Data Preprocessing ---
                st.subheader("2. Preprocessed Data")
                with st.spinner("Preprocessing data..."):
                    # The preprocess function expects a single data point, so we create a list
                    preprocessed_data = preprocess_weather_data(raw_data)

                if preprocessed_data is not None:
                    st.dataframe(preprocessed_data)

                    # --- 3. Prediction ---
                    st.subheader("3. Weather Prediction")
                    with st.spinner("Training model and making prediction..."):
                        # In a real-world scenario, you would load a pre-trained model.
                        # Here, we train a dummy model on the fly for demonstration.
                        # We create a slightly larger dummy dataset for the model to train on.
                        training_df = pd.concat([preprocessed_data.copy() for _ in range(10)], ignore_index=True)
                        model = train_weather_model(training_df)

                        if model:
                            # Use the single preprocessed data point for prediction
                            prediction = make_prediction(model, preprocessed_data)

                            # The prediction is based on normalized values. For display,
                            # we could inverse_transform, but for this simple case,
                            # we'll just show the raw prediction value.
                            st.write(f"**Predicted Future Condition (Normalized):** `{prediction[0]:.4f}`")
                            st.info("Note: This is a simulated prediction using a placeholder model trained on the current data point.")
                        else:
                            st.error("Failed to train the prediction model.")
                else:
                    st.error("Failed to preprocess the data.")
            else:
                st.error(f"Could not fetch weather data for '{city_name}'. This could be due to an invalid city name or a missing/incorrect API key.")
        else:
            st.warning("Please enter a city name.")

if __name__ == "__main__":
    main()