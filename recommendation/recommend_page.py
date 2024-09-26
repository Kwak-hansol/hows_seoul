import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import Counter
import re

# 한글 폰트 설정
font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 필요한 폰트 파일 경로
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

# 페이지 레이아웃 설정
st.set_page_config(
    page_title="서울 어때? 추천 음식점",
    layout="wide",
)

# 스타일 적용을 위한 CSS
st.write("""
    <style>
        .header, .footer {
            text-align: center; 
            padding: 10px; 
        }
        .header {
            background-color: lightblue; 
            text-align: center;
        }
        .footer {
            background-color: lightgray;
            text-align: center;
        }
        .section {
            background-color: #f0f0f0; 
            padding: 20px;
            margin: 10px 0;
        }
        .section h3 {
            text-align: center;
        }
        .dataframe thead th {
            text-align: center;
            white-space: nowrap;
        }
        .dataframe td.title {
            white-space: pre-wrap;
            text-align: left;
        }
        .dataframe td.review {
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .dataframe {
            font-size: 16px;
        }
""", unsafe_allow_html=True)

# 헤더
st.write("<div class='header'><h2>추천 음식점</h2></div>", unsafe_allow_html=True)

DATA_FILE_PATH = '식당_리뷰추가_2024-09-02.xlsx'

def load_data():
    """
    데이터 로드
    """
    df = pd.read_excel(DATA_FILE_PATH)
    df.columns = df.columns.str.lower().str.strip()  # Column name normalization
    return df

def get_review_word_count(df, review_term):
    """
    리뷰에 대한 단어 빈도 계산
    """
    word_count = Counter()
    for review in df['review'].dropna().astype(str):
        words = re.findall(r'\w+', review.lower())
        word_count.update(words)
    return word_count

def calculate_term_frequency(review, review_term):
    """
    특정 단어의 빈도 계산
    """
    words = re.findall(r'\w+', review.lower())
    return sum(words.count(word) for word in review_term.lower().split())

def truncate_review(review, max_chars_per_line=300):
    """
    리뷰를 최대 문자 수로 자르고 ... 추가
    """
    if len(review) > max_chars_per_line:
        return review[:max_chars_per_line] + '...'
    return review

def content_based_filtering(search_term, category_term, review_term, df, top_n=5):
    """
    추천 시스템 설정
    빈 칸 및 NAN제외 및 필터링 후 유사도에 따라 추천
    추천은 최대 5개 부족하면 카테고리에 맞게 5개 추천
    """
    # 리뷰 칼럼에서 빈 칸 및 NaN 제외
    df = df[df['review'].str.strip().ne('') & df['review'].notna()]

    # 조건에 맞는 초기 필터링
    search_matches = df[df['검색어'].str.contains(search_term, case=False, na=False)] if search_term else pd.DataFrame()
    category_matches = df[
        df['category'].str.contains(category_term, case=False, na=False)] if category_term else pd.DataFrame()
    review_matches = df[df['review'].str.contains(review_term, case=False, na=False)] if review_term else pd.DataFrame()

    results = pd.DataFrame()

    # 모든 조건이 입력된 경우
    if search_term and category_term and review_term:
        if not search_matches.empty:
            category_matches_in_search = search_matches[
                search_matches['category'].str.contains(category_term, case=False, na=False)]
            if not category_matches_in_search.empty:
                category_matches_in_search['review_term_frequency'] = category_matches_in_search['review'].apply(
                    lambda x: calculate_term_frequency(x, review_term))
                results = category_matches_in_search.sort_values(by='review_term_frequency', ascending=False).head(top_n)
            else:
                results = search_matches.sample(n=min(top_n, len(search_matches)), replace=False)
        else:
            results = pd.DataFrame()

    # 검색어와 카테고리 두 개만 입력된 경우
    elif search_term and category_term:
        if not search_matches.empty:
            category_matches_in_search = search_matches[
                search_matches['category'].str.contains(category_term, case=False, na=False)]
            if not category_matches_in_search.empty:
                results = category_matches_in_search.sample(n=min(top_n, len(category_matches_in_search)),
                                                            replace=False)
            else:
                results = search_matches.sample(n=min(top_n, len(search_matches)), replace=False)
        else:
            results = pd.DataFrame()

    # 검색어와 리뷰 두 개만 입력된 경우
    elif search_term and review_term:
        if not search_matches.empty:
            review_matches_in_search = search_matches[
                search_matches['review'].str.contains(review_term, case=False, na=False)]
            if not review_matches_in_search.empty:
                review_matches_in_search['review_term_frequency'] = review_matches_in_search['review'].apply(
                    lambda x: calculate_term_frequency(x, review_term))
                results = review_matches_in_search.sort_values(by='review_term_frequency', ascending=False).head(top_n)
            else:
                results = search_matches.sample(n=min(top_n, len(search_matches)), replace=False)
        else:
            results = pd.DataFrame()

    # 카테고리와 리뷰 두 개만 입력된 경우
    elif category_term and review_term:
        if not category_matches.empty:
            review_matches_in_category = category_matches[
                category_matches['review'].str.contains(review_term, case=False, na=False)]
            if not review_matches_in_category.empty:
                review_matches_in_category['review_term_frequency'] = review_matches_in_category['review'].apply(
                    lambda x: calculate_term_frequency(x, review_term))
                results = review_matches_in_category.sort_values(by='review_term_frequency', ascending=False).head(
                    top_n)
            else:
                results = category_matches.sample(n=min(top_n, len(category_matches)), replace=False)
        else:
            results = pd.DataFrame()

    # 단일 조건 입력된 경우
    elif search_term:
        if not search_matches.empty:
            results = search_matches.sample(n=min(top_n, len(search_matches)), replace=False)

    elif category_term:
        if not category_matches.empty:
            results = category_matches.sample(n=min(top_n, len(category_matches)), replace=False)

    elif review_term:
        if not review_matches.empty:
            review_matches['review_term_frequency'] = review_matches['review'].apply(
                lambda x: calculate_term_frequency(x, review_term))
            results = review_matches.sort_values(by='review_term_frequency', ascending=False).head(top_n)

    # 중복된 리뷰 제거
    results = results.drop_duplicates(subset='review')

    # 부족한 경우, 랜덤으로 항목 추가 (이미 존재하는 리뷰는 제외)
    if len(results) < top_n:
        if search_term and not search_matches.empty:
            additional_items = search_matches[~search_matches['review'].isin(results['review'])]
        elif category_term and not category_matches.empty:
            additional_items = category_matches[~category_matches['review'].isin(results['review'])]
        else:
            additional_items = df[~df['review'].isin(results['review'])]

        if not additional_items.empty:
            # 결과에 없는 항목들만 추가
            additional_items = additional_items[~additional_items['review'].isin(results['review'])]
            additional_items = additional_items.sample(n=min(top_n - len(results), len(additional_items)), replace=False)
            results = pd.concat([results, additional_items]).drop_duplicates(subset='review')

    # 리뷰를 최대 문자 수로 제한하여 표시
    results['review'] = results['review'].apply(lambda x: truncate_review(x, max_chars_per_line=300))

    # 결과를 5개로 제한
    results = results.head(top_n)

    # 결과의 인덱스를 1부터 시작하도록 설정
    results.index = range(1, len(results) + 1)

    return results[['검색어', 'title', 'category', 'review']]

