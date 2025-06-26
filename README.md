# 🤰 Pregnancy Risk Assistant – A Proactive RAG Chatbot for Maternal Risk Assessment

An intelligent AI assistant that proactively engages pregnant women, assesses their symptoms, and gives risk-based guidance using advanced language models and medical knowledge.

---

## Overview

Pregnancy is a sensitive and critical period where early identification of potential risks can save lives. The Pregnancy Risk Assistant is an AI-powered chatbot designed to support pregnant women by:

- Proactively asking key symptom-related questions
- Retrieving medically relevant information using RAG (Retrieval-Augmented Generation)
- Providing color-coded risk levels (Low, Medium, High) with suggested actions
- Maintaining a conversational, empathetic, and helpful tone

---
## Deployment

https://huggingface.co/spaces/Ejazaa/Risk_pregnancy_docker

---

## How the Chatbot Works – Step by Step

### 1. User Interaction Begins
- The chatbot automatically starts the conversation using Streamlit
- It asks 4 key health-related questions (bleeding, baby movement, headaches, other symptoms)
- Each question is asked one-by-one in a friendly and simple interface

### 2. Query Construction
- The user's responses are collected into a full query like:  
  "Assess pregnancy risk based on: I have slight bleeding; My baby is not moving today..."

### 3. Retrieval with LlamaIndex (RAG)
- LlamaIndex searches for relevant information from indexed documents:
  - risk_knowledge.txt
  - GraviLog_Pregnancy_Risk.pdf
  - PregnancyToDoChecklist.pdf
  - Pregnancy_Planner_508.pdf

### 4. Gemini Generates the Response
- The query and retrieved medical content are sent to Gemini 1.5 Flash
- The model responds with a detailed answer (e.g., concern for preeclampsia)

### 5. Risk Classification
- Custom logic detects keywords and categorizes the risk as:
  - Low
  - Medium
  - High
- Example:
  - "blurry vision", "swelling", and "no fetal movement" → High Risk

### 6. Output to User
- The app displays:
  - User's responses
  - Gemini's AI advice
  - Risk level with emojis and colors
  - A clear call-to-action

---
## 🗂 File Structure

```
├── app.py                  # Streamlit UI
├── backend.py              # RAG + Gemini logic + DB
├── requirements.txt        # All dependencies
├── .env                    # Gemini API key
├── risk_knowledge.txt      # Core knowledge file
├── data/                   # Folder containing source PDFs
├── chroma_store/           # Auto-generated vector index
├── chat_history.db         # Saved chats (runtime)
└── README.md               # This documentation
```

---
## Tech Stack

| Layer         | Tool/Library                        |
|---------------|-------------------------------------|
| LLM           | Gemini 1.5 Flash (google.generativeai) |
| RAG           | LlamaIndex + ChromaDB               |
| Embeddings    | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store  | Chroma (persistent local store)     |
| Frontend      | Streamlit                           |
| DB Storage    | SQLite (for chat logs)              |
| Hosting       | Hugging Face Spaces / Render        |

---
---

## 🧪 Sample Query and Output

**User Responses:**
- I have unusual discharge.
- My baby hasn’t moved much today.
- I’ve had a strong headache and blurred vision.

**AI Output:**
> The symptoms you’ve described — vaginal discharge, decreased fetal movement, and blurry vision — raise concern for a high-risk condition such as **preeclampsia or fetal distress**. Immediate evaluation by an obstetrician is recommended.

**Risk Level:** 🚨 High  
**Suggested Action:** Visit ER or OB emergency department immediately.

---

## Knowledge Sources Used

- risk_knowledge.txt (custom textual knowledge base)
- GraviLog_Pregnancy_Risk.pdf (medical reference)
- PregnancyToDoChecklist.pdf (self-care checklist)
- Pregnancy_Planner_508.pdf (planning guide)

---

## How to Run This Chatbot Locally

If you'd like to test or improve this project on your own machine, follow these step-by-step instructions:

### 1. Clone the GitHub Repository

```bash
https://github.com/ejazuddin55/pregnancy-risk-chatbot.git
cd pregnancy-risk-chatbot
```

Or download the ZIP file from GitHub and extract it.

---

### 2. Install Python Libraries

Make sure Python 3.8+ is installed. Then run:

```bash
pip install -r requirements.txt
```

---

### 3. Add Your Gemini API Key

Create a .env file in the project folder:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

You can get a free Gemini API key from: https://makersuite.google.com/app/apikey

---

### 4. Prepare the Knowledge Files

Ensure the following files are in place:

```
├── risk_knowledge.txt
├── data/
    ├── GraviLog_Pregnancy_Risk.pdf
    ├── PregnancyToDoChecklist.pdf
    ├── Pregnancy_Planner_508.pdf
```

---

### 5. Run the Streamlit App

Start the chatbot with:

```bash
streamlit run app.py
```

Visit `http://localhost:8501` to use the assistant.

---

### 6. Chat History & Reset

- All chats are saved in chat_history.db
- You can reset the app using the "Start Over" button

To force rebuild the index, delete the chroma_store/ folder.

---

## Developed By

Ejaz ud din  
Email: ejazuddin870@yahoo.com  
