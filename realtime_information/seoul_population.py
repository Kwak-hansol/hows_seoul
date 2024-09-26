# data_collector.py
import requests
import pandas as pd
from xml.etree.ElementTree import fromstring

import streamlit

access_key = '74694d524a6c6f653637674a65474f'

@streamlit.cache_data
def get_request_url(location):
    """
    데이터 수집
    """
    base_url1 = 'http://openapi.seoul.go.kr:8088'
    type = 'xml'
    base_url2 = 'citydata_ppltn'
    start_row = 1
    end_row = 5

    url = f'{base_url1}/{access_key}/{type}/{base_url2}/{start_row}/{end_row}/{location}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        xml_root = fromstring(response.text)

        if xml_root:
            data = []
            try:
                seoul_rtd = xml_root.find('SeoulRtd.citydata_ppltn')

                # 기본 정보 수집
                area_nm = seoul_rtd.find('AREA_NM').text
                area_cd = seoul_rtd.find('AREA_CD').text
                area_congest_lvl = seoul_rtd.find('AREA_CONGEST_LVL').text
                area_congest_msg = seoul_rtd.find('AREA_CONGEST_MSG').text
                area_ppltn_min = seoul_rtd.find('AREA_PPLTN_MIN').text
                area_ppltn_max = seoul_rtd.find('AREA_PPLTN_MAX').text
                male_ppltn_rate = seoul_rtd.find('MALE_PPLTN_RATE').text
                female_ppltn_rate = seoul_rtd.find('FEMALE_PPLTN_RATE').text
                ppltn_rate_0 = seoul_rtd.find('PPLTN_RATE_0').text
                ppltn_rate_10 = seoul_rtd.find('PPLTN_RATE_10').text
                ppltn_rate_20 = seoul_rtd.find('PPLTN_RATE_20').text
                ppltn_rate_30 = seoul_rtd.find('PPLTN_RATE_30').text
                ppltn_rate_40 = seoul_rtd.find('PPLTN_RATE_40').text
                ppltn_rate_50 = seoul_rtd.find('PPLTN_RATE_50').text
                ppltn_rate_60 = seoul_rtd.find('PPLTN_RATE_60').text
                ppltn_rate_70 = seoul_rtd.find('PPLTN_RATE_70').text
                resnt_ppltn_rate = seoul_rtd.find('RESNT_PPLTN_RATE').text
                non_resnt_ppltn_rate = seoul_rtd.find('NON_RESNT_PPLTN_RATE').text
                ppltn_time = seoul_rtd.find('PPLTN_TIME').text
                replace_yn = seoul_rtd.find('REPLACE_YN').text
                fcst_yn = seoul_rtd.find('FCST_YN').text

                # 예측 인구 데이터 수집
                fcst_times = []
                fcst_congest_lvls = []
                fcst_ppltn_mins = []
                fcst_ppltn_maxs = []

                for idx, fcst_ppltn in enumerate(seoul_rtd.findall('FCST_PPLTN/FCST_PPLTN')):
                    fcst_times.append(fcst_ppltn.find('FCST_TIME').text)
                    fcst_congest_lvls.append(fcst_ppltn.find('FCST_CONGEST_LVL').text)
                    fcst_ppltn_mins.append(fcst_ppltn.find('FCST_PPLTN_MIN').text)
                    fcst_ppltn_maxs.append(fcst_ppltn.find('FCST_PPLTN_MAX').text)

                # 모든 데이터를 하나의 행으로 조합
                row = [
                    area_nm, area_cd, area_congest_lvl, area_congest_msg, area_ppltn_min, area_ppltn_max,
                    male_ppltn_rate, female_ppltn_rate, ppltn_rate_0, ppltn_rate_10, ppltn_rate_20, ppltn_rate_30,
                    ppltn_rate_40, ppltn_rate_50, ppltn_rate_60, ppltn_rate_70, resnt_ppltn_rate, non_resnt_ppltn_rate,
                    ppltn_time, replace_yn, fcst_yn
                ]

                # 예측 데이터가 있는 만큼 반복
                for i in range(10):  # 최대 10개의 예측 데이터
                    if i < len(fcst_times):
                        row.extend([
                            fcst_times[i],
                            fcst_congest_lvls[i],
                            fcst_ppltn_mins[i],
                            fcst_ppltn_maxs[i]
                        ])
                    else:
                        # 예측 데이터가 없는 경우 빈 값 추가
                        row.extend([''] * 4)

                data.append(row)

            except Exception as e:
                print(f"Error processing XML data: {e}")
                return []  # 데이터 처리 중 오류 발생 시 빈 리스트 반환
        return data

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return []  # 요청 오류 발생 시 빈 리스트 반환

