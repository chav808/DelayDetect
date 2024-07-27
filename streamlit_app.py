import streamlit as st
import requests
import folium
from folium import IFrame
import matplotlib.pyplot as plt
import io
from streamlit_folium import st_folium

API_KEY = 'amk9ziucGrEtmkrDm0WGE7nGEB5Nosog'


AIRPORTS = {
    "Miami International Airport (MIA)": (25.7957, -80.2870),
    "LaGuardia Airport (LGA)": (40.7772, -73.8726),
    
}

# function to fetch weather data from Tomorrow.io
def get_weather_data(api_key, latitude, longitude, datetime_str):
    url = f"https://api.tomorrow.io/v4/timelines?location={latitude},{longitude}&fields=windSpeed&units=metric&timezone=America/New_York&startTime={datetime_str}&endTime={datetime_str}"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.json().get('message', 'No message available')}")
        return None

# function to create a folium map
def create_map(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup=f"Coordinates: ({latitude}, {longitude})").add_to(m)
    return m

# function to plot wind speed data
def plot_wind_speed(wind_speeds, times):
    fig, ax = plt.subplots()
    ax.plot(times, wind_speeds, label='Wind Speed (m/s)', color='blue')
    ax.set_xlabel('Time')
    ax.set_ylabel('Wind Speed (m/s)')
    ax.set_title('Wind Speed Over Time')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

# main function for Streamlit app
def main():
    st.title('Flight Delay Predictor Due to Weather')
    
    # display the logo at the top of the app
    logo = 'delayDetectorLogo.png'
    st.image(logo, use_column_width=True, caption='Welcome! Please fill the fields below!')
    
    radio_selection = st.radio("Select an option", ("Both departure and arrival", "Only departure", "Only arrival"))

    if radio_selection == "Only departure":
        departure_airport = st.selectbox('Select Departure Airport', list(AIRPORTS.keys()))
        arrival_airport = None
    elif radio_selection == "Only arrival":
        departure_airport = None
        arrival_airport = st.selectbox('Select Arrival Airport', list(AIRPORTS.keys()))
    else:
        departure_airport = st.selectbox('Select Departure Airport', list(AIRPORTS.keys()))
        arrival_airport = st.selectbox('Select Arrival Airport', list(AIRPORTS.keys()))
    
    flight_date = st.date_input('Select Flight Date')
    flight_time = st.time_input('Select Flight Time')

    if st.button('Check Delay'):
        if departure_airport or arrival_airport:
            if departure_airport:
                departure_coords = AIRPORTS[departure_airport]
                flight_datetime_str = f"{flight_date}T{flight_time}:00Z"
                departure_weather_data = get_weather_data(API_KEY, departure_coords[0], departure_coords[1], flight_datetime_str)
                
                if departure_weather_data:
                    # process and display weather data
                    departure_wind_speeds = [entry['values']['windSpeed'] for entry in departure_weather_data['data']['timelines'][0]['intervals']]
                    departure_times = [entry['startTime'] for entry in departure_weather_data['data']['timelines'][0]['intervals']]

                    # display maps
                    st.subheader(f'Departure Airport Map: {departure_airport}')
                    dep_map = create_map(departure_coords[0], departure_coords[1])
                    st_folium(dep_map, width=700, height=500)

                    # display wind speed plots
                    st.subheader(f'Wind Speed at {departure_airport}')
                    dep_fig = plot_wind_speed(departure_wind_speeds, departure_times)
                    st.pyplot(dep_fig)

                    # simple decision logic for delay prediction
                    wind_speed_threshold = 15  # example threshold for delay prediction
                    dep_max_wind = max(departure_wind_speeds)

                    if dep_max_wind > wind_speed_threshold:
                        st.warning("Flight may be delayed due to high wind speeds.")
                    else:
                        st.success("Flight is unlikely to be delayed due to wind speeds.")
            
            if arrival_airport:
                arrival_coords = AIRPORTS[arrival_airport]
                flight_datetime_str = f"{flight_date}T{flight_time}:00Z"
                arrival_weather_data = get_weather_data(API_KEY, arrival_coords[0], arrival_coords[1], flight_datetime_str)
                
                if arrival_weather_data:
                    # process and display weather data
                    arrival_wind_speeds = [entry['values']['windSpeed'] for entry in arrival_weather_data['data']['timelines'][0]['intervals']]
                    arrival_times = [entry['startTime'] for entry in arrival_weather_data['data']['timelines'][0]['intervals']]

                    # display maps
                    st.subheader(f'Arrival Airport Map: {arrival_airport}')
                    arr_map = create_map(arrival_coords[0], arrival_coords[1])
                    st_folium(arr_map, width=700, height=500)

                    # display wind speed plots
                    st.subheader(f'Wind Speed at {arrival_airport}')
                    arr_fig = plot_wind_speed(arrival_wind_speeds, arrival_times)
                    st.pyplot(arr_fig)

                    # simple decision logic for delay prediction
                    wind_speed_threshold = 15  # example threshold for delay prediction
                    arr_max_wind = max(arrival_wind_speeds)

                    if arr_max_wind > wind_speed_threshold:
                        st.warning("Flight may be delayed due to high wind speeds.")
                    else:
                        st.success("Flight is unlikely to be delayed due to wind speeds.")
        else:
            st.error("Please select at least one airport.")

    # Footer section
    st.markdown("---")
    st.subheader("Report Site Errors/Downtime Here")
    report_message = st.text_input("Enter your message")
    confirm_report = st.checkbox("I confirm my report")
    
    if confirm_report:
        if st.button("Send"):
            st.success("Thank you for your report!")
            st.experimental_rerun()  # refresh the page to hide the button after sending the report

if __name__ == "__main__":
    main()
