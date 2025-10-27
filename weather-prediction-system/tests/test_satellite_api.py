import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_satellite_data

class TestSatelliteAPI(unittest.TestCase):

    @patch('data_collection.satellite_api_handler.requests.get')
    def test_get_satellite_data_success(self, mock_get):
        """Test successful fetching of satellite data."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "info": {"satcount": 1},
            "above": [
                {
                    "satid": 25544,
                    "satname": "INTERNATIONAL SPACE STATION",
                    "intDesignator": "1998-067A",
                    "launchDate": "1998-11-20",
                    "satlat": 51.5074,
                    "satlng": -0.1278,
                    "satalt": 418.93
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        satellite_data = get_satellite_data(51.5074, -0.1278)
        self.assertIsNotNone(satellite_data)
        self.assertEqual(satellite_data['info']['satcount'], 1)
        self.assertEqual(satellite_data['above'][0]['satname'], "INTERNATIONAL SPACE STATION")

if __name__ == '__main__':
    unittest.main()