import cx_Oracle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

# 한글 폰트 설정
mpl.rcParams['font.family'] = 'Malgun Gothic'  # Windows
mpl.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

def plot_age_distribution(df):
    """
    나이대별로 데이터로 파이차트 생성
    """
    age_columns = [
        'PPLTN_RATE_0', 'PPLTN_RATE_10', 'PPLTN_RATE_20', 'PPLTN_RATE_30',
        'PPLTN_RATE_40', 'PPLTN_RATE_50', 'PPLTN_RATE_60', 'PPLTN_RATE_70'
    ]
    age_labels = [
        '0-9세', '10대', '20대', '30대', '40대', '50대', '60대', '70대 이상'
    ]

    # 데이터프레임의 각 열을 숫자로 변환
    for column in age_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # 빈 데이터프레임 처리
    if df.empty or df[age_columns].isnull().all().all():
        return plt.figure()  # 빈 그래프 반환

    age_values = df[age_columns].mean().fillna(0).values
    age_data = dict(zip(age_labels, age_values))

    # 파이 차트 생성
    plt.figure(figsize=(8, 6))
    plt.pie(
        x=list(age_data.values()),
        labels=list(age_data.keys()),
        startangle=90,
        colors=sns.color_palette("pastel"),
        autopct='%1.1f%%',
        pctdistance=0.85,  # 퍼센트 레이블과 원 중심 거리
    )
    plt.title('연령대별 비율')
    plt.legend()
    plt.axis('equal')
    return plt


def plot_gender_distribution(df):
    """
    성별 비율 데이터 파이차트 생성
    """
    # 성별 비율 데이터 준비
    df['MALE_PPLTN_RATE'] = pd.to_numeric(df['MALE_PPLTN_RATE'], errors='coerce')
    df['FEMALE_PPLTN_RATE'] = pd.to_numeric(df['FEMALE_PPLTN_RATE'], errors='coerce')

    # 빈 데이터프레임 처리
    if df.empty or df[['MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE']].isnull().all().all():
        return plt.figure()  # 빈 그래프 반환

    male_rate = df['MALE_PPLTN_RATE'].mean()
    female_rate = df['FEMALE_PPLTN_RATE'].mean()

    gender_data = {
        '남성': male_rate,
        '여성': female_rate
    }

    # 파이 차트 생성
    plt.figure(figsize=(8, 6))
    plt.pie(
        x=list(gender_data.values()),
        labels=list(gender_data.keys()),
        startangle=90,
        colors=sns.color_palette("pastel"),
        autopct='%1.1f%%'
    )
    plt.title('성별 비율')
    plt.legend()
    plt.axis('equal')
    return plt

def plot_forecast(df):
    """
    예측 인구수 차트 생성
    """
    # 예측 인구 데이터 준비
    fcst_times = []
    fcst_ppltn_mins = []
    fcst_ppltn_maxs = []

    for index, row in df.iterrows():
        for i in range(10):  # 최대 10개 예측 데이터
            fcst_time_col = f'FCST_TIME_{i + 1}'
            fcst_ppltn_min_col = f'FCST_PPLTN_MIN_{i + 1}'
            fcst_ppltn_max_col = f'FCST_PPLTN_MAX_{i + 1}'

            if pd.notna(row[fcst_time_col]) and pd.notna(row[fcst_ppltn_min_col]) and pd.notna(row[fcst_ppltn_max_col]):
                fcst_times.append(row[fcst_time_col])
                fcst_ppltn_mins.append(float(row[fcst_ppltn_min_col]))
                fcst_ppltn_maxs.append(float(row[fcst_ppltn_max_col]))

    # 빈 데이터 처리
    if not fcst_times:
        return plt.figure()  # 빈 그래프 반환

    plt.figure(figsize=(12, 10))
    sns.lineplot(x=fcst_times, y=fcst_ppltn_mins, marker='o', label='최소 인구수', color='blue')
    sns.lineplot(x=fcst_times, y=fcst_ppltn_maxs, marker='o', label='최대 인구수', color='red')

    plt.title('예측 인구수')
    plt.xlabel('시간')
    plt.xticks(rotation=45)
    plt.ylabel('인구수')
    plt.legend()
    return plt


