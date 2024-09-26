import cx_Oracle
import pandas as pd
import folium
from folium import IFrame
from streamlit_folium import st_folium
import streamlit as st

# Define a color map for subway lines
LINE_COLORS = {
    '1호선': 'blue',
    '2호선': 'green',
    '3호선': 'orange',
    '4호선': 'red',
    '5호선': 'purple',
    '6호선': 'brown',
    '7호선': 'lightblue',
    '8호선': 'lightgreen',
    '9호선': 'darkblue',
    '경의중앙선': 'pink',
    '공항철도': 'gray',
    '분당선': 'cyan',
    '신분당선': 'magenta'
}

def create_map(df, show_markers=True, center_coords=None):
    """
    데이터프레임으로 Folium 지도 생성
    """
    if center_coords is None:
        center_coords = [37.552987017, 126.972591728]  # 기본 중심 좌표 (서울역)
    m = folium.Map(location=center_coords, zoom_start=15)

    if show_markers and not df.empty:
        for _, row in df.iterrows():
            station_name = row['STATN_NM']
            station_line = row['호선'].lstrip('0')  # Remove leading '0' from station_line
            lat = row['열3']
            lon = row['열4']
            color = LINE_COLORS.get(station_line, 'black')  # 기본 색상은 검정색

            html = f"""
            <style>
                .popup-content {{
                    font-family: 'Arial', sans-serif;
                    color: #333;
                    max-width: 350px;
                    line-height: 1.6;
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                    padding: 15px;
                    margin: 0;
                }}
                .popup-content h2 {{
                    font-size: 22px;
                    color: {color};
                    margin-bottom: 15px;
                    border-bottom: 3px solid {color};
                    padding-bottom: 10px;
                }}
                .popup-content p {{
                    margin: 10px 0;
                    padding: 0;
                }}
                .popup-content p strong {{
                    color: #555;
                    font-weight: 600;
                }}
                .popup-content a {{
                    color: {color};
                    text-decoration: none;
                    font-weight: 600;
                    display: block;
                    margin-top: 5px;
                }}
                .popup-content a:hover {{
                    text-decoration: underline;
                }}
                .popup-content .address {{
                    font-style: italic;
                    color: #666;
                }}
            </style>
            <div class="popup-content">
                <h2>{station_name}역</h2>
            </div>
            """

            iframe = IFrame(html, width=300, height=130)
            popup = folium.Popup(iframe)

            folium.Marker(
                [lat, lon],
                popup=popup,
                tooltip=station_name,
                icon=folium.Icon(color=color)
            ).add_to(m)

    return m

def select_from_oracle():
    try:
        conn = cx_Oracle.connect('open_source/1111@192.168.0.22:1521/xe')
        cur = conn.cursor()

        sql_select = f'''
        SELECT *
        FROM subwaystation_info
        WHERE STATN_NM in
        (SELECT STATN_NM FROM SUBWAY_LIST)
        AND
        역지역 = '수도권'
        '''

        cur.execute(sql_select)

        rows = cur.fetchall()
        col_names = [row[0] for row in cur.description]

        df = pd.DataFrame(rows, columns=col_names)

        cur.close()
        conn.close()

        return df
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None

def show_map_trans(selected_line):
    """
    검색어와 선택된 카테고리에 따라 필터링된 데이터를 Streamlit으로 표시
    """

    subway_station_df = select_from_oracle()

    if selected_line != '모든 노선':
        subway_station_df = subway_station_df[subway_station_df['호선'].str.lstrip('0') == selected_line]

    map_ = st_folium(create_map(subway_station_df), height=700, width=1600)

    return map_

def station_info(map):
    """
    각 카테고리 파일 경로 및 이름 설정
    """

    subway_station_df = select_from_oracle()

    if map and map.get('last_object_clicked_tooltip'):
        return map["last_object_clicked_tooltip"]