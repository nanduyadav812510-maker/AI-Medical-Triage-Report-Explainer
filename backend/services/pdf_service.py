import logging
from typing import Tuple

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

MAX_PDF_FILE_SIZE_BYTES = 20 * 1024 * 1024


def extract_text_from_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> Tuple[str, int]:
    """
    Extract readable text from a PDF file's raw bytes using PyMuPDF.

    Returns:
        (extracted_text, total_pages)

    Raises:
        ValueError: for empty files, invalid PDF content, password-protected files,
                    oversized PDFs, or PDFs with no readable text.
    """
    if pdf_bytes is None:
        raise ValueError("Uploaded PDF is empty.")

    if not isinstance(pdf_bytes, (bytes, bytearray)):
        raise ValueError("PDF content must be provided as bytes.")

    if len(pdf_bytes) == 0:
        raise ValueError("Uploaded PDF is empty.")

    if len(pdf_bytes) > MAX_PDF_FILE_SIZE_BYTES:
        raise ValueError("PDF file size exceeds the 20 MB limit.")

    if filename and not filename.lower().endswith(".pdf"):
        raise ValueError("Invalid PDF file. Expected a .pdf file.")

    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("Invalid PDF file. The uploaded file is not a valid PDF.")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        logger.error("Failed to open uploaded PDF %s: %s", filename, exc)
        raise ValueError(f"Invalid or corrupted PDF file: {exc}") from exc

    try:
        if doc.is_encrypted:
            raise ValueError("Password-protected PDF files are not supported. Please upload an unlocked PDF.")

        total_pages = doc.page_count
        extracted_chunks = []

        for page_num in range(total_pages):
            try:
                page = doc.load_page(page_num)
                text = page.get_text("text")
            except Exception as exc:
                logger.warning("Unable to read page %s from PDF %s: %s", page_num + 1, filename, exc)
                text = ""

            if text and text.strip():
                extracted_chunks.append(f"--- Page {page_num + 1} ---\n{text.strip()}")

        if not extracted_chunks:
            raise ValueError(
                "Could not extract readable text from this PDF. "
                "The file may be scanned, image-based, or password protected."
            )

        full_text = "\n\n".join(extracted_chunks)
        return full_text, total_pages

    except ValueError:
        raise
    except Exception as exc:
        logger.error("Error extracting text from PDF %s: %s", filename, exc)
        raise ValueError(f"Failed to process PDF document: {exc}") from exc
    finally:
        try:
            doc.close()
        except Exception:
            pass

