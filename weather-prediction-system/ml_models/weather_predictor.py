# weather-prediction-system/ml_models/weather_predictor.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

def train_weather_model(data):
    """
    A placeholder function to train a weather prediction model.
    In a real application, this would involve a more sophisticated model
    and a much larger dataset.

    Args:
        data (pandas.DataFrame): The preprocessed training data.

    Returns:
        A trained model object (in this case, a simple RandomForestRegressor).
    """
    if data is None or data.empty:
        return None

    # For this example, we'll generate some dummy target data
    # In a real scenario, this would be the actual future weather data
    np.random.seed(42)
    data['future_temp'] = data['temp'] + np.random.normal(0, 0.1, len(data))

    # Features (X) and target (y)
    X = data[['temp', 'pressure', 'humidity']]
    y = data['future_temp']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train a simple model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model (optional, for demonstration)
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"Model Mean Squared Error: {mse:.4f}")

    return model

def make_prediction(model, input_data):
    """
    Makes a weather prediction using the trained model.

    Args:
        model: The trained model object.
        input_data (pandas.DataFrame): The input data for prediction.

    Returns:
        The prediction.
    """
    if model is None or input_data is None or input_data.empty:
        return None

    # Ensure input_data has the right columns
    input_features = input_data[['temp', 'pressure', 'humidity']]

    prediction = model.predict(input_features)
    return prediction

if __name__ == '__main__':
    # Example usage:
    # 1. Create some sample preprocessed data
    sample_data = {
        'temp': [0.5, 0.6, 0.4, 0.7],
        'pressure': [0.8, 0.7, 0.9, 0.6],
        'humidity': [0.4, 0.5, 0.3, 0.6]
    }
    df = pd.DataFrame(sample_data)

    # 2. Train the model
    print("Training a dummy weather model...")
    trained_model = train_weather_model(df)

    # 3. Make a prediction on new data
    if trained_model:
        new_data_point = pd.DataFrame({
            'temp': [0.55],
            'pressure': [0.75],
            'humidity': [0.45]
        })
        print("\nMaking a prediction for a new data point...")
        prediction = make_prediction(trained_model, new_data_point)
        if prediction is not None:
            print(f"Predicted future temperature: {prediction[0]:.4f}")
        else:
            print("Failed to make a prediction.")
    else:
        print("Model training failed.")