def convert_to_numeric(df, columns):
    """
    지정된 열들을 숫자형으로 변환합니다.
    """
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def plot_congestion_and_non_resident_population(df, congestion_level):
    """
    특정 혼잡도를 선택하여 인구수 및 비상주 인구 비율을 시각화하는 함수
    Args:
        df (DataFrame): 데이터프레임
        congestion_level (str): 선택된 혼잡도 레벨
    Returns:
        matplotlib.figure.Figure: 시각화된 Figure 객체
    """
    # 변환할 열 목록
    numeric_columns = [
        'AREA_PPLTN_MIN', 'AREA_PPLTN_MAX', 'NON_RESNT_PPLTN_RATE'
    ]

    # 데이터 변환
    df = convert_to_numeric(df, numeric_columns)

    # 추정 인구수 계산
    df['ESTIMATED_POPULATION'] = (df['AREA_PPLTN_MIN'] + df['AREA_PPLTN_MAX']) // 2
    df['ESTIMATED_NON_RESNT_POPULATION'] = df['ESTIMATED_POPULATION'] * df['NON_RESNT_PPLTN_RATE']

    # 선택된 혼잡도에 해당하는 데이터 필터링
    filtered_df = df[df['AREA_CONGEST_LVL'] == congestion_level]

    if filtered_df.empty:
        print(f"'{congestion_level}' 레벨에 해당하는 데이터가 없습니다.")
        return None

    # 인구수 Top 5 추출
    top5_by_population = filtered_df[['AREA_NM', 'ESTIMATED_POPULATION']].dropna().sort_values(by='ESTIMATED_POPULATION', ascending=False).head(5)

    # 비상주 인구수 Top 5 추출
    top5_by_non_resident_population = filtered_df[['AREA_NM', 'ESTIMATED_NON_RESNT_POPULATION']].dropna().sort_values(by='ESTIMATED_NON_RESNT_POPULATION', ascending=False).head(5)

    # 비상주 인구 비율 Top 5 추출
    # top5_by_non_resident = filtered_df[['AREA_NM', 'NON_RESNT_PPLTN_RATE']].dropna().sort_values(by='NON_RESNT_PPLTN_RATE', ascending=False).head(5)

    # 시각화 설정
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # 인구수 Top 5 그래프
    sns.barplot(x='ESTIMATED_POPULATION', y='AREA_NM', data=top5_by_population, palette='viridis', ax=axs[0])
    axs[0].set_title(f'{congestion_level} - 인구수 Top {len(top5_by_population)}')
    axs[0].set_xlabel('추정 인구수')
    axs[0].set_ylabel('지역')

    # 비상주 인구수 Top 5 그래프
    sns.barplot(x='ESTIMATED_NON_RESNT_POPULATION', y='AREA_NM', data=top5_by_non_resident_population, palette='magma', ax=axs[1])
    axs[1].set_title(f'{congestion_level} - 비상주 인구수 Top {len(top5_by_non_resident_population)}')
    axs[1].set_xlabel('비상주 인구수')
    axs[1].set_ylabel('지역')

    # 비상주 인구 비율 Top 5 그래프
    # sns.barplot(x='NON_RESNT_PPLTN_RATE', y='AREA_NM', data=top5_by_non_resident, palette='magma', ax=axs[1])
    # axs[1].set_title(f'{congestion_level} - 비상주 인구 비율 Top {len(top5_by_non_resident)}')
    # axs[1].set_xlabel('비상주 인구 비율')
    # axs[1].set_ylabel('지역')

    plt.tight_layout()
    return fig


