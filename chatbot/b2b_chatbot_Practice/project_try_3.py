from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
import uuid
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.documents import Document

# Load env vars
load_dotenv()

# Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("shihab-chatbot")

# Embeddings + LLM
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)

# Vectorstore wrapper
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

# FastAPI app
app = FastAPI()

# Data model
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


# Add training data
@app.post("/train_data")
def add_training_data(data: TrainingModel):
    unique_id = str(uuid.uuid4())
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
    vectorstore.add_documents([doc], ids=[unique_id])
    return {"message": "Training data added successfully.", "id": unique_id}


# Edit training data
@app.put("/train_data/{edit_id}")
def edit_training_data(edit_id: str, data: TrainingModel):
    # Delete first to avoid duplicates
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

# Delete training data
@app.delete("/train_data/{delete_id}")
def delete_training_data(delete_id: str):
    try:
        vectorstore.delete(ids=[delete_id])
        return {"message": f"Document with id {delete_id} deleted successfully."}
    except Exception as e:
        return {"error": str(e)}


# Retrieval QA setup
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


# Query endpoint
class QueryModel(BaseModel):
    query: str

@app.post("/query")
def query_data(query: QueryModel):
    result = qa_chain.invoke(query.query)
    return {"answer": result["result"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("project_try_3:app", host="0.0.0.0", port=8001, reload=True)

