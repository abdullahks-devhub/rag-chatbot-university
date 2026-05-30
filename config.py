import os
from dotenv import load_dotenv

load_dotenv()

# HuggingFace
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
LLM_MODEL = "openai/gpt-oss-120b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # free, local, lightweight

# ChromaDB
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "university_notes"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 5

# Data directory
DATA_DIR = "./data"
