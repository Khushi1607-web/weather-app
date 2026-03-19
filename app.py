import streamlit as st
import requests
import pandas as pd

# API KEY from secrets
API_KEY = st.secrets["API_KEY"]

st.set_page_config(page_title="🌍 Weather App", layout="wide")

st.title("🌍 Cloud Weather Monitoring System")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    country = st.text_input("Enter Country", "India")

with col2:
    city = st.text_input("Enter City", "Bangalore")

# ---------------- FETCH WEATHER ----------------
if city and country:
    location = f"{city},{country}"

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data["cod"] == "200":

        st.success(f"📍 Weather for {city}, {country}")

        current = data["list"][0]

        # ---------------- CURRENT WEATHER ----------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🌡️ Temp", f"{current['main']['temp']}°C")
        col2.metric("🤒 Feels Like", f"{current['main']['feels_like']}°C")
        col3.metric("💧 Humidity", f"{current['main']['humidity']}%")
        col4.metric("🌬️ Wind", f"{current['wind']['speed']} m/s")

        st.divider()

        # ---------------- FORECAST TABLE ----------------
        forecast_data = []
        temps = []
        dates = []

        for i in range(0, 40, 8):
            day = data["list"][i]

            forecast_data.append({
                "Date": day["dt_txt"],
                "Temp (°C)": day["main"]["temp"],
                "Humidity (%)": day["main"]["humidity"],
                "Weather": day["weather"][0]["description"],
                "Rain (%)": day.get("pop", 0) * 100
            })

            temps.append(day["main"]["temp"])
            dates.append(day["dt_txt"])

        df_forecast = pd.DataFrame(forecast_data)

        st.subheader("📅 5-Day Weather Report")
        st.dataframe(df_forecast)

        # ---------------- GRAPH ----------------
        df_graph = pd.DataFrame({
            "Date": dates,
            "Temperature": temps
        }).set_index("Date")

        st.subheader("📊 Temperature Trend")
        st.line_chart(df_graph)

        # ---------------- MIN MAX ----------------
        st.write(f"🔺 Max Temp: {max(temps)}°C")
        st.write(f"🔻 Min Temp: {min(temps)}°C")

        st.divider()

        # ---------------- MAP ----------------
        st.subheader("🗺️ Location Map")

        lat = data["city"]["coord"]["lat"]
        lon = data["city"]["coord"]["lon"]

        map_data = pd.DataFrame({
            "lat": [lat],
            "lon": [lon]
        })

        st.map(map_data)

        st.divider()

        # ---------------- AQI ----------------
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_response = requests.get(aqi_url)
        aqi_data = aqi_response.json()

        aqi_value = aqi_data["list"][0]["main"]["aqi"]

        aqi_status = {
            1: "Good 😊",
            2: "Fair 🙂",
            3: "Moderate 😐",
            4: "Poor 😷",
            5: "Very Poor ☠️"
        }

        st.subheader("🌫️ Air Quality Index (AQI)")
        st.metric("AQI Level", aqi_value)
        st.write(f"Status: {aqi_status.get(aqi_value)}")

        # AQI ALERT
        if aqi_value >= 4:
            st.error("⚠️ Air quality is poor! Wear a mask 😷")
        elif aqi_value == 3:
            st.warning("😐 Moderate air quality")
        else:
            st.success("😊 Air quality is good")

    else:
        st.error("❌ Location not found! Try again.")
