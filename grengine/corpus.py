"""Load the IT-department GRs from the sparse clone of orgpedia/mahGRs."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .normalize import devanagari_ratio
from .orders import key_str, order_key

DEFAULT_CORPUS_DIR = Path("corpus")  # copied unchanged from orgpedia/mahGRs at c96e88f; see corpus/README.md
COVERAGE = "Information Technology GRs, 2018 to 2024"

_PAGE_RE = re.compile(r"^# Page (\d+)\s*$", re.MULTILINE)


@dataclass
class GR:
    code: str
    date: str          # dd-mm-yyyy, from GRs.json (never from the code)
    title: str
    url: str
    order_number: str  # as in metadata
    order_type: str    # as in metadata; known to be unreliable, kept for reference only
    num_pages: int
    original_lang: str  # "mr" or "en", detected from the original-language text
    pages_orig: dict[int, str] = field(default_factory=dict)  # from <code>.pdf.mr.txt
    pages_en: dict[int, str] = field(default_factory=dict)    # from <code>.pdf.en.txt

    @property
    def order_key(self):
        return order_key(self.order_number)

    @property
    def text_orig(self) -> str:
        return "\n".join(self.pages_orig[p] for p in sorted(self.pages_orig))

    @property
    def text_en(self) -> str:
        return "\n".join(self.pages_en[p] for p in sorted(self.pages_en))

    def meta(self) -> dict:
        return {
            "code": self.code,
            "date": self.date,
            "title": self.title,
            "url": self.url,
            "order_number": self.order_number,
            "order_key": key_str(self.order_key),
            "order_type": self.order_type,
            "num_pages": self.num_pages,
            "original_lang": self.original_lang,
        }


def split_pages(text: str) -> dict[int, str]:
    """Split on '# Page N' lines. Text before the first marker goes to page 1."""
    pages: dict[int, str] = {}
    marks = list(_PAGE_RE.finditer(text))
    if not marks:
        return {1: text.strip()} if text.strip() else {}
    if text[: marks[0].start()].strip():
        pages[1] = text[: marks[0].start()].strip()
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        n = int(m.group(1))
        body = text[m.end():end].strip()
        pages[n] = (pages.get(n, "") + "\n" + body).strip()
    return pages


def load_corpus(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> tuple[list[GR], list[dict]]:
    """Return (grs, failures). A failure is {"code", "reason"}."""
    corpus_dir = Path(corpus_dir)
    meta_path = corpus_dir / "GRs.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"{meta_path} not found. The corpus ships in corpus/; "
                                "scripts/fetch_corpus.sh re-fetches it.")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    grs, failures = [], []
    for key, m in meta.items():
        code = m.get("code") or key.removesuffix(".pdf")
        try:
            orig_path = corpus_dir / f"{code}.pdf.mr.txt"
            en_path = corpus_dir / f"{code}.pdf.en.txt"
            missing = [p.name for p in (orig_path, en_path) if not p.exists()]
            if missing:
                raise FileNotFoundError("missing " + ", ".join(missing))
            for f in ("date", "url", "text"):
                if not m.get(f):
                    raise ValueError(f"metadata field '{f}' is empty")
            if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", m["date"]):
                raise ValueError(f"bad date {m['date']!r}")
            pages_orig = split_pages(orig_path.read_text(encoding="utf-8"))
            pages_en = split_pages(en_path.read_text(encoding="utf-8"))
            if not pages_orig or not pages_en:
                raise ValueError("empty text file")
            orig_text = " ".join(pages_orig.values())
            grs.append(GR(
                code=code,
                date=m["date"],
                title=m["text"].strip(),
                url=m["url"],
                order_number=m.get("order_number", ""),
                order_type=m.get("order_type", ""),
                num_pages=int(m.get("num_pages") or 0),
                original_lang="mr" if devanagari_ratio(orig_text) > 0.5 else "en",
                pages_orig=pages_orig,
                pages_en=pages_en,
            ))
        except Exception as e:  # report and continue; never drop a GR silently
            failures.append({"code": code, "reason": str(e)})

    # Files on disk with no metadata entry are also failures to report
    known = {g.code for g in grs} | {f["code"] for f in failures}
    for p in sorted(corpus_dir.glob("*.pdf.mr.txt")):
        c = p.name.split(".")[0]
        if c not in known:
            failures.append({"code": c, "reason": "text file without GRs.json entry"})
    return grs, failures
