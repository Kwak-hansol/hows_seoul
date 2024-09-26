# map_folium_test.py
import pandas as pd
import folium
from folium import IFrame
import streamlit as st


def load_excel(file_path):
    """
    엑셀 파일을 데이터프레임으로 반환
    """
    return pd.read_excel(file_path)


def create_map(df):
    """
    데이터프레임을 사용해 Folium 지도 생성
    """
    # 초기 지도 설정
    m = folium.Map(location=[37.552987017, 126.972591728], zoom_start=14)

    # 데이터프레임의 각 행에 대해 마커를 추가합니다.
    for _, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        title = row['title']
        link = row['link']
        category = row['category']
        address = row['address']
        roadAddress = row['roadAddress']

        # HTML로 마커 팝업을 구성합니다.
        html = f"""
        <h4>{title}</h4>
        <p><strong>지번주소:</strong> {address}</p>
        <p><strong>도로명주소:</strong> {roadAddress}</p>
        <p><strong>홈페이지:</strong> {link}</p>
        <p><strong>카테고리:</strong> {category}</p>
        """
        iframe = IFrame(html, width=250, height=150)
        popup = folium.Popup(iframe, max_width=300)

        # 마커를 추가합니다.
        folium.Marker([lat, lon], popup=popup).add_to(m)

    return m


def show_map(file_path):
    """
    파일 경로를 받아 지도를 Streamlit으로 표시
    """
    # 엑셀 파일에서 데이터프레임을 불러옵니다.
    df = load_excel(file_path)

    # 지도 생성
    map_ = create_map(df)

    # Streamlit을 사용하여 지도 표시
    st.components.v1.html(map_._repr_html_(), height=600)