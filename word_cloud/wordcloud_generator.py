import pandas as pd
import streamlit
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

@streamlit.cache_data
def load_and_preprocess_data():
    """
    워드 클라우드를 생성하기위한 기초작업
    """
    # 엑셀 파일 읽기
    instagram_reviews = pd.read_excel('./data/인스타그램크롤링_24-08-27.xlsx')
    naver_reviews1 = pd.read_excel('./data/음식점_네이버_리뷰_24-09-02_1.xlsx')
    naver_reviews2 = pd.read_excel('./data/숙박시설_네이버_리뷰_24-09-02.xlsx')
    naver_reviews3 = pd.read_excel('./data/카페_네이버_리뷰_24-09-02.xlsx')
    naver_blog_reviews = pd.read_excel('./data/네이버블로그크롤링_24-08-27.xlsx')

    # Instagram reviews 데이터프레임 전처리
    instagram_reviews = instagram_reviews[['검색어', '검색결과']].rename(columns={'검색어': '지역', '검색결과': '리뷰'})
    instagram_reviews['카테고리'] = '없음'
    instagram_reviews['상호명'] = '없음'
    instagram_reviews['태그'] = '없음'

    # Naver reviews 데이터프레임 전처리
    naver_reviews1 = naver_reviews1[['검색어', '검색결과', 'review']].rename(columns={'검색어': '지역', '검색결과': '상호명', 'review': '리뷰'})
    naver_reviews1['카테고리'] = '음식점'
    naver_reviews1['태그'] = '없음'

    naver_reviews2 = naver_reviews2[['검색어', '검색결과', 'review']].rename(columns={'검색어': '지역', '검색결과': '상호명', 'review': '리뷰'})
    naver_reviews2['카테고리'] = '숙박시설'
    naver_reviews2['태그'] = '없음'

    naver_reviews3 = naver_reviews3[['검색어', '검색결과', 'review']].rename(columns={'검색어': '지역', '검색결과': '상호명', 'review': '리뷰'})
    naver_reviews3['카테고리'] = '카페'
    naver_reviews3['태그'] = '없음'

    # Naver blog reviews 데이터프레임 전처리
    naver_blog_reviews = naver_blog_reviews[['검색어', '태그', '내용']].rename(columns={'검색어': '지역', '태그': '태그', '내용': '리뷰'})
    naver_blog_reviews['카테고리'] = '없음'
    naver_blog_reviews['상호명'] = '없음'

    # 데이터프레임 통합
    combined_reviews = pd.concat([
        instagram_reviews[['지역', '상호명', '리뷰', '카테고리', '태그']],
        naver_reviews1[['지역', '상호명', '리뷰', '카테고리', '태그']],
        naver_reviews2[['지역', '상호명', '리뷰', '카테고리', '태그']],
        naver_reviews3[['지역', '상호명', '리뷰', '카테고리', '태그']],
        naver_blog_reviews[['지역', '상호명', '리뷰', '카테고리', '태그']]
    ], ignore_index=True, sort=False)

    return combined_reviews

def get_nouns_from_texts(texts, stopwords_set):
    """
    불용어 제거
    """
    okt = Okt()
    nouns = []

    for text in texts:
        # 형태소 분석을 통해 명사만 추출
        nouns += okt.nouns(text)

    # 불용어 제거
    nouns = [noun for noun in nouns if noun not in stopwords_set]

    return nouns

cached_mask = None

@streamlit.cache_data
def get_image_mask(image_name='./img/seoul.PNG'):
    """
    워드 클라우드 생성
    """
    global cached_mask

    # mask가 이미 캐시되어 있다면 그대로 사용
    if cached_mask is not None:
        return cached_mask

    # mask가 캐시되지 않았다면 새로 생성
    target_image = Image.open(image_name)

    try:
        mask = Image.new("RGB", target_image.size, (255, 255, 255))
        mask.paste(target_image, target_image)
        mask = np.array(mask)
        print("mask 변환 방식1")
    except Exception as e:
        print(f"Error in mask creation: {e}")
        mask = np.array(Image.open(image_name))
        print("mask 변환 방식2")

    # 생성된 mask를 캐시에 저장
    cached_mask = mask

    # 시각화 (필요한 경우)
    plt.imshow(target_image)

    return cached_mask

@streamlit.cache_data
def generate_wordcloud(data, selected_region, selected_categories):
    """
    파일이 이미 존재하는 경우 파일 경로 반환
    """
    encoded_categories = encode_categories(selected_categories)
    wordcloud_image_path = f'./img/wordcloud_{selected_region}_{encoded_categories}.png'

    if os.path.exists(wordcloud_image_path):
        return wordcloud_image_path

    # 필터링
    if selected_region == '전체 보기' and (not selected_categories or '전체' in selected_categories):
        filtered_reviews = data.copy()
    else:
        filtered_reviews = data.copy()

        if selected_region != '전체 보기':
            filtered_reviews = filtered_reviews[filtered_reviews['지역'] == selected_region]

        if selected_categories and '전체 보기' not in selected_categories:
            filtered_reviews = filtered_reviews[filtered_reviews['카테고리'].isin(selected_categories)]

    # 리뷰 내용 추출
    texts = filtered_reviews['리뷰'].dropna().tolist()

    # 불용어 목록 로드
    stopwords_file_path = './data/stopwords-ko.txt'
    stopwords_set = load_stopwords(stopwords_file_path)

    # 텍스트 데이터에서 명사 추출 및 불용어 제거
    nouns = get_nouns_from_texts(texts, stopwords_set)

    if not nouns:
        raise ValueError("We need at least 1 word to plot a word cloud, got 0.")

    # 빈도수 계산
    count = Counter(nouns)

    get_image_mask(image_name='./img/seoul.PNG')

    image_colors = ImageColorGenerator(cached_mask)

    wordcloud_image_path = f'./img/wordcloud_{selected_region}_{encoded_categories}.png'

    # 워드클라우드 생성
    wordcloud = WordCloud(width=800, height=700, background_color='white', mask=cached_mask,
                              font_path='./font/Cafe24Ohsquare-v2.0.ttf').generate_from_frequencies(count)
    wordcloud.recolor(color_func=image_colors)

    # 워드클라우드 이미지를 파일로 저장
    wordcloud.to_file(wordcloud_image_path)

    return wordcloud_image_path

def load_stopwords(file_path):
    """
    파일의 경로
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(line.strip() for line in file)
    return stopwords


def encode_categories(selected_categories):
    """
    선택된 카테고리를 'r', 'h', 'c'로 변환하여 문자열로 표현합니다.
    """
    # 카테고리와 대응되는 문자 정의
    category_map = {
        '음식점': 'r',
        '숙박시설': 'h',
        '카페': 'c'
    }

    # 선택된 카테고리에서 대응되는 문자 추출
    encoded_string = ''.join(category_map[cat] for cat in selected_categories if cat in category_map)

    return encoded_string