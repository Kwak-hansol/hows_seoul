import streamlit as st
import requests
import cx_Oracle
import xml.etree.ElementTree as ET
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, timedelta
from streamlit_folium import st_folium
from geopy.distance import great_circle
from shapely.geometry import Point, box
from folium.plugins import FastMarkerCluster

# Ensure you have a valid API key
api_key = ''
@st.cache_data
def get_request_url(stdate, eddate, prfstate, kidstate):
    """
    Api키를 이용
    """
    params = {
        'service': api_key,
        'cpage': 1,
        'rows': 300,
        'stdate': stdate,
        'eddate': eddate,
        'shcate': 'GGGA',
        'kidstate': kidstate,
        'prfstate': prfstate
    }
    api_url = 'http://kopis.or.kr/openApi/restful/pblprfr'
    response = requests.get(api_url, params=params)
    return response.content

def calculate_distance(coord1, coord2):
    return great_circle(coord1, coord2).kilometers
@st.cache_data
def get_coordinates_and_facilities(venue_name):
    try:
        connection = cx_Oracle.connect('open_source/1111@192.168.0.18:1521/xe')
        cursor = connection.cursor()

        query = """
        SELECT la, lo, restaurant, cafe, store, nolibang, suyu,
               parkbarrier, restbarrier, runwbarrier, elevbarrier, parkinglot
        FROM locate
        WHERE fcltynm = :venue_name
        """
        cursor.execute(query, {'venue_name': venue_name})
        result = cursor.fetchone()
        return result
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        return None
    finally:
        if 'connection' in locals():
            connection.close()

def is_within_bounds(lat, lon, bounds):
    """Check if a coordinate is within the bounds."""
    point = Point(lon, lat)
    bounding_box = box(bounds[0][1], bounds[0][0], bounds[1][1], bounds[1][0])
    return bounding_box.contains(point)

# Date calculation
today = datetime.now()
next_month = today + timedelta(days=30)
last_month = today - timedelta(days=365)

stdate = last_month.strftime('%Y%m%d')
eddate = next_month.strftime('%Y%m%d')

# Initialize session state variables if not already set
if 'prfstate' not in st.session_state:
    st.session_state.prfstate = '02'  # Default: 공연중
if 'kidstate' not in st.session_state:
    st.session_state.kidstate = 'N'  # Default: 전부

# Streamlit app setup
st.title('뮤지컬 공연 정보 지도')

prfstate_options = {'공연중': '02', '공연예정': '01','공연완료': '03'}
selected_state = st.selectbox('공연 상태 선택', options=list(prfstate_options.keys()), index=list(prfstate_options.values()).index(st.session_state.prfstate))
prfstate = prfstate_options[selected_state]

kidstate_options = {'아동 공연': 'Y', '전부': 'N'}
selected_kidstate = st.selectbox('아동 공연 여부 선택', options=list(kidstate_options.keys()), index=list(kidstate_options.values()).index(st.session_state.kidstate))
kidstate = kidstate_options[selected_kidstate]

# Sidebar for error messages
error_messages = st.sidebar

# API request and XML parsing
def performance_request():
    response = get_request_url(stdate, eddate, prfstate, kidstate)
    root = ET.fromstring(response)

    performances = []
    missing_coordinates = []

    for item in root.findall(".//db"):
        facility_name = item.find('fcltynm').text if item.find('fcltynm') is not None else ""
        performance_name = item.find('prfnm').text if item.find('prfnm') is not None else ""
        prfcast = item.find('prfcast').text if item.find('prfcast') is not None else ""
        prfpdfrom = item.find('prfpdfrom').text if item.find('prfpdfrom') is not None else ""
        prfpdto = item.find('prfpdto').text if item.find('prfpdto') is not None else ""
        performances.append({
            'fcltynm': facility_name,
            'prfnm': performance_name,
            'prfcast': prfcast,
            'prfpdfrom': prfpdfrom,
            'prfpdto': prfpdto
        })
    return performances, missing_coordinates

# Create a two-column layout
col1, col2 = st.columns([2, 1])  # Adjust width ratio

