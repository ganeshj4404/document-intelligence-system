from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document


file_path = "data/input/scanned_test.pdf"

content = parse_document(file_path)

normalized = normalize_document(
    content,
    "scanned_test.pdf"
)

print("\n===== NORMALIZED DOCUMENT =====\n")

print(normalized)