"""
rag_chain.py
Builds the RAG pipeline:
  Query → ChromaDB retrieval → Context injection → LLM → Answer
"""

import logging
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate

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

    # LLM
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=LLM_MODEL,
        task="text-generation",
        max_new_tokens=1024,
        temperature=0.3,      # lower = more factual, less creative (good for study)
        huggingfacehub_api_token=HF_TOKEN,
    )
    llm = ChatHuggingFace(llm=llm_endpoint)

    # Conversational memory — keeps last 5 exchanges
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
    )

    # Full RAG chain with memory
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": RAG_PROMPT},
        verbose=False
    )

    return chain


def ask(chain, question: str) -> dict:
    """
    Ask a question and get answer + sources.
    Returns: {"answer": str, "sources": list}
    """
    result = chain.invoke({"question": question})

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
