import re


def extract_important_values(text):
    """
    Extract important factual values such as percentages,
    currency amounts, and dates.

    We deliberately avoid extracting every standalone number
    because ordinary counts and small numbers can create
    false validation warnings.
    """

    patterns = [
        # Percentages
        r"\b\d+(?:\.\d+)?%",

        # Indian currency amounts
        r"₹\s?\d+(?:\.\d+)?\s?(?:crore|lakh)",

        # Common date formats
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",

        # Years
        r"\b20\d{2}\b"
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            value = match.strip()

            # Normalize spaces
            value = re.sub(r"\s+", " ", value)

            if value not in values:
                values.append(value)

    return values


def validate_summary(source_text, summary_text):
    """
    Compare important values in the original document
    with the generated summary.
    """

    errors = []
    warnings = []

    if not summary_text or not summary_text.strip():
        errors.append("Generated summary is empty.")

        return {
            "status": "FAILED",
            "errors": errors,
            "warnings": warnings,
            "missing_values": []
        }

    source_values = extract_important_values(source_text)
    summary_values = extract_important_values(summary_text)

    missing_values = []

    for value in source_values:

        if value not in summary_values:
            missing_values.append(value)

    if missing_values:

        warnings.append(
            "Some important values from the source "
            "were not found in the summary."
        )

    if len(summary_text.strip()) < 50:

        warnings.append(
            "Generated summary is unusually short."
        )

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
        "missing_values": missing_values
    }