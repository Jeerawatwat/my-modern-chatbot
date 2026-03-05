import streamlit as st
import re
import os
import base64
import PyPDF2
import google.generativeai as genai

# --- [ส่วนที่ 1: การตกแต่ง - ดึงมาจาก HTML.txt และ Styles] ---
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* พื้นหลัง Nebula & Glassmorphism จาก HTML ของคุณ */
    .stApp {
        background: radial-gradient(circle at bottom center, #121c30, #080c1c) !important;
        background-attachment: fixed !important;
        color: #f5faff;
    }

    /* ตกแต่ง Sidebar แบบโปร่งแสง */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ตัวหนังสือชื่อมหาลัยแบบเรืองแสง (Shine Effect) */
    .univ-name {
        background: linear-gradient(90deg, #00ffcc, #f472b6, #00ffcc);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        animation: shine 3s linear infinite;
    }
    @keyframes shine { to { background-position: 200% center; } }

    /* ตกแต่งกล่องแชท */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [ส่วนที่ 2: ระบบประมวลผล - ดึงมาจาก Logic] ---
def get_room_info(room_code, lang):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) >= 4:
        b, f = code[0:2], code[2]
        return f"📍 ห้องนี้อยู่ **ตึก {b} ชั้น {f}** ครับ" if lang == "TH" else f"📍 Located at **Building {b}, Floor {f}**."
    return None

@st.cache_resource
def load_model():
    # ใส่ API Key ของคุณตรงนี้ หรือใช้ st.secrets
    api_key = st.secrets.get("GEMINI_API_KEY") 
    if not api_key: return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# --- [ส่วนที่ 3: หน้าจอหลักและการทำงาน] ---
def main():
    st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
    apply_custom_css()

    # ตั้งค่าตัวแปรเริ่มต้น
    if "messages" not in st.session_state: st.session_state.messages = []
    if "lang" not in st.session_state: st.session_state.lang = "TH"

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="univ-name">Kasetsart University</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; color:#8291aa; font-size:10px;">SRIRACHA CAMPUS</div>', unsafe_allow_html=True)
        st.divider()
        if st.button("🔄 ล้างแชท (Clear)"): st.session_state.messages = []
        
    # แสดงแชท
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # รับคำถาม
    if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            # เช็คเรื่องห้องก่อน
            room = get_room_info(prompt, st.session_state.lang)
            if room:
                response = room
            else:
                response = "พี่นนทรีได้รับข้อความแล้วครับ กำลังประมวลผล..." # ส่วนนี้เชื่อม AI ต่อได้
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
