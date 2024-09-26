import streamlit as st
from map_naver_test import show_map

# 네이버 지도 API Key 입력
api_key = st.sidebar.text_input("네이버 지도 API Key를 입력하세요:")

# 파일 업로드
uploaded_file = st.sidebar.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file and api_key:
    # 엑셀 파일과 API Key가 모두 제공되었을 때
    show_map(uploaded_file, api_key)
else:
    st.sidebar.write("엑셀 파일과 API Key를 제공해야 합니다.")
