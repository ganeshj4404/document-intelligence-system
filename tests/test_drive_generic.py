from app.services.google_drive_service import (
    get_drive_service,
    process_drive_file,
)


def main():

    print("===== GENERIC DRIVE FILE TEST =====\n")

    service = get_drive_service()

    # Test 1: normal PDF
    print("1. Processing normal PDF...")

    pdf_file = process_drive_file(
        service,
        "1p8LemUGto5pdwNUF7ZXA1i1M1zy7IRMj",
        "untitled.pdf",
        "application/pdf",
    )

    print(f"PDF saved to: {pdf_file}\n")

    # Test 2: Google Doc
    print("2. Processing Google Doc...")

    doc_file = process_drive_file(
        service,
        "1Ujvi1aZ_5zjTAEAwW_pkSCfMSNBcPW2vuJeE9A0S-r8",
        "siddheshresume",
        "application/vnd.google-apps.document",
    )

    print(f"Google Doc saved to: {doc_file}\n")

    print("===== GENERIC DRIVE TEST PASSED =====")


if __name__ == "__main__":
    main()