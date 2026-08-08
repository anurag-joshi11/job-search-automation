from __future__ import annotations


def validate_text(text: str, minimum_length: int = 1) -> str:
    """Reject empty or obviously invalid model responses before saving them."""
    cleaned = text.strip()
    if len(cleaned) < minimum_length:
        raise ValueError("Model returned an empty response")
    return cleaned

