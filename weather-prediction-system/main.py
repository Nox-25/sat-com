
Satellite-based Weather Data Acquisition and Analysis System
A comprehensive system with AI-powered anomaly detection, satellite tracking,
forecast fusion, NLP summaries, disaster risk scoring, and global warming analysis.
"""

import json
import random
import math
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error
import threading
from collections import deque
import numpy as np
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

N2YO_API_KEY = os.environ.get("N2YO_API_KEY")
NASA_API_KEY = os.environ.get("NASA_API_KEY")
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

# Weather satellite NORAD IDs
WEATHER_SATELLITES = {
"NOAA-18": 28654,
"NOAA-19": 33591,
"NOAA-20": 43013,
"METOP-B": 38771,
"METOP-C": 43689
}

# Global data store
weather_data_history = deque(maxlen=1000)
satellite_positions = {}
anomalies = []
global_warming_data = []
city_cache = {} # Cache for city-specific data

# Major world cities database
WORLD_CITIES = {
'chennai': (13.0827, 80.2707, 'Chennai, India'),
'delhi': (28.6139, 77.2090, 'Delhi, India'),
'mumbai': (19.0760, 72.8777, 'Mumbai, India'),
'bangalore': (12.9716, 77.5946, 'Bangalore, India'),
'kolkata': (22.5726, 88.3639, 'Kolkata, India'),
'hyderabad': (17.3850, 78.4867, 'Hyderabad, India'),
'pune': (18.5204, 73.8567, 'Pune, India'),
'ahmedabad': (23.0225, 72.5714, 'Ahmedabad, India'),
'jaipur': (26.9124, 75.7873, 'Jaipur, India'),
'lucknow': (26.8467, 80.9462, 'Lucknow, India'),
'new york': (40.7128, -74.0060, 'New York, USA'),
'london': (51.5074, -0.1278, 'London, UK'),
'tokyo': (35.6762, 139.6503, 'Tokyo, Japan'),
'paris': (48.8566, 2.3522, 'Paris, France'),
'dubai': (25.2048, 55.2708, 'Dubai, UAE'),
'singapore': (1.3521, 103.8198, 'Singapore'),
'sydney': (-33.8688, 151.2093, 'Sydney, Australia'),
'beijing': (39.9042, 116.4074, 'Beijing, China'),
'moscow': (55.7558, 37.6173, 'Moscow, Russia'),
'toronto': (43.6532, -79.3832, 'Toronto, Canada'),
'los angeles': (34.0522, -118.2437, 'Los Angeles, USA'),
'berlin': (52.5200, 13.4050, 'Berlin, Germany'),
'rome': (41.9028, 12.4964, 'Rome, Italy'),
'madrid': (40.4168, -3.7038, 'Madrid, Spain'),
'bangkok': (13.7563, 100.5018, 'Bangkok, Thailand'),
'cairo': (30.0444, 31.2357, 'Cairo, Egypt'),
'mexico city': (19.4326, -99.1332, 'Mexico City, Mexico'),
'sao paulo': (-23.5505, -46.6333, 'São Paulo, Brazil'),
'istanbul': (41.0082, 28.9784, 'Istanbul, Turkey'),
'seoul': (37.5665, 126.9780, 'Seoul, South Korea'),
}

# ============================================================================
# GEOCODING - Get coordinates from city name
# ============================================================================

def geocode_city(city_name):
"""Get coordinates for a city name using Nominatim API"""
city_lower = city_name.lower().strip()

# Check local database first
if city_lower in WORLD_CITIES:
lat, lon, full_name = WORLD_CITIES[city_lower]
return {'lat': lat, 'lon': lon, 'name': full_name, 'found': True}

# Try OpenStreetMap Nominatim API
try:
query = urllib.parse.quote(city_name)
url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
req = urllib.request.Request(url, headers={'User-Agent': 'WeatherAnalysisSystem/1.0'})

with urllib.request.urlopen(req, timeout=10) as response:
data = json.loads(response.read().decode())
if data and len(data) > 0:
result = data[0]
return {
'lat': float(result['lat']),
'lon': float(result['lon']),
'name': result['display_name'],
'found': True
}
except Exception as e:
print(f"Geocoding error for {city_name}: {e}")

return {'found': False, 'error': 'City not found'}

# ============================================================================
# DATA ACQUISITION
# ============================================================================

def fetch_satellite_position(sat_id, sat_name, observer_lat=13.0827, observer_lng=80.2707):
"""Fetch real-time satellite position from N2YO API"""
try:
url = f"https://api.n2yo.com/rest/v1/satellite/positions/{sat_id}/{observer_lat}/{observer_lng}/0/1/&apiKey={N2YO_API_KEY}"
with urllib.request.urlopen(url, timeout=10) as response:
data = json.loads(response.read().decode())
if 'positions' in data and len(data['positions']) > 0:
pos = data['positions'][0]
return {
'name': sat_name,
'latitude': pos['satlatitude'],
'longitude': pos['satlongitude'],
'altitude': pos['sataltitude'],
'azimuth': pos['azimuth'],
'elevation': pos['elevation'],
'timestamp': pos['timestamp']
}
except Exception as e:
print(f"Error fetching satellite {sat_name}: {e}")
return None

def fetch_openweathermap_data(lat, lon):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("cod") != 200:
                print(f"Error fetching OpenWeatherMap data: {data.get('message')}")
                return None

            return {
                'temperature': data['main']['temp'],
                'precipitation': data.get('rain', {}).get('1h', 0),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'cloud_cover': data['clouds']['all']
            }
    except Exception as e:
        print(f"Error fetching OpenWeatherMap data: {e}")
        return None


# ============================================================================
# AI-POWERED ANOMALY DETECTION
# ============================================================================

class WeatherAnomalyDetector:
    """Dynamically learns norms to detect weather anomalies."""

    def __init__(self, threshold=3.0): # Using a slightly higher threshold
        self.threshold = threshold
        self.stats = {}

    def update_stats(self, data_history):
        """Update statistics from historical data for a specific location."""
        if len(data_history) < 20: # Require more data for stable stats
            return

        params_to_track = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation', 'cloud_cover']
        for param in params_to_track:
            values = [d[param] for d in data_history if param in d and d[param] is not None]
            if len(values) > 10:
                mean = np.mean(values)
                std = np.std(values)
                if std > 0: # Avoid division by zero
                    self.stats[param] = {'mean': mean, 'std': std}

    def detect_anomaly(self, data):
        """Detect if a data point is anomalous based on learned stats."""
        anomalies_detected = []
        anomaly_score = 0

        if not self.stats:
            return {
                'is_anomaly': False,
                'score': 0,
                'details': [{'message': "Insufficient historical data for anomaly detection."}]
            }

        for param, stats in self.stats.items():
            if param in data and data[param] is not None:
                value = data[param]
                z_score = abs((value - stats['mean']) / stats['std'])
                if z_score > self.threshold:
                    anomaly_score += z_score
                    anomalies_detected.append({
                        'parameter': param,
                        'value': value,
                        'expected': round(stats['mean'], 2),
                        'z_score': round(z_score, 2)
                    })

        return {
            'is_anomaly': len(anomalies_detected) > 0,
            'score': round(anomaly_score, 2),
            'details': anomalies_detected
        }

# ============================================================================
# WEATHER FORECAST FUSION
# ============================================================================

def fetch_openweathermap_forecast(lat, lon):
    """Fetch 5-day/3-hour forecast data from OpenWeatherMap API"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("cod") != "200":
                print(f"Error fetching OpenWeatherMap forecast: {data.get('message')}")
                return None
            return data['list']
    except Exception as e:
        print(f"Error fetching OpenWeatherMap forecast: {e}")
        return None

