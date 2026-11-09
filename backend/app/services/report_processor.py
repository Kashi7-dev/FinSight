import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.models.extraction_job import ExtractionJob
from app.models.financial_report import FinancialReport
from app.services.ocr_service import extract_pdf_pages_with_ocr


logger = logging.getLogger(__name__)

# report_processor.py nằm trong backend/app/services/,
# nên parents[2] trỏ tới thư mục backend.
BACKEND_DIR = Path(__file__).resolve().parents[2]
PRIVATE_REPORTS_DIR = BACKEND_DIR / "storage" / "private_reports"

CHUNK_SIZE = 2500
CHUNK_OVERLAP = 200


def _resolve_pdf_path(storage_key: str) -> Path:
    """Tìm đường dẫn PDF trên ổ đĩa từ storage_key trong database."""
    key_path = Path(storage_key)

    # Một số cách lưu trữ có thể giữ đường dẫn tuyệt đối.
    if key_path.is_absolute() and key_path.is_file():
        return key_path

    # Thử storage_key như một đường dẫn tương đối từ backend.
    backend_candidate = BACKEND_DIR / key_path
    if backend_candidate.is_file():
        return backend_candidate

    # Trường hợp storage_key chỉ là tên file.
    private_candidate = PRIVATE_REPORTS_DIR / key_path.name
    if private_candidate.is_file():
        return private_candidate

    # Trả về vị trí dự kiến để lỗi FileNotFoundError chỉ rõ đường dẫn cần tìm.
    return private_candidate


def _split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Chia văn bản dài thành các đoạn có phần chồng lặp nhỏ."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # Cố gắng cắt ở cuối dòng để đỡ cắt giữa câu hoặc khoản mục.
        if end < text_length:
            newline_position = cleaned_text.rfind("\n", start, end)
            if newline_position > start:
                end = newline_position

        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Phần overlap giúp giữ ngữ cảnh giữa hai chunk liền kề.
        start = max(end - overlap, start + 1)

    return chunks


def process_pdf_report(report_id: UUID) -> None:
    """Đọc PDF, OCR các trang scan và lưu văn bản vào DocumentChunk."""
    db = SessionLocal()

    try:
        # Tìm job đang chờ xử lý mới nhất của báo cáo này.
        job = db.scalar(
            select(ExtractionJob)
            .where(
                ExtractionJob.report_id == report_id,
                ExtractionJob.status == "QUEUED",
            )
            .order_by(ExtractionJob.created_at.desc())
        )

        # Có thể job đã được xử lý hoặc không tồn tại.
        if job is None:
            logger.warning(
                "No queued extraction job found for report_id=%s",
                report_id,
            )
            return

        report = db.get(FinancialReport, report_id)
        if report is None:
            job.status = "FAILED"
            job.error_message = "Financial report was not found."
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        if not report.storage_key:
            job.status = "FAILED"
            job.error_message = "The report has no storage key."
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        job.status = "PROCESSING"
        job.started_at = datetime.now(timezone.utc)
        job.error_message = None
        db.commit()

        pdf_path = _resolve_pdf_path(report.storage_key)
        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF file was not found at: {pdf_path}"
            )

        # Trang có lớp chữ được đọc bằng pypdf.
        # Trang scan không có chữ sẽ được render và OCR trong hàm này.
        pages = extract_pdf_pages_with_ocr(pdf_path)

        pages_with_text = [
            page
            for page in pages
            if str(page.get("text", "")).strip()
        ]

        if not pages_with_text:
            job.status = "REVIEW_REQUIRED"
            job.error_message = (
                "OCR did not recognize readable text in this PDF."
            )
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Xóa các chunk cũ của báo cáo để tránh trùng khi chạy lại job.
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.report_id == report.id
            )
        )

        chunk_index = 0

        for page_data in pages_with_text:
            page_number = int(page_data["page_number"])
            page_text = str(page_data["text"])

            for chunk_text in _split_text(page_text):
                chunk = DocumentChunk(
                    report_id=report.id,
                    chunk_index=chunk_index,
                    page_start=page_number,
                    page_end=page_number,
                    content=chunk_text,
                )
                db.add(chunk)
                chunk_index += 1

        job.status = "COMPLETED"
        job.error_message = None
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            "PDF text extraction completed: report_id=%s, chunks=%s",
            report_id,
            chunk_index,
        )

    except Exception as exc:
        db.rollback()
        logger.exception(
            "PDF processing failed for report_id=%s",
            report_id,
        )

        # Ghi trạng thái lỗi sau khi rollback transaction xử lý.
        try:
            failed_job = db.scalar(
                select(ExtractionJob)
                .where(ExtractionJob.report_id == report_id)
                .order_by(ExtractionJob.created_at.desc())
            )

            if failed_job and failed_job.status in {"QUEUED", "PROCESSING"}:
                failed_job.status = "FAILED"
                failed_job.error_message = str(exc)[:2000]
                failed_job.finished_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "Could not save failed status for report_id=%s",
                report_id,
            )

    finally:
        db.close()