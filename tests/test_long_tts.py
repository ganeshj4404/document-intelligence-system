from pathlib import Path

from app.services.tts_service import generate_speech


# Create a reasonably large piece of text.
paragraph = """
The Document Intelligence System processes documents from
Google Drive and extracts their contents using document parsing
and OCR. The system normalizes the extracted information,
validates the document, creates chunks when necessary, and uses
a local language model to generate a concise summary. It also
supports paraphrasing while preserving important factual
information such as names, dates, numbers, percentages, and
financial values. The complete document can be converted into
speech and saved as an MP3 audio file.
"""

# Repeat the paragraph many times to simulate a large document.
long_text = "\n\n".join(
    paragraph.strip()
    for _ in range(100)
)

output_file = Path(
    "data/audio/long_document_test.mp3"
)

print("===== LONG DOCUMENT TTS TEST =====")

print(
    f"Text characters: {len(long_text)}"
)

print("Generating audio...")

result = generate_speech(
    long_text,
    output_file
)

print("\n===== RESULT =====")

print(f"Audio file: {result}")

if result.exists():

    file_size = result.stat().st_size

    print(f"Audio size: {file_size} bytes")

    if file_size > 0:

        print(
            "\nTEST PASSED: "
            "Long document audio was generated successfully."
        )

    else:

        print(
            "\nTEST FAILED: "
            "Audio file is empty."
        )

else:

    print(
        "\nTEST FAILED: "
        "Audio file was not created."
    )