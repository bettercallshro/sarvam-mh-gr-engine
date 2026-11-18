"""Find dates in GR text (English and Marathi) and return them as dd-mm-yyyy."""
import re
from dataclasses import dataclass

from .normalize import to_ascii_digits

MONTHS = {
    # English
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
    # Marathi, with common spelling and OCR variants
    "जानेवारी": 1, "जानेवरी": 1,
    "फेब्रुवारी": 2, "फेब्रुवरी": 2, "फेब्रवारी": 2,
    "मार्च": 3,
    "एप्रिल": 4,
    "मे": 5,
    "जून": 6, "जुन": 6,
    "जुलै": 7, "जुलाई": 7,
    "ऑगस्ट": 8, "ऑगष्ट": 8, "आगस्ट": 8,
    "सप्टेंबर": 9, "सप्टेबर": 9, "सप्टेंम्बर": 9,
    "ऑक्टोबर": 10, "ऑक्टोंबर": 10, "आक्टोबर": 10,
    "नोव्हेंबर": 11, "नोव्हेबर": 11, "नोहेंबर": 11,
    "डिसेंबर": 12, "डिसेबर": 12,
}

_MONTH_ALT = "|".join(sorted((re.escape(m) for m in MONTHS), key=len, reverse=True))

# 29.01.2018, 29/1/2018, 29-01-2018, 24.12.19 (OCR may put spaces around separators)
# OCR can glue the next list number onto the year: "29.01.20183.सामान्य" is 29.01.2018 + "3."
_NUMERIC = re.compile(r"(?<!\d)(\d{1,2}) ?[./-] ?(\d{1,2}) ?[./-] ?((?:19|20)\d{2}(?=\d[.)])|\d{4}(?!\d)|\d{2}(?!\d))")
# 29th January 2018, 27 नोव्हेंबर, 2020
_DAY_MONTH_YEAR = re.compile(
    rf"(?<!\d)(\d{{1,2}})(?:st|nd|rd|th)?[\s,.]*({_MONTH_ALT})(?![a-zऀ-ॿ])[\s,.]*(\d{{4}})(?!\d)",
    re.IGNORECASE,
)
# January 29, 2018
_MONTH_DAY_YEAR = re.compile(
    rf"(?<![a-z])({_MONTH_ALT})[\s.]+(\d{{1,2}})(?:st|nd|rd|th)?[\s,]+(\d{{4}})(?!\d)",
    re.IGNORECASE,
)


@dataclass
class DateMention:
    date: str  # dd-mm-yyyy
    start: int
    end: int
    raw: str


def _valid(d: int, m: int, y: int) -> bool:
    return 1 <= d <= 31 and 1 <= m <= 12 and 1990 <= y <= 2030


def _fmt(d: int, m: int, y: int) -> str:
    return f"{d:02d}-{m:02d}-{y:04d}"


def find_dates(text: str) -> list[DateMention]:
    """All date mentions, positions refer to `text` (digit conversion keeps length)."""
    ascii_text = to_ascii_digits(text)
    found: dict[int, DateMention] = {}

    for m in _NUMERIC.finditer(ascii_text):
        d, mo, y = int(m.group(1)), int(m.group(2)), m.group(3)
        y = int(y) + 2000 if len(y) == 2 else int(y)
        if _valid(d, mo, y):
            found[m.start()] = DateMention(_fmt(d, mo, y), m.start(), m.end(), text[m.start():m.end()])

    for m in _DAY_MONTH_YEAR.finditer(ascii_text):
        d, mo, y = int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))
        if _valid(d, mo, y) and m.start() not in found:
            found[m.start()] = DateMention(_fmt(d, mo, y), m.start(), m.end(), text[m.start():m.end()])

    for m in _MONTH_DAY_YEAR.finditer(ascii_text):
        mo, d, y = MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        if _valid(d, mo, y) and m.start() not in found:
            found[m.start()] = DateMention(_fmt(d, mo, y), m.start(), m.end(), text[m.start():m.end()])

    return [found[k] for k in sorted(found)]


def date_key(ddmmyyyy: str) -> tuple[int, int, int]:
    """Sortable (yyyy, mm, dd) from dd-mm-yyyy."""
    d, m, y = ddmmyyyy.split("-")
    return int(y), int(m), int(d)
