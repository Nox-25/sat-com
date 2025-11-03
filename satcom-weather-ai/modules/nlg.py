
def generate_summary(city, weather, anomaly_info, risk_scores):
    """Generates a human-readable summary of the weather conditions."""

    # Start with the basic conditions
    temp = weather.get('temperature', 'N/A')
    condition = "clear skies"
    if weather.get('cloud_cover', 0) > 75:
        condition = "overcast"
    elif weather.get('cloud_cover', 0) > 25:
        condition = "partly cloudy"
    if weather.get('precipitation', 0) > 5:
        condition = "rainy"

    summary = f"In {city}, the weather is currently {condition} with a temperature of {temp}°C."

    # Add anomaly information
    if anomaly_info.get('is_anomaly'):
        anomalous_params = list(anomaly_info['details'].keys())
        summary += f" ⚠️ ANOMALY DETECTED in {', '.join(anomalous_params)}."

    # Add risk information
    high_risk = [risk for risk, score in risk_scores.items() if score > 65]
    if high_risk:
        summary += f" There is a HIGH risk of {', '.join(high_risk)}."

    return summary
