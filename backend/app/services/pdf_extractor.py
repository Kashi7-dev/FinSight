from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(file_path: Path) -> list[dict[str, int | str]]:
    reader = PdfReader(str(file_path))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported")

    pages: list[dict[str, int | str]] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text(extraction_mode="layout") or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text.strip(),
            }
        )

    return pages