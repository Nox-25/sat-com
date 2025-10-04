# weather-prediction-system/data_preprocessing/data_cleaning.py

import pandas as pd

def preprocess_historical_data(historical_data):
    """
    Preprocesses the historical weather data fetched from the NASA POWER API.
    Converts the list of records into a pandas DataFrame and sets the date
    as a datetime index.

    Args:
        historical_data (list): A list of dictionaries, where each dictionary
                                represents a day's weather data.

    Returns:
        pandas.DataFrame: A preprocessed DataFrame with a datetime index,
                          or None if the input is invalid.
    """
    if not historical_data:
        return None

    try:
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Ensure all columns are numeric, coercing errors
        for col in ['temperature', 'humidity', 'pressure']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with any NaN values that might have been coerced
        df.dropna(inplace=True)

        return df

    except (KeyError, TypeError) as e:
        print(f"Error during data preprocessing: {e}")
        return None

if __name__ == '__main__':
    # Example usage with sample data
    sample_data = [
        {'date': '2023-01-01', 'temperature': 9.18, 'humidity': 94.45, 'pressure': 99.89},
        {'date': '2023-01-02', 'temperature': 4.84, 'humidity': 96.35, 'pressure': 100.76},
        {'date': '2023-01-03', 'temperature': 7.7, 'humidity': 96.34, 'pressure': 100.91}
    ]

    preprocessed_df = preprocess_historical_data(sample_data)

    if preprocessed_df is not None:
        print("Preprocessed Historical Data:")
        print(preprocessed_df)
        print("\nDataFrame Info:")
        preprocessed_df.info()
    else:
        print("Failed to preprocess historical data.")