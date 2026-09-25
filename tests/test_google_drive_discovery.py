from app.services.google_drive_service import (
    get_drive_service,
    list_supported_files,
)


def main():

    print("===== GOOGLE DRIVE FILE DISCOVERY TEST =====\n")

    print("1. Connecting to Google Drive...")
    service = get_drive_service()

    print("Google Drive connected.\n")

    print("2. Searching for supported documents...")

    files = list_supported_files(service)

    if not files:

        print("No supported documents found.")
        return

    print(f"Found {len(files)} supported file(s).\n")

    print("===== SUPPORTED DOCUMENTS =====\n")

    for index, file in enumerate(files, start=1):

        print(f"{index}. {file['name']}")
        print(f"   ID: {file['id']}")
        print(f"   MIME type: {file['mimeType']}")
        print(f"   Modified: {file.get('modifiedTime', 'N/A')}")
        print(f"   Size: {file.get('size', 'N/A')}")
        print()

    print("===== DISCOVERY TEST PASSED =====")


if __name__ == "__main__":
    main()