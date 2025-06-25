# app.py - Complete Pregnancy Risk Assistant (Frontend + Backend)

import streamlit as st
import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# ==================== BACKEND FUNCTIONS ====================
# Initialize environment
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Database setup
def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT,
            bot_response TEXT,
            risk_level TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_chat_to_db(user_question, bot_response, risk_level, action):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat (user_question, bot_response, risk_level, action)
        VALUES (?, ?, ?, ?)
    ''', (user_question, bot_response, risk_level, action))
    conn.commit()
    conn.close()

def assess_risk(response_text):
    response_text = response_text.lower()

    high_risk_phrases = [
        "blurry vision", "severe swelling", "heavy vaginal bleeding", "cramping",
        "severe abdominal pain", "ectopic pregnancy", "fever > 38.5", "fever with chills",
        "intrauterine infection", "no fetal movement", "reduced fetal movement",
        "fetal distress", "preeclampsia"
    ]

    medium_risk_phrases = [
        "spotting", "mild vaginal bleeding", "persistent vomiting", "vomiting > 3x",
        "elevated blood pressure", "blood pressure ≥140/90",
        "gestational diabetes", "excessive thirst", "frequent urination"
    ]

    if any(phrase in response_text for phrase in high_risk_phrases):
        return "High", "Visit ER or OB immediately"
    elif any(phrase in response_text for phrase in medium_risk_phrases):
        return "Medium", "Contact doctor within 24 hours"
    else:
        return "Low", "Self-monitor, routine prenatal follow-up"

def ask_bot(query):
    try:
        prompt = f"""You are a helpful assistant for pregnancy-related risks.
        
        Please assess the following situation and provide advice:
        {query}
        
        Consider these risk factors:
        - Bleeding or discharge
        - Baby movements
        - Headaches/vision changes
        - Other symptoms
        
        Provide:
        1. Recommended action
        2. Clear explanation
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        risk_level, action = assess_risk(response.text)
        
        save_chat_to_db(query, response.text, risk_level, action)
        return response.text, risk_level, action
    except Exception as e:
        st.error(f"Error in ask_bot: {str(e)}")
        return f"An error occurred: {str(e)}", "Unknown", "Please try again later"

# ==================== FRONTEND UI ====================
# Set page configuration (EXACTLY AS IN YOUR ORIGINAL)
st.set_page_config(
    page_title="Pregnancy Risk Assistant 🤰",
    page_icon="🤰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS (EXACTLY AS IN YOUR ORIGINAL)
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .welcome-text {
        font-size: 1.2em;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 1.5em;
    }
    .question-box {
        background-color: #F1F8E9;
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
        font-weight: bold;
        color: #1B5E20;
    }
    .response-box {
        background-color: #E3F2FD;
        padding: 1em;
        border-radius: 10px;
        margin-top: 1em;
    }
    .risk-low {
        background-color: #C8E6C9;
        padding: 1em;
        border-radius: 10px;
        color: #2E7D32;
        font-weight: bold;
    }
    .risk-medium {
        background-color: #FFF9C4;
        padding: 1em;
        border-radius: 10px;
        color: #F57C00;
        font-weight: bold;
    }
    .risk-high {
        background-color: #FFCDD2;
        padding: 1em;
        border-radius: 10px;
        color: #B71C1C;
        font-weight: bold;
    }
    .reset-button {
        display: flex;
        justify-content: center;
        margin-top: 1.5em;
    }
    .emoji {
        font-size: 1.5em;
        vertical-align: middle;
        margin-right: 0.2em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state (EXACTLY AS IN YOUR ORIGINAL)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.current_question = 0
    st.session_state.responses_collected = False
    st.session_state.analyzing = False
    init_db()  # Initialize database

# Symptom prompts (EXACTLY AS IN YOUR ORIGINAL)
symptom_prompts = [
    "🩺 Are you currently experiencing any unusual bleeding or discharge?",
    "👶 How would you describe your baby's movements today compared to yesterday?",
    "😷 Have you had any headaches that won't go away or that affect your vision?",
    "🤒 Are you experiencing any other symptoms? (If yes, please describe briefly)"
]

# Header and welcome message (EXACTLY AS IN YOUR ORIGINAL)
st.markdown('<div class="main-title">🤰 Pregnancy Risk Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="welcome-text">💚 I\'m here to help you and your baby stay safe!👼 Please answer the following questions about your symptoms. Type your answer and Click submit response or Press Ctrl+Enter to submit your Response 👩‍🍼.</div>', unsafe_allow_html=True)

# Progress indicator (EXACTLY AS IN YOUR ORIGINAL)
st.progress(st.session_state.current_question / len(symptom_prompts))

# Question flow (EXACTLY AS IN YOUR ORIGINAL)
if st.session_state.current_question < len(symptom_prompts):
    st.markdown(f'<div class="question-box">{symptom_prompts[st.session_state.current_question]}</div>', unsafe_allow_html=True)
    with st.form(key=f"input_form_{st.session_state.current_question}", clear_on_submit=True):
        user_input = st.text_area(
            "Your response:",
            key=f"input_{st.session_state.current_question}",
            height=100,
            placeholder="Type your answer Like 'I have some bleeding' or 'My baby is moving less than usual'"
        )
        submit = st.form_submit_button("Submit Response")
        
        if submit and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.current_question += 1
            if st.session_state.current_question == len(symptom_prompts):
                st.session_state.analyzing = True
            st.rerun()
        elif submit and not user_input.strip():
            st.warning("⚠️ Please provide a response before submitting.")

# Analysis and results (EXACTLY AS IN YOUR ORIGINAL)
if st.session_state.current_question == len(symptom_prompts) and not st.session_state.responses_collected:
    with st.spinner("💁‍♀️ AI analyzing your responses..."):
        query = "Assess pregnancy risk based on: " + "; ".join([msg for _, msg in st.session_state.chat_history])
        try:
            answer, risk_level, action = ask_bot(query)
            st.session_state.responses_collected = True
            st.session_state.analyzing = False
            st.session_state.answer = answer
            st.session_state.risk_level = risk_level
            st.session_state.action = action
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}. Please try again.")
            st.session_state.analyzing = False
        st.rerun()

# Display results (EXACTLY AS IN YOUR ORIGINAL)
if st.session_state.responses_collected:
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.write(f"📝 **Your Responses**:")
    for _, response in st.session_state.chat_history:
        st.write(f"- {response}")
    st.write(f"💁‍♀️ **AI Agent Response**: {st.session_state.answer}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display risk level (EXACTLY AS IN YOUR ORIGINAL)
    risk_class = {
        "Low": "risk-low",
        "Medium": "risk-medium",
        "High": "risk-high"
    }.get(st.session_state.risk_level, "risk-low")
    risk_emoji = {
        "Low": "✅",
        "Medium": "⚠️",
        "High": "🚨"
    }.get(st.session_state.risk_level, "✅")
    st.markdown(f'<div class="{risk_class}">{risk_emoji} Risk Level: {st.session_state.risk_level}<br>Suggested Action: {st.session_state.action}</div>', unsafe_allow_html=True)

    # Reset button (EXACTLY AS IN YOUR ORIGINAL)
    if st.button("🔄 Start Over", key="reset", help="Restart the questionnaire"):
        st.session_state.chat_history = []
        st.session_state.current_question = 0
        st.session_state.responses_collected = False
        st.session_state.analyzing = False
        st.rerun()

# Footer (EXACTLY AS IN YOUR ORIGINAL)
st.markdown("""
    <div style='text-align: center; margin-top: 2em; color: #4A4A4A;'>
        Created by Ejaz ud din 🌟 | ejazuddin870@yahoo.com
    </div>
""", unsafe_allow_html=True)
