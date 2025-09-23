from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
import uuid
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Load env vars
load_dotenv()

# Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("shihab-chatbot")

# Embeddings + LLM
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)

prompt_template = """
You are an AI support agent for a B2B chatbot.
Speak naturally, in a human-like and professional tone, as if you are chatting directly with the user.
Use the following context to answer the question clearly and accurately.

If the answer is not found or is unclear based on the context, do not attempt to guess.
Instead, respond politely by saying: 
"We’re connecting you with our support team for further assistance."

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

# Add training data (client must provide ID)
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



# Edit training data
@app.put("/train_data/{edit_id}")
def edit_training_data(edit_id: str, data: TrainingModel):
    try:
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
    except Exception as e:
        return {"error": str(e)}


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
from langchain.chains import RetrievalQA

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": custom_prompt}
)



class QueryModel(BaseModel):
    session_id: str
    query: str


@app.post("/query")
def query_data(query: QueryModel):
    result = qa_chain.invoke({"question": query.query})
    return {"answer": result["answer"]}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("final_project_till_8-20-25:app", host="0.0.0.0", port=8000, reload=True)

