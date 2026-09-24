from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_chunker import chunk_document


print("TEST STARTED")

file_path = "data/input/scanned_test.pdf"

# Step 1: Extract document
content = parse_document(file_path)

print("PARSING COMPLETE")

# Step 2: Normalize document
normalized = normalize_document(
    content,
    "scanned_test.pdf"
)

print("NORMALIZATION COMPLETE")

# Step 3: Create chunks
chunks = chunk_document(
    normalized,
    max_characters=1000
)

print("CHUNKING COMPLETE")

print("\n===== DOCUMENT CHUNKS =====\n")

for chunk in chunks:

    print(f"Chunk ID: {chunk['chunk_id']}")
    print(f"Characters: {chunk['character_count']}")
    print("-" * 50)
    print(chunk["text"])
    print("-" * 50)