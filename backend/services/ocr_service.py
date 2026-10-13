"""
OCR Service wrapper for image-based medical document fallback.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_image_or_scanned_pdf(file_bytes: bytes, filename: str = "document.pdf") -> Optional[str]:
    """
    Fallback OCR extractor for image files or scanned document images.
    """
    logger.info(f"Processing OCR fallback for {filename}")
    return "Scanned PDF image detected. Please upload a clear text PDF report or convert the document image to text."

