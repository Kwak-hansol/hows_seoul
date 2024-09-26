import requests
import xml.etree.ElementTree as ET
import streamlit as st

# 지하철 호선 ID와 이름 매핑
SUBWAY_LINE_MAPPING = {
    '1001': '1호선',
    '1002': '2호선',
    '1003': '3호선',
    '1004': '4호선',
    '1005': '5호선',
    '1006': '6호선',
    '1007': '7호선',
    '1008': '8호선',
    '1009': '9호선',
    '1061': '중앙선',
    '1063': '경의중앙선',
    '1065': '공항철도',
    '1067': '경춘선',
    '1075': '수의분당선',
    '1077': '신분당선',
    '1092': '우이신설선',
    '1093': '서해선',
    '1081': '경강선',
    '1032': 'GTX-A'
}

def get_request_url(location='서울'):
    """
    지하철 데이터 URL
    """
    base_url1 = 'http://swopenAPI.seoul.go.kr/api/subway'
    access_key = '58427970596c6f65353957704f5644'
    type = 'xml'
    base_url2 = 'realtimeStationArrival'
    start_row = 0
    end_row = 5

    # 완성된 URL
    url = f'{base_url1}/{access_key}/{type}/{base_url2}/{start_row}/{end_row}/{location}'
    return url

def fetch_subway_data(location='서울'):
    """
    지하철 데이터 추출
    """
    url = get_request_url(location)
    response = requests.get(url)
    if response.status_code == 200:
        return response.content  # XML 데이터를 반환
    else:
        return None


def parse_subway_data(xml_data):
    """
    지하철의 정보 데이터화
    """
    root = ET.fromstring(xml_data)
    subway_info = []

    for row in root.findall('.//row'):
        subway_id = row.find('subwayId').text
        train_line_nm = SUBWAY_LINE_MAPPING.get(subway_id, '알 수 없음')  # ID를 이름으로 변환
        station_name = row.find('statnNm').text
        arrival_message = row.find('arvlMsg2').text
        train_status = row.find('btrainSttus').text
        reception_time = row.find('recptnDt').text
        bstatn_nm = row.find('bstatnNm').text

        subway_info.append({
            "subway_id": subway_id,
            "train_line_nm": train_line_nm,
            "station_name": station_name,
            "arrival_message": arrival_message,
            "train_status": train_status,
            "reception_time": reception_time,
            "bstatn_nm": bstatn_nm
        })

    return subway_info

def search_subway_info(subway_info, search_query):
    """
    검색어를 기반으로 지하철 정보 필터링
    """
    search_query = search_query.lower()
    filtered_info = [info for info in subway_info if search_query in info["station_name"].lower()]
    return filtered_info


def dict_to_table(data_list, table_title=""):
    """
    딕셔너리 형식의 데이터를 테이블화

    Args:
        data_list (list of dict): 출력할 딕셔너리 리스트.
        table_title (str): 테이블의 제목. (옵션)
    """
    # 스타일과 테이블 구조 정의
    html = """
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
    """

    # 테이블 제목 추가
    if table_title:
        html += f"<h3>{table_title}</h3>"

    # 테이블 헤더 생성
    html += "<table class='custom-table'><thead><tr>"
    # 컬럼 이름을 한글로 변경
    column_headers = ['호선', '도착정보', '유형', '종착역']
    for header in column_headers:
        html += f"<th>{header}</th>"
    html += "</tr></thead><tbody>"

    # 테이블 데이터 생성
    for data in data_list:
        html += "<tr>"
        # 각 컬럼의 데이터만 추출
        html += f"<td>{data.get('train_line_nm')}</td>"
        html += f"<td>{data.get('arrival_message')}</td>"
        html += f"<td>{data.get('train_status')}</td>"
        html += f"<td>{data.get('bstatn_nm')}</td>"
        html += "</tr>"

    html += "</tbody></table>"

    # Streamlit에서 HTML로 렌더링
    st.markdown(html, unsafe_allow_html=True)