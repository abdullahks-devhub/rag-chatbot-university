"""
rag_chain.py
Builds the RAG pipeline:
  Query → ChromaDB retrieval → Context injection → LLM → Answer
"""

import logging
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from config import (
    HF_TOKEN, LLM_MODEL, EMBEDDING_MODEL,
    CHROMA_DIR, COLLECTION_NAME, TOP_K
)

logger = logging.getLogger(__name__)

# ── Prompt Template ──────────────────────────────────────────────────────────
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question", "chat_history"],
    template="""You are a helpful university study assistant. Use the provided context from the student's notes to answer their question clearly and accurately.

If the answer is found in the context, provide a thorough explanation.
If the answer is not in the context, say: "I couldn't find this in your notes. You may want to check your textbook or ask your professor."
Never make up information that isn't in the context.

Chat History:
{chat_history}

Context from your notes:
{context}

Student Question: {question}

Answer:"""
)


def load_vectorstore():
    """Load the existing ChromaDB vector store."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    count = vectorstore._collection.count()
    logger.info(f"Loaded vector store with {count} vectors")
    return vectorstore


def build_rag_chain():
    """Build the full conversational RAG chain."""

    # Load vector store
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximal Marginal Relevance — reduces redundant chunks
        search_kwargs={
            "k": TOP_K,
            "fetch_k": TOP_K * 2,
        }
    )

    # LLM — openai/gpt-oss-120b via HuggingFace Inference Router
    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=HF_TOKEN,
        openai_api_base="https://router.huggingface.co/v1",
        temperature=0.3,
    )

    # Full RAG chain (stateless)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": RAG_PROMPT},
        verbose=False
    )

    return chain


def build_fallback_chain():
    """Build the conversational RAG chain with a reliable high-capacity fallback model."""
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": TOP_K,
            "fetch_k": TOP_K * 2,
        }
    )

    # High capacity backup model on HF router
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-72B-Instruct",
        openai_api_key=HF_TOKEN,
        openai_api_base="https://router.huggingface.co/v1",
        temperature=0.3,
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": RAG_PROMPT},
        verbose=False
    )
    return chain


def _format_result(result) -> dict:
    # Extract unique source pages
    sources = []
    seen = set()
    for doc in result.get("source_documents", []):
        key = f"{doc.metadata.get('source', 'Unknown')} — Page {doc.metadata.get('page', '?')}"
        if key not in seen:
            seen.add(key)
            sources.append(key)

    return {
        "answer": result["answer"],
        "sources": sources
    }


def ask(chain, question: str, chat_history: list = None) -> dict:
    """
    Ask a question and get answer + sources.
    Uses exponential backoff retries and falls back to a high-capacity model on 429.
    """
    if chat_history is None:
        chat_history = []

    import time
    max_retries = 3
    delay = 1.5

    for attempt in range(max_retries):
        try:
            result = chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            return _format_result(result)
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = any(term in err_msg.lower() for term in ["429", "too_many_requests", "queue_exceeded", "traffic", "rate_limit"])
            
            if is_rate_limit and attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed due to rate limit/queue. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
            
            # Fall back to Qwen 2.5 72B if retries are exhausted or it's another connection error
            logger.warning(f"Primary model query failed: {err_msg}. Running fallback model (Qwen 2.5 72B)...")
            try:
                fallback_chain = build_fallback_chain()
                result = fallback_chain.invoke({
                    "question": question,
                    "chat_history": chat_history
                })
                return _format_result(result)
            except Exception as fallback_err:
                logger.critical(f"Fallback model query also failed: {fallback_err}")
                raise e
