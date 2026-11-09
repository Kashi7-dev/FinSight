from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


STORAGE_DIR = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "private_reports"
)
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


async def save_private_pdf(
    upload_file: UploadFile,
) -> tuple[str, str]:
    original_filename = Path(
        (upload_file.filename or "report.pdf").replace("\\", "/")
    ).name

    if Path(original_filename).suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    header = await upload_file.read(1024)
    if b"%PDF-" not in header:
        raise ValueError("The uploaded file is not a valid PDF")

    await upload_file.seek(0)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    storage_key = f"{uuid4()}.pdf"
    destination = STORAGE_DIR / storage_key
    total_bytes = 0

    try:
        with destination.open("wb") as saved_file:
            while chunk := await upload_file.read(1024 * 1024):
                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise ValueError("PDF file exceeds the 20 MB limit")

                saved_file.write(chunk)

        if total_bytes == 0:
            raise ValueError("The uploaded PDF is empty")

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    finally:
        await upload_file.close()

    return storage_key, original_filename[:255]


def get_private_pdf_path(storage_key: str) -> Path:
    if Path(storage_key).name != storage_key:
        raise ValueError("Invalid storage key")

    return STORAGE_DIR / storage_key


def delete_private_pdf(storage_key: str) -> None:
    path = get_private_pdf_path(storage_key)
    path.unlink(missing_ok=True)