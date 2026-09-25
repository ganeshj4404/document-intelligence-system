from pathlib import Path

from app.services.google_drive_service import (
    get_drive_service,
    list_supported_files,
    process_drive_file,
    get_or_create_output_folder,
    upload_file_to_drive,
)

from app.services.document_pipeline import process_document


def run_drive_pipeline():
    """
    Find a supported document in Google Drive,
    process it, and upload the generated outputs
    back to Google Drive.
    """

    print("===== DOCUMENT INTELLIGENCE DRIVE PIPELINE =====\n")

    # -------------------------------------------------
    # 1. Connect to Google Drive
    # -------------------------------------------------

    print("1. Connecting to Google Drive...")

    service = get_drive_service()

    print("Google Drive connected.\n")

    # -------------------------------------------------
    # 2. Find supported documents
    # -------------------------------------------------

    print("2. Finding supported documents...")

    output_folder_id = get_or_create_output_folder(
    service
)

    files = list_supported_files(
        service,
        exclude_folder_id=output_folder_id
    )

    if not files:
        raise RuntimeError(
            "No supported documents were found in Google Drive."
        )

    print(f"Found {len(files)} supported document(s).\n")

    # -------------------------------------------------
    # 3. Display documents
    # -------------------------------------------------

    print("===== AVAILABLE DOCUMENTS =====\n")

    for index, file in enumerate(files, start=1):

        print(
            f"{index}. "
            f"{file['name']} "
            f"({file['mimeType']})"
        )

    print()

    # -------------------------------------------------
    # 4. Ask user to select document
    # -------------------------------------------------

    while True:

        choice = input(
            "Enter the document number to process: "
        ).strip()

        try:

            choice_number = int(choice)

            if 1 <= choice_number <= len(files):
                break

            print(
                f"Please enter a number between "
                f"1 and {len(files)}."
            )

        except ValueError:

            print("Please enter a valid number.")

    selected_file = files[choice_number - 1]

    file_id = selected_file["id"]
    file_name = selected_file["name"]
    mime_type = selected_file["mimeType"]

    print(
        f"\nSelected document: {file_name}"
    )

    # -------------------------------------------------
    # 5. Download / export
    # -------------------------------------------------

    print("\n3. Downloading / exporting document...")

    local_file = process_drive_file(
        service,
        file_id,
        file_name,
        mime_type,
        destination_directory="data/input"
    )

    print(
        f"Local document: {local_file}\n"
    )

    # -------------------------------------------------
    # 6. Process document
    # -------------------------------------------------

    print("4. Running document intelligence pipeline...\n")

    result = process_document(
        local_file
    )

    # -------------------------------------------------
    # 7. Get/create Drive output folder
    # -------------------------------------------------

    print("\n5. Preparing Google Drive output folder...")

    output_folder_id = get_or_create_output_folder(
        service
    )

    print(
        f"Output folder ID: "
        f"{output_folder_id}\n"
    )

    # -------------------------------------------------
    # 8. Upload generated outputs
    # -------------------------------------------------

    print("6. Uploading generated outputs...\n")

    output_files = [
        result["summary_path"],
        result["paraphrase_path"],
        result["audio_path"],
    ]

    uploaded_files = []

    for output_file in output_files:

        uploaded = upload_file_to_drive(
            service,
            output_file,
            output_folder_id
        )

        uploaded_files.append(uploaded)

    # -------------------------------------------------
    # 9. Display results
    # -------------------------------------------------

    print("\n===== PIPELINE COMPLETE =====")

    print(
        f"\nProcessed document: "
        f"{file_name}"
    )

    print(
        f"\nDocument validation:\n"
        f"{result['validation']}"
    )

    print(
        f"\nSummary validation:\n"
        f"{result['summary_validation']}"
    )

    print("\nUploaded files:")

    for uploaded in uploaded_files:

        print(
            f"- {uploaded['name']}"
        )

    print("\n===== DRIVE PIPELINE SUCCESS =====")

    return {
        "source_file": file_name,
        "local_file": str(local_file),
        "validation": result["validation"],
        "summary_validation": result["summary_validation"],
        "uploaded_files": uploaded_files,
    }