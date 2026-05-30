"""
app.py
UniMind — University RAG Study Assistant
Clean, minimal UI inspired by modern AI chat products.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="UniMind",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background-color: #FAF9F7;
    color: #1a1a1a;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #F2EFE9;
    border-right: 1px solid #E5E0D8;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {
    color: #4a4a4a;
    font-size: 13px;
}

/* ── Chat area ── */
[data-testid="stChatMessage"] {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    margin: 0;
    box-shadow: none;
}

/* User message row */
[data-testid="stChatMessage"][data-testid*="user-message"],
div[data-testid="stChatMessage"]:has([data-testid="StyledFullScreenButton"]) {
    background: transparent;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #FFFFFF;
    border: 1px solid #E0DBD3;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #1a1a1a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #AAA49C !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #FFFFFF;
    color: #3a3a3a;
    border: 1px solid #DDD8D0;
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 14px;
    transition: all 0.15s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stButton > button:hover {
    background: #F2EFE9;
    border-color: #C9C3BB;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07);
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed #D4CFC7;
    border-radius: 12px;
    padding: 8px;
    background: #FDFCFA;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #E5E0D8; margin: 12px 0; }

/* ── Source pills ── */
.source-pill {
    display: inline-block;
    background: #F2EFE9;
    border: 1px solid #E0DBD3;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 500;
    color: #7A756E;
    margin: 3px 4px 3px 0;
}

/* ── Status badge ── */
.badge-ready {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #EDFAF4;
    border: 1px solid #B7EDD8;
    color: #1F7A5C;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}
.badge-not-ready {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #B91C1C;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 48px 0 16px;
}
.app-logo {
    font-size: 2rem;
    margin-bottom: 8px;
}
.app-name {
    font-size: 2.4rem;
    font-weight: 600;
    color: #1a1a1a;
    letter-spacing: -0.04em;
    line-height: 1.1;
}
.app-tagline {
    font-size: 15px;
    color: #9A948C;
    font-weight: 400;
    margin-top: 6px;
}

/* ── Welcome screen suggestions ── */
.suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 560px;
    margin: 32px auto 0;
}
.suggestion-card {
    background: #FFFFFF;
    border: 1px solid #E5E0D8;
    border-radius: 12px;
    padding: 14px 16px;
    cursor: pointer;
    font-size: 13px;
    color: #4a4a4a;
    font-weight: 400;
    line-height: 1.4;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.suggestion-card strong {
    display: block;
    color: #1a1a1a;
    font-weight: 500;
    margin-bottom: 2px;
    font-size: 13px;
}

/* ── Metric ── */
.stat-box {
    background: #FFFFFF;
    border: 1px solid #E5E0D8;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.stat-number {
    font-size: 1.5rem;
    font-weight: 600;
    color: #A89880;
    letter-spacing: -0.02em;
}
.stat-label {
    font-size: 11px;
    font-weight: 500;
    color: #B0AA9F;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)


# ── Cached resources ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading knowledge base...")
def load_chain():
    from rag_chain import build_rag_chain
    return build_rag_chain()


@st.cache_data(show_spinner=False)
def get_vector_count():
    from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL
    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        vs = Chroma(persist_directory=CHROMA_DIR, embedding_function=emb, collection_name=COLLECTION_NAME)
        return vs._collection.count()
    except Exception:
        return 0


# ── State ────────────────────────────────────────────────────────────────────
from config import CHROMA_DIR
store_exists = os.path.exists(CHROMA_DIR)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = None

if store_exists and st.session_state.chain is None:
    try:
        st.session_state.chain = load_chain()
    except Exception as e:
        st.error(f"Failed to load chain: {e}")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### UniMind")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Status
    if store_exists:
        vec_count = get_vector_count()
        st.markdown(f'<div class="badge-ready">● Ready</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="stat-box"><div class="stat-number">{vec_count:,}</div><div class="stat-label">Chunks Indexed</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-not-ready">● No Index Found</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Upload
    with st.expander("📎 Upload Notes", expanded=not store_exists):
        uploaded_files = st.file_uploader(
            "PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files and st.button("Index Notes", use_container_width=True):
            os.makedirs("data", exist_ok=True)
            for f in uploaded_files:
                with open(f"data/{f.name}", "wb") as out:
                    out.write(f.read())
            with st.spinner("Indexing..."):
                import subprocess, sys
                result = subprocess.run([sys.executable, "ingest.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Done!")
                    st.cache_resource.clear()
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(result.stderr[-500:] if result.stderr else "Ingestion failed.")

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chain = None
        st.cache_resource.clear()
        st.rerun()

    st.markdown("")
    st.markdown(
        '<div style="font-size:11px;color:#B0AA9F;">LangChain · ChromaDB · HuggingFace</div>',
        unsafe_allow_html=True
    )


# ── Main area ─────────────────────────────────────────────────────────────────
col_main = st.container()

with col_main:
    # Header — only show when chat is empty
    if not st.session_state.messages:
        st.markdown("""
        <div class="app-header">
            <div class="app-logo">🎓</div>
            <div class="app-name">UniMind</div>
            <div class="app-tagline">Ask anything from your university notes</div>
        </div>
        <div class="suggestion-grid">
            <div class="suggestion-card"><strong>Summarize a topic</strong>Explain the key ideas from Chapter 3</div>
            <div class="suggestion-card"><strong>Exam prep</strong>What are the most important concepts to know?</div>
            <div class="suggestion-card"><strong>Deep dive</strong>Explain how AES encryption works</div>
            <div class="suggestion-card"><strong>Compare</strong>What is the difference between DES and AES?</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Compact header when chatting
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px;font-size:18px;font-weight:600;color:#1a1a1a;letter-spacing:-0.02em;">UniMind</div>',
            unsafe_allow_html=True
        )

    st.markdown("")

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                pills = "".join(f'<span class="source-pill">📄 {s}</span>' for s in msg["sources"])
                st.markdown(f'<div style="margin-top:8px;">{pills}</div>', unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Ask anything from your notes…"):
        if not store_exists:
            st.error("No notes indexed yet — upload your PDFs in the sidebar first.")
        elif st.session_state.chain is None:
            st.error("Chain not ready. Check your HUGGINGFACEHUB_API_TOKEN.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner(""):
                    try:
                        from rag_chain import ask
                        result = ask(st.session_state.chain, prompt)
                        answer = result["answer"]
                        sources = result["sources"]

                        st.markdown(answer)
                        if sources:
                            pills = "".join(f'<span class="source-pill">📄 {s}</span>' for s in sources)
                            st.markdown(f'<div style="margin-top:8px;">{pills}</div>', unsafe_allow_html=True)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        })
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
