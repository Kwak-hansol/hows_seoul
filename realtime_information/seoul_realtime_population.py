import cx_Oracle
import requests
import pandas as pd
import time
from xml.etree.ElementTree import fromstring

access_key = '74694d524a6c6f653637674a65474f'


def get_request_url(no):
    """
    실시간 인구 및 예측 인구 데이터를 수집
    """
    base_url1 = 'http://openapi.seoul.go.kr:8088'
    type = 'xml'
    base_url2 = 'citydata_ppltn'
    start_row = 1
    end_row = 5
    location = select_from_oracle(no)

    url = f'{base_url1}/{access_key}/{type}/{base_url2}/{start_row}/{end_row}/{location[0]}'
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


def select_from_oracle(no):
    """
    오라클에 적재된 데이터베이스 추출
    """
    try:
        conn = cx_Oracle.connect('open_source/1111@192.168.0.22:1521/xe')
        cur = conn.cursor()

        sql_select = '''
        select AREA_NM, CATEGORY
        from seoul_location
        where no = :no
        '''

        cur.execute(sql_select, [no])
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result

    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None  # 데이터베이스 오류 발생 시 None 반환


def main():
    """
    인구 데이터 표시
    """
    while True:
        data = []
        print('최신 데이터 수집을 시작합니다.')
        for i in range(1, 116):  # 여기서 no 범위를 정의합니다.
            try:
                result = get_request_url(i)
                if result:
                    data.extend(result)  # 크롤링한 데이터가 있으면 리스트에 추가
                print(f'{i}번째 데이터 수집 완료')
            except Exception as e:
                print(f"Error during data collection for index {i}: {e}")
                continue  # 예외 발생 시 다음 인덱스 진행

        # 데이터프레임 생성
        if data:
            columns = [
                'AREA_NM', 'AREA_CD', 'AREA_CONGEST_LVL', 'AREA_CONGEST_MSG', 'AREA_PPLTN_MIN', 'AREA_PPLTN_MAX',
                'MALE_PPLTN_RATE', 'FEMALE_PPLTN_RATE', 'PPLTN_RATE_0', 'PPLTN_RATE_10', 'PPLTN_RATE_20',
                'PPLTN_RATE_30',
                'PPLTN_RATE_40', 'PPLTN_RATE_50', 'PPLTN_RATE_60', 'PPLTN_RATE_70', 'RESNT_PPLTN_RATE',
                'NON_RESNT_PPLTN_RATE',
                'PPLTN_TIME', 'REPLACE_YN', 'FCST_YN'
            ]

            # 예측 데이터 컬럼 추가 (최대 10개 예측)
            for i in range(10):
                columns.extend([
                    f'FCST_TIME_{i + 1}',
                    f'FCST_CONGEST_LVL_{i + 1}',
                    f'FCST_PPLTN_MIN_{i + 1}',
                    f'FCST_PPLTN_MAX_{i + 1}'
                ])

            df = pd.DataFrame(data, columns=columns)
            df.to_excel('data.xlsx')
            print(df)

        print('현재시간: ', time.strftime("%Y-%m-%d %H:%M:%S"))
        print('데이터 수집 완료 후 5분 대기')
        time.sleep(300)  # 5분 대기