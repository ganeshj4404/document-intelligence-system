def normalize_document(content, file_name):
    """
    Convert extracted document content into a common structure.
    """

    normalized_content = []

    # PDF / DOCX structured content
    if isinstance(content, list):

        for item in content:

            item_type = item.get("type")

            if item_type in ["text", "ocr_text"]:
                normalized_content.append({
                    "type": "paragraph",
                    "page": item.get("page"),
                    "text": item.get("content", ""),
                    "ocr": item_type == "ocr_text"
                })

            elif item_type == "heading":
                normalized_content.append({
                    "type": "heading",
                    "page": item.get("page"),
                    "text": item.get("text", "")
                })

            elif item_type == "bullet":
                normalized_content.append({
                    "type": "bullet",
                    "page": item.get("page"),
                    "text": item.get("text", "")
                })

            elif item_type == "table":
                normalized_content.append({
                    "type": "table",
                    "page": item.get("page"),
                    "rows": item.get("rows", [])
                })

    # TXT / other plain text content
    elif isinstance(content, str):

        normalized_content.append({
            "type": "paragraph",
            "page": None,
            "text": content,
            "ocr": False
        })

    return {
        "document": {
            "file_name": file_name
        },
        "content": normalized_content
    }