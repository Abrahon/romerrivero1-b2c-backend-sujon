from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List, TypedDict
import os
from dotenv import load_dotenv

# LangChain & Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

# -----------------------------
# Load env & init LLM / vectorstore
# -----------------------------
load_dotenv()

# Pinecone setup
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("shihab-chatbot")

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Prompt template
prompt_template = """
You are an AI support agent for a B2B chatbot.
Speak naturally, in a human-like and professional tone, as if you are chatting directly with the user.

Context:
{context}

Question:
{question}

Answer:
"""
custom_prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="B2B Chatbot with LangGraph Memory")

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# LangGraph memory setup
# -----------------------------
# Define state schema first
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Chat node function
def chat_node(state: ChatState):
    user_message = state["messages"][-1].content
    chat_history = [
        (msg.type, msg.content) for msg in state["messages"][:-1]
    ]

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
        return_source_documents=False,
    )

    result = qa_chain.invoke({
        "question": user_message,
        "chat_history": chat_history
    })

    response_message = BaseMessage(type="ai", content=result["answer"])
    return {"messages": [response_message]}

# In-memory checkpointer
checkpointer = InMemorySaver()

# Build LangGraph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot_graph = graph.compile(checkpointer=checkpointer)

# -----------------------------
# Pydantic models for training/chat
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
    thread_id: str  # used for user/thread memory
    query: str

# -----------------------------
# Training endpoints
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

@app.get("/metadata/{doc_id}")
def get_metadata(doc_id: str):
    try:
        response = index.fetch(ids=[doc_id])
        if doc_id not in response.vectors:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")
        return response.vectors[doc_id].metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Chat endpoint with thread-specific LangGraph memory
# -----------------------------
@app.post("/query")
def query_data(query: QueryModel):
    result = chatbot_graph.invoke(
        {"messages": [{"role": "user", "content": query.query}]},
        {"configurable": {"thread_id": query.thread_id}}
    )
    return {"answer": result["messages"][0].content}

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("final_project_till_8-20-25_copy_3:app", host="0.0.0.0", port=8000, reload=True)
