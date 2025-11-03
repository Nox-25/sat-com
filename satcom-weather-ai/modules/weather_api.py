import requests
import config

def get_weather_data(lat, lon):
    """Fetch weather data from OpenWeatherMap API."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={config.OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Extract relevant data
        weather_data = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'precipitation': data.get('rain', {}).get('1h', 0),
            'cloud_cover': data['clouds']['all']
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        # Fallback to wttr.in (example)
        return get_fallback_weather_data(lat, lon)

def get_fallback_weather_data(lat, lon):
    """Fallback to wttr.in if OpenWeatherMap fails."""
    url = f"https://wttr.in/{lat},{lon}?format=j1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['current_condition'][0]

        weather_data = {
            'temperature': float(data['temp_C']),
            'humidity': float(data['humidity']),
            'pressure': float(data['pressure']),
            'wind_speed': float(data['windspeedKmph']) / 3.6,  # Convert km/h to m/s
            'precipitation': float(data['precipMM']),
            'cloud_cover': float(data['cloudcover'])
        }
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fallback weather data: {e}")
        return None