class ForecastFusion:
    """Hybrid forecast engine combining multiple sources."""

    def __init__(self):
        # Weights can be adjusted based on model reliability
        self.source_weights = {
            'OpenWeatherMap': 0.6,
            'Synthetic_GFS': 0.2,
            'Synthetic_ECMWF': 0.2
        }

    def get_forecasts(self, lat, lon):
        """Get forecasts from multiple sources, including real and synthetic."""
        forecasts = {}

        # Real data from OpenWeatherMap
        owm_forecast = fetch_openweathermap_forecast(lat, lon)
        if owm_forecast and len(owm_forecast) > 0:
            # Taking the forecast for the next 24 hours (8 * 3-hour intervals)
            next_24h = owm_forecast[:8]
            forecasts['OpenWeatherMap'] = {
                'temperature': np.mean([f['main']['temp'] for f in next_24h]),
                'humidity': np.mean([f['main']['humidity'] for f in next_24h]),
                'precipitation_prob': np.mean([f.get('pop', 0) for f in next_24h]) * 100,
                'wind_speed': np.mean([f['wind']['speed'] for f in next_24h])
            }

        # Synthetic data for other models (for demonstration)
        base_temp = forecasts.get('OpenWeatherMap', {'temperature': 25})['temperature']
        forecasts['Synthetic_GFS'] = {
            'temperature': base_temp + random.uniform(-2, 2),
            'humidity': 65 + random.uniform(-15, 15),
            'precipitation_prob': random.uniform(0, 100),
            'wind_speed': 10 + random.uniform(-7, 7)
        }
        forecasts['Synthetic_ECMWF'] = {
            'temperature': base_temp + random.uniform(-1, 1),
            'humidity': 65 + random.uniform(-10, 10),
            'precipitation_prob': random.uniform(0, 100),
            'wind_speed': 10 + random.uniform(-5, 5)
        }

        return forecasts

    def fuse_forecasts(self, forecasts):
        """Combine forecasts using a weighted average."""
        fused = {}
        total_weight = sum(self.source_weights.get(source, 0) for source in forecasts)

        if total_weight == 0:
            return {'error': 'No forecast data available'}

        for param in ['temperature', 'humidity', 'precipitation_prob', 'wind_speed']:
            weighted_sum = sum(
                forecasts[source][param] * self.source_weights.get(source, 0)
                for source in forecasts if source in self.source_weights and param in forecasts[source]
            )
            fused[param] = round(weighted_sum / total_weight, 2)

        # Confidence based on the weight of the real data source
        fused['confidence'] = round(self.source_weights.get('OpenWeatherMap', 0) / total_weight * 100, 2)
        fused['sources'] = {k: {p: round(v, 2) for p, v in d.items()} for k, d in forecasts.items()}

        return fused

