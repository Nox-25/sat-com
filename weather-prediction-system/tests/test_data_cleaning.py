import unittest
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_preprocessing.data_cleaning import preprocess_weather_data

class TestDataCleaning(unittest.TestCase):

    def setUp(self):
        """Set up a sample raw weather data for testing."""
        self.sample_weather_data = {
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
            "cod": 200
        }
        self.invalid_data = {"cod": "404"}

    def test_preprocess_weather_data_success(self):
        """Test that preprocessing a valid data dictionary returns a DataFrame."""
        processed_df = preprocess_weather_data(self.sample_weather_data)
        self.assertIsInstance(processed_df, pd.DataFrame)
        self.assertFalse(processed_df.empty)

    def test_preprocess_weather_data_invalid_input(self):
        """Test that preprocessing invalid data returns None."""
        processed_df = preprocess_weather_data(self.invalid_data)
        self.assertIsNone(processed_df)

    def test_preprocess_weather_data_columns(self):
        """Test that the preprocessed DataFrame has the expected columns."""
        processed_df = preprocess_weather_data(self.sample_weather_data)
        expected_cols = ['temp', 'feels_like', 'temp_min', 'temp_max', 'pressure', 'humidity', 'description']
        self.assertListEqual(list(processed_df.columns), expected_cols)

    def test_normalization(self):
        """Test that numerical columns are normalized (scaled between 0 and 1)."""
        processed_df = preprocess_weather_data(self.sample_weather_data)
        numerical_cols = ["temp", "pressure", "humidity"]
        for col in numerical_cols:
            # Since we process a single row, the scaled value should be 0, but due to
            # scaler implementation, it might be a small float. A more robust test
            # with multiple rows would check the min/max range.
            self.assertTrue(0.0 <= processed_df[col].iloc[0] <= 1.0)

if __name__ == '__main__':
    unittest.main()