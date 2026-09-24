def chunk_document(normalized_document, max_characters=4000):
    """
    Split normalized document content into smaller chunks.
    """

    chunks = []
    current_chunk = []
    current_length = 0
    chunk_number = 1

    for item in normalized_document.get("content", []):

        # Convert the item into text
        if item.get("type") == "table":
            rows = item.get("rows", [])

            item_text = "\n".join(
                " | ".join(str(cell) for cell in row)
                for row in rows
            )

        else:
            item_text = item.get("text", "")

        item_text = item_text.strip()

        if not item_text:
            continue

        item_length = len(item_text)

        # If adding this item exceeds the limit,
        # save the current chunk first.
        if current_chunk and current_length + item_length > max_characters:

            chunks.append({
                "chunk_id": chunk_number,
                "text": "\n\n".join(current_chunk),
                "character_count": current_length
            })

            chunk_number += 1
            current_chunk = []
            current_length = 0

        current_chunk.append(item_text)
        current_length += item_length

    # Add the final chunk
    if current_chunk:

        chunks.append({
            "chunk_id": chunk_number,
            "text": "\n\n".join(current_chunk),
            "character_count": current_length
        })

    return chunks