# ============================================================================
# DISASTER RISK SCORING
# ============================================================================

class DisasterRiskScorer:
    """Calculates disaster risk with more nuanced, non-linear scoring."""

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + math.exp(-x))

    @staticmethod
    def calculate_flood_risk(data):
        """Calculate flood risk (0-100) with weighted and scaled factors."""
        score = 0

        # Precipitation is the most critical factor
        precip = data.get('precipitation', 0)
        score += (precip ** 1.5) * 5 # Exponential impact

        # Humidity contributes, but less critically
        humidity = data.get('humidity', 0)
        if humidity > 80:
            score += (humidity - 80) * 0.5

        # Low pressure systems can indicate heavy rain
        pressure = data.get('pressure', 1013)
        if pressure < 1000:
            score += (1000 - pressure) * 1.5

        return min(round(score), 100)

    @staticmethod
    def calculate_drought_risk(data, city_history):
        """Calculate drought risk (0-100) considering recent weather patterns."""
        score = 0

        # High temperature is a key driver
        temp = data.get('temperature', 20)
        if temp > 30:
            score += (temp - 30) * 2.5

        # Lack of precipitation
        precip = data.get('precipitation', 0)
        if precip < 1:
            score += (1 - precip) * 15

        # Consider historical rainfall
        if len(city_history) > 10:
            recent_precip = np.mean([d.get('precipitation', 0) for d in city_history[-30:]])
            if recent_precip < 0.5:
                score += (0.5 - recent_precip) * 30

        return min(round(score), 100)

    @staticmethod
    def calculate_storm_risk(data):
        """Calculate storm risk (0-100) with a focus on wind and pressure drop."""
        score = 0

        # Wind speed is the primary indicator
        wind_speed = data.get('wind_speed', 0)
        score += (wind_speed ** 1.7) * 1.5 # Wind has a high power relationship with damage

        # Rapidly dropping or low pressure
        pressure = data.get('pressure', 1013)
        if pressure < 1005:
            score += (1005 - pressure) * 2

        # Heavy precipitation
        precip = data.get('precipitation', 0)
        if precip > 5:
            score += precip * 2

        return min(round(score), 100)

