# weather-prediction-system/frontend/dashboard.py

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import altair as alt
import folium
from streamlit_folium import st_folium

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.satellite_api_handler import get_weather_data

def display_current_weather(data):
    """Displays the current weather conditions in a structured UI."""
    st.subheader("Current Climatic Conditions")

    current = data.get('current', {})
    if not current:
        st.warning("Current weather data not available.")
        return

    main = current.get("main", {})
    wind = current.get("wind", {})
    weather_desc = current.get("weather", [{}])[0].get("description", "N/A")

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{main.get('temp', 'N/A')}°C", f"Feels like {main.get('feels_like', 'N/A')}°C")
    col2.metric("Humidity", f"{main.get('humidity', 'N/A')}%")
    col3.metric("Pressure", f"{main.get('pressure', 'N/A')} hPa")

    st.markdown(f"**Condition:** `{weather_desc.capitalize()}`")

    with st.expander("See More Details (including Lat/Lon)"):
        coords = current.get("coord", {})
        sys_info = current.get("sys", {})

        st.metric("Latitude", f"{coords.get('lat', 'N/A')}")
        st.metric("Longitude", f"{coords.get('lon', 'N/A')}")

        col1_detail, col2_detail, col3_detail = st.columns(3)
        col1_detail.metric("Wind Speed", f"{wind.get('speed', 'N/A')} m/s")
        col2_detail.metric("Cloudiness", f"{current.get('clouds', {}).get('all', 'N/A')}%")
        col3_detail.metric("Visibility", f"{current.get('visibility', 'N/A')} m")

        sunrise = datetime.utcfromtimestamp(sys_info.get('sunrise', 0)).strftime('%H:%M:%S UTC') if sys_info.get('sunrise') else 'N/A'
        sunset = datetime.utcfromtimestamp(sys_info.get('sunset', 0)).strftime('%H:%M:%S UTC') if sys_info.get('sunset') else 'N/A'
        col1_detail.metric("Sunrise", sunrise)
        col2_detail.metric("Sunset", sunset)

def display_hourly_forecast(data):
    """Displays the 3-hour interval forecast for the next 24 hours."""
    st.subheader("Hourly Forecast (in 3-hour intervals)")

    forecast_list = data.get('forecast', {}).get('list', [])
    if not forecast_list:
        st.warning("Hourly forecast data not available.")
        return

    for item in forecast_list[:8]:
        dt_time = datetime.utcfromtimestamp(item.get('dt', 0))
        time_str = dt_time.strftime('%Y-%m-%d %H:%M')

        main = item.get('main', {})
        weather_desc = item.get('weather', [{}])[0].get('description', 'N/A')

        st.markdown(f"**{time_str} UTC**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Temp", f"{main.get('temp', 'N/A')}°C")
        col2.metric("Humidity", f"{main.get('humidity', 'N/A')}%")
        col3.metric("Condition", weather_desc.capitalize())
        st.divider()

def display_visualizations(data):
    """Displays the graph and map visualizations."""
    st.subheader("Visualizations")

    forecast_list = data.get('forecast', {}).get('list', [])
    current_data = data.get('current', {})

    if not forecast_list or not current_data:
        st.warning("Data not available for visualization.")
        return

    # --- Temperature Graph ---
    df_forecast = pd.DataFrame(forecast_list)
    df_forecast['dt_txt'] = pd.to_datetime(df_forecast['dt_txt'])
    df_forecast['temp'] = df_forecast['main'].apply(lambda x: x.get('temp'))

    temp_chart = alt.Chart(df_forecast).mark_line().encode(
        x=alt.X('dt_txt:T', title='Time'),
        y=alt.Y('temp:Q', title='Temperature (°C)'),
        tooltip=['dt_txt:T', 'temp:Q']
    ).properties(
        title="Temperature Forecast (Next 5 Days, 3-hr intervals)"
    ).interactive()
    st.altair_chart(temp_chart, use_container_width=True)

    # --- NASA GIBS Map ---
    coords = current_data.get('coord', {})
    if coords:
        # Using the TMS URL format for better compatibility
        gibs_layer = 'MODIS_Terra_CorrectedReflectance_TrueColor'
        current_date = datetime.utcnow().strftime('%Y-%m-%d')
        tile_url = (
            'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/'
            f'{gibs_layer}/default/{current_date}/1km/{{z}}/{{y}}/{{x}}.jpg'
        )

        m = folium.Map(location=[coords['lat'], coords['lon']], zoom_start=5)

        folium.TileLayer(
            tiles=tile_url,
            attr='NASA GIBS',
            name='NASA True Color',
            overlay=True,
            control=True
        ).add_to(m)

        folium.Marker([coords['lat'], coords['lon']], popup=current_data.get('name', 'Selected Location')).add_to(m)
        folium.LayerControl().add_to(m)

        st_folium(m, width=725, height=500)
    else:
        st.warning("Coordinates not available for map visualization.")

def display_prediction_summary(data):
    """Displays a simple summary of the forecast."""
    st.subheader("Prediction Summary")

    forecast_list = data.get('forecast', {}).get('list', [])
    if not forecast_list:
        st.warning("Forecast data not available for summary.")
        return

    temps = [item['main']['temp'] for item in forecast_list]
    min_temp = min(temps)
    max_temp = max(temps)

    conditions = [item['weather'][0]['main'] for item in forecast_list[:8]]
    most_common_condition = max(set(conditions), key=conditions.count)

    summary_text = f"""
    Over the next few days, the temperature will range from a low of **{min_temp}°C** to a high of **{max_temp}°C**.
    The weather will predominantly feature **{most_common_condition}**.
    """
    st.markdown(summary_text)

def main():
    st.title("Weather Prediction System")

    city_name = st.text_input("Enter a city name:", "London")

    if st.button("Get Weather"):
        if city_name:
            with st.spinner(f"Fetching weather data for {city_name}..."):
                weather_data = get_weather_data(city_name)

            if weather_data and 'current' in weather_data and 'forecast' in weather_data:
                display_current_weather(weather_data)
                display_hourly_forecast(weather_data)
                display_visualizations(weather_data)
                display_prediction_summary(weather_data)
            else:
                st.error(f"Could not fetch complete weather data for '{city_name}'. Please check the city name or API key.")
        else:
            st.warning("Please enter a city name.")

if __name__ == "__main__":
    main()