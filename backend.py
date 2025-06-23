import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Chroma persistent directory
PERSIST_DIR = os.path.join(os.getcwd(), "chroma_store")

# Chat history DB setup (runs once)
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

# Save chat to SQLite
def save_chat_to_db(user_question, bot_response, risk_level, action):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat (user_question, bot_response, risk_level, action)
        VALUES (?, ?, ?, ?)
    ''', (user_question, bot_response, risk_level, action))
    conn.commit()
    conn.close()

# Load documents
def load_documents():
    docs = SimpleDirectoryReader(input_files=["risk_knowledge.txt"]).load_data()
    docs += SimpleDirectoryReader(input_dir="data").load_data()
    return docs

# Build or load index
def build_or_load_index():
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if not os.path.exists(PERSIST_DIR):
        print("📚 Building Chroma index and saving it...")
        documents = load_documents()
        chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
        chroma_collection = chroma_client.get_or_create_collection("pregnancy_risk")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print("✅ Loading Chroma index...")
        chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
        chroma_collection = chroma_client.get_or_create_collection("pregnancy_risk")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, storage_context=storage_context
        )

    return index

# Assess risk level
# Assess risk level (updated from assignment PDF)
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



# Ask bot (single-question)
def ask_bot(query):
    index = build_or_load_index()
    retriever = index.as_retriever()
    nodes = retriever.retrieve(query)

    context = "\n\n".join([n.get_content() for n in nodes])
    prompt = f"""You are a helpful assistant for pregnancy-related risks.

Context:
{context}

Question: {query}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    risk_level, action = assess_risk(response.text)

    save_chat_to_db(query, response.text, risk_level, action)  # ✅ Save to DB

    return response.text, risk_level, action

import nltk
import os

# Set writable path
nltk_data_path = "/mount/temp/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Download punkt manually
nltk.download("punkt", download_dir=nltk_data_path)



# Run test
if __name__ == "__main__":
    init_db()  # ✅ Initialize DB on first run
    question = "I have bleeding. Should I go to a hospital?"
    answer, risk_level, action = ask_bot(question)
    print("🤖 Bot:", answer)
    print(f"Risk Level: {risk_level}")
    print(f"Suggested Action: {action}")
