import streamlit as st
from backend import ask_bot, assess_risk

# Set page configuration
st.set_page_config(
    page_title="Pregnancy Risk Assistant 🤰",
    page_icon="🤰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling and emoji enhancement
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

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.current_question = 0
    st.session_state.responses_collected = False
    st.session_state.analyzing = False

# Symptom prompts from document (page 6)
symptom_prompts = [
    "🩺 Are you currently experiencing any unusual bleeding or discharge?",
    "👶 How would you describe your baby's movements today compared to yesterday?",
    "😷 Have you had any headaches that won't go away or that affect your vision?",
    "🤒 Are you experiencing any other symptoms? (If yes, please describe briefly)"

]

# Header and welcome message
st.markdown('<div class="main-title">🤰 Pregnancy Risk Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="welcome-text">💚 I’m here to help you and your baby stay safe!👼 Please answer the following questions about your symptoms. Type your answer and Click submit response or Press Ctrl+Enter to submit your Response 👩‍🍼.</div>', unsafe_allow_html=True)

# Progress indicator
st.progress(st.session_state.current_question / len(symptom_prompts))

# Ask symptom questions using a form
if st.session_state.current_question < len(symptom_prompts):
    st.markdown(f'<div class="question-box">{symptom_prompts[st.session_state.current_question]}</div>', unsafe_allow_html=True)
    with st.form(key=f"input_form_{st.session_state.current_question}", clear_on_submit=True):
        user_input = st.text_area(
            "Your response:",
            key=f"input_{st.session_state.current_question}",
            height=100,
            placeholder="Type your answer Like 'I have some bleeding' or 'My baby is moving less than usual'"
        )
        submit = st.form_submit_button("Submit Response ")
        
        if submit and user_input.strip():
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.current_question += 1
            if st.session_state.current_question == len(symptom_prompts):
                st.session_state.analyzing = True
            st.rerun()
        elif submit and not user_input.strip():
            st.warning("⚠️ Please provide a response before submitting.")

# Process responses with analyzing indicator
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
            st.error(f"❌ An error occurred: {str(e)}. Please try again or check the backend.")
            st.session_state.analyzing = False
        st.rerun()

# Display results
if st.session_state.responses_collected:
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.write(f"📝 **Your Responses**:")
    for _, response in st.session_state.chat_history:
        st.write(f"- {response}")
    st.write(f"💁‍♀️ **AI Agent Response**: {st.session_state.answer}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display risk level with color coding and emojis
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

    # Reset button
    if st.button("🔄 Start Over", key="reset", help="Restart the questionnaire"):
        st.session_state.chat_history = []
        st.session_state.current_question = 0
        st.session_state.responses_collected = False
        st.session_state.analyzing = False
        st.rerun()

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 2em; color: #4A4A4A;'>
        Created by Ejaz ud din 🌟 | ejazuddin870@yahoo.com
    </div>
""", unsafe_allow_html=True)



























