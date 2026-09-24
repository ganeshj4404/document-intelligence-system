from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_chunker import chunk_document
from app.services.summarizer import summarize_document


print("===== DOCUMENT SUMMARIZATION TEST =====")

file_path = "data/input/scanned_test.pdf"

# 1. Parse document
print("\n1. Parsing document...")
content = parse_document(file_path)

# 2. Normalize
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

# 4. Summarize using local LLM
print("\n4. Sending chunks to local LLM...")

summaries = summarize_document(chunks)

# 5. Display results
print("\n===== GENERATED SUMMARY =====\n")

for item in summaries:

    print(f"CHUNK {item['chunk_id']}")
    print("-" * 50)
    print(item["summary"])
    print("-" * 50)