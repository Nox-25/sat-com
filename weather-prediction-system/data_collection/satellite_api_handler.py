# weather-prediction-system/data_collection/satellite_api_handler.py

import requests
import json

# IMPORTANT: Replace "Your_API_Key" with your actual OpenWeatherMap API key.
# You can get a free API key by signing up on the OpenWeatherMap website: https://openweathermap.org/appid
API_KEY = "Your_API_Key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city_name):
    """
    Fetches weather data for a given city from the OpenWeatherMap API.

    Args:
        city_name (str): The name of the city for which to fetch weather data.

    Returns:
        dict: A dictionary containing the weather data, or None if the city is not found.
    """
    if API_KEY == "Your_API_Key":
        print("Please replace 'Your_API_Key' with your actual OpenWeatherMap API key.")
        return None

    complete_url = f"{BASE_URL}?appid={API_KEY}&q={city_name}"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        return data
    else:
        print(f"City '{city_name}' not found.")
        return None

if __name__ == '__main__':
    # Example usage:
    city = "London"
    weather_data = get_weather_data(city)

    if weather_data:
        # Extract and print relevant information
        main_data = weather_data.get("main", {})
        temperature_kelvin = main_data.get("temp")
        pressure = main_data.get("pressure")
        humidity = main_data.get("humidity")

        weather_description = "N/A"
        if "weather" in weather_data and weather_data["weather"]:
            weather_description = weather_data["weather"][0].get("description")

        # Convert temperature from Kelvin to Celsius for better readability
        temperature_celsius = temperature_kelvin - 273.15 if temperature_kelvin else None

        print(f"Weather in {city}:")
        if temperature_celsius is not None:
            print(f"  Temperature: {temperature_celsius:.2f}°C")
        else:
            print("  Temperature: Not available")
        print(f"  Atmospheric Pressure: {pressure} hPa")
        print(f"  Humidity: {humidity}%")
        print(f"  Description: {weather_description.capitalize()}")
    else:
        print("Could not retrieve weather data.")