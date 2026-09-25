from pathlib import Path

from app.services.google_drive_service import (
    get_drive_service,
    download_drive_file
)

from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_validator import validate_document


FILE_ID = "1p8LemUGto5pdwNUF7ZXA1i1M1zy7IRMj"
FILE_NAME = "untitled.pdf"

OUTPUT_PATH = Path("data/input") / FILE_NAME


def main():

    print("===== GOOGLE DRIVE DOWNLOAD + PARSING TEST =====\n")

    # 1. Authenticate
    print("1. Connecting to Google Drive...")
    service = get_drive_service()

    print("Google Drive connected.\n")

    # 2. Download
    print("2. Downloading document...")

    downloaded_file = download_drive_file(
        service,
        FILE_ID,
        OUTPUT_PATH
    )

    print(f"Downloaded: {downloaded_file}\n")

    # 3. Verify local file
    print("3. Checking local file...")

    if not downloaded_file.exists():

        raise FileNotFoundError(
            "Downloaded file was not found."
        )

    print(
        f"Local file size: "
        f"{downloaded_file.stat().st_size} bytes\n"
    )

    # 4. Parse downloaded document
    print("4. Parsing downloaded document...")

    content = parse_document(
        downloaded_file
    )

    print(
        f"Extracted {len(content)} content items.\n"
    )

    # 5. Normalize
    print("5. Normalizing document...")

    normalized = normalize_document(
        content,
        FILE_NAME
    )

    print("Normalization complete.\n")

    # 6. Validate
    print("6. Validating document...")

    validation = validate_document(
        normalized
    )

    print("\n===== VALIDATION RESULT =====")
    print(validation)

    print("\n===== TEST COMPLETE =====")


if __name__ == "__main__":
    main()