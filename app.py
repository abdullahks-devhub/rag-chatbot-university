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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600&family=Outfit:wght@400;500;600;700;800&display=swap');

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
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-bottom: 1px solid #EAE6DF !important;
}
[data-testid="stChatMessage"]:last-child {
    border-bottom: none !important;
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
    display: inline-flex;
    align-items: center;
    background: #F5F3EE;
    border: 1px solid #EAE6DF;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 10.5px;
    font-weight: 500;
    color: #8C867E;
    margin: 2px 4px 2px 0;
}

/* ── Status badge ── */
.badge-ready {
    display: inline-flex;
    align-items: center;
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
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #B91C1C;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
}
.status-dot.ready {
    background-color: #1F7A5C;
}
.status-dot.not-ready {
    background-color: #B91C1C;
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
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #2b2620 0%, #A89880 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 12px;
}
.sidebar-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #2b2620 0%, #A89880 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 8px 0;
}
.app-tagline {
    font-size: 15px;
    color: #9A948C;
    font-weight: 400;
    margin-top: 6px;
}

/* ── Welcome screen suggestions (Streamlit Button overrides) ── */
div[data-testid="column"] button {
    display: block !important;
    text-align: left !important;
    background: #FFFFFF !important;
    border: 1px solid #E5E0D8 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    color: #4a4a4a !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    height: 84px !important;
    white-space: normal !important;
    width: 100% !important;
}

div[data-testid="column"] button:hover {
    background: #FDFCFA !important;
    border-color: #C9C3BB !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
}

div[data-testid="column"] button p {
    margin: 0 !important;
    color: #4a4a4a !important;
    font-size: 13px !important;
}

div[data-testid="column"] button strong {
    display: block !important;
    color: #1a1a1a !important;
    font-weight: 500 !important;
    margin-bottom: 2px !important;
    font-size: 13px !important;
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


# ── LaTeX Delimiter Fix for Streamlit ─────────────────────────────────────────
def format_latex(text: str) -> str:
    if not text:
        return text
    # Replace block LaTeX delimiters with $$ with newlines
    text = text.replace(r"\[", "\n$$\n").replace(r"\]", "\n$$\n")
    # Replace inline LaTeX delimiters with $
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    return text


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
if "prompt_trigger" not in st.session_state:
    st.session_state.prompt_trigger = None

if store_exists and st.session_state.chain is None:
    try:
        st.session_state.chain = load_chain()
    except Exception as e:
        st.error(f"Failed to load chain: {e}")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">UniMind</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Status
    if store_exists:
        vec_count = get_vector_count()
        st.markdown(f'<div class="badge-ready"><span class="status-dot ready"></span>Ready</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f'<div class="stat-box"><div class="stat-number">{vec_count:,}</div><div class="stat-label">Chunks Indexed</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-not-ready"><span class="status-dot not-ready"></span>No Index Found</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Upload
    with st.expander("Upload Notes", expanded=not store_exists):
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
            <div class="app-logo">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#A89880" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                    <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"/>
                </svg>
            </div>
            <div class="app-name" style="margin-top: 12px;">UniMind</div>
            <div class="app-tagline">Ask anything from your university notes</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Render suggestion buttons styled as cards
        st.markdown('<div style="max-width: 560px; margin: 32px auto 0;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("**Summarize a topic**\nExplain the key ideas from Chapter 3", key="btn_s1", use_container_width=True):
                st.session_state.prompt_trigger = "Explain the key ideas from Chapter 3"
                st.rerun()
            if st.button("**Deep dive**\nExplain how AES encryption works", key="btn_s3", use_container_width=True):
                st.session_state.prompt_trigger = "Explain how AES encryption works"
                st.rerun()
        with col2:
            if st.button("**Exam prep**\nWhat are the most important concepts to know?", key="btn_s2", use_container_width=True):
                st.session_state.prompt_trigger = "What are the most important concepts to know?"
                st.rerun()
            if st.button("**Compare**\nWhat is the difference between DES and AES?", key="btn_s4", use_container_width=True):
                st.session_state.prompt_trigger = "What is the difference between DES and AES?"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
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
                pills = "".join(
                    f'<span class="source-pill">'
                    f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px; flex-shrink: 0;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'
                    f'{s}</span>'
                    for s in msg["sources"]
                )
                st.markdown(f'<div style="margin-top:8px; display: flex; flex-wrap: wrap;">{pills}</div>', unsafe_allow_html=True)

    # Capture prompt from input or card buttons
    chat_input_prompt = st.chat_input("Ask anything from your notes…")

    prompt = None
    if st.session_state.prompt_trigger:
        prompt = st.session_state.prompt_trigger
        st.session_state.prompt_trigger = None  # Clear trigger
    elif chat_input_prompt:
        prompt = chat_input_prompt

    if prompt:
        if not store_exists:
            st.error("No notes indexed yet — upload your PDFs in the sidebar first.")
        elif st.session_state.chain is None:
            st.error("Chain not ready. Check your HUGGINGFACEHUB_API_TOKEN.")
        else:
            # Optimistically append user message so it's visible immediately
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner("Thinking…"):
                try:
                    # Build chat history from all messages except the current user prompt
                    chat_history = []
                    temp_user = None
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            temp_user = msg["content"]
                        elif msg["role"] == "assistant" and temp_user is not None:
                            chat_history.append((temp_user, msg["content"]))
                            temp_user = None

                    from rag_chain import ask
                    result = ask(st.session_state.chain, prompt, chat_history=chat_history)
                    answer = format_latex(result["answer"])
                    sources = result["sources"]

                    # Append assistant response — history loop renders it after rerun
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })
                except Exception as e:
                    # Roll back the optimistic user message on failure
                    st.session_state.messages.pop()
                    st.error(f"Something went wrong: {e}")

            # Force a clean rerun so the history loop is the single renderer
            st.rerun()
