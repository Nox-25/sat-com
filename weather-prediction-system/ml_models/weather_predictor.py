# weather-prediction-system/ml_models/weather_predictor.py

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

def create_features(df, label=None):
    """
    Creates time series features from a datetime index.
    """
    df = df.copy()
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week.astype(int)

    if label:
        X = df.drop([label], axis=1)
        y = df[label]
        return X, y
    return df

def train_time_series_model(df):
    """
    Trains a time-series forecasting model using a RandomForestRegressor.
    This model uses past temperature data to predict future temperature.

    Args:
        df (pandas.DataFrame): The preprocessed historical data with a datetime index.

    Returns:
        A trained model object with feature names stored.
    """
    if df is None or df.empty or 'temperature' not in df.columns:
        print("Input DataFrame is invalid for training.")
        return None

    # Create features and target
    X, y = create_features(df, label='temperature')

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    # *** FIX: Store the feature names on the model object ***
    model.feature_names = list(X.columns)

    print("Time-series model trained successfully.")
    return model

def make_time_series_prediction(model, prediction_date, historical_df):
    """
    Makes a weather prediction for a future date.

    Args:
        model: The trained time-series model, with `feature_names` attribute.
        prediction_date (datetime.date): The date for which to make a prediction.
        historical_df (pandas.DataFrame): The historical data, used for context.

    Returns:
        float: The predicted temperature.
    """
    if model is None or not hasattr(model, 'feature_names'):
        print("Model is invalid or does not have feature names.")
        return None

    # Create a DataFrame for the prediction date to generate features
    future_date_index = pd.to_datetime([prediction_date])
    future_df = pd.DataFrame(index=future_date_index)

    # Generate the same date-based features
    future_features = create_features(future_df)

    # Use the mean of the historical data for the other features
    future_features['humidity'] = historical_df['humidity'].mean()
    future_features['pressure'] = historical_df['pressure'].mean()

    # *** FIX: Reorder the columns to match the training order ***
    future_features = future_features[model.feature_names]

    prediction = model.predict(future_features)
    return prediction[0]

if __name__ == '__main__':
    # Example usage:
    # 1. Create sample historical data
    date_rng = pd.date_range(start='2022-01-01', end='2023-01-01', freq='D')
    sample_df = pd.DataFrame(date_rng, columns=['date'])
    sample_df['temperature'] = np.random.randint(0, 25, size=(len(date_rng)))
    sample_df['humidity'] = np.random.randint(70, 100, size=(len(date_rng)))
    sample_df['pressure'] = np.random.randint(98, 102, size=(len(date_rng)))
    sample_df.set_index('date', inplace=True)

    # 2. Train the model
    print("Training a dummy time-series model...")
    trained_model = train_time_series_model(sample_df)

    # 3. Make a prediction for a future date
    if trained_model:
        future_date = pd.to_datetime('2023-01-02').date()
        print(f"\nMaking a prediction for {future_date}...")
        # Pass the historical df for context
        prediction = make_time_series_prediction(trained_model, future_date, sample_df)
        if prediction is not None:
            print(f"Predicted temperature: {prediction:.2f}°C")
        else:
            print("Failed to make a prediction.")
    else:
        print("Model training failed.")