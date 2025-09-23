from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_chroma import Chroma
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, Literal
import uuid
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Embeddings + LLM
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)

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
    keywords: str = Field(..., description="Keywords of the training data")


# Vectorstore creation
vectorstore = Chroma(
    collection_name="training_data",
    embedding_function=embeddings,
    persist_directory=r"C:\Users\shbsh\OneDrive\Documents\Shihab_Work\Chatbot_for_b2b\my_chroma_db"
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)


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
    vectorstore.add_texts(
        [content_text],
        metadatas=[{
            "category": data.category,
            "context": data.context,
            "question": data.question,
            "ai_response": data.ai_response,
            "keywords": data.keywords
        }],
        ids=[unique_id]
    )
    vectorstore.persist()
    return {"message": "Training data added successfully.", "id": unique_id}


@app.put("/train_data/{edit_id}")
def edit_training_data(edit_id: str, data: TrainingModel):
    existing_docs = vectorstore.get(ids=[edit_id])
    if not existing_docs["documents"]:
        return {"error": f"No document found with id {edit_id}"}

    content_text = (
        f"Category: {data.category}\n"
        f"Context: {data.context}\n"
        f"Question: {data.question}\n"
        f"AI Response: {data.ai_response}\n"
        f"Keywords: {data.keywords}"
    )

    # Now you can re-add with same ID (it overwrites in Chroma)
    vectorstore.add_texts(
        [content_text],
        metadatas=[{
            "category": data.category,
            "context": data.context,
            "question": data.question,
            "ai_response": data.ai_response,
            "keywords": data.keywords
        }],
        ids=[edit_id]
    )

    vectorstore.persist()

    return {"message": f"Document with id {edit_id} updated successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("project_try_1:app", host="0.0.0.0", port=8000, reload=True)