@staticmethod
def get_all_risks(data, city_history):
    """Get all risk scores."""
    return {
        'flood': DisasterRiskScorer.calculate_flood_risk(data),
        'drought': DisasterRiskScorer.calculate_drought_risk(data, city_history),
        'storm': DisasterRiskScorer.calculate_storm_risk(data)
    }

# ============================================================================
# GLOBAL WARMING ANALYSIS
# ============================================================================

class GlobalWarmingAnalyzer:
"""Track and analyze temperature trends"""

def __init__(self):
self.baseline_temp = 25.0
self.historical_data = deque(maxlen=365) # Store 1 year

def add_data_point(self, temperature):
"""Add temperature data point"""
self.historical_data.append({
'temperature': temperature,
'timestamp': datetime.now()
})

def analyze_trend(self):
"""Analyze temperature trends"""
if len(self.historical_data) < 30:
return {
'trend': 'insufficient_data',
'change': 0,
'average_temp': self.baseline_temp
}

recent_avg = np.mean([d['temperature'] for d in list(self.historical_data)[-30:]])
older_avg = np.mean([d['temperature'] for d in list(self.historical_data)[:30]])

change = recent_avg - older_avg

return {
'trend': 'rising' if change > 0.5 else 'falling' if change < -0.5 else 'stable',
'change': round(change, 2),
'recent_average': round(recent_avg, 2),
'baseline_average': round(older_avg, 2),
'annual_projection': round(change * 12, 2) # Monthly to annual
}

# ============================================================================
# NLP WEATHER SUMMARY GENERATOR
# ============================================================================

class WeatherSummaryGenerator:
    """Generates insightful, human-readable weather summaries."""

    @staticmethod
    def get_weather_condition(data):
        """Translate weather data into a descriptive condition."""
        temp = data.get('temperature', 20)
        precip = data.get('precipitation', 0)
        cloud_cover = data.get('cloud_cover', 0)

        if precip > 2.5:
            return f"heavy rain with temperatures around {temp}°C"
        if precip > 0.5:
            return f"light rain and {temp}°C"
        if cloud_cover > 80:
            return f"heavily overcast skies and {temp}°C"
        if cloud_cover > 50:
            return f"cloudy skies with temperatures at {temp}°C"
        if temp > 32:
            return f"very hot and sunny conditions at {temp}°C"
        if temp < 10:
            return f"clear but cold weather at {temp}°C"
        return f"pleasant weather with clear skies at {temp}°C"

    @staticmethod
    def generate_summary(data, anomaly_info, risks):
        """Generate a more detailed and context-aware summary."""
        location = data.get('city', 'an unknown location')
        condition = WeatherSummaryGenerator.get_weather_condition(data)

        summary = f"Currently, {location} is experiencing {condition}."

        # Add wind details
        wind_speed = data.get('wind_speed', 0)
        if wind_speed > 10:
            summary += f" Expect strong winds of up to {wind_speed:.1f} m/s."

        # Anomaly reporting
        if anomaly_info.get('is_anomaly'):
            details = anomaly_info.get('details', [{}])[0]
            param = details.get('parameter', 'weather').replace('_', ' ')
            summary += f" An unusual {param} reading has been detected, which is outside the normal range for this area."

        # Risk assessment
        high_risks = {r_type: r_val for r_type, r_val in risks.items() if r_val > 65}
        if high_risks:
            risk_type = max(high_risks, key=high_risks.get)
            summary += f" There is a HIGH risk of {risk_type}, please take necessary precautions."

        # Forecast outlook
        forecast = data.get('forecast', {})
        if forecast and 'temperature' in forecast:
            forecast_temp = forecast['temperature']
            summary += f" The 24-hour forecast suggests an average temperature of {forecast_temp:.1f}°C."

        return summary

