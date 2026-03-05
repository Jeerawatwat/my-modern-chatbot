import streamlit as st
import base64
import os

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="KU SRC AI Assistant", page_icon="🌳", layout="wide")

def apply_full_custom_css():
    st.markdown("""
    <style>
    /* นำเข้า Fonts ตามแบบในไฟล์โค้ดเพิ่มเติม */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* พื้นหลังแบบ Dynamic Gradient & Glassmorphism */
    .stApp {
        background: radial-gradient(circle at top right, #fdfdfd 0%, #e8f5e9 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* Sidebar ตกแต่งแบบ iOS Control Center */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(25px) saturate(180%);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* หัวข้อภาษาอังกฤษ (Fredoka) และลูกเล่นแสงเงา */
    .univ-title {
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #006633, #b5a01e, #006633);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        margin-bottom: 0px;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* ปุ่มกดจัดเต็ม (Neo-Brutalism Style) */
    div.stButton > button {
        background: white !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        border-radius: 20px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        position: relative;
        overflow: hidden;
    }

    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        background: #006633 !important;
        color: #E2C792 !important; /* เปลี่ยนตัวอักษรเป็นสีทอง */
        box-shadow: 0 15px 30px rgba(0, 102, 51, 0.2) !important;
    }

    /* กล่องแชทแบบ Floating Card */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
    }

    /* ปรับแต่ง Input Bar */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 1.5px solid rgba(0, 102, 51, 0.1) !important;
        box-shadow: 0 -10px 25px rgba(0,0,0,0.02) !important;
    }

    /* ซ่อน Streamlit Elements ที่ไม่จำเป็น */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & TRANSLATIONS ---
translation = {
    "TH": {
        "univ": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ เริ่มแชทใหม่",
        "tools": "🛠 เครื่องมือนิสิต",
        "exam": "📅 ตารางสอบ",
        "gpa": "🧮 คำนวณเกรด",
        "forms": "📄 แบบฟอร์ม",
        "placeholder": "คุยกับพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต! มีอะไรให้พี่ช่วยไหมครับ?"
    },
    "EN": {
        "univ": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ New Conversation",
        "tools": "🛠 Student Tools",
        "exam": "📅 Exam Schedule",
        "gpa": "🧮 GPA Calculator",
        "forms": "📄 Student Forms",
        "placeholder": "Talk to Nontri...",
        "welcome": "Hello Student! How can I assist you today?"
    }
}

# --- 3. MAIN APP ---
def main():
    apply_full_custom_css()
    
    # เริ่มต้น Session State สำหรับภาษา
    if 'lang' not in st.session_state:
        st.session_state.lang = "TH"
    
    t = translation[st.session_state.lang]

    # --- Sidebar ---
    with st.sidebar:
        # ส่วนหัว (Logo & Title)
        st.markdown(f'<div class="univ-title">{t["univ"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; color:#666; font-size:12px; letter-spacing:2px; margin-bottom:20px;">{t["campus"]}</div>', unsafe_allow_html=True)
        
        # ปุ่มเลือกภาษาแบบสวยงาม
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇹🇭 TH"): st.session_state.lang = "TH"; st.rerun()
        with col2:
            if st.button("🇺🇸 EN"): st.session_state.lang = "EN"; st.rerun()
        
        st.markdown("---")
        
        # Quick Action Buttons
        st.button(t["new_chat"])
        st.markdown(f"#### {t['tools']}")
        st.button(t["exam"])
        st.button(t["gpa"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU SRC Smart Assistant v2.5")

    # --- Chat Interface ---
    # แสดงหัวข้อแอปในหน้าหลัก
    st.markdown(f'<h2 style="color:#006633; font-family:Fredoka;">P\'Nontri AI Buddy</h2>', unsafe_allow_html=True)
    
    # ตัวอย่างข้อความต้อนรับ
    with st.chat_message("assistant", avatar="🌳"):
        st.markdown(f"**{t['welcome']}**")

    # ส่วนรับ Input
    st.chat_input(t["placeholder"])

if __name__ == "__main__":
    main()
