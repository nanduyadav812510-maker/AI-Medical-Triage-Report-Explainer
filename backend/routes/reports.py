from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.models.report import (
    ReportAnalysisRequest,
    ReportAnalysisResponse,
)
from backend.services.pdf_service import extract_text_from_pdf_bytes
from backend.services.report_service import analyze_medical_report
from backend.services.translation_service import translate_text


router = APIRouter(
    prefix="/api/reports",
    tags=["Medical Reports"]
)

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_pdf_report(file: UploadFile = File(...)):
    """
    Upload a PDF medical report and extract readable text.

    Validations:
    - Only PDF files are accepted
    - Maximum file size: 20 MB
    - PDF magic header must be present
    """

    # 1. Check filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF files are supported."
        )

    try:
        # 2. Read uploaded file
        contents = await file.read()

        # 3. Check file size
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 20 MB limit."
            )

        # 4. Check PDF header
        if not contents.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. The uploaded file appears corrupted."
            )

        # 5. Extract text
        extracted_text, total_pages = extract_text_from_pdf_bytes(
            contents,
            file.filename
        )

        # 6. Make sure text was extracted
        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract readable text from this PDF. "
                    "The PDF may be scanned, image-based, or password protected."
                )
            )

        # 7. Return extracted information
        return {
            "success": True,
            "filename": file.filename,
            "total_pages": total_pages,
            "text_length": len(extracted_text),
            "extracted_text": extracted_text,
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(error)}"
        )


@router.post(
    "/analyze",
    response_model=ReportAnalysisResponse
)
async def analyze_report(payload: ReportAnalysisRequest):
    """
    Analyze extracted medical report text.

    The AI converts technical report information into
    easier-to-understand language.

    This is informational only and is not a medical diagnosis.
    """

    # 1. Validate report text
    if not payload.report_text or not payload.report_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Report text cannot be empty."
        )

    try:
        # 2. Send report to AI analysis service
        response = analyze_medical_report(payload)

        # 3. Translate summary if requested
        if (
            payload.language
            and payload.language.lower() != "english"
        ):
            response.summary = translate_text(
                response.summary,
                payload.language
            )

        # 4. Return result
        return response

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Report analysis failed: {str(error)}"
        )