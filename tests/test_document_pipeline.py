from app.services.document_pipeline import process_document


FILE_PATH = "data/input/untitled.pdf"


def main():

    print("===== END-TO-END DOCUMENT TEST =====")

    result = process_document(
        FILE_PATH
    )

    print("\n===== RESULTS =====")

    print(
        f"\nDocument: "
        f"{result['file_name']}"
    )

    print(
        f"\nDocument validation:\n"
        f"{result['validation']}"
    )

    print(
        f"\nSummary validation:\n"
        f"{result['summary_validation']}"
    )

    print(
        f"\nAudio file:\n"
        f"{result['audio_path']}"
    )

    print(
        f"\nSummary file:\n"
        f"{result['summary_path']}"
    )

    print(
        f"\nParaphrase file:\n"
        f"{result['paraphrase_path']}"
    )

    print("\n===== TEST COMPLETE =====")


if __name__ == "__main__":
    main()