import streamlit as st
from streamlit.components.v1 import html

# Streamlit 앱 설정
st.set_page_config(page_title="JavaScript to Streamlit", layout="wide")

# 자바스크립트와 Streamlit 간의 상호작용을 위한 HTML 및 JavaScript
def add_marker_click_script():
    """
    Streamlit과 Java스크립트 연결
    """
    js_code = """
    <script>
        function sendMessageToStreamlit(message) {
            window.parent.postMessage(message, '*');
        }

        document.addEventListener('DOMContentLoaded', function() {
            sendMessageToStreamlit({ type: 'test_message', content: 'Hello from JavaScript!' });
        });

        window.addEventListener('message', function(event) {
            if (event.data.type === 'test_message') {
                console.log('Received message from JavaScript:', event.data.content);
            }
        });
    </script>
    """
    return js_code

# HTML 코드와 자바스크립트 삽입
html_code = f"""
<html>
<head>
    <script>
        {add_marker_click_script()}
    </script>
</head>
<body>
    <h1>JavaScript to Streamlit Test</h1>
</body>
</html>
"""

html(html_code, height=500)

# Streamlit에서 메시지 수신 및 처리
def handle_messages():
    if 'message' in st.session_state:
        st.write(f"Received message: {st.session_state['message']}")

handle_messages()
