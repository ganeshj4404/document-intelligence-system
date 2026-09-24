from app.services.document_parser import parse_document
from app.services.document_normalizer import normalize_document
from app.services.document_validator import validate_document


file_path = "data/input/scanned_test.pdf"

# Step 1: Extract
content = parse_document(file_path)

# Step 2: Normalize
normalized = normalize_document(
    content,
    "scanned_test.pdf"
)

# Step 3: Validate
validation = validate_document(normalized)

print("\n===== VALIDATION RESULT =====\n")

print(validation)