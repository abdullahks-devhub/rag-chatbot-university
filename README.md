---
title: UniMind — University RAG Study Assistant
emoji: 🎓
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.45.1"
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
short_description: Ask questions about your university notes using AI.
---

# 🎓 UniMind — University RAG Study Assistant

A **Retrieval-Augmented Generation (RAG)** chatbot that answers questions from university lecture notes and PDFs.

## ✨ Features

- **RAG Pipeline** — retrieves relevant context from your documents before answering
- **Local Embeddings** — uses `sentence-transformers/all-MiniLM-L6-v2` (no API cost)
- **LLM via HuggingFace** — powered by `mistralai/Mistral-7B-Instruct-v0.2`
- **Conversation Memory** — remembers the last 5 exchanges in a session
- **Multi-format PDF support** — text-based and scanned PDFs (with OCR)

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| RAG Framework | LangChain |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers |
| LLM | Mistral-7B via HuggingFace Inference API |

## 🔑 Required Secrets

Set this in your HuggingFace Space → **Settings → Repository secrets**:

| Secret Name | Description |
|---|---|
| `HUGGINGFACEHUB_API_TOKEN` | Your HuggingFace API token (free at hf.co/settings/tokens) |

## 📁 Local Setup

```bash
git clone https://github.com/abdullahks-devhub/rag-chatbot-university.git
cd rag-chatbot-university
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Place your PDFs in the data/ folder, then:
python ingest.py

# Run the app:
streamlit run app.py
```
