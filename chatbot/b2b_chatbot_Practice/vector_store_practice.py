import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


import streamlit as st
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
load_dotenv()
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os

# Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')
llm=ChatGoogleGenerativeAI(model='gemini-2.5-pro')

# Initialize Chroma vector store (persisted locally)
persist_directory = r"C:\Users\shbsh\OneDrive\Documents\Shihab_Work\Chatbot_for_b2b\my_chroma_db"
vectorstore = Chroma(collection_name="training_data", embedding_function=embeddings, persist_directory=persist_directory)

st.set_page_config(page_title="Training Data Form", layout="centered")
st.title("Add Training Data")

with st.form("training_form"):
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["", "Sales", "Support", "General"])
    with col2:
        context = st.selectbox("Context", ["", "E-commerce", "Retail", "Wholesale"])

    question = st.text_input("Question/Intent", placeholder="Enter customer question or intent...")
    ai_response = st.text_area("AI Response", placeholder="Enter the AI response...", height=100)
    keywords = st.text_input("Keywords (comma-separated)", placeholder="pricing, wholesale, bulk, discount...")

    submitted = st.form_submit_button("Add training data")

if submitted:
    if not question.strip() or not ai_response.strip():
        st.error("Please fill in both the question and AI response.")
    else:
        # Combine into one document
        content_text = f"Category: {category}\nContext: {context}\nQuestion: {question}\nAI Response: {ai_response}\nKeywords: {keywords}"

        # Add to vector store
        vectorstore.add_texts([content_text], metadatas=[{
            "category": category,
            "context": context,
            "question": question,
            "ai_response": ai_response,
            "keywords": keywords
        }])

        vectorstore.persist()

        st.success("✅ Data stored in vector store successfully!")
