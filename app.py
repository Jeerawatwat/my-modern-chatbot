import streamlit as st
import re
import os
import base64
import PyPDF2
import google.generativeai as genai

# ==========================================
# 1. ส่วนการตกแต่ง (Styles & HTML Customization)
# ==========================================
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* พื้นหลัง Nebula + Glassmorphism จากไฟล์ HTML ของคุณ */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #fdfdfd 0%, #e8f0eb 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* Sidebar ตกแต่งแบบ iOS Style */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(25px) saturate(150%);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* ชื่อมหาวิทยาลัยพร้อมเอฟเฟกต์ Shine และ Float */
    .univ-name {
        background: linear-gradient(90deg, #006633, #b5a01e, #006633);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        animation: shineText 3s linear infinite, float 4s ease-in-out infinite;
        padding: 10px 0;
    }

    @keyframes shineText { to { background-position: 200% center; } }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

    /* ปุ่มกด (Buttons) - ลูกเล่นจัดเต็มแบบ Neo-Brutalism */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        border-radius: 18px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.03) !important;
        background: linear-gradient(135deg, #006633 0%, #004d26 100%) !important;
        color: #E2C792 !important;
        box-shadow: 0 15px 30px rgba(0, 102, 51, 0.2) !important;
    }

    /* กล่องแชท (Chat Bubbles) */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ส่วนคำนวณและข้อมูล (Logic & Data)
# ==========================================

translation = {
    "TH": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ เริ่มบทสนทนาใหม่",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ดาวน์โหลดแบบฟอร์ม",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต!",
        "ai_identity": "พี่นนทรี AI รุ่นพี่ มก.ศรช. ยินดีที่ได้พบคุณครับ",
        "loading": "พี่นนทธีกำลังหาข้อมูลให้นะจ๊ะ...",
        "not_found": "ข้อมูลส่วนนี้พี่ยังไม่มีในระบบ รบกวนน้องตรวจสอบที่เว็บ reg.src.ku.ac.th อีกทีนะจ๊ะ"
    },
    "EN": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ New Conversation",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Student Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello Student!",
        "ai_identity": "I'm Nontri AI, your friendly KU Sriracha senior buddy.",
        "loading": "Nontri is thinking...",
        "not_found": "I don't have this info yet. Please check reg.src.ku.ac.th"
    }
}

def get_room_info(room_code, lang):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        b, f, r = code[:2], code[2], code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {b} ชั้น {f} ห้อง {r}** ครับน้อง" if lang == "TH" else f"Building {b}, Floor {f}, Room {r}."
    elif len(code) == 4:
        b, f, r = code[0], code[1], code[2:]
        return f"ห้องนี้คือ **ตึก {b} ชั้น {f} ห้อง {r}** ครับผม" if lang == "TH" else f"Building {b}, Floor {f}, Room {r}."
    return None

@st.cache_resource
def load_model():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except: return None

def get_knowledge_base():
    combined_text = ""
    # อ่านไฟล์ TXT
    if os.path.exists("ku_data.txt"):
        with open("ku_data.txt", "r", encoding="utf-8") as f: txt_data = f.read()
        combined_text += txt_data
    
    # อ่านไฟล์ PDF ในโฟลเดอร์ knowledge_pool
    directory = "knowledge_pool"
    if not os.path.exists(directory): os.makedirs(directory)
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    for filename in pdf_files:
        try:
            with open(os.path.join(directory, filename), "rb") as f:
                pdf = PyPDF2.PdfReader(f)
                combined_text += f"\n\n--- ข้อมูลจากไฟล์: {filename} ---\n"
                for page in pdf.pages:
                    combined_text += page.extract_text() + "\n"
        except: pass
    return combined_text

# ==========================================
# 3. ส่วนหน้าแอปหลัก (Main App Interface)
# ==========================================

def main():
    st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
    apply_custom_css()

    if "lang" not in st.session_state: st.session_state.lang = "TH"
    if "messages" not in st.session_state: st.session_state.messages = []
    
    curr = translation[st.session_state.lang]
    model = load_model()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(f'<div class="univ-name">{curr["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; color:#666; font-size:11px; margin-top:-10px; letter-spacing:2px;">{curr["campus"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🌐 {st.session_state.lang}"):
            st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
            st.rerun()

        st.divider()
        if st.button(curr["new_chat"]):
            st.session_state.messages = []
            st.rerun()

        st.markdown(f"#### 🎓 บริการนิสิต")
        st.button(curr["exam_table"])
        st.button(curr["gpa_calc"])
        st.button(curr["forms"])

    # --- Chat Interface ---
    st.markdown(f"<h2 style='color: #006633;'><span style='font-size:40px;'>🦖</span> AI KUSRC</h2>", unsafe_allow_html=True)

    # แสดงประวัติการแชท
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
            st.markdown(message["content"])

    # ส่วนรับคำถาม
    if prompt := st.chat_input(curr["input_placeholder"]):
        st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🦖"):
            # 1. เช็คเลขห้องก่อน
            room_info = get_room_info(prompt, st.session_state.lang)
            if room_info:
                full_response = room_info
                st.markdown(full_response)
            else:
                # 2. ถ้าไม่ใช่เรื่องห้อง ให้ถาม AI Gemini
                placeholder = st.empty()
                placeholder.markdown(curr["loading"])
                
                if model:
                    kb = get_knowledge_base()
                    full_context = f"คุณคือ {curr['ai_identity']} จงตอบคำถามโดยใช้ข้อมูลนี้: {kb}\nคำถาม: {prompt}"
                    try:
                        response = model.generate_content(full_context)
                        full_response = response.text
                        placeholder.markdown(full_response)
                    except:
                        full_response = curr["not_found"]
                        placeholder.markdown(full_response)
                else:
                    full_response = "กรุณาตั้งค่า GEMINI_API_KEY ใน Secrets ก่อนนะจ๊ะ"
                    placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
