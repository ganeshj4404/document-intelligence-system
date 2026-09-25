from app.services.document_parser import parse_document


files = [
    "data/input/test.csv",
    "data/input/test.pptx",
    "data/input/test_image.png",
]

for file_path in files:

    print("\n===================================")
    print(f"TESTING: {file_path}")
    print("===================================\n")

    content = parse_document(file_path)

    print(content)