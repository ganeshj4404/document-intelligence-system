from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_chunker import chunk_document
from app.services.summarizer import summarize_document
from app.services.summary_validator import validate_summary


print("===== SUMMARY VALIDATION TEST =====")

file_path = "data/input/scanned_test.pdf"

# 1. Parse document
print("\n1. Parsing document...")
content = parse_document(file_path)

# 2. Normalize document
print("2. Normalizing document...")
normalized = normalize_document(
    content,
    "scanned_test.pdf"
)

# 3. Create chunks
print("3. Creating chunks...")
chunks = chunk_document(
    normalized,
    max_characters=1000
)

print(f"Created {len(chunks)} chunks.")

# 4. Generate summaries
print("\n4. Generating summaries...")
summaries = summarize_document(chunks)

# 5. Validate each summary
print("\n5. Validating summaries...\n")

for chunk, summary_item in zip(chunks, summaries):

    validation = validate_summary(
        chunk["text"],
        summary_item["summary"]
    )

    print(f"CHUNK {chunk['chunk_id']}")
    print("-" * 50)

    print("SUMMARY:")
    print(summary_item["summary"])

    print("\nVALIDATION RESULT:")
    print(validation)

    print("-" * 50)