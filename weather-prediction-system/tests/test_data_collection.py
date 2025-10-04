import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_weather_data, get_coordinates

class TestDataCollection(unittest.TestCase):

    @patch('data_collection.satellite_api_handler.requests.get')
    def test_get_coordinates_success(self, mock_get):
        """Test successful geocoding of a city name."""
        mock_response = Mock()
        mock_response.json.return_value = [{'lat': '51.5074', 'lon': '-0.1278'}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        coords = get_coordinates('London')
        self.assertIsNotNone(coords)
        self.assertEqual(coords['latitude'], 51.5074)
        self.assertEqual(coords['longitude'], -0.1278)

    @patch('data_collection.satellite_api_handler.requests.get')
    def test_get_weather_data_success(self, mock_get):
        """Test successful fetching of both current and forecast weather data."""
        # Mock the geocoding call first
        with patch('data_collection.satellite_api_handler.get_coordinates') as mock_get_coords:
            mock_get_coords.return_value = {'latitude': 51.5074, 'longitude': -0.1278}

            # Prepare mock responses for the two API calls
            mock_current = Mock()
            mock_current.json.return_value = {"main": {"temp": 15}, "weather": [{"description": "clear"}], "coord": {}}
            mock_current.raise_for_status = Mock()

            mock_forecast = Mock()
            mock_forecast.json.return_value = {"list": [{"main": {"temp": 16}}]}
            mock_forecast.raise_for_status = Mock()

            mock_get.side_effect = [mock_current, mock_forecast]

            weather_data = get_weather_data('London')
            self.assertIsNotNone(weather_data)
            self.assertIn('current', weather_data)
            self.assertIn('forecast', weather_data)
            self.assertEqual(weather_data['current']['main']['temp'], 15)
            self.assertEqual(weather_data['forecast']['list'][0]['main']['temp'], 16)

    @patch('data_collection.satellite_api_handler.get_coordinates', return_value=None)
    def test_get_weather_data_no_coords(self, mock_get_coords):
        """Test failure when geocoding returns no coordinates."""
        weather_data = get_weather_data('InvalidCity')
        self.assertIsNone(weather_data)

if __name__ == '__main__':
    unittest.main()