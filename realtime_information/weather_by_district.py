import requests
import json
import pandas as pd
from datetime import datetime

# OpenWeatherMap API 설정
apikey = "ebe454df1dca0593cd4588522db29cbc"
lang = "kr"

def load_data():
    """
    데이터 파일을 로드하고 데이터프레임으로 반환
    """
    return pd.read_excel('./data/음식점_세부정보_24-08-31.xlsx')  # 엑셀 파일로 가정

def find_location_center(data, search_term):
    """
    데이터에서 검색어를 기반으로 위도와 경도의 중앙값을 계산
    """
    filtered_data = data[data['검색어'] == search_term]  # '검색어' 열에서 검색어와 일치하는 데이터를 필터링
    if filtered_data.empty:
        return 37.552987017, 126.972591728

    # 위도와 경도 열이 '위도', '경도'라고 가정
    lat_center = round(filtered_data['latitude'].median(), 2)
    lon_center = round(filtered_data['longitude'].median(), 2)

    return lat_center, lon_center

def fetch_weather(lat, lon):
    """
    OpenWeatherMap API에서 데이터를 가져오고 반환
    """
    api = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&lang={lang}&units=metric"

    try:
        result = requests.get(api)
        result.raise_for_status()  # 요청이 실패했는지 확인
        return json.loads(result.text)
    except requests.exceptions.RequestException as e:
        print(f"요청 중 오류 발생: {e}")
        return None

def format_weather(data):
    """
    날씨 데이터를 정리하여 반환
    """
    weather_desc = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    icon_code = data["weather"][0]["icon"]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "weather_desc": weather_desc,
        "temperature": temperature,
        "feels_like": feels_like,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "icon_code": icon_code,
        "current_time": current_time
    }

def display_weather(st, weather_data, search_term):
    """
    Streamlit을 사용하여 날씨 정보를 출력
    """
    if weather_data:
        formatted_weather = format_weather(weather_data)
        weather_desc = formatted_weather["weather_desc"]
        temperature = formatted_weather["temperature"]
        feels_like = formatted_weather["feels_like"]
        humidity = formatted_weather["humidity"]
        wind_speed = formatted_weather["wind_speed"]
        icon_code = formatted_weather["icon_code"]
        current_time = formatted_weather["current_time"]

        # 날씨 정보 출력
        default = '서울시'
        if search_term == '전체 보기':
            st.write(f"**{default}**의 날씨 정보 - {current_time}")
        else:
            st.write(f"**{search_term}**의 날씨 정보 - {current_time}")

        st.write(f"**날씨**: {weather_desc}")
        st.write(f"**온도**: {temperature}°C (체감 온도: {feels_like}°C)")
        st.write(f"**습도**: {humidity}%")
        st.write(f"**풍속**: {wind_speed} m/s")

        # 날씨 아이콘 출력
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        st.image(icon_url)

def get_weather_by_search_term(st, search_term):
    """
    검색어를 기반으로 파일에서 위치 정보 조회, 날씨 표시
    """
    # 데이터 로드
    data = load_data()

    # 검색어에 해당하는 위치의 중앙값 계산
    lat, lon = find_location_center(data, search_term)

    if lat is not None and lon is not None:
        # 날씨 데이터 가져오기
        weather_data = fetch_weather(lat, lon)

        # 날씨 데이터 표시
        display_weather(st, weather_data, search_term)
    else:
        st.write("검색어에 해당하는 위치 정보를 찾을 수 없습니다.")