def main():
    """
    추천 시스템 메인페이지
    """
    # 데이터 로드
    df = load_data()

    # 사용자 입력
    search_term = st.text_input("지명을 입력하세요", placeholder="예: 성수카페거리")
    category_term = st.text_input("카테고리에서 검색할 단어를 입력하세요", placeholder="예: 한식, 양식, 일식")
    review_term = st.text_input("리뷰에서 검색할 단어를 입력하세요", placeholder="예: 맛, 가격")

    if search_term or category_term or review_term:
        # 추천 항목 가져오기
        recommended_items = content_based_filtering(search_term, category_term, review_term, df)

        if not recommended_items.empty:
            # 중복된 리뷰 제거 후 부족한 항목을 채우기
            recommended_items = recommended_items.drop_duplicates(subset='review')

            # 최종적으로 5개로 제한
            if len(recommended_items) < 5:
                additional_items_needed = 5 - len(recommended_items)
                additional_items = df[df['검색어'].str.contains(search_term, case=False, na=False)]
                additional_items = additional_items[~additional_items['review'].isin(recommended_items['review'])]
                additional_items = additional_items[
                    additional_items['review'].str.strip().ne('') & additional_items['review'].notna()]
                additional_items = additional_items.sample(n=min(additional_items_needed, len(additional_items)), replace=False)
                recommended_items = pd.concat([recommended_items, additional_items]).drop_duplicates(subset='review').head(5)

            # 리뷰를 최대 문자 수로 제한하여 표시
            recommended_items['review'] = recommended_items['review'].apply(lambda x: truncate_review(x, max_chars_per_line=300))

            # HTML 테이블을 사용하여 스타일 적용
            html_table = recommended_items[['검색어', 'title', 'category', 'review']].to_html(
                classes='dataframe', escape=False,
                index=False
            )

            # HTML 테이블에 클래스 추가
            html_table = html_table.replace('<td>', '<td class="title">').replace('<td class="review">', '<td class="review">')

            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.write("추천 결과가 없습니다.")
    else:
        st.write("지명, 카테고리, 리뷰 중 하나 이상을 입력해주세요.")

if __name__ == "__main__":
    main()

st.write("<div class='footer'><h5>대경 ICT</h5></div>", unsafe_allow_html=True)