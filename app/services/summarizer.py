from app.services.llm_service import generate_response


def summarize_chunk(chunk_text):
    """
    Generate a point-wise summary for one document chunk.
    """

    prompt = f"""
You are a document summarization assistant.

Summarize the following document content into clear bullet points.

Rules:
- Use only information present in the document.
- Do not invent or assume facts.
- Preserve names, dates, numbers, amounts, and important technical details.
- Keep the important information.
- Make the summary concise and easy to understand.

Document content:

{chunk_text}

Return only the bullet-point summary.
"""

    return generate_response(prompt)


def summarize_document(chunks):
    """
    Summarize all document chunks.
    """

    summaries = []

    for chunk in chunks:

        summary = summarize_chunk(
            chunk["text"]
        )

        summaries.append({
            "chunk_id": chunk["chunk_id"],
            "summary": summary
        })

    return summaries