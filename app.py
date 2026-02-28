import streamlit as st
import time

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Modern AI Chat", page_icon="💬", layout="centered")

# --- ส่วนของการตกแต่ง CSS (เพื่อให้ดู Modern ขึ้น) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 My Modern Assistant")
st.caption("ตัวอย่าง Chatbot จำลอง พัฒนาด้วย Python & Streamlit")

# --- ส่วนจัดการประวัติการแชท (Memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ! ผมคือบอทจำลอง มีอะไรให้ผมช่วยไหมครับ?"}
    ]

# แสดงข้อความทั้งหมดในประวัติการแชท
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ส่วนรับ Input และ Logic การตอบกลับ ---
if prompt := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    # 1. แสดงข้อความของ User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. จำลองการคิดของ Bot (Streaming Effect)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Logic จำลองการตอบคำถามแบบง่ายๆ
        if "สวัสดี" in prompt:
            assistant_response = "สวัสดีครับ ยินดีที่ได้รู้จัก! วันนี้อากาศดีนะว่าไหม?"
        elif "ทำอะไรได้บ้าง" in prompt:
            assistant_response = "ผมสามารถจำลองการแชท และช่วยแสดงโครงสร้างเว็บไซต์เบื้องต้นให้คุณดูได้ครับ"
        else:
            assistant_response = f"คุณพิมพ์ว่า: '{prompt}' ใช่ไหมครับ? เป็นคำถามที่น่าสนใจมาก!"

        # ทำ Effect ค่อยๆ พิมพ์ข้อความออกมา
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)

    # 3. บันทึกคำตอบของ Bot ลง Session
    st.session_state.messages.append({"role": "assistant", "content": full_response})
