
def calculate_risk_scores(weather_data, knn_prediction):
    """
    Calculates risk scores for flood, drought, and storm.
    Combines rule-based logic with KNN model's prediction.
    """
    scores = {'flood': 0, 'drought': 0, 'storm': 0}

    # Rule-based scoring
    if weather_data.get('precipitation', 0) > 15:
        scores['flood'] += 50
    if weather_data.get('humidity', 0) > 85:
        scores['flood'] += 20

    if weather_data.get('temperature', 20) > 35 and weather_data.get('humidity', 100) < 30:
        scores['drought'] += 60

    if weather_data.get('wind_speed', 0) > 20:
        scores['storm'] += 50
    if weather_data.get('pressure', 1013) < 1000:
        scores['storm'] += 30

    # Integrate KNN prediction
    if knn_prediction == 'High':
        # Boost all scores if KNN predicts high risk
        scores['flood'] = min(100, scores['flood'] + 30)
        scores['drought'] = min(100, scores['drought'] + 30)
        scores['storm'] = min(100, scores['storm'] + 30)
    elif knn_prediction == 'Moderate':
        scores['flood'] = min(100, scores['flood'] + 15)
        scores['storm'] = min(100, scores['storm'] + 15)

    return scores