# ============================================================================
# COMPREHENSIVE WEATHER ANALYSIS FOR CITY
# ============================================================================

def analyze_city_weather(city_name):
"""Complete weather analysis for a given city"""

# Geocode city
location = geocode_city(city_name)
if not location.get('found'):
return {'error': 'City not found', 'city': city_name}

lat = location['lat']
lon = location['lon']
full_name = location['name']

# Fetch weather data
weather_data = fetch_openweathermap_data(lat, lon)
if not weather_data or not weather_data.get('temperature'):
    return {'error': 'Could not fetch weather data', 'city': city_name}

weather_data['latitude'] = lat
weather_data['longitude'] = lon
weather_data['timestamp'] = datetime.now().isoformat()

weather_data['city'] = full_name
weather_data['coordinates'] = {'lat': lat, 'lon': lon}

# AI Anomaly Detection
city_history = [d for d in weather_data_history if d.get('city') == full_name]
anomaly_detector = WeatherAnomalyDetector()
anomaly_detector.update_stats(city_history)
anomaly_info = anomaly_detector.detect_anomaly(weather_data)
weather_data['anomaly'] = anomaly_info

if anomaly_info['is_anomaly']:
    anomalies.append({
        'city': full_name,
        'timestamp': datetime.now().isoformat(),
        'details': anomaly_info['details']
    })

# Disaster Risk Scoring
risks = DisasterRiskScorer.get_all_risks(weather_data, city_history)
weather_data['risks'] = risks

# Forecast Fusion
fusion = ForecastFusion()
forecasts = fusion.get_forecasts(lat, lon)
fused_forecast = fusion.fuse_forecasts(forecasts)
weather_data['forecast'] = fused_forecast

# Satellite Coverage
nearest_satellites = []
for sat_name, sat_data in satellite_positions.items():
if sat_data:
# Calculate simple distance
sat_lat = sat_data.get('latitude', 0)
sat_lon = sat_data.get('longitude', 0)
dist = math.sqrt((lat - sat_lat)**2 + (lon - sat_lon)**2)
nearest_satellites.append({
'name': sat_name,
'distance': round(dist, 2),
'data': sat_data
})

nearest_satellites.sort(key=lambda x: x['distance'])
weather_data['satellites'] = nearest_satellites[:3] # Top 3 nearest

# Global Warming Analysis
global_warming_analyzer = GlobalWarmingAnalyzer()
if 'temperature' in weather_data:
global_warming_analyzer.add_data_point(weather_data['temperature'])
trend = global_warming_analyzer.analyze_trend()
weather_data['climate_trend'] = trend

# NLP Summary
summary = WeatherSummaryGenerator.generate_summary(
weather_data, anomaly_info, risks
)
weather_data['ai_summary'] = summary

# Store in history
weather_data_history.append(weather_data)

# Cache result
city_cache[city_name.lower()] = {
'data': weather_data,
'timestamp': time.time()
}

return weather_data

# ============================================================================
# DATA COLLECTION WORKER
# ============================================================================

def data_collection_worker():
"""Background worker to collect data periodically"""

default_locations = [
(13.0827, 80.2707, "Chennai"),
(28.6139, 77.2090, "Delhi"),
(19.0760, 72.8777, "Mumbai"),
]

while True:
try:
# Update satellite positions
for sat_name, sat_id in WEATHER_SATELLITES.items():
pos = fetch_satellite_position(sat_id, sat_name)
if pos:
satellite_positions[sat_name] = pos

# Collect weather data for default locations
for lat, lon, city in default_locations:
try:
analyze_city_weather(city)
except Exception as e:
print(f"Error analyzing {city}: {e}")

time.sleep(120) # Update every 2 minutes

except Exception as e:
print(f"Error in data collection: {e}")
time.sleep(60)

# ============================================================================
# WEB SERVER
# ============================================================================

