import streamlit as st
import pandas as pd
from PIL import Image
import os
import csv                               
from datetime import datetime             

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

# 1. Web basic configuration
st.set_page_config(page_title="Time Capsule Decoder", page_icon="📜", layout="wide")

# --- Added: Custom CSS for Iframe Embedding ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {
                background-color: #F4F1EA; 
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# ----------------------------------------------

# 2. Load the data
CSV_PATH = "demo_cards_final.csv"
IMG_DIR = "Demo_Images"

if not os.path.exists(CSV_PATH):
    st.error(f"Can't find {CSV_PATH}")
    st.stop()

df = pd.read_csv(CSV_PATH)

st.sidebar.markdown("### Filter Postcards")
available_langs = ["All"] + list(df['Language'].dropna().unique())
selected_lang = st.sidebar.selectbox("Select Language", available_langs)

if selected_lang != "All":
    df = df[df['Language'] == selected_lang].reset_index(drop=True)

# 3. Initialize the game 
if 'card_index' not in st.session_state:
    st.session_state.card_index = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.title(" Decode the Past: Can You Read This?")
st.markdown(f"### Help us decode the **Belgian Digital Heritage**")

if st.session_state.card_index >= len(df):
    st.success(" You have completed all postcards for this language! Awesome job!")
    st.stop()

st.progress((st.session_state.card_index + 1) / len(df))

current_card = df.iloc[st.session_state.card_index]
mms_id = str(current_card['MMS_ID'])

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader(" Historical Postcard (Verso)")
    img_path = os.path.join(IMG_DIR, f"{mms_id}_back.jpg")
    if os.path.exists(img_path):
        image = Image.open(img_path)
        st.image(image, use_container_width=True)
    else:
        st.error(f"Image not found: {img_path}")

with col2:
    st.subheader(" AI's Failed Attempt")
    st.info(f"**AI Confidence:** {current_card['AI_Confidence'] * 100:.1f}%")
    st.code(current_card['AI_Detected_Text'], language="text")
    
    st.divider()
    
    st.subheader(" Your Transcription")
    user_input = st.text_area("Can you read what's actually written?", placeholder="Type your transcription here...")
    
    if st.button("Submit & Contribute"):
        if user_input:
            lang = current_card.get('Language', 'Unknown') if 'Language' in current_card else 'Unknown'
            save_transcription(mms_id, lang, user_input)
            st.balloons()
            st.success(" Incredible! You've just saved a piece of history.")
            st.session_state.submitted = True
        else:
            st.warning("Please try to type at least one word!")

    if st.session_state.submitted:
        if st.button("Next Challenge "):
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
        
    st.sidebar.info(f" {latest_text}")
    
else:
    st.sidebar.metric(label="Total Contributions", value=0)
    st.sidebar.write("Waiting for the first hero to contribute...")

st.sidebar.markdown("---")
st.sidebar.caption(" All data is securely mapped via MMS_ID for future DB merging.")