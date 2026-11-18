"""Order (GR) number keys.

GR numbers are written many ways, in two scripts, with OCR noise:
    मातंस ३८१४/प्र.क्र.१७४/३९        DIT-2018/C.R.17 ( 1 )/D-1/39
    GAD-2018/CR 25/Sect3/39         GAD-IT-060/3/2017
    मातंसं-००८८/२७/२०१६-DIR IT      GAD-11090/2/2020
The stable part is the file number and the case number (प्र.क्र. / C.R.).
Each is reduced to a key ("F", file, case), so the Marathi and English forms
of the same number compare equal. The department suffix (/39), section and
series prefix are ignored.
"""
import re

from .normalize import compact_numbers

# Case-number markers: Marathi प्र.क्र. (and OCR forms), English C.R. / CR No.,
# and the machine-translation renderings seen in .en.txt (Q.No., P.No., P.S., PR No.)
_CASE = (r"(?:प्र\.?\s?क(?:्र)?\.?\s?|सेतू/प्र\.?क्र\.?\s?|C\.?\s?R\.?(?:\s?NO\.?)?[-.]?\s?"
         r"|Q\.?\s?No\.?\s?|P\.?\s?(?:R\.?\s?)?No\.?\s?|P\.\s?S\.\s?)")

# 2018/प्र.क्र.53   2018/C.R.17   2018/CR 25   1717/111/   11090/प्र.क्र.2
_FILE_CASE = re.compile(rf"(?<!\d)(\d{{4,5}})(?:-\d{{2}})?/(?:{_CASE})?(\d{{1,3}})(?!\d)", re.IGNORECASE)
# 065/प्र.क्र.1/2018 (short file number, case marker required)
_SHORT_FILE_CASE = re.compile(rf"(?<!\d)(\d{{2,3}})/{_CASE}(\d{{1,3}})(?!\d)", re.IGNORECASE)
# 060/3/2017   088/27/2016   080/4/2014
_FILE_CASE_YEAR = re.compile(r"(?<!\d)(\d{2,5})/(\d{1,3})/((?:19|20)\d{2})(?!\d)")


def find_order_keys(text: str) -> list[tuple[tuple, int, int]]:
    """Return (key, start, end) for each order number in `text`.

    Positions refer to compact_numbers(text), not to the original.
    """
    compact = compact_numbers(text)
    out: dict[int, tuple] = {}
    for m in _FILE_CASE_YEAR.finditer(compact):
        a, b = m.group(1), m.group(2)
        if len(a) <= 2 and 1 <= int(a) <= 31 and 1 <= int(b) <= 12:
            continue  # dd/mm/yyyy date, not an order number
        key = ("F", int(m.group(1)), int(m.group(2)))
        out[m.start()] = (key, m.start(), m.end())
    for m in list(_SHORT_FILE_CASE.finditer(compact)) + list(_FILE_CASE.finditer(compact)):
        if m.start() in out:
            continue
        key = ("F", int(m.group(1)), int(m.group(2)))
        out[m.start()] = (key, m.start(), m.end())
    return [out[k] for k in sorted(out)]


def order_key(order_number: str) -> tuple | None:
    """Key of a metadata order number, or None if it has no recognisable number."""
    keys = find_order_keys(order_number)
    return keys[0][0] if keys else None


def key_str(key: tuple | None) -> str | None:
    return None if key is None else f"{key[1]}/{key[2]}"