# Base map creation in the first column
with col1:
    performances, missing_coordinates = performance_request()
    map = folium.Map(location=[36.5, 127.5], zoom_start=7)

    # Initialize the MarkerCluster
    marker_cluster = MarkerCluster().add_to(map)

    # Retrieve coordinates and add markers to the map
    bounds = []  # List to store coordinates within bounds

    for performance in performances:
        venue_name = performance['fcltynm']
        performance_name = performance['prfnm']
        coordinates_and_facilities = get_coordinates_and_facilities(venue_name)

        if coordinates_and_facilities:
            lat, lon = coordinates_and_facilities[0], coordinates_and_facilities[1]

            # Check if coordinates are valid
            if lat and lon:
                bounds.append([lat, lon])  # Add to bounds list

                # Add marker to the cluster
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<b>{performance_name}",
                    tooltip=performance_name,
                    icon=folium.Icon(color='blue', icon='bookmark')
                ).add_to(marker_cluster)
            else:
                missing_coordinates.append(venue_name)
        else:
            missing_coordinates.append(venue_name)

    # Display the map
    map_display = st_folium(map, height=600, width=800)

# Right column to display selected marker information
with col2:
    st.subheader("공연 상세 정보")

    # Display information about the clicked marker
    if map_display and map_display.get('last_clicked'):
        click_lat = map_display['last_clicked']['lat']
        click_lon = map_display['last_clicked']['lng']
        clicked_coord = (click_lat, click_lon)

        nearest_performance = None
        min_distance = float('inf')

        for performance in performances:
            venue_name = performance['fcltynm']
            coordinates_and_facilities = get_coordinates_and_facilities(venue_name)

            if coordinates_and_facilities:
                marker_lat = coordinates_and_facilities[0]
                marker_lon = coordinates_and_facilities[1]
                performance_coord = (marker_lat, marker_lon)

                distance = calculate_distance(clicked_coord, performance_coord)
                if distance < min_distance:
                    min_distance = distance
                    nearest_performance = performance
                    nearest_facilities = coordinates_and_facilities

        if nearest_performance:
            linked_name = nearest_performance['prfnm']
            linked_link = "/pages/nearest_performance['prfnm']"
            print(nearest_performance['prfcast'])
            st.write(f"**공연 이름**: [{linked_name}]({linked_link})")
            st.write(f"**공연장**: {nearest_performance['fcltynm']}")
            st.write(f"**출연진**: {nearest_performance['prfcast']}")
            st.write(f"**시작일**: {nearest_performance['prfpdfrom']}")
            st.write(f"**종료일**: {nearest_performance['prfpdto']}")
            # .replace('[', '&#91;').replace(']', '&#93;').replace('(', '&#40;').replace(')', '&#41;')
            facilities = {
                '레스토랑': 'O' if nearest_facilities[2] == 'Y' else 'X',
                '카페': 'O' if nearest_facilities[3] == 'Y' else 'X',
                '편의점': 'O' if nearest_facilities[4] == 'Y' else 'X',
                '놀이방': 'O' if nearest_facilities[5] == 'Y' else 'X',
                '수유실': 'O' if nearest_facilities[6] == 'Y' else 'X',
                '장애시설-주차장': 'O' if nearest_facilities[7] == 'Y' else 'X',
                '장애시설-화장실': 'O' if nearest_facilities[8] == 'Y' else 'X',
                '장애시설-경사로': 'O' if nearest_facilities[9] == 'Y' else 'X',
                '장애시설-엘리베이터': 'O' if nearest_facilities[10] == 'Y' else 'X',
                '주차시설': 'O' if nearest_facilities[11] == 'Y' else 'X'
            }

            st.write("**시설 정보**:")
            for facility, available in facilities.items():
                if available == 'O':
                    st.write(f"{facility}: 사용 가능")
        else:
            st.write("주어진 좌표와 가까운 공연 정보를 찾을 수 없습니다.")
    else:
        st.info("지도를 클릭하여 공연 정보를 확인하세요.")

# Display missing coordinates in the sidebar
if missing_coordinates:
    error_messages.warning("아래의 장소가 표시되지 않습니다.")
    for venue in missing_coordinates:
        error_messages.write(f'{venue}')