class WeatherHTTPHandler(BaseHTTPRequestHandler):

def do_GET(self):
if self.path == '/':
self.send_response(200)
self.send_header('Content-type', 'text/html')
self.end_headers()
self.wfile.write(HTML_TEMPLATE.encode())

elif self.path == '/api/weather':
self.send_response(200)
self.send_header('Content-type', 'application/json')
self.end_headers()
response = {
'weather_data': list(weather_data_history)[-100:],
'satellites': satellite_positions,
'anomalies': anomalies[-20:],
}
self.wfile.write(json.dumps(response).encode())

elif self.path.startswith('/api/city/'):
city_name = urllib.parse.unquote(self.path.split('/api/city/')[1])
self.send_response(200)
self.send_header('Content-type', 'application/json')
self.send_header('Access-Control-Allow-Origin', '*')
self.end_headers()

try:
result = analyze_city_weather(city_name)
self.wfile.write(json.dumps(result).encode())
except Exception as e:
error_response = {'error': str(e), 'city': city_name}
self.wfile.write(json.dumps(error_response).encode())

else:
self.send_response(404)
self.end_headers()

def log_message(self, format, *args):
pass # Suppress logs

# ============================================================================
# HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = """












🛰️ Satellite Weather Analysis System


AI-Powered Weather Monitoring with Real-Time Satellite Tracking






🔍 Enter City Name for Complete Weather Analysis




onkeypress="if(event.key==='Enter') searchCity()">





Examples:
Chennai
Mumbai
Delhi
New York
London
Tokyo














📊 Current Weather Data










🛰️ Satellite Coverage










⚠️ AI Anomaly Detection










🚨 Disaster Risk Assessment










🔮 Hybrid Forecast Model










🌡️ Climate Trend Analysis












🤖 AI-Generated Weather Summary
















"""

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function to start the application."""
    # Check for API keys
    if not N2YO_API_KEY or not OPENWEATHERMAP_API_KEY:
        print("=" * 70)
        print("ERROR: API akeys are not configured.")
        print("Please set the following environment variables:")
        print("  export N2YO_API_KEY='Your N2YO API Key'")
        print("  export OPENWEATHERMAP_API_KEY='Your OpenWeatherMap API Key'")
        print("=" * 70)
        return

    print("=" * 70)
    print("🛰️ SATELLITE WEATHER ANALYSIS SYSTEM")
    print("=" * 70)
    print("\nStarting system with features:")
print(" ✓ AI-Powered Weather Anomaly Detection")
print(" ✓ Real-Time Satellite Position Tracking")
print(" ✓ Multi-Source Forecast Fusion")
print(" ✓ NLP Weather Summary Generation")
print(" ✓ Disaster Risk Scoring System")
print(" ✓ Global Warming Trend Analysis")
print(" ✓ City Search Functionality")
print("\n" + "=" * 70)

# Start data collection worker in background
collector_thread = threading.Thread(target=data_collection_worker, daemon=True)
collector_thread.start()
print("\n✓ Data collection worker started")

# Start web server
PORT = 8000
server = HTTPServer(('0.0.0.0', PORT), WeatherHTTPHandler)

print(f"\n🌐 Web dashboard starting on http://localhost:{PORT}")
print("\n" + "=" * 70)
print("📊 How to Use:")
print(" 1. Open http://localhost:8000 in your browser")
print(" 2. Enter any city name (e.g., Chennai, New York, Tokyo)")
print(" 3. Get comprehensive weather analysis with all parameters:")
print(" • Current weather data")
print(" • Nearest satellite coverage")
print(" • AI anomaly detection")
print(" • Disaster risk scores (Flood, Drought, Storm)")
print(" • Hybrid forecast from multiple models")
print(" • Climate trend analysis")
print(" • Natural language summary")
print("=" * 70)
print("\n✨ System is ready! Open http://localhost:8000 in your browser\n")

try:
server.serve_forever()
except KeyboardInterrupt:
print("\n\n🛑 Shutting down system...")
server.shutdown()
print("✓ System stopped successfully\n")

if __name__ == "__main__":
main()
