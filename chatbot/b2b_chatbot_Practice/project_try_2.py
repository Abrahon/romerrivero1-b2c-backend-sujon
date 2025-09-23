import os
import json
from typing import List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import numpy as np
import faiss # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# -------------------------
# CONFIG
# -------------------------
load_dotenv()

# LLM & Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.5)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# DB
DATABASE_URL = "sqlite:///./vectordb.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Embedding dims for Gemini "models/embedding-001"
EMBED_DIM = 768  

# -------------------------
# DB MODEL + SCHEMAS
# -------------------------
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    embedding = Column(String)  # JSON array

Base.metadata.create_all(bind=engine)

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemOut(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True

# -------------------------
# APP + DEP
# -------------------------
app = FastAPI(title="FastAPI + SQLite + FAISS + Gemini Embeddings")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# FAISS INDEX MANAGEMENT
# -------------------------
_faiss_index: Optional[faiss.Index] = None
_id_map: List[int] = []  

def build_faiss_index_from_db(db: Session):
    global _faiss_index, _id_map
    items = db.query(Item).filter(Item.embedding != None).all()
    if len(items) == 0:
        _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
        _id_map = []
        return

    mats = []
    ids = []
    for it in items:
        emb = np.array(json.loads(it.embedding), dtype="float32")
        norm = np.linalg.norm(emb)
        if norm != 0:
            emb = emb / norm
        mats.append(emb)
        ids.append(it.id)

    mat = np.vstack(mats).astype("float32")
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(mat)
    _faiss_index = index
    _id_map = ids

def ensure_index(db: Session):
    global _faiss_index
    if _faiss_index is None:
        build_faiss_index_from_db(db)

# -------------------------
# EMBEDDING UTIL
# -------------------------
def get_embedding(text: str) -> List[float]:
    """Get Gemini embedding as a list of floats."""
    return embeddings.embed_query(text)

def normalize_vector(vec: np.ndarray) -> np.ndarray:
    vec = vec.astype("float32")
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec / norm
    return vec

# -------------------------
# CRUD + VECTOR SYNCH
# -------------------------
@app.post("/items/", response_model=ItemOut)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    text = f"{payload.name}\n{payload.description}"
    emb = np.array(get_embedding(text), dtype="float32")
    db_item = Item(name=payload.name, description=payload.description, embedding=json.dumps(emb.tolist()))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    build_faiss_index_from_db(db)
    return db_item

@app.get("/items/", response_model=List[ItemOut])
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.name is not None:
        db_item.name = payload.name
    if payload.description is not None:
        db_item.description = payload.description
    text = f"{db_item.name}\n{db_item.description}"
    emb = np.array(get_embedding(text), dtype="float32")
    db_item.embedding = json.dumps(emb.tolist())
    db.commit()
    db.refresh(db_item)
    build_faiss_index_from_db(db)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    build_faiss_index_from_db(db)
    return {"message": "Item deleted"}

# -------------------------
# SEMANTIC SEARCH
# -------------------------
@app.get("/search/", response_model=List[ItemOut])
def semantic_search(query: str = Query(..., min_length=1), k: int = Query(3, ge=1), db: Session = Depends(get_db)):
    ensure_index(db)
    if _faiss_index is None or _faiss_index.ntotal == 0:
        return []

    q_emb = np.array(get_embedding(query), dtype="float32")
    q_emb = normalize_vector(q_emb).reshape(1, -1)

    D, I = _faiss_index.search(q_emb, k)
    positions = I[0].tolist()
    found_ids = [ _id_map[pos] for pos in positions if pos >= 0 ]

    if not found_ids:
        return []

    items = db.query(Item).filter(Item.id.in_(found_ids)).all()
    id_to_item = {it.id: it for it in items}
    return [id_to_item[iid] for iid in found_ids if iid in id_to_item]

# -------------------------
# BOOTSTRAP
# -------------------------
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        build_faiss_index_from_db(db)
        print("FAISS index built. items:", len(_id_map))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
