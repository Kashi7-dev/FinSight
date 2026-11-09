import shutil
from pathlib import Path

import pypdfium2 as pdfium
import pytesseract
from pypdf import PdfReader


# Nếu Tesseract chưa có trong PATH, chỉ rõ vị trí đã cài trên máy này.
if shutil.which("tesseract") is None:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def extract_pdf_pages_with_ocr(
    pdf_path: str | Path,
) -> list[dict[str, int | str]]:
    pdf_path = Path(pdf_path)

    # Thử đọc lớp văn bản có sẵn trước.
    reader = PdfReader(str(pdf_path))

    # PDFium sẽ chuyển các trang scan thành ảnh để Tesseract đọc.
    rendered_pdf = pdfium.PdfDocument(str(pdf_path))
    extracted_pages: list[dict[str, int | str]] = []

    try:
        for page_index, source_page in enumerate(reader.pages):
            text = (source_page.extract_text() or "").strip()
            extraction_method = "PDF_TEXT"

            # Chỉ OCR trang mà pypdf không lấy được văn bản.
            if not text:
                rendered_page = rendered_pdf[page_index]
                image = rendered_page.render(
                    scale=300 / 72,
                    grayscale=True,
                ).to_pil()

                text = pytesseract.image_to_string(
                    image,
                    lang="vie+eng",
                    config="--psm 3",
                ).strip()
                extraction_method = "OCR"

            extracted_pages.append({
                "page_number": page_index + 1,
                "text": text,
                "extraction_method": extraction_method,
            })
    finally:
        rendered_pdf.close()

    return extracted_pages