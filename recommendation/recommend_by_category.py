import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st
#
# # 한글 폰트 설정
# font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 필요한 폰트 파일 경로
# font_name = fm.FontProperties(fname=font_path).get_name()
# plt.rc('font', family=font_name)

# 데이터 로드 함수
def load_data(file_path):
    """
    데이터 로드
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.lower().str.strip()  # Column name normalization
    return df

def get_review_word_count(df, review_term):
    """
    리뷰에서 단어 빈도를 계산하는 함수
    """
    word_count = Counter()
    for review in df['review'].dropna().astype(str):
        words = re.findall(r'\w+', review.lower())
        word_count.update(words)
    return word_count

def calculate_term_frequency(review, review_term):
    """
    특정 단어 빈도 계산 함수
    """
    words = re.findall(r'\w+', review.lower())
    return sum(words.count(word) for word in review_term.lower().split())

def truncate_review(review, max_chars_per_line=300):
    """
    리뷰를 일정 길이로 잘라주는 함수
    """
    if len(review) > max_chars_per_line:
        return review[:max_chars_per_line] + '...'
    return review

def content_based_filtering(search_term, category_term, review_term, df, top_n=5):
    """
    필터링 및 추천 로직 함수
    """
    # 데이터 전처리: 빈 리뷰와 NaN 제거
    df = df[df['review'].str.strip().ne('') & df['review'].notna()]

    # 초기 필터링
    filtered_df = df.copy()

    # 1단계: search_term 필터링 (정규식으로 처리하지 않도록 regex=False)
    if search_term:
        filtered_df = filtered_df[filtered_df['검색어'].str.contains(search_term, case=False, na=False, regex=False)]

    # 2단계: category_term 필터링
    if category_term:
        filtered_df = filtered_df[filtered_df['category'].str.contains(category_term, case=False, na=False)]

    # 3단계: review_term 필터링 및 정렬
    if review_term:
        filtered_df = filtered_df[filtered_df['review'].str.contains(review_term, case=False, na=False)]
        filtered_df['review_term_frequency'] = filtered_df['review'].apply(lambda x: calculate_term_frequency(x, review_term))
        filtered_df = filtered_df.sort_values(by='review_term_frequency', ascending=False)

    # 최종 결과 추출 및 중복 제거
    results = filtered_df.drop_duplicates(subset='review').head(top_n)

    # 추가 아이템 채우기 (결과가 top_n보다 적을 경우)
    if len(results) < top_n:
        remaining_count = top_n - len(results)
        additional_items = df[~df['review'].isin(results['review'])]

        if not additional_items.empty:
            additional_items = additional_items.sample(n=min(remaining_count, len(additional_items)), replace=False)
            results = pd.concat([results, additional_items]).drop_duplicates(subset='review')

    # 리뷰 길이 제한
    results['review'] = results['review'].apply(lambda x: truncate_review(x, max_chars_per_line=300))

    # 인덱스 초기화
    results.index = range(1, len(results) + 1)

    return results[['검색어', 'title', 'category', 'review']]


def category(name):
    """
    카테고리별 로드
    """
    file_path1 = './data/음식점_세부정보_24-08-31.xlsx'
    restaurant_df = pd.read_excel(file_path1)
    file_path2 = './data/숙박시설_세부정보_24-08-31.xlsx'
    hotel_df = pd.read_excel(file_path2)
    file_path3 = './data/카페_세부정보_24-08-31.xlsx'
    cafe_df = pd.read_excel(file_path3)
    combined_df = pd.concat([restaurant_df, hotel_df, cafe_df], ignore_index=True)
    filtered_df = combined_df[combined_df['title'] == name]
    if not filtered_df.empty:
        # 첫 번째 행의 'category' 값 반환
        return filtered_df.iloc[0]['category']
    else:
        # 데이터가 없을 때의 처리
        return None  # 또는 적절한 기본값

def recommend(search_term, name):
    """
    사용자의 입력값을 받기
    """
    categories = category(name)

    DATA_FILE_PATH = './data/카테고리_분류_리뷰추가_2024-09-04.xlsx'

    # 데이터 로드
    df = load_data(DATA_FILE_PATH)

    # 사용자 입력 받기
    category_term = st.text_input("카테고리에서 검색할 단어를 입력하세요", placeholder="예: 한식, 양식, 일식")
    review_term = st.text_input("리뷰에서 검색할 단어를 입력하세요", placeholder="예: 맛, 가격")

    if search_term or category_term or review_term:
        if search_term != "전체 보기":
            recommended_items = content_based_filtering(search_term, category_term, review_term, df)

            if not recommended_items.empty:
                # HTML 테이블로 출력
                html_table = recommended_items[['검색어', 'title', 'category', 'review']].to_html(classes='dataframe',
                                                                                               escape=False,
                                                                                               index=False)
                html_table = html_table.replace('<td>', '<td class="title">').replace('<td class="review">',
                                                                                      '<td class="review">')
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.write("추천 결과가 없습니다.")
    else:
        st.write("지명, 카테고리, 리뷰 중 하나 이상을 입력해주세요.")