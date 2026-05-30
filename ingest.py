"""
ingest.py
Loads all PDFs → chunks them → embeds with sentence-transformers → stores in ChromaDB
Run this once (or whenever you add new notes):
    python ingest.py
"""

import os
import shutil
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from pdf_loader import load_all_pdfs
from config import (
    DATA_DIR, CHROMA_DIR, COLLECTION_NAME,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def chunk_documents(documents):
    """Split documents into overlapping chunks for better retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def build_vector_store(chunks):
    """Embed chunks and store in ChromaDB."""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    logger.info("Building ChromaDB vector store...")
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    vectorstore.add_documents(chunks)

    logger.info(f"✓ Vector store saved to {CHROMA_DIR}")
    logger.info(f"✓ Total vectors stored: {vectorstore._collection.count()}")
    return vectorstore


def main():
    # Check data directory
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.error(f"Created empty data directory at '{DATA_DIR}'. Please add your PDF notes there and re-run.")
        return

    # Determine which PDF files are already indexed
    existing_sources = set()
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    if os.path.exists(CHROMA_DIR):
        logger.info(f"Loading existing vector store at {CHROMA_DIR}...")
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=embeddings,
                collection_name=COLLECTION_NAME
            )
            # Retrieve all metadata from collection
            results = vectorstore.get(include=["metadatas"])
            if results and results.get("metadatas"):
                for m in results["metadatas"]:
                    if m and "source" in m:
                        existing_sources.add(os.path.basename(m["source"]))
            logger.info(f"Currently indexed files: {existing_sources}")
        except Exception as e:
            logger.warning(f"Could not read existing vector store: {e}. Rebuilding...")
            shutil.rmtree(CHROMA_DIR, ignore_errors=True)

    # Load PDFs
    logger.info("=" * 50)
    logger.info("STEP 1: Loading PDFs")
    logger.info("=" * 50)
    
    from pathlib import Path
    from pdf_loader import load_pdf
    
    pdf_files = list(Path(DATA_DIR).rglob("*.pdf"))
    new_pdfs = [p for p in pdf_files if p.name not in existing_sources]

    if not new_pdfs:
        logger.info("All PDF files in data/ are already indexed. Nothing to add.")
        return

    logger.info(f"Found {len(pdf_files)} PDF files in total. {len(new_pdfs)} are new and will be indexed.")

    documents = []
    for pdf_path in new_pdfs:
        try:
            docs = load_pdf(str(pdf_path))
            documents.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load {pdf_path.name}: {e}")

    if not documents:
        logger.error("No new documents loaded.")
        return

    # Chunk
    logger.info("=" * 50)
    logger.info("STEP 2: Chunking Documents")
    logger.info("=" * 50)
    chunks = chunk_documents(documents)

    # Embed + Store
    logger.info("=" * 50)
    logger.info("STEP 3: Embedding & Storing in ChromaDB")
    logger.info("=" * 50)
    build_vector_store(chunks)

    logger.info("=" * 50)
    logger.info("✓ Ingestion complete! You can now run the app.")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
