"""
api.py
FastAPI backend for the RAG system.
Endpoints:
  POST /ask        — ask a question
  POST /ingest     — trigger re-ingestion of notes
  GET  /health     — health check
  GET  /stats      — vector store stats
"""

import os
import logging
import subprocess
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from rag_chain import build_rag_chain, ask
from config import CHROMA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global chain instance
rag_chain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load RAG chain on startup."""
    global rag_chain
    if os.path.exists(CHROMA_DIR):
        logger.info("Loading RAG chain...")
        rag_chain = build_rag_chain()
        logger.info("RAG chain ready.")
    else:
        logger.warning("No vector store found. Run ingest.py first.")
    yield


app = FastAPI(
    title="University RAG API",
    description="Ask questions about your university notes",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {
        "status": "ok",
        "chain_loaded": rag_chain is not None,
        "vector_store_exists": os.path.exists(CHROMA_DIR)
    }


@app.get("/stats")
def stats():
    if not os.path.exists(CHROMA_DIR):
        return {"vectors": 0, "status": "No vector store found. Run ingest.py first."}
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from config import EMBEDDING_MODEL, COLLECTION_NAME
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings, collection_name=COLLECTION_NAME)
        return {"vectors": vs._collection.count(), "status": "ready"}
    except Exception as e:
        return {"vectors": 0, "status": str(e)}


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    global rag_chain
    if rag_chain is None:
        raise HTTPException(
            status_code=503,
            detail="RAG chain not loaded. Please run ingest.py first and restart the API."
        )
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = ask(rag_chain, request.question)
        return QuestionResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
def trigger_ingest():
    """Trigger re-ingestion of notes and reload the chain."""
    global rag_chain
    try:
        subprocess.run([sys.executable, "ingest.py"], check=True)
        rag_chain = build_rag_chain()
        return {"status": "Ingestion complete. Chain reloaded."}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
