from app.services.llm_service import generate_response


def paraphrase_text(text):
    """
    Paraphrase text while preserving its original meaning
    and important factual information.
    """

    prompt = f"""
You are a professional document paraphrasing assistant.

Paraphrase the text below while preserving its exact meaning.

Rules:
- Do not add new information.
- Do not remove important information.
- Do not strengthen or weaken statements.
- Do not use emotional, exaggerated, or promotional words.
- Preserve names exactly.
- Preserve dates exactly.
- Preserve numbers, percentages, and financial amounts exactly.
- Preserve technical terms where appropriate.
- Do not change facts.
- Keep the same level of certainty as the original.
- Use clear, natural professional language.

Text to paraphrase:

{text}

Return only the paraphrased text.
"""

    return generate_response(prompt)