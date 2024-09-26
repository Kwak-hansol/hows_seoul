# weather.py

import requests
import json
from datetime import datetime

# OpenWeatherMap API 설정
city = 'Seoul'
apikey = "b6213d9acdb71be9771d6f0f03207148"
lang = "kr"
api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"

def fetch_weather():
    """
    OpenWeatherMap API에서 데이터 반환
    """
    try:
        result = requests.get(api)
        result.raise_for_status()  # 요청이 실패했는지 확인
        return json.loads(result.text)
    except requests.exceptions.RequestException as e:
        print(f"요청 중 오류 발생: {e}")
        return None

def format_weather(data):
    """
    데이터를 정리하여 반환
    """
    city_name = data.get("name")
    weather_desc = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    icon_code = data["weather"][0]["icon"]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "city_name": city_name,
        "weather_desc": weather_desc,
        "temperature": temperature,
        "feels_like": feels_like,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "icon_code": icon_code,
        "current_time": current_time
    }

def display_weather(st, weather_data):
    """
    Streamlit을 사용하여 날씨 정보를 출력
    """
    if weather_data:
        formatted_weather = format_weather(weather_data)
        city_name = formatted_weather["city_name"]
        weather_desc = formatted_weather["weather_desc"]
        temperature = formatted_weather["temperature"]
        feels_like = formatted_weather["feels_like"]
        humidity = formatted_weather["humidity"]
        wind_speed = formatted_weather["wind_speed"]
        icon_code = formatted_weather["icon_code"]
        current_time = formatted_weather["current_time"]

        # 날씨 정보 출력
        st.write(f"**{'서울시'}**의 날씨 정보 - {current_time}")
        st.write(f"**날씨**: {weather_desc}")
        st.write(f"**온도**: {temperature}°C (체감 온도: {feels_like}°C)")
        st.write(f"**습도**: {humidity}%")
        st.write(f"**풍속**: {wind_speed} m/s")

        # 날씨 아이콘 출력
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        st.image(icon_url)