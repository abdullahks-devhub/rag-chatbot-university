---
title: UniMind - University RAG Study Assistant
emoji: 🎓
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.45.1"
app_file: app.py
pinned: false
---

# 🎓 UniMind — University RAG Study Assistant

A production-grade RAG (Retrieval-Augmented Generation) chatbot that answers questions from your university notes.

## Features
- 📄 Upload any PDF notes (text-based, scanned, mixed)
- 🔍 Semantic search with ChromaDB vector store
- 🧠 Powered by HuggingFace LLM (gpt-oss-120b)
- 💬 Conversational memory (remembers last 5 exchanges)
- 📚 Source citations for every answer

## Tech Stack
- **LangChain** — RAG orchestration
- **ChromaDB** — Local vector database
- **sentence-transformers** — Free local embeddings
- **HuggingFace Inference API** — LLM (free tier)
- **Streamlit** — Chat UI
- **FastAPI** — Backend API
- **pdfplumber + PyMuPDF + Tesseract** — Universal PDF parsing

## Setup (Local)
```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Add your HuggingFace token
echo "HUGGINGFACEHUB_API_TOKEN=your_token_here" > .env

# 3. Add your PDF notes to data/
mkdir data
# copy your PDFs into data/

# 4. Ingest notes
python ingest.py

# 5. Run the app
streamlit run app.py

# 6. (Optional) Run the API separately
uvicorn api:app --reload --port 8000
```

## HuggingFace Spaces Deployment
Set `HUGGINGFACEHUB_API_TOKEN` as a **Secret** in your Space settings.
