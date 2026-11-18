"""Text normalisation helpers.

Matching (dates, order numbers, amounts) runs on normalised text with ASCII
digits. The original text is always kept separately for quotes.
"""
import re
import unicodedata

DEVANAGARI_DIGITS = "०१२३४५६७८९"
_DIGIT_MAP = str.maketrans(DEVANAGARI_DIGITS, "0123456789")


def to_ascii_digits(text: str) -> str:
    """Replace Devanagari digits with ASCII digits. Length is preserved."""
    return text.translate(_DIGIT_MAP)


def normalize(text: str) -> str:
    """NFC, ASCII digits, collapsed whitespace. For matching, not for quotes."""
    text = unicodedata.normalize("NFC", text)
    text = to_ascii_digits(text)
    return re.sub(r"\s+", " ", text).strip()


def compact_numbers(text: str) -> str:
    """Remove OCR spaces inside number-like tokens.

    OCR often splits tokens: "३ ९" for 39, "प्र.क्र . २५", "C . R.17".
    This joins digit-space-digit and drops spaces around / . - ( ).
    Use only for order-number matching.
    """
    text = to_ascii_digits(text)
    text = re.sub(r"(?<=\d) +(?=\d)", "", text)
    text = re.sub(r" *([/.\-()]) *", r"\1", text)
    return text


def devanagari_ratio(text: str) -> float:
    """Share of letters that are Devanagari; used to tell Marathi originals from English."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    deva = sum(1 for c in letters if "ऀ" <= c <= "ॿ")
    return deva / len(letters)


def tokens(text: str) -> list[str]:
    """Lowercased word tokens (Latin or Devanagari) with ASCII digits."""
    text = normalize(text).lower()
    return re.findall(r"[a-z0-9]+|[ऀ-ॿ]+", text)
