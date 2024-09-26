import streamlit as st
import requests

def get_youtube_results(search_term, max_results=12):
    """
    유튜브 API를 사용해 검색 결과 추출
    """
    API_KEY = "AIzaSyAOdYlNbzlMwKQoNCkekhcaRG0_j8Gc8tY"  # 본인의 API 키를 여기에 입력하세요.
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    params = {
        'part': 'snippet',
        'q': search_term,
        'type': 'video',
        'maxResults': max_results,  # 한 페이지에 표시할 동영상 수
        'key': API_KEY,
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        st.error("API 요청에 실패했습니다. API 키나 요청 파라미터를 확인하세요.")
        return []

    data = response.json()

    videos = []
    if 'items' in data:
        for item in data['items']:
            video = {
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video)

    return videos

def render_youtube_search(search_term, selected_categories, max_results=12):
    """
    유튜브 검색 결과를 Streamlit UI로 렌더링
    """
    if not search_term:
        return  # 검색어가 없을 때는 아무것도 표시하지 않음
    elif search_term == '전체 보기':
        search_term = '서울 여행'
    else:
        search_term = ' '.join([search_term] + selected_categories)

    results = get_youtube_results(search_term, max_results)

    if results:
        cols = st.columns(4)
        for index, video in enumerate(results):
            with cols[index % 4]:
                # 썸네일과 제목을 HTML로 감싸서 링크로 만듦
                st.markdown(f"""
                    <a href="{video['video_url']}" target="_blank">
                        <img src="{video['thumbnail']}" style="width:100%;"/>
                        <p><strong>{video['title']}</strong></p>
                    </a>
                """, unsafe_allow_html=True)
    else:
        st.write("검색 결과가 없습니다.")