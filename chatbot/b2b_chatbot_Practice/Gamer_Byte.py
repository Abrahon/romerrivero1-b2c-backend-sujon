from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated, Literal, List
import os
from dotenv import load_dotenv

# LangChain imports
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Pinecone client (gRPC)
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

# -----------------------------------
# Load environment variables
# -----------------------------------
load_dotenv()

# Initialize Pinecone (gRPC)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "gamer-byte-chatbot"


# Create index if not exists
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        vector_type="dense",
        dimension=1536,   # matches text-embedding-3-large
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        deletion_protection="disabled",
        tags={
            "environment": "development"
        }
    )

index = pc.Index(index_name)

# -----------------------------------
# Embeddings & LLM (OpenAI)
# -----------------------------------
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(temperature=0.5)

# -----------------------------------
# Custom Prompt
# -----------------------------------
prompt_template = """
You are ByteBot, the official snack assistant for Gamer Bytes — a B2C snack and novelty food retailer that sells gaming-themed treats, exotic snack boxes, and branded candy. 
Your job is to be both informative and fun, like a friendly gamer buddy who also knows everything about Gamer Bytes products, policies, and orders. 
Always use retrieved knowledge from the Gamer Bytes database before answering.

Guidelines:
- Keep the tone playful, upbeat, and snack/gamer-themed, while still being clear and professional.
- When describing products, highlight flavors, themes, and uniqueness (e.g., “Level Up Sour gummies pack a tangy punch that hits harder than a boss battle”).
- For curated boxes (like Exotic Snacks and Candy Box), emphasize the surprise, global taste experience, and gifting vibe.
- When customers ask about availability, prices, or shipping, be direct and accurate.
- For order tracking, returns, or policies, explain the steps simply and politely.
- Suggest related snacks when relevant (like pairing a sour candy with a crunchy chip box), but never be pushy.
- If context is missing or the answer is incomplete, acknowledge it and guide the customer toward customer support.
- Never invent product details — stick to retrieved knowledge only.
- Always sound like a mix of a helpful store rep and a gamer friend.

Example responses:
Q: “What comes in the Exotic Snacks and Candy Box?”
A: “The Exotic Snacks and Candy Box is a curated surprise pack with trending international treats. It could include anything from Rap Snacks chips to Korean gummy bears to Japanese soda candy. The fun is in the mystery — every box feels like opening loot in a game!”

Q: “Do you sell Dalgona cookies like in Squid Game?”
A: “Yes, we do! Our Dalgona Cookies come with the classic stamped shapes so you can take on the challenge yourself. Just… no consequences if you fail, promise 😉”

Q: “What’s your return policy?”
A: “We accept returns within 14 days for unopened products. If something arrives damaged or wrong, we’ll replace it at no cost. Want me to walk you through how to start a return?”


---

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


# -----------------------------------
# Vectorstore Retriever
# -----------------------------------
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# -----------------------------------
# FastAPI app
# -----------------------------------
app = FastAPI(title="B2B Chatbot")

# -----------------------------------
# CORS setup
# -----------------------------------
origins = [
    "http://localhost:3000",  # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# Pydantic Models
# -----------------------------------
class TrainingModel(BaseModel):
    category: Annotated[
        Literal["FAQ", "Product Information", "Service Details", "Company Policies", "Pricing Information"],
        Field(..., description="Category of the training data"),
    ]
    context: Annotated[
        Literal["B2B Only", "B2C Only", "Both Platforms"],
        Field(..., description="Context of the training data"),
    ]
    question: str = Field(..., description="Question of the training data")
    ai_response: str = Field(..., description="AI response of the training data")
    keywords: List[str] = Field(..., description="List of keywords")


class QueryModel(BaseModel):
    query: str

# -----------------------------------
# Training Data Endpoints
# -----------------------------------
@app.post("/train_data")
def add_training_data(data: TrainingModel, doc_id: str):
    """Add new training data into Pinecone"""
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
                "keywords": data.keywords,
            },
        )
        vectorstore.add_documents([doc], ids=[doc_id])
        return {"message": "Training data added successfully.", "id": doc_id}
    except Exception as e:
        return {"error": str(e)}


@app.get("/metadata/{doc_id}")
def get_metadata(doc_id: str):
    """Fetch metadata for a document by ID"""
    try:
        response = index.fetch(ids=[doc_id])

        if doc_id not in response.vectors:
            raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")

        return response.vectors[doc_id].metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/train_data/{edit_id}")
def edit_training_data(edit_id: str, data: TrainingModel):
    """Edit existing training data"""
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
                "keywords": data.keywords,
            },
        )
        vectorstore.add_documents([doc], ids=[edit_id])
        return {"message": f"Document with id {edit_id} updated successfully."}
    except Exception as e:
        return {"error": str(e)}


@app.delete("/train_data/{delete_id}")
def delete_training_data(delete_id: str):
    """Delete training data by ID"""
    try:
        vectorstore.delete(ids=[delete_id])
        return {"message": f"Document with id {delete_id} deleted successfully."}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# Chat Endpoint with Memory
# -----------------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
)

@app.post("/query")
def query_data(query: QueryModel):
    """Chat endpoint with conversational memory"""
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
    )

    result = qa_chain.invoke({"question": query.query})

    # Wrap the answer in a dict so Django can safely do .get("result")
    return {
        "answer": {"result": result["answer"]},  # ✅ changed here
        "history": result["chat_history"]
    }
# -----------------------------------
# Run Server
# -----------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gamer_byte:app", host="0.0.0.0", port=8000, reload=True)
