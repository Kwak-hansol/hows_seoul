import pandas as pd
import streamlit as st

def load_excel(file):
    """
    엑셀 파일을 데이터프레임으로 반환
    """
    return pd.read_excel(file)


def generate_marker_code(df):
    """
    데이터프레임의 각 행에 대해 마커 추가를 위한 JavaScript 코드 생성
    """
    marker_code = ""

    # 열 이름 확인
    print("데이터프레임 열 이름:", df.columns)

    for _, row in df.iterrows():
        lat = row.get('latitude', None)
        lon = row.get('longitude', None)
        title = row.get('title', '').replace("'", "\\'")  # 문자열에서 작은따옴표 처리
        link = row.get('link', '').replace("'", "\\'")  # 문자열에서 작은따옴표 처리
        category = row.get('category', '').replace("'", "\\'")  # 문자열에서 작은따옴표 처리
        address = row.get('address', '').replace("'", "\\'")  # 문자열에서 작은따옴표 처리
        roadAddress = row.get('roadAddress', '').replace("'", "\\'")  # 문자열에서 작은따옴표 처리

        if lat and lon:
            marker_code += f"""
            var marker = new naver.maps.Marker({{
                position: new naver.maps.LatLng({lat}, {lon}),
                map: map
            }});

            var infowindow = new naver.maps.InfoWindow({{
                content: '<div style="width:250px; padding:10px;"><h4>{title}</h4><p><strong>지번주소:</strong> {address}</p><p><strong>도로명주소:</strong> {roadAddress}</p><p><strong>홈페이지:</strong> <a href="{link}" target="_blank">{link}</a></p><p><strong>카테고리:</strong> {category}</p></div>',
                maxWidth: 300
            }});

            naver.maps.Event.addListener(marker, 'click', function() {{
                infowindow.open(map, marker);
            }});
            """

    return marker_code


def generate_map_html(df, api_key):
    """
    데이터프레임을 사용하여 네이버 지도의 HTML 코드 생성
    """

    # 기본 HTML 템플릿
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId={api_key}"></script>
        <style>
            #map {{
                width: 100%;
                height: 600px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            function initMap() {{
                var map = new naver.maps.Map('map', {{
                    center: new naver.maps.LatLng(37.552987017, 126.972591728),
                    zoom: 14
                }});

                // 마커 추가
                {generate_marker_code(df)}
            }}

            initMap();
        </script>
    </body>
    </html>
    """

    return html_template


def show_map(uploaded_file, api_key):
    """
    파일 경로를 받아 지도를 생성하고 Streamlit으로 표시
    """
    # 엑셀 파일에서 데이터프레임을 불러옵니다.
    df = load_excel(uploaded_file)

    # 데이터프레임의 열 이름을 확인합니다.
    print("데이터프레임 열 이름:", df.columns)

    # 지도 HTML 코드 생성
    map_html = generate_map_html(df, api_key)

    # Streamlit을 사용하여 지도 표시
    st.components.v1.html(map_html, height=600)
