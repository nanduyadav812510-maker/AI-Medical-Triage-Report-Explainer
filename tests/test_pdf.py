import io

import pytest
import fitz

from backend.services.pdf_service import extract_text_from_pdf_bytes


def _create_valid_pdf(text: str = "Complete Blood Count: WBC 6.5 x10^3/uL. Normal range.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    return buffer.getvalue()


def test_pdf_extraction():
    pdf_bytes = _create_valid_pdf()

    text, page_count = extract_text_from_pdf_bytes(pdf_bytes, "blood_report.pdf")
    assert page_count == 1
    assert "Complete Blood Count" in text


def test_empty_pdf_bytes_raises_error():
    with pytest.raises(ValueError, match="empty"):
        extract_text_from_pdf_bytes(b"")


def test_corrupted_pdf_bytes_raises_error():
    with pytest.raises(ValueError, match="Invalid PDF|corrupt|Failed to process"):
        extract_text_from_pdf_bytes(b"not-a-real-pdf-content")


def test_password_protected_pdf_raises_error():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Protected content")
    buffer = io.BytesIO()
    doc.save(
        buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret",
        owner_pw="owner",
    )
    doc.close()

    with pytest.raises(ValueError, match="Password-protected|password"):
        extract_text_from_pdf_bytes(buffer.getvalue(), "protected.pdf")


def test_too_large_pdf_raises_error():
    with pytest.raises(ValueError, match="20 MB|size"):
        extract_text_from_pdf_bytes(b"A" * (20 * 1024 * 1024 + 1), "big.pdf")
