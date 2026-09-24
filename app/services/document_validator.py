def validate_document(normalized_document):
    """
    Validate the normalized document before further processing.
    """

    errors = []
    warnings = []

    # Check document information
    document_info = normalized_document.get("document", {})

    file_name = document_info.get("file_name")

    if not file_name:
        errors.append("File name is missing.")

    # Get extracted content
    content = normalized_document.get("content", [])

    # Check whether content exists
    if not content:
        errors.append("No content was extracted from the document.")

    # Count pages
    pages = set()

    for item in content:

        page = item.get("page")

        if page is not None:
            pages.add(page)

    page_count = len(pages)

    if page_count == 0:
        warnings.append("No page information was found.")

    # Check text content
    text_items = 0
    empty_items = 0
    ocr_items = 0

    for item in content:

        item_type = item.get("type")

        if item_type in ["paragraph", "heading", "bullet"]:

            text = item.get("text", "").strip()

            if text:
                text_items += 1
            else:
                empty_items += 1

        if item.get("ocr") is True:
            ocr_items += 1

    # Warn about empty extracted items
    if empty_items > 0:
        warnings.append(
            f"{empty_items} extracted content items are empty."
        )

    # Warn if OCR was used
    if ocr_items > 0:
        warnings.append(
            f"OCR was used for {ocr_items} content items."
        )

    # Warn if very little text was extracted
    if text_items == 0:
        errors.append(
            "No readable text content was extracted."
        )

    # Final validation status
    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "page_count": page_count,
        "text_items": text_items,
        "ocr_items": ocr_items
    }
