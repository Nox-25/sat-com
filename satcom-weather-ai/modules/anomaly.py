import numpy as np
import pandas as pd

class AnomalyDetector:
    def __init__(self, historical_data):
        self.historical_data = historical_data
        self.stats = {}

    def calculate_stats(self, city):
        """Calculate mean and std dev for a city's weather parameters."""
        city_data = self.historical_data[self.historical_data['city'] == city]
        if len(city_data) < 30: # Need enough data to be statistically significant
            return

        self.stats[city] = {
            'temperature': {'mean': city_data['temperature'].mean(), 'std': city_data['temperature'].std()},
            'humidity': {'mean': city_data['humidity'].mean(), 'std': city_data['humidity'].std()},
            'pressure': {'mean': city_data['pressure'].mean(), 'std': city_data['pressure'].std()},
        }

    def detect_anomalies(self, city, current_data):
        """Detect anomalies in the current weather data."""
        if city not in self.stats:
            self.calculate_stats(city)

        anomalies = {}
        city_stats = self.stats.get(city)
        if not city_stats:
            return {'is_anomaly': False, 'details': "Insufficient historical data."}

        for param, values in city_stats.items():
            if param in current_data:
                mean, std = values['mean'], values['std']
                if std > 0:
                    z_score = (current_data[param] - mean) / std
                    if abs(z_score) > 3.0: # 3-sigma rule
                        anomalies[param] = {
                            'value': current_data[param],
                            'mean': mean,
                            'z_score': z_score
                        }

        return {'is_anomaly': bool(anomalies), 'details': anomalies}
