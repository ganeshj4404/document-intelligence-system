from pathlib import Path

from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_validator import validate_document
from app.services.document_chunker import chunk_document
from app.services.summarizer import summarize_document
from app.services.summary_validator import validate_summary
from app.services.paraphraser import paraphrase_text
from app.services.tts_service import generate_speech


def build_full_document_text(normalized_document):
    """
    Convert the normalized document into one readable text string.

    This text is used for full-document TTS.
    """

    parts = []

    for item in normalized_document.get("content", []):

        item_type = item.get("type")

        if item_type in ["paragraph", "heading", "bullet"]:

            text = item.get("text", "").strip()

            if text:
                parts.append(text)

        elif item_type == "table":

            rows = item.get("rows", [])

            for row in rows:

                row_text = " | ".join(
                    str(cell)
                    for cell in row
                ).strip()

                if row_text:
                    parts.append(row_text)

    return "\n\n".join(parts)


def save_text(text, output_path):
    """
    Save text output to a file.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        text,
        encoding="utf-8"
    )

    return output_path


def process_document(file_path):
    """
    Run the complete document intelligence pipeline
    on a local document.
    """

    file_path = Path(file_path)

    print("\n===== DOCUMENT PIPELINE =====")

    # -------------------------------------------------
    # 1. Parse
    # -------------------------------------------------

    print("\n1. Parsing document...")

    content = parse_document(file_path)

    # -------------------------------------------------
    # 2. Normalize
    # -------------------------------------------------

    print("2. Normalizing document...")

    normalized = normalize_document(
        content,
        file_path.name
    )

    # -------------------------------------------------
    # 3. Validate
    # -------------------------------------------------

    print("3. Validating document...")

    validation = validate_document(
        normalized
    )

    if validation["status"] == "FAILED":

        raise ValueError(
            f"Document validation failed: "
            f"{validation['errors']}"
        )

    print(
        f"Validation status: "
        f"{validation['status']}"
    )

    # -------------------------------------------------
    # 4. Build full document text
    # -------------------------------------------------

    print("4. Building full document text...")

    full_document_text = build_full_document_text(
        normalized
    )

    if not full_document_text.strip():

        raise ValueError(
            "No usable document text was created."
        )

    # -------------------------------------------------
    # 5. Prepare output directory
    # -------------------------------------------------

    output_directory = (
        Path("data/processed")
        / file_path.stem
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # -------------------------------------------------
    # 6. Full-document TTS
    # -------------------------------------------------

    print("5. Generating full-document audio...")

    audio_path = (
        output_directory
        / "full_document.mp3"
    )

    generate_speech(
        full_document_text,
        audio_path
    )

    # -------------------------------------------------
    # 6. Chunk document
    # -------------------------------------------------

    print("6. Creating document chunks...")

    chunks = chunk_document(
        normalized,
        max_characters=4000
    )

    print(
        f"Created {len(chunks)} chunk(s)."
    )

    # -------------------------------------------------
    # 7. Generate summary
    # -------------------------------------------------

    print("7. Generating summary...")

    summaries = summarize_document(
        chunks
    )

    combined_summary = "\n\n".join(
        item["summary"]
        for item in summaries
    )

    # -------------------------------------------------
    # 8. Validate summary
    # -------------------------------------------------

    print("8. Validating summary...")

    summary_validation = validate_summary(
        full_document_text,
        combined_summary
    )

    # -------------------------------------------------
    # 9. Paraphrase summary
    # -------------------------------------------------

    print("9. Generating paraphrase...")

    paraphrased = paraphrase_text(
        combined_summary
    )

    # -------------------------------------------------
    # 10. Summary TTS
    # -------------------------------------------------

    print("10. Generating summary audio...")

    summary_audio_path = (
        output_directory
        / "summary.mp3"
    )

    generate_speech(
        combined_summary,
        summary_audio_path,
        rate="+15%"
    )

    print("11. Saving outputs...")

    summary_path = save_text(
        combined_summary,
        output_directory / "summary.txt"
    )

    paraphrase_path = save_text(
        paraphrased,
        output_directory / "paraphrased.txt"
    )

    print("\n===== PIPELINE COMPLETE =====")

    return {
        "file_name": file_path.name,
        "validation": validation,
        "full_document_text": full_document_text,
        "chunks": chunks,
        "summary": combined_summary,
        "summary_validation": summary_validation,
        "paraphrase": paraphrased,
        "audio_path": str(audio_path),
        "summary_audio_path": str(summary_audio_path),
        "summary_path": str(summary_path),
        "paraphrase_path": str(paraphrase_path)
    }