def plot_top5_by_age(df):
    """
    연령대별 인구수 그래프 생성
    """
    # 변환할 열 목록
    age_columns = [
        'PPLTN_RATE_0', 'PPLTN_RATE_10', 'PPLTN_RATE_20', 'PPLTN_RATE_30',
        'PPLTN_RATE_40', 'PPLTN_RATE_50', 'PPLTN_RATE_60', 'PPLTN_RATE_70'
    ]
    age_labels = [
        '0-9세', '10대', '20대', '30대', '40대', '50대', '60대', '70대 이상'
    ]

    # 데이터 변환
    df = convert_to_numeric(df, age_columns + ['AREA_PPLTN_MIN', 'AREA_PPLTN_MAX'])

    # 추정 인구수 계산
    df['ESTIMATED_POPULATION'] = (df['AREA_PPLTN_MIN'] + df['AREA_PPLTN_MAX']) // 2

    # 각 연령대별 실시간 인구수 계산
    for i, age_column in enumerate(age_columns):
        df[age_labels[i]] = df[age_column] * df['ESTIMATED_POPULATION']

    # 시각화 설정
    fig, axs = plt.subplots(2, 4, figsize=(20, 10))
    for i, age_label in enumerate(age_labels):
        top5_by_age = df[['AREA_NM', age_label]].dropna().sort_values(by=age_label, ascending=False).head(5)

        sns.barplot(x='AREA_NM', y=age_label, data=top5_by_age, ax=axs[i // 4, i % 4], palette='coolwarm')
        axs[i // 4, i % 4].set_title(f'{age_label} - 인구수 Top {len(top5_by_age)}')
        axs[i // 4, i % 4].set_ylabel('추정 인구수')
        axs[i // 4, i % 4].set_xlabel('지역')
        axs[i // 4, i % 4].tick_params(rotation=45)

    plt.tight_layout()
    return fig


def plot_top5_by_gender(df):
    """
    성별별 Top5 그래프 생성
    """
    # 데이터 변환
    df = convert_to_numeric(df, ['MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE', 'AREA_PPLTN_MIN', 'AREA_PPLTN_MAX'])

    # 추정 인구수 계산
    df['ESTIMATED_POPULATION'] = (df['AREA_PPLTN_MIN'] + df['AREA_PPLTN_MAX']) // 2

    # 성별 실시간 인구수 계산
    df['남성'] = df['MALE_PPLTN_RATE'] * df['ESTIMATED_POPULATION']
    df['여성'] = df['FEMALE_PPLTN_RATE'] * df['ESTIMATED_POPULATION']

    # 시각화 설정
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # 남성 인구수 Top 5 그래프
    top5_by_male = df[['AREA_NM', '남성']].dropna().sort_values(by='남성', ascending=False).head(5)
    sns.barplot(x='남성', y='AREA_NM', data=top5_by_male, palette='Blues', ax=axs[0])
    axs[0].set_title(f'남성 인구수 Top {len(top5_by_male)}')
    axs[0].set_xlabel('추정 인구수')
    axs[0].set_ylabel('지역')

    # 여성 인구수 Top 5 그래프
    top5_by_female = df[['AREA_NM', '여성']].dropna().sort_values(by='여성', ascending=False).head(5)
    sns.barplot(x='여성', y='AREA_NM', data=top5_by_female, palette='Reds', ax=axs[1])
    axs[1].set_title(f'여성 인구수 Top {len(top5_by_female)}')
    axs[1].set_xlabel('추정 인구수')
    axs[1].set_ylabel('지역')

    plt.tight_layout()
    return fig


def fetch_seoul_location_data():
    """
    서울 지역 데이터베이스에서 데이터 추출
    """
    try:
        conn = cx_Oracle.connect('open_source/1111@192.168.0.22:1521/xe')
        cur = conn.cursor()

        sql_select = '''
        SELECT AREA_NM, CATEGORY
        FROM seoul_location
        '''

        cur.execute(sql_select)
        rows = cur.fetchall()
        col_names = [row[0] for row in cur.description]

        df_seoul_location = pd.DataFrame(rows, columns=col_names)

        cur.close()
        conn.close()

        return df_seoul_location
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None


def plot_population_by_category(df):
    """
    서울 지역구분별 인구수 파이차트
    """
    # 서울 지역 데이터 가져오기
    df_seoul_location = fetch_seoul_location_data()

    if df_seoul_location is None or df_seoul_location.empty:
        print("서울 지역 데이터 가져오기 실패")
        return plt.figure()  # 빈 그래프 반환

    # df와 df_seoul_location을 AREA_NM을 기준으로 병합
    df = df.merge(df_seoul_location[['AREA_NM', 'CATEGORY']], on='AREA_NM', how='left')

    # 데이터 변환
    df['AREA_PPLTN_MAX'] = pd.to_numeric(df['AREA_PPLTN_MAX'], errors='coerce')
    df['AREA_PPLTN_MIN'] = pd.to_numeric(df['AREA_PPLTN_MIN'], errors='coerce')

    # 인구수 계산: (최대 인구수 + 최소 인구수) / 2
    df['AREA_PPLTN'] = (df['AREA_PPLTN_MAX'] + df['AREA_PPLTN_MIN']) / 2

    # 카테고리별 인구수 합계 계산
    category_population = df.groupby('CATEGORY')['AREA_PPLTN'].sum().reset_index()

    # 빈 데이터 처리
    if category_population.empty or category_population['AREA_PPLTN'].isnull().all():
        return plt.figure()  # 빈 그래프 반환

    # 파이 차트 생성
    plt.figure(figsize=(10, 8))
    plt.pie(
        x=category_population['AREA_PPLTN'],
        labels=category_population['CATEGORY'],
        startangle=90,
        colors=sns.color_palette("pastel"),
        autopct='%1.1f%%'
    )
    plt.title('지역구분별 인구수 비율')
    plt.axis('equal')
    return plt

def plot_population_congestion_heatmap(df):
    """
    지역구분별 혼잡도에 따른 인구수 히트맵
    """
    df_seoul_location = fetch_seoul_location_data()

    if df is None or df.empty:
        print("데이터를 가져오는 데 실패했습니다.")
        return plt.figure()  # 빈 그래프 반환

    # df와 df_seoul_location을 AREA_NM을 기준으로 병합
    df = df.merge(df_seoul_location[['AREA_NM', 'CATEGORY']], on='AREA_NM', how='left')

    # 데이터 변환
    df['AREA_PPLTN_MAX'] = pd.to_numeric(df['AREA_PPLTN_MAX'], errors='coerce')
    df['AREA_PPLTN_MIN'] = pd.to_numeric(df['AREA_PPLTN_MIN'], errors='coerce')
    df['AREA_PPLTN'] = (df['AREA_PPLTN_MAX'] + df['AREA_PPLTN_MIN']) / 2

    # 카테고리별 인구수 합계 계산
    pivot_table = df.pivot_table(
        index='AREA_CONGEST_LVL',  # y축으로 혼잡도
        columns='CATEGORY',        # x축으로 지역구분
        values='AREA_PPLTN',
        aggfunc='sum'
    )

    # 혼잡도 순서 정의
    congestion_order = ["붐빔", "약간 붐빔", "보통", "여유"]

    # 실제 데이터에서 사용 가능한 혼잡도 레벨만 필터링
    available_congestion_levels = [lvl for lvl in congestion_order if lvl in pivot_table.index]
    pivot_table = pivot_table.loc[available_congestion_levels]

    # 히트맵 생성
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        pivot_table,
        cmap='YlGnBu',  # 색상 맵, 인구수에 따라 색상 진하기를 표현
        annot=True,     # 셀에 값 표시
        fmt='.0f',      # 숫자 형식
        linewidths=0.5, # 셀 간의 간격
        linecolor='gray', # 셀 간의 선 색상
        cbar_kws={'label': '인구수'}  # 색상 바 레이블
    )

    plt.title('지역구분별 혼잡도에 따른 인구수 히트맵')
    plt.xlabel('지역구분')
    plt.ylabel('혼잡도')
    plt.tight_layout()
    return plt