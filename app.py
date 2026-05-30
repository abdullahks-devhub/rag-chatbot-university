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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, h5, h6, .rag-title, .metric-value { font-family: 'Outfit', sans-serif; }
code, pre { font-family: 'Inter', monospace; font-size: 0.9em; }

/* Background */
.stApp {
    background: #FDFBF7;
    color: #2D3748;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F4F1EA;
    border-right: 1px solid #E2E8F0;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    margin: 12px 0;
    padding: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* User message */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: #FAF8F2;
    border-color: #D6CBBD;
    box-shadow: 0 2px 6px rgba(214,203,189,0.2);
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    border: 1px solid #D6CBBD !important;
    color: #2D3748 !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #B0A08B !important;
    box-shadow: 0 0 0 2px rgba(176,160,139,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: #FFFFFF;
    color: #4A5568;
    border: 1px solid #CBD5E0;
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.stButton > button:hover {
    background: #F4F1EA;
    border-color: #B0A08B;
    color: #2D3748;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

/* Source pills */
.source-pill {
    display: inline-block;
    background: #F4F1EA;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 500;
    color: #718096;
    margin: 4px 6px 4px 0;
}

/* Header */
.rag-header {
    text-align: center;
    padding: 3rem 0 1.5rem;
}
.rag-title {
    font-size: 3.2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #B0A08B 0%, #D6CBBD 50%, #A0AEC0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}
.rag-subtitle {
    color: #718096;
    font-size: 1rem;
    font-weight: 400;
    margin-top: 0.5rem;
}

/* Status badge */
.status-ready {
    display: inline-block;
    background: #E6FFFA;
    border: 1px solid #B2F5EA;
    color: #319795;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
}
.status-not-ready {
    display: inline-block;
    background: #FFF5F5;
    border: 1px solid #FED7D7;
    color: #E53E3E;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
}

/* Metric cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 600;
    color: #B0A08B;
}
.metric-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #A0AEC0;
    margin-top: 4px;
}

/* Divider */
hr { border-color: #E2E8F0; }
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
        from langchain_chroma import Chroma
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
    <div style="font-size:12px; color:#718096; font-weight: 500;">
    Built with LangChain · ChromaDB<br>
    HuggingFace · Streamlit<br><br>
    <a href="https://github.com/abdullahks-devhub" style="color:#B0A08B; text-decoration: none;">github.com/abdullahks-devhub</a>
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
    <div style="text-align:center; padding: 4rem 0; color: #4A5568;">
        <div style="font-size:3.5rem; margin-bottom:1.5rem;">📚</div>
        <div style="font-size:1rem; font-weight: 400; line-height: 1.6;">
            Upload your notes in the sidebar, then ask anything.<br><br>
            <span style="color:#718096;">e.g. "Explain the difference between RAG and fine-tuning"</span><br>
            <span style="color:#718096;">e.g. "Summarize chapter 3 on neural networks"</span><br>
            <span style="color:#718096;">e.g. "What are the key concepts I need to know for the exam?"</span>
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
