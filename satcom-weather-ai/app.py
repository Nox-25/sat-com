import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Import your modules
import modules.weather_api as weather_api
import modules.satellite as satellite
from modules.anomaly import AnomalyDetector
import modules.risk as risk
import modules.nlg as nlg
from models.knn_model import KNNModel

# --- Page Configuration ---
st.set_page_config(
    page_title="SatCom Weather AI Platform",
    page_icon="🛰️",
    layout="wide"
)

# --- Load Data and Models ---
@st.cache_data
def load_data():
    """Load historical weather data and city geocodes."""
    historical_data = pd.read_csv('satcom-weather-ai/data/sample_weather.csv')
    city_geocodes = pd.read_csv('satcom-weather-ai/data/city_geocodes.csv')
    return historical_data, city_geocodes

historical_data, city_geocodes = load_data()
anomaly_detector = AnomalyDetector(historical_data)
knn_model = KNNModel()

# --- UI Sidebar ---
st.sidebar.title("🌍 City Selection")
city_name = st.sidebar.selectbox("Select a city:", city_geocodes['city'])
analyze_button = st.sidebar.button("Analyze Weather", type="primary")

st.sidebar.markdown("---")
st.sidebar.header("🛰️ Satellite Coverage")
# Placeholder for satellite reliability
st.sidebar.dataframe(pd.DataFrame({
    'Satellite': list(satellite.config.WEATHER_SATELLITES.keys()),
    'Reliability': [f"{100*0.95:.1f}%"] * len(satellite.config.WEATHER_SATELLITES) # Mock reliability
}))

# --- Main Dashboard ---
st.title("🛰️ SatCom Weather AI Platform")

if analyze_button:
    # --- Geocoding ---
    city_info = city_geocodes[city_geocodes['city'] == city_name].iloc[0]
    lat, lon = city_info['latitude'], city_info['longitude']

    # --- API Calls ---
    with st.spinner("Fetching real-time data..."):
        weather_data = weather_api.get_weather_data(lat, lon)
        satellite_positions = satellite.get_satellite_positions(lat, lon)

    if weather_data:
        st.header(f"Weather Analysis for {city_name}")

        # --- NLP Summary ---
        knn_prediction = knn_model.predict(weather_data)
        risk_scores = risk.calculate_risk_scores(weather_data, knn_prediction)
        anomaly_info = anomaly_detector.detect_anomalies(city_name, weather_data)
        summary = nlg.generate_summary(city_name, weather_data, anomaly_info, risk_scores)
        st.info(summary)

        # --- Metrics Display ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{weather_data['temperature']} °C")
        col2.metric("Humidity", f"{weather_data['humidity']}%")
        col3.metric("Pressure", f"{weather_data['pressure']} hPa")
        col4.metric("Wind Speed", f"{weather_data['wind_speed']:.2f} m/s")

        # --- Anomaly & Risk ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚨 Anomaly Detection")
            if anomaly_info['is_anomaly']:
                st.error("Anomaly Detected!")
                st.write(anomaly_info['details'])
            else:
                st.success("No anomalies detected.")
        with col2:
            st.subheader("📈 Risk Scores")
            st.dataframe(pd.DataFrame.from_dict(risk_scores, orient='index', columns=['Score']))

        # --- Satellite Map ---
        st.subheader("🛰️ Satellite Positions")
        m = folium.Map(location=[lat, lon], zoom_start=4)
        folium.Marker([lat, lon], popup=city_name, icon=folium.Icon(color='red')).add_to(m)
        for sat, pos in satellite_positions.items():
            folium.Marker(
                [pos['satlatitude'], pos['satlongitude']],
                popup=f"{sat} (Alt: {pos['sataltitude']:.2f} km)",
                icon=folium.Icon(icon='satellite', prefix='fa')
            ).add_to(m)
        st_folium(m, width=700, height=500)

        # --- Temperature History ---
        st.subheader("🌡️ Temperature History")
        city_history = historical_data[historical_data['city'] == city_name]
        st.line_chart(city_history.set_index('date')['temperature'])

    else:
        st.error("Could not fetch weather data. Please try again later.")
else:
    st.info("Select a city and click 'Analyze Weather' to begin.")
