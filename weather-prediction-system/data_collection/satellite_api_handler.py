# weather-prediction-system/data_collection/satellite_api_handler.py

import requests
import json
from datetime import datetime

# The user-provided NASA POWER API key.
# Based on documentation, this is not typically used as a URL parameter
# for the basic public API, but it's stored here as requested.
API_KEY = "LLG5HAJdq5vhOr9smY9QLnJibDNgPk6PsTt9Xfsf"
NASA_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
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

def get_historical_weather_data(city_name, start_date, end_date):
    """
    Fetches historical weather data from the NASA POWER API.

    Args:
        city_name (str): The name of the city.
        start_date (str): The start date in YYYY-MM-DD format.
        end_date (str): The end date in YYYY-MM-DD format.

    Returns:
        dict: A dictionary containing the parsed historical weather data, or None on failure.
    """
    coords = get_coordinates(city_name)
    if not coords:
        print(f"Could not get coordinates for '{city_name}'.")
        return None

    try:
        start_str = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d")
        end_str = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return None

    params = {
        "parameters": "T2M,RH2M,PS",  # Temp at 2m, Humidity at 2m, Surface Pressure
        "community": "RE",
        "longitude": coords["longitude"],
        "latitude": coords["latitude"],
        "start": start_str,
        "end": end_str,
        "format": "JSON",
    }

    try:
        response = requests.get(NASA_POWER_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Parse the data into a more friendly format (e.g., a DataFrame-like structure)
        return parse_nasa_power_data(data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA POWER data: {e}")
    except json.JSONDecodeError:
        print(f"Error decoding NASA POWER API response. Response was: {response.text}")
    return None

def parse_nasa_power_data(raw_data):
    """
    Parses the complex JSON structure from the NASA POWER API into a simple
    list of records, which is easier to convert to a pandas DataFrame.
    """
    params = raw_data.get('properties', {}).get('parameter', {})
    if not params:
        return None

    # Assuming T2M, RH2M, PS are the requested parameters
    t2m = params.get('T2M', {})
    rh2m = params.get('RH2M', {})
    ps = params.get('PS', {})

    dates = list(t2m.keys())
    records = []

    for date_str in dates:
        # The API returns -999 for missing values
        temp = t2m.get(date_str)
        humidity = rh2m.get(date_str)
        pressure = ps.get(date_str)

        if -999 in (temp, humidity, pressure):
            continue # Skip days with missing data

        records.append({
            "date": datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d"),
            "temperature": temp,
            "humidity": humidity,
            "pressure": pressure
        })

    return records

if __name__ == '__main__':
    # Example usage:
    city = "London"
    start = "2023-01-01"
    end = "2023-01-05"

    print(f"Fetching historical weather data for {city} from {start} to {end}...")
    historical_data = get_historical_weather_data(city, start, end)

    if historical_data:
        print("Successfully fetched and parsed data:")
        for record in historical_data[:3]: # Print first 3 records
            print(record)
    else:
        print("Failed to fetch historical weather data.")