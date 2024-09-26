import streamlit as st
import speech_recognition as sr
import pyttsx3
from openai import OpenAI

# OpenAI API 설정
API_KEY = ""
ASSISTANT_ID = 'asst_Y8enHNm0M0f4I2va47IeSmdV'
THREAD_ID = 'thread_rA5W6O9mrKUixN4TnLn5D0JB'

client = OpenAI(api_key=API_KEY)


# Initialize session state for messages and input_text
def initialize_session_state():
    """
    챗봇 기본 문구 및 입력칸 생성
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "저는 이 페이지에 대해 안내하는 챗봇이에요. 무엇을 도와드릴까요?"}]
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    if "new_message" not in st.session_state:
        st.session_state.new_message = False


def recognize_speech():
    """
    음성 인식
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="ko-KR")
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError:
        return "음성 인식 서비스에 문제가 있습니다."


def speak(text):
    """
    TTS로 답변
    속도 및 소리 조절 가능
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust speaking rate if necessary
    engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
    engine.say(text)
    engine.runAndWait()

def get_ai_response(prompt):
    """
    미리 입력한 thread및 assistant로 답변
    """
    try:
        message = client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=prompt
        )
        # 결과를 받기 위해 실행
        run = client.beta.threads.runs.create_and_poll(
            thread_id=THREAD_ID,
            assistant_id=ASSISTANT_ID,
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=THREAD_ID)
            last_message = messages.data[0].content[0].text.value
            return last_message
        else:
            return "AI 응답에 실패했습니다."
    except Exception as e:
        return f"Error: {e}"

def chatbot_ui():
    """
    챗봇의 위치 고정
    """
    initialize_session_state()  # Ensure session state is initialized

    st.sidebar.markdown("""
        <style>
        .sidebar-chat-container {
            height: 300px;
            overflow-y: auto;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .sidebar-search-container {
            position: fixed;
            bottom: 50px;
            width: 100%;
            display: flex;
            gap: 10px;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 채팅 내역
    st.sidebar.write('<div class="sidebar-chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        st.sidebar.markdown(f"**{message['role']}**: {message['content']}")
    st.sidebar.write('</div>', unsafe_allow_html=True)

    # 음성인식 및 채팅 입력창
    with st.sidebar:
        if st.button("🎤", key="mic_button"):
            recognized_text = recognize_speech()
            if recognized_text:
                # 음성 인식 결과를 채팅 내역에 추가
                st.session_state.messages.append({"role": "user", "content": recognized_text})
                st.session_state.new_message = True
                st.session_state.input_text = recognized_text
                process_input(recognized_text)

        # 텍스트 입력창
        input_text = st.text_input("", value=st.session_state.input_text, key="input_text", placeholder="질문을 입력하세요",
                                   on_change=lambda: process_input(st.session_state.input_text))


def process_input(input_text):
    """
    챗봇의 행동
    """
    if input_text:
        # 사용자의 입력 추가
        st.session_state.messages.append({"role": "user", "content": input_text})

        # OpenAI API 호출하여 AI 답변 추가
        ai_response = get_ai_response(input_text)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # 페이지 새로고침
        st.session_state.new_message = True

        # 입력 후 텍스트 필드를 초기화
        st.session_state.input_text = ""

        # TTS 음성을 재생
        if st.session_state.new_message:
            speak(ai_response)
            st.session_state.new_message = False


if __name__ == "__main__":
    chatbot_ui()
