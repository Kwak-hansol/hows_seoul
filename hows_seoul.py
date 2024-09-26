import streamlit as st
import matplotlib.font_manager as fm
import numpy as np
import os

from realtime_information.seoul_population_charts import plot_age_distribution, plot_gender_distribution, plot_forecast, \
    plot_congestion_and_non_resident_population, plot_top5_by_age, plot_top5_by_gender, \
    plot_population_by_category, plot_population_congestion_heatmap
from realtime_information.seoul_population import collect_data, collect_all_data
from realtime_information.weather_by_district import get_weather_by_search_term
from map.map_by_input import show_map, marker_info
import recommendation.recommend_by_cosine_similarity as reccs
from word_cloud.wordcloud_generator import load_and_preprocess_data, generate_wordcloud
from realtime_information.weather import fetch_weather, display_weather
import recommendation.recommend_by_youtube as recyt
# from chatbot.chat_bot2 import handle_chatbot
from chatbot.chat_bot3 import chatbot_ui, initialize_session_state
from map.map_by_transfortation import show_map_trans, station_info, select_from_oracle
import realtime_information.subway as sw
import recommendation.naver_reviews as nrv

# 페이지 설정
st.set_page_config(
    page_title="서울어때?",
    layout="wide",
)

def unique(list):
    x = np.array(list)
    return np.unique(x)

@st.cache_data
def fontRegistered():
    font_dirs = [os.getcwd() + '/font']
    font_files = fm.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        fm.fontManager.addfont(font_file)
    fm._load_fontmanager(try_read_cache=False)

fontRegistered()
fontNames = [f.name for f in fm.fontManager.ttflist]

