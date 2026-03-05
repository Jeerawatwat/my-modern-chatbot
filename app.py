import streamlit as st
import re
import os
import base64
import PyPDF2
import google.generativeai as genai

# --- 1. ส่วนการตกแต่ง (Styles - ย้ายจาก styles.py และ html.txt มาไว้ที่นี่) ---
def apply_custom_design():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* พื้นหลัง Nebula จากไฟล์ HTML ของคุณ */
    .stApp {
        background: radial-gradient(circle at bottom center, #121c30, #080c1c) !important;
        background-attachment: fixed !important;
        font-family: 'Sarabun', sans-serif !important;
        color: #f5faff;
    }

    /* ชื่อมหาวิทยาลัยแบบมีลูกเล่น Shine */
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

    /* ปรับแต่งปุ่มให้ดู Premium */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #06b6d4, #ec4899) !important;
        border: none !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนคำนวณ (Logic - ย้ายจาก logic.py มาไว้ที่นี่) ---
def get_room_info(prompt, lang):
    code = re.sub(r'\D', '', str(prompt))
    if len(code) >= 4:
        b, f = code[0:2], code[2]
        return f"📍 ตึก {b} ชั้น {f}" if lang == "TH" else f"📍 Building {b}, Floor {f}"
    return None

@st.cache_resource
def load_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") # ตั้งค่าใน Streamlit Cloud Secrets
    if not api_key: return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ส่วนการทำงานหลัก (App Interface) ---
def main():
    st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
    apply_custom_design()

    if "messages" not in st.session_state: st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="univ-name">Kasetsart University</div>', unsafe_allow_html=True)
        st.divider()
        if st.button("➕ แชทใหม่"): 
            st.session_state.messages = []
            st.rerun()

    # Chat Display
    st.markdown("### 🦖 พี่นนทรี AI Assistant")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input & Logic Connection
    if prompt := st.chat_input("ถามข้อมูลมหาลัยได้เลย..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.chat_message("assistant"):
            # เชื่อมต่อ Logic: เช็คห้องก่อน ถ้าไม่ใช่ค่อยถาม AI
            room = get_room_info(prompt, "TH")
            if room:
                response = room
            else:
                model = load_gemini()
                if model:
                    try:
                        res = model.generate_content(prompt)
                        response = res.text
                    except: response = "ขออภัยจ้า ระบบ AI ขัดข้องชั่วคราว"
                else:
                    response = "กรุณาติดตั้ง API Key ก่อนนะจ๊ะ"
            
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
