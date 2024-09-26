import pandas as pd
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def load_excel(file_path):
    """
    엑셀 파일 불러오기
    """
    return pd.read_excel(file_path)

def filter_data_by_keyword(df, keyword):
    """
    데이터에서 검색어로 필터링된 텍스트 추출
    """
    filtered_df = df[df['검색어'].str.contains(keyword, na=False)]
    texts = filtered_df['검색결과'].dropna().tolist()
    return texts

def get_nouns_from_texts(texts, stopwords_set):
    """
    텍스트 데이터에서 형태소 분석을 통해 명사 추출 및 불용어 제거
    """
    okt = Okt()
    nouns = []

    for text in texts:
        # 형태소 분석을 통해 명사만 추출
        nouns += okt.nouns(text)

    # 불용어 제거
    nouns = [noun for noun in nouns if noun not in stopwords_set]

    return nouns

def create_wordcloud(nouns):
    """
    워드클라우드 생성
    """
    # 빈도수 계산
    count = Counter(nouns)

    # 워드클라우드 생성
    wordcloud = WordCloud(
        font_path='../font/Cafe24Ohsquare-v2.0.ttf',  # 한글 폰트 경로 지정
        background_color='black',
        width=800,
        height=600
    ).generate_from_frequencies(count)

    # 워드클라우드 시각화
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def load_stopwords(file_path):
    """
    불용어 목록 로드
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(line.strip() for line in file)
    return stopwords

# 파일 경로를 지정합니다.
file_path = '../data/인스타그램크롤링_24-08-27.xlsx'
stopwords_file_path = '../data/stopwords-ko.txt'

# 엑셀 파일에서 데이터프레임을 불러옵니다.
df = load_excel(file_path)

# 불용어 목록 로드
stopwords_set = load_stopwords(stopwords_file_path)

# 사용자로부터 검색어 입력받기
keyword = input("검색어를 입력하세요: ")

# 검색어로 필터링된 텍스트 데이터 추출
texts = filter_data_by_keyword(df, keyword)

# 텍스트 데이터에서 명사 추출 및 불용어 제거
nouns = get_nouns_from_texts(texts, stopwords_set)

# 워드클라우드 생성 및 시각화
if nouns:
    create_wordcloud(nouns)
else:
    print("해당 검색어에 대한 데이터가 없습니다.")
