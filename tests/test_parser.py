from app.services.document_parser import parse_document


file_path = "data/input/scanned_test.pdf"

content = parse_document(file_path)

print("\n===== EXTRACTED DOCUMENT =====\n")

for item in content:
    print(item)