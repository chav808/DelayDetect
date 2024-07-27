import streamlit as st
import requests
from datetime import datetime

# API key and endpoint
api_key = "amk9ziucGrEtmkrDm0WGE7nGEB5Nosog"
api_url = "https://api.tomorrow.io/v4/timelines"

# Title and header
st.title("Flight Delay Predictor")
st.header("Check the likelihood of flight delays based on weather conditions")

# Instructions
st.markdown("""
Enter your flight information to check if there is a high likelihood of delays due to thunderstorms or severe winds.
""")

# User input: Location and Date
country = st.selectbox("Select your country", ["USA", "Canada", "UK", "Australia", "Other"])
state = st.text_input("Enter your state (if applicable)")
city = st.text_input("Enter your city")
flight_date = st.date_input("Select your flight date")

# Function to get weather data
@st.cache_data
def get_weather_data(lat, lon, start_time, end_time):
    params = {
        "apikey": api_key,
        "location": f"{lat},{lon}",
        "fields": ["temperature", "precipitationType", "windSpeed"],
        "units": "metric",
        "timesteps": "1h",
        "startTime": start_time,
        "endTime": end_time
    }
    response = requests.get(api_url, params=params)
    return response.json()

# Convert location to coordinates (using geocoding API)
def get_coordinates(city, state, country):
    geocoding_api_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&limit=1&appid={api_key}"
    response = requests.get(geocoding_api_url)
    data = response.json()
    if data:
        return data[0]['lat'], data[0]['lon']
    else:
        return None, None

# Main logic
if city and flight_date:
    # Get coordinates
    lat, lon = get_coordinates(city, state, country)
    if lat is not None and lon is not None:
        # Get weather data
        start_time = datetime.combine(flight_date, datetime.min.time()).isoformat()
        end_time = datetime.combine(flight_date, datetime.max.time()).isoformat()
        weather_data = get_weather_data(lat, lon, start_time, end_time)
        
        # Check for severe weather conditions
        delay_likelihood = "Low"
        for interval in weather_data['data']['timelines'][0]['intervals']:
            if interval['values']['precipitationType'] == 1:  # 1 indicates thunderstorms
                delay_likelihood = "High"
                break
            if interval['values']['windSpeed'] > 25:  # Example threshold for severe winds
                delay_likelihood = "High"
                break
        
        # Display results
        st.write(f"Flight Date: {flight_date}")
        st.write(f"Location: {city}, {state}, {country}")
        st.write(f"Likelihood of Delay: {delay_likelihood}")
        
        # Show weather details
        for interval in weather_data['data']['timelines'][0]['intervals']:
            st.write(f"Time: {interval['startTime']}, Temperature: {interval['values']['temperature']}°C, Wind Speed: {interval['values']['windSpeed']} m/s")
    else:
        st.warning("Could not find the location. Please check your inputs.")
else:
    st.info("Please enter your flight information.")
