import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class KNNModel:
    def __init__(self, model_path='satcom-weather-ai/models/knn_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None

    def train(self, data_path='satcom-weather-ai/data/sample_weather.csv'):
        """Train the KNN model and save it."""
        df = pd.read_csv(data_path)
        features = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation', 'cloud_cover']
        target = 'risk_level'

        X = df[features]
        y = df[target]

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        self.model = KNeighborsClassifier(n_neighbors=5)
        self.model.fit(X_train_scaled, y_train)

        # Save the trained model and scaler
        joblib.dump((self.model, self.scaler), self.model_path)

    def predict(self, weather_data):
        """Predict the risk level for new weather data."""
        if self.model is None or self.scaler is None:
            if os.path.exists(self.model_path):
                self.model, self.scaler = joblib.load(self.model_path)
            else:
                self.train() # Train if model doesn't exist

        df = pd.DataFrame([weather_data])
        features = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation', 'cloud_cover']
        X_new = df[features]

        X_new_scaled = self.scaler.transform(X_new)

        return self.model.predict(X_new_scaled)[0]