# 스타일 적용을 위한 CSS
st.markdown("""
    <style>
        .header, .footer {
            text-align: center; 
            padding: 10px; 
        }
        .header {
            background-color: #87CEFA; /* Sky Blue */
            color: white;
        }
        .footer {
            background-color: #D3D3D3; /* Light Gray */
            color: black;
            position: fixed; 
            bottom: 0; 
            width: 100%;
        }
        .col {
            background-color: #f9f9f9; 
            padding: 5px;
            margin: 5px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            height: 80%; /* Ensure columns fill the height */
        }
        .column-container {
            display: flex;
            justify-content: space-between;
        }
    </style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("<div class='header'><h2>서울어때?</h2></div>", unsafe_allow_html=True)
def page1():
    """
    메인페이지를 구성
    지도, 날씨, 워드클라우드, 위치, 추천리스트, 필터링, 기초적인 통계
    챗봇, 페이지와 관련된 사이드 바를 제공
    """
    selected_categories = []
    locations = [
        "전체 보기",
        # 발달상권
        "성수카페거리", "가로수길", "북촌한옥마을", "인사동·익선동", "광장(전통)시장", "압구정로데오거리",
        # 인구밀집지역
        "홍대입구역(2호선)", "이태원역", "강남역", "서울식물원·마곡나루역",
        # 관광특구
        "동대문 관광특구", "명동 관광특구", "잠실 관광특구", "종로·청계 관광특구",
        # 고궁 문화유산
        "경복궁", "광화문·덕수궁", "창덕궁·종묘", "보신각",
        # 공원
        "반포한강공원", "고척돔", "남산공원", "잠실종합운동장", "서울숲공원", "국립중앙박물관·용산가족공원", "서울대공원"
    ]

    with st.sidebar:
        search_term = st.selectbox("지역을 선택하세요:", options=locations)
        is_restaurant = st.checkbox("음식점", value=True)
        is_hotel = st.checkbox("숙박시설", value=True)
        is_cafe = st.checkbox("카페", value=True)

        # 선택된 체크박스 상태를 리스트로 수집
        selected_categories = []
        if is_restaurant:
            selected_categories.append("음식점")
        if is_hotel:
            selected_categories.append("숙박시설")
        if is_cafe:
            selected_categories.append("카페")

        if st.button("통합 교통 정보"):
            st.session_state.page = "page2"
        if st.button("종합 통계 정보"):
            st.session_state.page = "page3"

        # 사이드바 안에 챗봇 UI 생성
        st.sidebar.markdown(
            """
            <style>
            .chat-box {
                max-height: 600px;  /* 최대 높이 고정 */
                overflow-y: auto;   /* 넘치는 내용 스크롤 */
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                font-size: 16px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 챗봇
        # 사이드바 내의 플레이스홀더 생성
        chat_box = st.sidebar.empty()

        # 챗봇 함수 실행
        # handle_chatbot(chat_box)
        chatbot_ui()


    # 본문 레이아웃 (3x2)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("<div class='col'><h3>지도</h3>", unsafe_allow_html=True)

        # 검색어가 입력되었을 때 show_map 함수를 호출하여 지도 표시
        map = show_map(search_term, selected_categories)  # Excel 파일 경로와 검색어 전달
        name = marker_info(map, selected_categories)

        # 관련 네이버 블로그
        if name:
            st.markdown("<div class='col'><h3>관련 블로그</h3>", unsafe_allow_html=True)
            if search_term == '전체 보기':
                query = '서울' + name
            else:
                query = search_term + name
            df = nrv.display_blog_info(nrv.search_blog_posts(query))
            nrv.display_blog_table(df)

        # 추천 리스트
        st.markdown("<div class='col'><h3>추천 리스트</h3>", unsafe_allow_html=True)

        df = reccs.load_data()

        review_similarity, category_similarity = reccs.compute_similarity_matrices(df)

        if name in df['title'].values:
            recommendations = reccs.recommend_place(df, name, review_similarity, category_similarity)

            # 추천된 업체 중 입력된 업체 이름을 제외하도록 필터링
            recommendations = recommendations[recommendations['title'] != name]

            # 결과가 5개로 보장되도록 필터링
            if not recommendations.empty:
                reccs.recommended_place_link(recommendations)
            else:
                st.write('추천 결과가 없습니다.')
        else:
            st.write('추천할 업체를 찾을 수 없습니다.')

        # 관련 유튜브 영상
        st.markdown("<div class='col'><h3>관련 유튜브 영상 </h3>", unsafe_allow_html=True)
        recyt.render_youtube_search(search_term, selected_categories, max_results=4)

    with col2:
        st.markdown("<div class='col'><h3>현재 날씨</h3>", unsafe_allow_html=True)
        col2_1, col2_2 = st.columns([1, 1])
        with col2_1:
            # 날씨 데이터 가져오기
            weather_data = fetch_weather()
            display_weather(st, weather_data)
        with col2_2:
            # 해당 지역 날씨 데이터 가져오기
            get_weather_by_search_term(st, search_term)

        # 데이터 로드 및 전처리
        combined_reviews = load_and_preprocess_data()

        # 워드클라우드 생성 및 파일로 저장
        wordcloud_image_path = generate_wordcloud(combined_reviews, search_term, selected_categories)

        # 워드클라우드 이미지 파일로 표시
        with st.container():
            st.image(wordcloud_image_path, use_column_width=True)

    if search_term != '전체 보기':
        st.markdown(f"<div class='col'><h3><strong>{search_term}</strong> 실시간 통계 정보</h3>", unsafe_allow_html=True)
        df = collect_data(search_term)
        if 'AREA_CONGEST_MSG' in df:
            st.markdown(f"{df['AREA_CONGEST_MSG'].iloc[0]}")
        if search_term != '전체 보기':
            col4_1, col4_2, col4_3 = st.columns([1, 1, 1])
            with col4_1:
                fig_age = plot_age_distribution(df)
                st.pyplot(fig_age)
            with col4_2:
                fig_gender = plot_gender_distribution(df)
                st.pyplot(fig_gender)
            with col4_3:
                fig_fcst = plot_forecast(df)
                if fig_fcst:
                    st.pyplot(fig_fcst)

def page2():
    """
    교통과 관련된 정보를 제공
    지금은 지하철 정보만 제공중
    """
    with st.sidebar:
        subway_station_df = select_from_oracle()

        # Get unique subway lines for dropdown menu
        subway_lines = subway_station_df['호선'].str.lstrip('0').unique()
        subway_lines = sorted(subway_lines)  # Sort for better dropdown order
        subway_lines.insert(0, '모든 노선')  # Add an option to show all lines

        selected_line = st.selectbox('노선 선택', subway_lines)

        if st.button("메인 페이지"):
            st.session_state.page = "page1"
        if st.button("종합 통계 정보"):
            st.session_state.page = "page3"

    trans_col1, trans_col2 = st.columns([3, 1])
    with trans_col1:
        map_trans = show_map_trans(selected_line)
        station_name = station_info(map_trans)

    with trans_col2:
        subway_info_xml = sw.fetch_subway_data(station_name)
        subway_info = sw.parse_subway_data(subway_info_xml)
        if station_name:
            sw.dict_to_table(subway_info, f'지하철 {station_name}역 실시간 도착정보')

def page3():
    """
    유동인구와 관련된 세부정보 제공 페이지
    """
    with st.sidebar:
        if st.button("메인 페이지"):
            st.session_state.page = "page1"
        if st.button("통합 교통 정보"):
            st.session_state.page = "page2"

    st.markdown(f"<div class='col'><h3>서울 25개 지역 혼잡도 순위</h3>", unsafe_allow_html=True)
    df = collect_all_data()
    congestion_level = st.radio(
        "혼잡도를 선택하세요",
        ('여유', '보통', '약간 붐빔', '붐빔'),
        horizontal=True
    )

    stat_col1, stat_col2 = st.columns([1, 1])
    with stat_col1:
        fig_1 = plot_congestion_and_non_resident_population(df, congestion_level)

        if fig_1:  # fig가 None이 아닌 경우에만 출력
            st.pyplot(fig_1)

    with stat_col2:
        fig_3 = plot_top5_by_gender(df)
        if fig_3:
            st.pyplot(fig_3)

    fig_2 = plot_top5_by_age(df)

    if fig_2:
        st.pyplot(fig_2)

    stat_col3, stat_col4 = st.columns([1, 1])
    with stat_col3:
        fig_4 = plot_population_by_category(df)
        if fig_4:
            st.pyplot(fig_4)

    with stat_col4:
        fig_5 = plot_population_congestion_heatmap(df)
        if fig_5:
            st.pyplot(fig_5)



if 'page' not in st.session_state:
    st.session_state.page = "page1"

if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
elif st.session_state.page == "page3":
    page3()

# 푸터
st.markdown("<div class='footer'><h4>대경 ICT 산업협회</h4></div>", unsafe_allow_html=True)