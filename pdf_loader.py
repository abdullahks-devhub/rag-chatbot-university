"""
pdf_loader.py
Handles all PDF types:
- Text-based PDFs       → pdfplumber (best text extraction)
- Scanned/image PDFs   → PyMuPDF + pytesseract OCR
- Mixed PDFs           → auto-detected, both methods combined
- Corrupted/edge cases → pypdf fallback
"""

import logging
from typing import List
from pathlib import Path

import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pypdf import PdfReader
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_scanned_page(page) -> bool:
    """Detect if a pdfplumber page is scanned (image-only) by checking text density."""
    text = page.extract_text() or ""
    return len(text.strip()) < 30  # fewer than 30 chars = likely scanned


def _ocr_pdf_page(pdf_path: str, page_num: int) -> str:
    """OCR a single page using PyMuPDF + Tesseract."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        # Render at 2x resolution for better OCR accuracy
        mat = fitz.Matrix(2.0, 2.0)
        clip = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [clip.width, clip.height], clip.samples)
        text = pytesseract.image_to_string(img, lang="eng")
        doc.close()
        return text
    except Exception as e:
        logger.warning(f"OCR failed on page {page_num}: {e}")
        return ""


def _load_with_pdfplumber(pdf_path: str) -> List[Document]:
    """Primary loader — handles text-based and mixed PDFs."""
    documents = []
    filename = Path(pdf_path).name

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""

            # If page looks scanned, fall back to OCR
            if _is_scanned_page(page):
                logger.info(f"  Page {page_num + 1} appears scanned — running OCR...")
                text = _ocr_pdf_page(pdf_path, page_num)

            # Also extract tables if present
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if row:
                            row_text = " | ".join(str(cell) for cell in row if cell)
                            text += "\n" + row_text

            if text.strip():
                documents.append(Document(
                    page_content=text.strip(),
                    metadata={
                        "source": filename,
                        "page": page_num + 1,
                        "total_pages": len(pdf.pages),
                        "loader": "pdfplumber"
                    }
                ))

    return documents


def _load_with_pypdf_fallback(pdf_path: str) -> List[Document]:
    """Fallback loader using pypdf for corrupted or edge-case PDFs."""
    documents = []
    filename = Path(pdf_path).name

    try:
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(Document(
                    page_content=text.strip(),
                    metadata={
                        "source": filename,
                        "page": page_num + 1,
                        "total_pages": len(reader.pages),
                        "loader": "pypdf_fallback"
                    }
                ))
    except Exception as e:
        logger.error(f"pypdf fallback also failed for {filename}: {e}")

    return documents


def load_pdf(pdf_path: str) -> List[Document]:
    """
    Load a single PDF file — automatically handles:
    - Normal text PDFs
    - Scanned / image-only PDFs (OCR)
    - Mixed PDFs
    - Password-free encrypted PDFs
    """
    filename = Path(pdf_path).name
    logger.info(f"Loading: {filename}")

    try:
        docs = _load_with_pdfplumber(pdf_path)
        if docs:
            logger.info(f"  ✓ Loaded {len(docs)} pages from {filename}")
            return docs
        else:
            logger.warning("  pdfplumber got no content, trying fallback...")
            return _load_with_pypdf_fallback(pdf_path)
    except Exception as e:
        logger.warning(f"  pdfplumber failed ({e}), trying fallback...")
        return _load_with_pypdf_fallback(pdf_path)


def load_all_pdfs(data_dir: str) -> List[Document]:
    """Load all PDFs from a directory recursively."""
    all_docs = []
    pdf_files = list(Path(data_dir).rglob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {data_dir}")
        return []

    logger.info(f"Found {len(pdf_files)} PDF file(s) in {data_dir}")

    for pdf_path in pdf_files:
        try:
            docs = load_pdf(str(pdf_path))
            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load {pdf_path.name}: {e}")
            continue

    logger.info(f"Total pages loaded: {len(all_docs)}")
    return all_docs