def collect_data(search_term):
    """
    분류별 데이터 수집
    """
    try:
        # search_term을 사용하여 데이터 요청
        result = get_request_url(search_term)
        if result:
            print(f'{search_term} 데이터 수집 완료')
        else:
            print(f'{search_term}에 대한 데이터가 없습니다.')
            return []
    except Exception as e:
        print(f"Error during data collection for location {search_term}: {e}")
        return []

    columns = [
        'AREA_NM', 'AREA_CD', 'AREA_CONGEST_LVL', 'AREA_CONGEST_MSG', 'AREA_PPLTN_MIN', 'AREA_PPLTN_MAX',
        'MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE', 'PPLTN_RATE_0', 'PPLTN_RATE_10', 'PPLTN_RATE_20',
        'PPLTN_RATE_30',
        'PPLTN_RATE_40', 'PPLTN_RATE_50', 'PPLTN_RATE_60', 'PPLTN_RATE_70', 'RESNT_PPLTN_RATE',
        'NON_RESNT_PPLTN_RATE',
        'PPLTN_TIME', 'REPLACE_YN', 'FCST_YN'
    ]

    for i in range(10):
        columns.extend([
            f'FCST_TIME_{i + 1}',
            f'FCST_CONGEST_LVL_{i + 1}',
            f'FCST_PPLTN_MIN_{i + 1}',
            f'FCST_PPLTN_MAX_{i + 1}'
        ])

    df = pd.DataFrame(result, columns=columns)
    return df

import pandas as pd

@streamlit.cache_data
def collect_all_data():
    """
    특정 위치의 데이터 수집
    """
    locations = [
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

    all_data = []

    for location in locations:
        try:
            # 각 지역에 대해 데이터 요청
            result = get_request_url(location)
            if result:
                all_data.extend(result)  # 크롤링한 데이터가 있으면 리스트에 추가
            else:
                print(f'{location}에 대한 데이터가 없습니다.')
        except Exception as e:
            print(f"Error during data collection for location {location}: {e}")

    columns = [
        'AREA_NM', 'AREA_CD', 'AREA_CONGEST_LVL', 'AREA_CONGEST_MSG', 'AREA_PPLTN_MIN', 'AREA_PPLTN_MAX',
        'MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE', 'PPLTN_RATE_0', 'PPLTN_RATE_10', 'PPLTN_RATE_20',
        'PPLTN_RATE_30',
        'PPLTN_RATE_40', 'PPLTN_RATE_50', 'PPLTN_RATE_60', 'PPLTN_RATE_70', 'RESNT_PPLTN_RATE',
        'NON_RESNT_PPLTN_RATE',
        'PPLTN_TIME', 'REPLACE_YN', 'FCST_YN'
    ]

    for i in range(10):
        columns.extend([
            f'FCST_TIME_{i + 1}',
            f'FCST_CONGEST_LVL_{i + 1}',
            f'FCST_PPLTN_MIN_{i + 1}',
            f'FCST_PPLTN_MAX_{i + 1}'
        ])

    # 데이터프레임 생성
    df = pd.DataFrame(all_data, columns=columns)
    return df