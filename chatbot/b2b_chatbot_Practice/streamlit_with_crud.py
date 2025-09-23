import asyncio
import sys
import uuid
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA

# Safe rerun function compatible with different Streamlit versions
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.warning("Streamlit rerun is not supported in this version. Please manually refresh the page.")

# Initialize embedding model and LLM
embeddings = GoogleGenerativeAIEmbeddings(model='gemini-embedding-001')
llm = ChatGoogleGenerativeAI(model='gemini-2.5-pro')

# Initialize Chroma vector store (persisted locally)
persist_directory = 'chroma db'
vectorstore = Chroma(collection_name="training_data", embedding_function=embeddings, persist_directory=persist_directory)

# Setup retrieval QA chain
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

st.set_page_config(page_title="Training Data Form + QA", layout="centered")
st.title("Add / Manage Training Data")

# Load edit state
if "edit_id" in st.session_state:
    is_edit = True
    edit_id = st.session_state["edit_id"]
    category = st.session_state.get("category", "")
    context = st.session_state.get("context", "")
    question = st.session_state.get("question", "")
    ai_response = st.session_state.get("ai_response", "")
    keywords = st.session_state.get("keywords", "")
else:
    is_edit = False
    edit_id = None
    category = ""
    context = ""
    question = ""
    ai_response = ""
    keywords = ""

with st.form("training_form"):
    category = st.selectbox(
        "Category",
        ["", "Sales", "Support", "General"],
        index=["", "Sales", "Support", "General"].index(category) if category else 0,
    )
    context = st.selectbox(
        "Context",
        ["", "E-commerce", "Retail", "Wholesale"],
        index=["", "E-commerce", "Retail", "Wholesale"].index(context) if context else 0,
    )
    question = st.text_input("Question/Intent", value=question, placeholder="Enter customer question or intent...")
    ai_response = st.text_area("AI Response", value=ai_response, placeholder="Enter the AI response...", height=100)
    keywords = st.text_input("Keywords (comma-separated)", value=keywords, placeholder="pricing, wholesale, bulk, discount...")

    submitted = st.form_submit_button("Save" if is_edit else "Add training data")

if submitted:
    if not question.strip() or not ai_response.strip():
        st.error("Please fill in both the question and AI response.")
    else:
        doc_id = edit_id if is_edit else str(uuid.uuid4())
        content_text = (
            f"ID: {doc_id}\nCategory: {category}\nContext: {context}\n"
            f"Question: {question}\nAI Response: {ai_response}\nKeywords: {keywords}"
        )

        # Fetch all existing data
        data = vectorstore._collection.get(include=["metadatas", "documents"])
        docs = data["documents"]
        metas = data["metadatas"]
        ids = data["ids"]

        # Filter out old doc if editing
        new_docs = []
        new_metas = []
        for i, m in enumerate(metas):
            current_id = m.get("id", ids[i])
            if not (is_edit and current_id == doc_id):
                new_docs.append(docs[i])
                new_metas.append(m)

        # Add new or updated doc
        new_docs.append(content_text)
        new_metas.append({
            "id": doc_id,
            "category": category,
            "context": context,
            "question": question,
            "ai_response": ai_response,
            "keywords": keywords
        })

        # Rebuild collection
        vectorstore._collection.delete(ids=ids)
        vectorstore._collection.add(documents=new_docs, metadatas=new_metas, ids=[m["id"] for m in new_metas])
        vectorstore.persist()

        # Clear edit state
        if is_edit:
            for key in ["edit_id", "category", "context", "question", "ai_response", "keywords"]:
                if key in st.session_state:
                    del st.session_state[key]

        st.success("✅ Data saved successfully!")
        safe_rerun()

# Display all training data with edit/delete options
st.markdown("---")
st.header("Manage Existing Training Data")

data = vectorstore._collection.get(include=["metadatas", "documents"])
docs = data["documents"]
metas = data["metadatas"]
ids = data["ids"]

for i, m in enumerate(metas):
    doc_id = m.get("id", ids[i])
    with st.expander(f"ID: {doc_id} - {m.get('question', 'No question')}"):
        st.write(f"**Category:** {m.get('category','')}")
        st.write(f"**Context:** {m.get('context','')}")
        st.write(f"**Question:** {m.get('question','')}")
        st.write(f"**AI Response:** {m.get('ai_response','')}")
        st.write(f"**Keywords:** {m.get('keywords','')}")

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Edit", key=f"edit_{doc_id}"):
                st.session_state["edit_id"] = doc_id
                st.session_state["category"] = m.get("category", "")
                st.session_state["context"] = m.get("context", "")
                st.session_state["question"] = m.get("question", "")
                st.session_state["ai_response"] = m.get("ai_response", "")
                st.session_state["keywords"] = m.get("keywords", "")
                safe_rerun()
        with col2:
            if st.button("Delete", key=f"delete_{doc_id}"):
                # Remove this doc and rebuild
                new_docs = []
                new_metas = []
                for j, meta in enumerate(metas):
                    if meta.get("id", ids[j]) != doc_id:
                        new_docs.append(docs[j])
                        new_metas.append(meta)

                vectorstore._collection.delete(ids=ids)
                if new_docs:  # only add if non-empty to avoid errors
                    vectorstore._collection.add(documents=new_docs, metadatas=new_metas, ids=[m["id"] for m in new_metas])
                vectorstore.persist()
                st.success(f"🗑️ Deleted ID: {doc_id}")
                safe_rerun()

# Sidebar QA interface
st.sidebar.header("Ask a Question")
user_query = st.sidebar.text_input("Enter your question here")

if st.sidebar.button("Get Answer") and user_query.strip():
    with st.spinner("Searching for the best answer..."):
        answer = qa_chain.run(user_query)
    st.sidebar.markdown("### Answer:")
    st.sidebar.write(answer)
