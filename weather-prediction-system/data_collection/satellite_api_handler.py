# weather-prediction-system/data_collection/satellite_api_handler.py

import requests
import json

# The user-provided OpenWeatherMap API key.
API_KEY = "fec017c5aa337914a16aca5e3e7c154b"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_API_URL = "https://nominatim.openstreetmap.org/search"

def get_coordinates(city_name):
    """
    Geocodes a city name to its latitude and longitude using Nominatim.
    A User-Agent is required by the Nominatim usage policy.
    """
    params = {'q': city_name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'WeatherPredictionSystem/1.0 (https://example.com/contact)'}
    try:
        response = requests.get(GEOCODING_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"])
            }
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding for '{city_name}': {e}")
    return None

def get_weather_data(city_name):
    """
    Fetches current weather and 5-day/3-hour forecast data using the standard
    OpenWeatherMap APIs.

    Args:
        city_name (str): The name of the city.

    Returns:
        dict: A dictionary containing both 'current' and 'forecast' data, or None on failure.
    """
    coords = get_coordinates(city_name)
    if not coords:
        print(f"Could not get coordinates for '{city_name}'.")
        return None

    # --- Fetch Current Weather ---
    current_params = {
        "lat": coords["latitude"],
        "lon": coords["longitude"],
        "appid": API_KEY,
        "units": "metric",
    }
    try:
        current_response = requests.get(CURRENT_WEATHER_URL, params=current_params, timeout=30)
        current_response.raise_for_status()
        current_data = current_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding current weather response: {current_response.text}")
        return None

    # --- Fetch 5-Day/3-Hour Forecast ---
    forecast_params = {
        "lat": coords["latitude"],
        "lon": coords["longitude"],
        "appid": API_KEY,
        "units": "metric",
    }
    try:
        forecast_response = requests.get(FORECAST_URL, params=forecast_params, timeout=30)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast weather: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding forecast weather response: {forecast_response.text}")
        return None

    return {
        "current": current_data,
        "forecast": forecast_data
    }

if __name__ == '__main__':
    # Example usage:
    city = "London"

    print(f"Fetching current and forecast weather for {city}...")
    weather_data = get_weather_data(city)

    if weather_data:
        print("\nSuccessfully fetched data:")
        if 'current' in weather_data:
            print(f"  Current Temp: {weather_data['current'].get('main', {}).get('temp')}°C")
            print(f"  Current Condition: {weather_data['current']['weather'][0]['description']}")

        if 'forecast' in weather_data:
            print(f"  Forecast timestamps available: {len(weather_data['forecast'].get('list', []))}")
            if weather_data['forecast'].get('list'):
                print(f"  Temp in 3 hours: {weather_data['forecast']['list'][0]['main']['temp']}°C")
    else:
        print("\nFailed to fetch weather data.")