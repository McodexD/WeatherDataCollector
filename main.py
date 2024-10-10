import requests
import datetime
import pandas as pd

# SMHI URL
smhi_url = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.02151508449004/lat/59.30996552541549/data.json"

# OpenWeatherMap API key and URL template
api_key = "7db4f19cdc84c813872be152f1a500c6"  # Update with your actual OpenWeatherMap API key
owm_url_template = "https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_key}&units=metric"

def fetch_smhi_data():
    response = requests.get(smhi_url)
    print(f"SMHI Response Status Code: {response.status_code}")  # Debugging line
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from SMHI: {response.text}")  # Debugging line
        return None

def fetch_owm_data(lat, lon, api_key):
    owm_url = owm_url_template.format(lat=lat, lon=lon, part="current,minutely,hourly,daily", API_key=api_key)
    response = requests.get(owm_url)
    print(f"OpenWeatherMap Response Status Code: {response.status_code}")  # Debugging line
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data from OpenWeatherMap: {response.text}")  # Debugging line
        return None

def process_and_save_smhi_data(data):
    # Implement processing for SMHI data
    forecasts = []
    created_at = datetime.datetime.now()

    for forecast in data['timeSeries']:
        date = forecast['validTime']['start'].split('T')[0]  # Adjust based on the actual structure
        hour = int(forecast['validTime']['start'].split('T')[1][:2])
        temperature = forecast['parameters'][0]['values'][0]  # Update according to the actual structure
        rain_or_snow = 'precipitation' in forecast['parameters'][0] and forecast['parameters'][0]['values'][0] > 0

        forecasts.append({
            'Created': created_at,
            'Longitude': 18.02151508449004,
            'Latitude': 59.30996552541549,
            'Datum': date,
            'Hour': hour,
            'Temperature': temperature,
            'RainOrSnow': rain_or_snow,
            'Provider': 'SMHI'
        })

    df = pd.DataFrame(forecasts)
    check_and_save_new_data(df)

def process_and_save_owm_data(data):
    forecasts = []
    created_at = datetime.datetime.now()

    # Adjust the processing based on the structure of the OpenWeatherMap data
    for daily_forecast in data['daily']:
        date = datetime.datetime.fromtimestamp(daily_forecast['dt']).date()  # Get date from timestamp
        temperature = daily_forecast['temp']['day']  # Daily temperature
        rain_or_snow = daily_forecast.get('rain', 0) > 0  # Check for rain

        forecasts.append({
            'Created': created_at,
            'Longitude': 18.02151508449004,
            'Latitude': 59.30996552541549,
            'Datum': date,
            'Temperature': temperature,
            'RainOrSnow': rain_or_snow,
            'Provider': 'OpenWeatherMap'
        })

    df = pd.DataFrame(forecasts)
    check_and_save_new_data(df)

def check_and_save_new_data(df):
    try:
        existing_df = pd.read_excel('weather_data.xlsx')
        df = pd.concat([existing_df, df]).drop_duplicates(subset=['Datum', 'Hour', 'Provider'])
        df.to_excel('weather_data.xlsx', index=False)
    except FileNotFoundError:
        df.to_excel('weather_data.xlsx', index=False)

def display_weather_data():
    try:
        df = pd.read_excel('weather_data.xlsx')
        print(df)  # Adjust this line based on how you want to display the data
    except FileNotFoundError:
        print("Inga väderdata tillgängliga.")

def main_menu(api_key):
    while True:
        print("1. Hämta data (SMHI eller OpenWeatherMap eller båda)")
        print("2. Skriv ut senaste prognosen (SMHI eller OpenWeatherMap)")
        print("9. Avsluta")
        choice = input("Välj ett alternativ: ")

        if choice == '1':
            service_choice = input("Välj tjänst: 1 för SMHI, 2 för OpenWeatherMap, 3 för båda: ")
            if service_choice == '1':
                data = fetch_smhi_data()
                if data:
                    process_and_save_smhi_data(data)
            elif service_choice == '2':
                data = fetch_owm_data(59.30996552541549, 18.02151508449004, api_key)
                if data:
                    process_and_save_owm_data(data)
            elif service_choice == '3':
                data_smhi = fetch_smhi_data()
                if data_smhi:
                    process_and_save_smhi_data(data_smhi)
                data_owm = fetch_owm_data(59.30996552541549, 18.02151508449004, api_key)
                if data_owm:
                    process_and_save_owm_data(data_owm)
            else:
                print("Ogiltigt val.")
        elif choice == '2':
            service_choice = input("Välj tjänst: 1 för SMHI, 2 för OpenWeatherMap: ")
            if service_choice == '1':
                display_weather_data()  # You might want to specify which data to display
            elif service_choice == '2':
                display_weather_data()  # Same here
        elif choice == '9':
            break
        else:
            print("Ogiltigt val, försök igen.")

if __name__ == "__main__":
    main_menu(api_key)
