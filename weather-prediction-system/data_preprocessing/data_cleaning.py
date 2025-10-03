# weather-prediction-system/data_preprocessing/data_cleaning.py

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def preprocess_weather_data(data):
    """
    Cleans and preprocesses the raw weather data.

    Args:
        data (dict): A dictionary containing the raw weather data from the API.

    Returns:
        pandas.DataFrame: A preprocessed DataFrame, or None if the input is invalid.
    """
    if not data or "main" not in data:
        return None

    # Convert the relevant parts of the data into a DataFrame
    df = pd.DataFrame([data["main"]])

    # Add weather description
    if "weather" in data and data["weather"]:
        df["description"] = data["weather"][0]["description"]
    else:
        df["description"] = "N/A"

    # --- Handle Missing Values ---
    # For this example, we'll fill missing values with the mean.
    # In a real-world scenario, more sophisticated methods might be needed.
    df.fillna(df.mean(numeric_only=True), inplace=True)

    # --- Normalize Numerical Features ---
    # We will normalize the 'temp', 'pressure', and 'humidity' columns.
    scaler = MinMaxScaler()
    numerical_cols = ["temp", "pressure", "humidity"]

    # Ensure all numerical columns exist before trying to scale them
    existing_numerical_cols = [col for col in numerical_cols if col in df.columns]
    if existing_numerical_cols:
        df[existing_numerical_cols] = scaler.fit_transform(df[existing_numerical_cols])

    return df

if __name__ == '__main__':
    # Example usage with sample data
    sample_weather_data = {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
        "base": "stations",
        "main": {
            "temp": 289.92,
            "feels_like": 289.32,
            "temp_min": 288.71,
            "temp_max": 290.93,
            "pressure": 1012,
            "humidity": 72
        },
        "visibility": 10000,
        "wind": {"speed": 1.54, "deg": 350},
        "clouds": {"all": 0},
        "dt": 1633356000,
        "sys": {
            "type": 2,
            "id": 2019646,
            "country": "GB",
            "sunrise": 1633327337,
            "sunset": 1633368297
        },
        "timezone": 3600,
        "id": 2643743,
        "name": "London",
        "cod": 200
    }

    preprocessed_df = preprocess_weather_data(sample_weather_data)

    if preprocessed_df is not None:
        print("Preprocessed Weather Data:")
        print(preprocessed_df)
    else:
        print("Failed to preprocess weather data.")