import streamlit as st
import pandas as pd
from PIL import Image
import os
import csv
from datetime import datetime
import time

# 1. Web basic configuration
st.set_page_config(page_title="Time Capsule Decoder", page_icon="📜", layout="wide")

# --- Added: Save user's data---
def save_transcription(mms_id, language, user_text):
    file_name = "user_transcriptions.csv"
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "MMS_ID", "Language", "User_Input"])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, mms_id, language, user_text])

# --- Added: Custom CSS for Museum Label Typography & Animation ---
custom_css = """
<style>
    /* 引入顶级复古字体，同时强制引入 Google Material 图标库抢救系统图标 */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

    /* 1. 全局字体：精准施加，放过带有 material-symbols 类的图标元素 */
    html, body, p, div:not([class*="material-symbols"]), span:not([class*="material-symbols"]), label {
        font-family: 'Playfair Display', serif !important;
        color: #2C241F !important; 
    }

    /* 🔥 2. 强力保护：让所有图标恢复魔法，不再显示乱码文本 🔥 */
    .material-symbols-rounded, 
    span[class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', sans-serif !important;
        font-feature-settings: 'liga' !important; /* 关键：让纯文本变成图标 */
        -webkit-font-feature-settings: 'liga' !important;
    }

    /* 3. 精准隐藏左下角 Admin Access 折叠框的展开箭头 */
    [data-testid="stExpander"] details summary span[class*="material-symbols"] {
        display: none !important;
    }
    
    [data-testid="stExpander"] details summary::-webkit-details-marker {
        display: none !important;
    }

    /* --- 以下是标题和排版的复古美化 --- */
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 600 !important; 
        color: #382A24 !important; 
        letter-spacing: 1.5px !important; 
        font-size: 3.2rem !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05); 
    }

    h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 600 !important;
        color: #4A3A31 !important; 
        letter-spacing: 0.8px !important;
    }

    h1 em, h2 em, h3 em {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-weight: 400 !important;
        color: #6D5A4F !important; 
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.8rem !important; 
        letter-spacing: 0px !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 0px !important;
        border-bottom: 1px solid #D6CFC4; 
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
        font-size: 0.95rem !important; 
    }

    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important; 
        color: #4A3A31 !important;
        font-family: 'Cormorant Garamond', serif !important;
    }

    [data-testid="stSidebar"] [data-testid="stInfo"] {
        background-color: #EBE6DF !important;
        border: 1px dashed #C2B8AA !important; 
        color: #382A24 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stInfo"] svg {
        display: none; 
    }

    [data-testid="stSidebar"] small {
        font-size: 0.8rem !important;
        color: #8C7A6B !important;
    }

    [data-testid="stExpander"] details summary {
        font-family: 'Playfair Display', serif !important;
        color: #8C7A6B !important; 
        font-size: 0.9rem !important;
        list-style-type: none; 
    }

    /* 隐藏默认菜单，动画等 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @keyframes fadeAndSlideIn {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    .stApp {
        background-color: #F4F1EA; 
        animation: fadeAndSlideIn 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ----------------------------------------------

# 2. Load the data
CSV_PATH = "demo_cards_final.csv"
IMG_DIR = "Demo_Images"

if not os.path.exists(CSV_PATH):
    st.error(f"Can't find {CSV_PATH}. Please make sure the file exists.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# 3. Initialize the game session states
if 'card_index' not in st.session_state:
    st.session_state.card_index = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_lang' not in st.session_state:
    st.session_state.current_lang = "All"

st.title("Decode the Past: Can You Read This?")
st.markdown("### *Help us decode the Belgian Digital Heritage*")

# --- Language Filter Logic ---
available_langs = ["All"] + list(df['Language'].dropna().unique())
selected_lang = st.selectbox("Filter Postcards by Language:", available_langs)

if selected_lang != st.session_state.current_lang:
    st.session_state.current_lang = selected_lang
    st.session_state.card_index = 0
    st.session_state.submitted = False
    st.rerun()

if selected_lang != "All":
    df = df[df['Language'] == selected_lang].reset_index(drop=True)
# =================================================

if st.session_state.card_index >= len(df):
    st.success("You have completed all postcards for this language! Awesome job!")
    st.stop()

st.progress((st.session_state.card_index + 1) / len(df))

current_card = df.iloc[st.session_state.card_index]
mms_id = str(current_card['MMS_ID'])

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("Historical Postcard (Verso)")
    img_path = os.path.join(IMG_DIR, f"{mms_id}_back.jpg")
    if os.path.exists(img_path):
        image = Image.open(img_path)
        st.image(image, use_container_width=True)
    else:
        st.error(f"Image not found: {img_path}")

with col2:
    st.subheader("AI's Failed Attempt")
    # --- (Stopwords Filter) ---
    raw_ai_text = str(current_card['AI_Detected_Text'])
    print_words = ["CARTE", "POSTALE", "POSTKAART", "Correspondance", "Briefwisseling", "Adresse", "Adres", "Union", "universelle"]
    
    segments = [s.strip() for s in raw_ai_text.split('|')]
    cleaned_segments = [s for s in segments if not any(pw.lower() in s.lower().replace(" ", "") for pw in print_words)]
    
    final_text = " | ".join(cleaned_segments)
    if not final_text:
        final_text = "[Only printed boilerplate detected by AI]"
        
    st.code(final_text, language="text")
    # ----------------------------------------
    
    st.divider()
    
    st.subheader("Your Transcription")
    user_input = st.text_area("Can you read what's actually written?", placeholder="Type your transcription here...")
    
    if st.button("Submit & Contribute"):
        if user_input:
            lang = current_card.get('Language', 'Unknown') if 'Language' in current_card else 'Unknown'
            
            with st.spinner("Connecting to database & fine-tuning models..."):
                time.sleep(1.5) 
                save_transcription(mms_id, lang, user_input)
            
            st.balloons()
            st.success("Incredible! You've just saved a piece of history.")
            st.session_state.submitted = True
        else:
            st.warning("Please try to type at least one word!")

    if st.session_state.submitted:
        if st.button("Next Challenge"):
            st.session_state.card_index += 1
            st.session_state.submitted = False 
            st.rerun()  

# 4. Sidebar: Live Stats
st.sidebar.title("🏆 Live Leaderboard")
st.sidebar.markdown("---")

if os.path.isfile("user_transcriptions.csv"):
    user_df = pd.read_csv("user_transcriptions.csv")
    total_contributions = len(user_df)
    
    st.sidebar.metric(label="Total Contributions", value=total_contributions, delta="Live Update")
    st.sidebar.markdown("**Latest Decoded Text:**")

    latest_text = str(user_df.iloc[-1]['User_Input'])
    if len(latest_text) > 40:
        latest_text = latest_text[:40] + "..."
        
    st.sidebar.info(f"{latest_text}")
else:
    st.sidebar.metric(label="Total Contributions", value=0)
    st.sidebar.write("Waiting for the first hero to contribute...")

st.sidebar.markdown("---")
st.sidebar.caption("All data is securely mapped via MMS_ID for future DB merging.")

# ==========================================
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Admin Access"):
    admin_password = st.text_input("Enter Admin Password:", type="password")

    if admin_password == "KULeuven2026":
        st.success("Access Granted!")
        if os.path.isfile("user_transcriptions.csv"):
            with open("user_transcriptions.csv", "rb") as f:
                st.download_button(
                    label="📥 Download Data",
                    data=f,
                    file_name=f"postscript_data_{datetime.now().strftime('%m%d_%H%M')}.csv",
                    mime="text/csv",
                    type="primary" 
                )
        else:
            st.warning("No data available yet.")
    elif admin_password != "":
        st.error("Incorrect Password.")