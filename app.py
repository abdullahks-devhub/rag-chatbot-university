"""
app.py
Streamlit chat UI for the University RAG system.
This is the main entry point for HuggingFace Spaces deployment.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UniMind — Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

* { font-family: 'IBM Plex Sans', sans-serif; }
code, pre { font-family: 'IBM Plex Mono', monospace; }

/* Background */
.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e3a;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #111120;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    margin: 8px 0;
    padding: 4px;
}

/* User message */
[data-testid="stChatMessage"][data-testid*="user"] {
    border-color: #3d3d8a;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #111120 !important;
    border: 1px solid #2a2a5a !important;
    color: #e8e8f0 !important;
    border-radius: 12px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #5555cc !important;
    box-shadow: 0 0 0 2px rgba(85,85,204,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: #1e1e3a;
    color: #a0a0e0;
    border: 1px solid #2a2a5a;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #2a2a5a;
    border-color: #5555cc;
    color: #e8e8f0;
}

/* Source pills */
.source-pill {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 11px;
    color: #7070b0;
    margin: 2px 4px 2px 0;
    font-family: 'IBM Plex Mono', monospace;
}

/* Header */
.rag-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.rag-title {
    font-size: 2.8rem;
    font-weight: 600;
    background: linear-gradient(135deg, #7070e0 0%, #a070f0 50%, #7090ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.rag-subtitle {
    color: #5050a0;
    font-size: 0.95rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 0.3rem;
}

/* Status badge */
.status-ready {
    display: inline-block;
    background: #0a2a0a;
    border: 1px solid #1a4a1a;
    color: #50c050;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
}
.status-not-ready {
    display: inline-block;
    background: #2a0a0a;
    border: 1px solid #4a1a1a;
    color: #c05050;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
}

/* Metric cards */
.metric-card {
    background: #111120;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: #7070e0;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-label {
    font-size: 0.75rem;
    color: #505080;
    margin-top: 2px;
}

/* Divider */
hr { border-color: #1e1e3a; }
</style>
""", unsafe_allow_html=True)


# ── Load RAG chain (cached) ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading your notes into memory...")
def load_chain():
    from rag_chain import build_rag_chain
    return build_rag_chain()


@st.cache_data(show_spinner=False)
def get_vector_stats():
    from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings, collection_name=COLLECTION_NAME)
        return vs._collection.count()
    except Exception:
        return 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎓 UniMind")
    st.markdown("---")

    # Vector store check
    from config import CHROMA_DIR
    store_exists = os.path.exists(CHROMA_DIR)

    if store_exists:
        vec_count = get_vector_stats()
        st.markdown('<span class="status-ready">● READY</span>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="metric-card"><div class="metric-value">{vec_count:,}</div><div class="metric-label">Vectors Indexed</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-not-ready">● NOT READY</span>', unsafe_allow_html=True)
        st.warning("No notes indexed yet.\nRun `python ingest.py` first.")

    st.markdown("---")

    st.markdown("**📁 Upload & Index Notes**")
    uploaded_files = st.file_uploader(
        "Upload PDF notes",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload your university PDF notes"
    )

    if uploaded_files:
        if st.button("📥 Index Uploaded Notes", use_container_width=True):
            os.makedirs("data", exist_ok=True)
            for f in uploaded_files:
                with open(f"data/{f.name}", "wb") as out:
                    out.write(f.read())
            with st.spinner("Ingesting notes..."):
                import subprocess
                import sys
                result = subprocess.run([sys.executable, "ingest.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✓ Notes indexed successfully!")
                    st.cache_resource.clear()
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Ingestion failed:\n{result.stderr}")

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chain = None
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#303060; font-family:'IBM Plex Mono',monospace;">
    Built with LangChain · ChromaDB<br>
    HuggingFace · Streamlit<br><br>
    <a href="https://github.com/abdullahks-devhub" style="color:#404080;">github.com/abdullahks-devhub</a>
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
    <div class="rag-title">UniMind</div>
    <div class="rag-subtitle">// RAG-powered study assistant · ask anything from your notes</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = None

# Load chain
if store_exists and st.session_state.chain is None:
    try:
        st.session_state.chain = load_chain()
    except Exception as e:
        st.error(f"Failed to load chain: {e}")

# Welcome message
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #303060;">
        <div style="font-size:3rem; margin-bottom:1rem;">📚</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.9rem;">
            Upload your notes in the sidebar, then ask anything.<br><br>
            <span style="color:#404080;">e.g. "Explain the difference between RAG and fine-tuning"</span><br>
            <span style="color:#404080;">e.g. "Summarize chapter 3 on neural networks"</span><br>
            <span style="color:#404080;">e.g. "What are the key concepts I need to know for the exam?"</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            sources_html = "".join(f'<span class="source-pill">📄 {s}</span>' for s in msg["sources"])
            st.markdown(f'<div style="margin-top:8px;">{sources_html}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask anything from your notes..."):
    if not store_exists:
        st.error("Please upload and index your notes first using the sidebar.")
    elif st.session_state.chain is None:
        st.error("Chain not loaded. Please check your HuggingFace API token in the .env file.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Searching your notes..."):
                try:
                    from rag_chain import ask
                    result = ask(st.session_state.chain, prompt)
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    if sources:
                        sources_html = "".join(f'<span class="source-pill">📄 {s}</span>' for s in sources)
                        st.markdown(f'<div style="margin-top:8px;">{sources_html}</div>', unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    err_msg = f"Error: {str(e)}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
