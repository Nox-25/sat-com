import unittest
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_preprocessing.data_cleaning import preprocess_historical_data

class TestPreprocessHistoricalData(unittest.TestCase):

    def setUp(self):
        """Set up sample historical weather data for testing."""
        self.sample_historical_data = [
            {'date': '2023-01-01', 'temperature': 9.18, 'humidity': 94.45, 'pressure': 99.89},
            {'date': '2023-01-02', 'temperature': 4.84, 'humidity': 96.35, 'pressure': 100.76},
            {'date': '2023-01-03', 'temperature': 'invalid', 'humidity': 96.34, 'pressure': 100.91}, # Test coercion
            {'date': '2023-01-04', 'temperature': 8.0, 'humidity': 95.0, 'pressure': 101.0}
        ]
        self.empty_data = []
        self.invalid_format_data = [{"day": "2023-01-01", "temp": 10}]

    def test_preprocess_success(self):
        """Test that preprocessing valid historical data returns a DataFrame."""
        processed_df = preprocess_historical_data(self.sample_historical_data)
        self.assertIsInstance(processed_df, pd.DataFrame)
        # Should drop the row with 'invalid' temperature
        self.assertEqual(len(processed_df), 3)

    def test_preprocess_empty_input(self):
        """Test that preprocessing empty data returns None."""
        processed_df = preprocess_historical_data(self.empty_data)
        self.assertIsNone(processed_df)

    def test_preprocess_invalid_format(self):
        """Test that preprocessing data with incorrect keys returns None or an empty frame."""
        # This should fail during the DataFrame creation or key access
        processed_df = preprocess_historical_data(self.invalid_format_data)
        self.assertIsNone(processed_df)

    def test_dataframe_properties(self):
        """Test that the preprocessed DataFrame has the correct properties."""
        processed_df = preprocess_historical_data(self.sample_historical_data)

        # Test index is a DatetimeIndex
        self.assertIsInstance(processed_df.index, pd.DatetimeIndex)

        # Test column names
        expected_cols = ['temperature', 'humidity', 'pressure']
        self.assertListEqual(list(processed_df.columns), expected_cols)

        # Test data types
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['temperature']))
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['humidity']))
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['pressure']))

if __name__ == '__main__':
    unittest.main()