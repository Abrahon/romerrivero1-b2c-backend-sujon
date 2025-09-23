from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
import uuid
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain.memory import LangGraphMemory
from langchain.vectorstores import Pinecone



# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("shihab-chatbot")

# Embeddings and LLM
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)

# Human-like B2B chatbot prompt
prompt_template = """
You are an AI support agent for a B2B chatbot.
Speak naturally, in a human-like and professional tone, as if you are chatting directly with the user.
Use the following context to answer the question clearly and accurately.
"

Context:
{context}

Question:
{question}

Answer:
"""

custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)

# Vectorstore wrapper
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# FastAPI app
app = FastAPI(title="B2B Chatbot with Session Memory")

# -----------------------------
# CORS setup
# -----------------------------
origins = [
    "http://localhost:3000",  # your frontend
    # Add production frontend domains here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Session-specific memories
session_memories = {}  # session_id -> ConversationBufferMemory

# -----------------------------
# Pydantic models
# -----------------------------
class TrainingModel(BaseModel):
    category: Annotated[
        Literal["FAQ", "Product Information", "Service Details", "Company Policies", "Pricing Information"],
        Field(..., description="Category of the training data")
    ]
    context: Annotated[
        Literal["B2B Only", "B2C Only", "Both Platforms"],
        Field(..., description="Context of the training data")
    ]
    question: str = Field(..., description="Question of the training data")
    ai_response: str = Field(..., description="AI response of the training data")
    keywords: List[str] = Field(..., description="List of keywords")

class QueryModel(BaseModel):
    session_id: str
    query: str

# -----------------------------
# Training data endpoints
# -----------------------------
@app.post("/train_data")
def add_training_data(data: TrainingModel, doc_id: str):
    try:
        content_text = (
            f"Category: {data.category}\n"
            f"Context: {data.context}\n"
            f"Question: {data.question}\n"
            f"AI Response: {data.ai_response}\n"
            f"Keywords: {data.keywords}"
        )
        doc = Document(
            page_content=content_text,
            metadata={
                "category": data.category,
                "context": data.context,
                "question": data.question,
                "ai_response": data.ai_response,
                "keywords": data.keywords
            }
        )
        vectorstore.add_documents([doc], ids=[doc_id])
        return {"message": "Training data added successfully.", "id": doc_id}
    except Exception as e:
        return {"error": str(e)}
    

@app.get("/metadata/{doc_id}")
def get_metadata(doc_id: str):
    try:
        response = index.fetch(ids=[doc_id])

        if doc_id not in response.vectors:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")

        # Return only the metadata
        return response.vectors[doc_id].metadata

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/train_data/{edit_id}")
def edit_training_data(edit_id: str, data: TrainingModel):
    try:
        vectorstore.delete(ids=[edit_id])
        content_text = (
            f"Category: {data.category}\n"
            f"Context: {data.context}\n"
            f"Question: {data.question}\n"
            f"AI Response: {data.ai_response}\n"
            f"Keywords: {data.keywords}"
        )
        doc = Document(
            page_content=content_text,
            metadata={
                "category": data.category,
                "context": data.context,
                "question": data.question,
                "ai_response": data.ai_response,
                "keywords": data.keywords
            }
        )
        vectorstore.add_documents([doc], ids=[edit_id])
        return {"message": f"Document with id {edit_id} updated successfully."}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/train_data/{delete_id}")
def delete_training_data(delete_id: str):
    try:
        vectorstore.delete(ids=[delete_id])
        return {"message": f"Document with id {delete_id} deleted successfully."}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Chat endpoints
# -----------------------------
@app.post("/query")
def query_data(query: QueryModel):
    # Get or create session memory
    if query.session_id not in session_memories:
        session_memories[query.session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    memory = session_memories[query.session_id]

    # Build session-specific QA chain
    qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": custom_prompt},
    return_source_documents=False
)


    result = qa_chain.invoke({"question": query.query})

    return {
        "answer": result["answer"],
        "chat_history": [
            {"role": msg.type, "content": msg.content}
            for msg in memory.chat_memory.messages
        ],
    }

@app.get("/memory/{session_id}")
def get_memory(session_id: str):
    if session_id not in session_memories:
        raise HTTPException(status_code=404, detail="Session not found")
    memory = session_memories[session_id]
    return {
        "chat_history": [
            {"role": msg.type, "content": msg.content}
            for msg in memory.chat_memory.messages
        ]
    }

@app.delete("/memory/{session_id}")
def reset_memory(session_id: str):
    if session_id in session_memories:
        session_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        return {"message": f"Memory for session {session_id} has been reset."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# -----------------------------
# Run the server
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("final_project_till_8-20-25 copy:app", host="0.0.0.0", port=8000, reload=True)
