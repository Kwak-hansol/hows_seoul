import urllib.request
import urllib.parse
import json
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

def search_blog_posts(query):
    """
    네이버 블로그 API
    """
    # 네이버 API 클라이언트 ID와 Secret
    client_id = "I7_6f3EI2WNWpgsf73H8"
    client_secret = "_L4qvnXWlk"

    """네이버 블로그 검색 API를 호출하여 검색 결과를 출력하는 함수"""

    # 검색어 및 요청 URL 설정
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}"

    # HTTP 요청 준비
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    # API 요청 및 응답 처리
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            return data

        else:
            print("Error Code:" + str(rescode))

    except Exception as e:
        print(f"Failed to retrieve data: {e}")


def display_blog_info(data):
    """
    블로그 정보 데이터를 이쁜 테이블 형태로 출력하는 함수
    """
    if data and 'items' in data:
        items = data['items']

        # 데이터프레임 생성
        df = pd.DataFrame(items, columns=['title', 'link', 'description', 'bloggername', 'bloggerlink', 'postdate'])

        # 데이터프레임의 각 컬럼에 대해 텍스트 잘림 처리 (선택 사항)
        pd.set_option('display.max_colwidth', None)

        return df
    else:
        print("No data available to display.")


def clean_html(text):
    """
    HTML 태그를 제거하는 함수
    """
    return BeautifulSoup(text, 'html.parser').text


def display_blog_table(df):
    """
    HTML로 변환하여 출력
    """
    # HTML 태그 제거 및 링크 추가
    df['제목'] = df['title'].apply(clean_html)
    df['제목'] = df.apply(lambda row: f"<a href='{row['link']}' target='_blank'>{clean_html(row['title'])}</a>",
                           axis=1)
    df['내용 요약'] = df['description'].apply(clean_html)
    df['작성일자'] = df['postdate']

    # 필요 없는 컬럼 제거
    df = df[['작성일자', '제목', '내용 요약']]

    # 스타일 정의
    st.markdown("""
        <style>
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        .custom-table th, .custom-table td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }
        .custom-table th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .custom-table tr:hover {
            background-color: #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

    # 데이터프레임을 HTML로 변환하여 출력
    st.markdown(df.to_html(escape=False, index=False, classes='custom-table'), unsafe_allow_html=True)