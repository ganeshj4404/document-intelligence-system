from pathlib import Path

from app.services.google_drive_service import (
    get_drive_service,
    export_google_doc,
)

from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_validator import validate_document


FILE_ID = "1Ujvi1aZ_5zjTAEAwW_pkSCfMSNBcPW2vuJeE9A0S-r8"

OUTPUT_PATH = Path(
    "data/input/siddheshresume.docx"
)


def main():

    print("===== GOOGLE DOC EXPORT TEST =====\n")

    print("1. Connecting to Google Drive...")
    service = get_drive_service()

    print("Google Drive connected.\n")

    print("2. Exporting Google Doc as DOCX...")

    exported_file = export_google_doc(
        service,
        FILE_ID,
        OUTPUT_PATH
    )

    print(f"Exported file: {exported_file}\n")

    print("3. Parsing exported DOCX...")

    content = parse_document(
        exported_file
    )

    print(
        f"Extracted {len(content)} content items.\n"
    )

    print("4. Normalizing document...")

    normalized = normalize_document(
        content,
        exported_file.name
    )

    print("Normalization complete.\n")

    print("5. Validating document...")

    validation = validate_document(
        normalized
    )

    print("\n===== VALIDATION RESULT =====")
    print(validation)

    print("\n===== TEST PASSED =====")


if __name__ == "__main__":
    main()