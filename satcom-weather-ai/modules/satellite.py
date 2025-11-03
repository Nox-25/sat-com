import requests
import config
from datetime import datetime

def get_satellite_positions(lat, lon):
    """Fetch positions of weather satellites from N2YO API."""
    positions = {}
    for sat_name, sat_id in config.WEATHER_SATELLITES.items():
        url = f"https://api.n2yo.com/rest/v1/satellite/positions/{sat_id}/{lat}/{lon}/0/1/&apiKey={config.N2YO_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if 'positions' in data and data['positions']:
                positions[sat_name] = data['positions'][0]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching satellite data for {sat_name}: {e}")
    return positions

def get_space_weather():
    """Fetch space weather data from NASA's OMNIWeb API (for SatCom Reliability Index)."""
    # This is a placeholder for a more complex API call
    # For now, we'll return a mock Kp-index
    return {'kp_index': 3}
