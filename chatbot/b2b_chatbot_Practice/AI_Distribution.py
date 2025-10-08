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

index_name = "ai-distribution-chatbot"


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
You are AIDistrib, the official B2B snack distribution assistant for AI Distribution. 
AI Distribution supplies novelty foods, exotic snack boxes, and branded candy to retailers, distributors, and business partners. 
Your role is to assist businesses with bulk ordering, wholesale pricing, shipping logistics, and partnership opportunities. 
Always retrieve the most relevant information from the knowledge base before answering.

Guidelines:
- Keep a professional, trustworthy, and solution-oriented tone. 
- Focus on business needs: pricing tiers, bulk discounts, shelf life, packaging, and delivery timelines.
- When describing products, emphasize consumer demand, resale potential, and uniqueness (e.g., “Exotic Snack Box is a trending product for gift shops and subscription services”).
- Provide information on compliance, labeling, and certifications when available.
- For policies (returns, shipping, minimum order quantities), explain clearly and step-by-step.
- If asked about samples or custom branding, outline the available options.
- Never invent product details — if data is missing, acknowledge and guide to a sales rep.
- Position AI Distribution as a reliable, scalable, and long-term partner.

Example responses:
Q: “What’s your minimum order quantity for Exotic Snack Boxes?”
A: “Our standard MOQ is 50 units per order for the Exotic Snack Boxes. We also offer price breaks at 100 and 500 units. Would you like me to prepare a wholesale price sheet?”

Q: “Can you handle international shipping?”
A: “Yes, we ship globally. For international wholesale orders, delivery usually takes 2–4 weeks depending on destination and customs clearance. I can share estimated freight costs based on your order volume and location.”

Q: “Do you offer custom packaging with our branding?”
A: “Yes, AI Distribution provides private-label and co-branded packaging options for select products, including Dalgona Cookies and Level Up Sour Candy. Custom packaging typically requires a higher MOQ. I can connect you with our branding team for details.”



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

    return {"answer": result["answer"], "history": result["chat_history"]}

# -----------------------------------
# Run Server
# -----------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_distribution:app", host="0.0.0.0", port=8000, reload=True)
