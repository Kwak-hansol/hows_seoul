import cx_Oracle
import pandas as pd
import folium
from folium import IFrame
import streamlit as st
from streamlit_folium import st_folium


# 지도 생성 함수
def create_map(df, show_markers=True, center_coords=None):
    """
    데이터프레임으로 Folium 지도 생성
    """
    # 중심 좌표 및 줌 레벨 설정
    if center_coords is None:
        center_coords = [37.552987017, 126.972591728]  # 기본 중심 좌표 (서울역)
    m = folium.Map(location=center_coords, zoom_start=16)

    # 카테고리별 마커 색상 및 아이콘 설정
    category_icons = {
        '음식점': {'color': 'red', 'icon': 'cutlery'},  # 음식점은 빨간색, 포크 아이콘
        '숙박시설': {'color': 'blue', 'icon': 'bed'},  # 숙박시설은 파란색, 침대 아이콘
        '카페': {'color': 'green', 'icon': 'coffee'}  # 카페는 초록색, 커피 아이콘
    }

    if show_markers and not df.empty:
        # 데이터프레임의 각 행에 대해 마커를 추가
        for _, row in df.iterrows():
            lat = row['LATITUDE']
            lon = row['LONGITUDE']
            title = row['TITLE']
            link = row['LINK']
            category = row['CATEGORY']
            categories = row['CATEGORIES']
            address = row['ADDRESS']
            roadAddress = row['ROADADDRESS']

            # HTML로 마커 팝업을 구성
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
                    color: #007BFF;
                    margin-bottom: 15px;
                    border-bottom: 3px solid #007BFF;
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
                    color: #007BFF;
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
                <h2>{title}</h2>
                <p><strong>지번주소:</strong> <span class="address">{address}</span></p>
                <p><strong>도로명주소:</strong> <span class="address">{roadAddress}</span></p>
                <p><a href="{link}" target="_blank">{'홈페이지 열기'}</a></p>
                <p><strong>업종:</strong> {categories}</p>
            </div>
            """

            iframe = IFrame(html, width=300, height=250)
            popup = folium.Popup(iframe, max_width=400)

            # 카테고리에 맞는 아이콘 설정
            icon_props = category_icons.get(category, {'color': 'gray', 'icon': 'info-sign'})
            icon = folium.Icon(color=icon_props['color'], icon=icon_props['icon'], prefix='fa')

            # 마커를 지도에 추가
            folium.Marker([lat, lon], popup=popup, icon=icon, tooltip=title).add_to(m)

    return m


def select_from_oracle(category):
    """
    Oracle데이터베이스에서 데이터프레임 불러오기
    """
    try:
        # Oracle 데이터베이스에 연결
        conn = cx_Oracle.connect('open_source/1111@192.168.0.22:1521/xe')
        cur = conn.cursor()

        # SQL 쿼리 작성
        sql_select = f'''
        select *
        from {category}_info
        '''

        # SQL 쿼리 실행
        cur.execute(sql_select)

        # 모든 결과 가져오기
        rows = cur.fetchall()

        # 컬럼 이름 가져오기
        col_names = [row[0] for row in cur.description]

        # 데이터프레임으로 변환
        df = pd.DataFrame(rows, columns=col_names)

        # 커서 및 연결 닫기
        cur.close()
        conn.close()

        return df
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None


# 지도와 데이터를 Streamlit으로 보여주는 함수
def show_map(search_term, selected_categories):
    """
    검색어와 선택된 카테고리에 따라 필터링된 데이터를 사용 후 지도 생성 및 Streamlit으로 표시
    """

    # 각 카테고리 파일 로드
    restaurant_df = select_from_oracle('restaurant')
    hotel_df = select_from_oracle('hotel')
    cafe_df = select_from_oracle('cafe')

    # 데이터프레임 합치기
    dataframes = [df for df in [restaurant_df, hotel_df, cafe_df] if df is not None]
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        # Handle the case where all DataFrames are None or empty
        combined_df = pd.DataFrame()

    # 검색어 필터링
    if search_term != "전체 보기":
        # 특수 문자를 이스케이프하거나 정규 표현식 비활성화
        filtered_df = combined_df[combined_df['검색어'].str.contains(search_term, case=False, regex=False, na=False)]
    else:
        filtered_df = combined_df  # '전체 보기' 선택 시 전체 데이터를 보여줌

    # 카테고리 필터링
    if selected_categories:
        filtered_df = filtered_df[filtered_df['CATEGORY'].isin(selected_categories)]

    # 필터링 결과가 없을 때 경고 메시지
    if filtered_df.empty and selected_categories:
        st.warning(f"'{search_term}' 및 선택된 카테고리에 대한 결과를 찾을 수 없습니다.")
        return

    # 중심 좌표 계산
    if search_term != "전체 보기" and not filtered_df.empty:
        # 특정 지역의 위경도 좌표 중앙값 계산
        center_coords = [
            filtered_df['LATITUDE'].median(),
            filtered_df['LONGITUDE'].median()
        ]
    else:
        center_coords = None  # 전체보기일 경우 서울역 좌표 사용

    # 카테고리 선택이 없는 경우 빈 지도 생성
    if not selected_categories:
        st.warning("카테고리를 선택해 주세요.")
        # 빈 지도 생성
        map_ = create_map(pd.DataFrame(), show_markers=False)
        st_folium(map_, height=700, width=1600)
        return

    # 지도 생성
    map_ = st_folium(create_map(filtered_df, center_coords=center_coords), height=700, width=1600, zoom=16)

    return map_


def marker_info(map, selected_categories):
    """
    카테고리의 데이터프레임 로드
    """
    # 각 카테고리 파일 경로 및 이름 설정

    restaurant_df = select_from_oracle('restaurant')
    hotel_df = select_from_oracle('hotel')
    cafe_df = select_from_oracle('cafe')

    # 데이터프레임 합치기
    dataframes = [df for df in [restaurant_df, hotel_df, cafe_df] if df is not None]
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        # Handle the case where all DataFrames are None or empty
        combined_df = pd.DataFrame()

    # 선택된 카테고리의 데이터프레임 동적 로드
    selected_dfs = []

    for category in selected_categories:
        if len(combined_df) > 0:
            selected_dfs.append(combined_df[combined_df['CATEGORY'] == category])

    if map and map.get('last_object_clicked_tooltip'):
        return map["last_object_clicked_tooltip"]