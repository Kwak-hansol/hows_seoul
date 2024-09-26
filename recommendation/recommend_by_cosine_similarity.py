import cx_Oracle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


def load_data():
    """
    데이터 파일에서 데이터프레임 로드
    NaN 값을 빈 문자열로 대체
    """
    df = pd.read_excel('./data/카테고리_분류_리뷰추가_2024-09-04.xlsx')

    df['review'].fillna('', inplace=True)
    df['category'].fillna('', inplace=True)

    return df


def compute_similarity_matrices(df):
    """
    코사인 유사도 계산
    """
    # 텍스트 벡터화
    vectorizer = CountVectorizer(tokenizer=lambda x: x.lower().split())
    review_matrix = vectorizer.fit_transform(df['review'])

    # 카테고리 벡터화
    category_vectorizer = CountVectorizer(tokenizer=lambda x: x.split('|'))
    category_matrix = category_vectorizer.fit_transform(df['category'])

    # 코사인 유사도 계산
    review_similarity = cosine_similarity(review_matrix)
    category_similarity = cosine_similarity(category_matrix)

    return review_similarity, category_similarity

def compute_combined_similarity(index, review_similarity, category_similarity, review_weight=1.0, category_weight=1.0):
    """
    최종 유사도 계산 함수
    """
    review_sim = review_similarity[index]
    category_sim = category_similarity[index]

    combined_sim = (review_weight * review_sim) + (category_weight * category_sim)
    return combined_sim


def recommend_place(df, title, review_similarity, category_similarity, review_weight=1.0, category_weight=3.0, num_recommendations=5):
    """
    음식점 추천
    """
    if not title:
        return df
    # 음식점의 인덱스 찾기
    idx = df.index[df['title'] == title].tolist()
    if not idx:
        return df  # 입력한 title이 없을 경우 빈 데이터프레임 반환
    idx = idx[0]

    combined_sim = compute_combined_similarity(idx, review_similarity, category_similarity, review_weight, category_weight)

    # 유사도에 따라 항목 정렬
    sim_scores = list(enumerate(combined_sim))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    seen_reviews = set()

    # 상위 유사한 음식점 선택 (중복 리뷰 제거)
    for i, (index, score) in enumerate(sim_scores):
        if df['review'].iloc[index] not in seen_reviews and index != idx:
            recommendations.append(index)
            seen_reviews.add(df['review'].iloc[index])
        if len(recommendations) == num_recommendations:
            break

    # 추천된 음식점들을 원래 데이터 프레임에서 추출하고 특정 열만 선택
    recommended_df = df.iloc[recommendations].reset_index(drop=True)
    recommended_df = recommended_df[['검색어', 'title', 'category']]

    return recommended_df

def select_from_oracle(category):
    """
    Oracle 데이터 베이스 불러오기
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

def recommended_place_link(df):
    """
    데이터 프레임을 HTML로 변환하여 추천
    """
    restaurant_df = select_from_oracle('restaurant')
    hotel_df = select_from_oracle('hotel')
    cafe_df = select_from_oracle('cafe')

    combined_df = pd.concat([restaurant_df, hotel_df, cafe_df])

    link_added_df = df.merge(combined_df[['TITLE', 'LINK']], left_on='title', right_on='TITLE', how='left')

    # 링크가 있는 경우 title 컬럼에 하이퍼링크 설정
    link_added_df['title'] = link_added_df.apply(
        lambda row: f"<a href='{row['LINK']}' target='_blank'>{row['title']}</a>"
        if pd.notnull(row['LINK']) else row['title'], axis=1)

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