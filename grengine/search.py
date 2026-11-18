"""E2 retrieval: BM25 over passages of both text files, plus direct lookup.

A GR is found in up to four ways, and the scores are added:
  text      BM25 over passages (original-language text and English version,
            title prepended to each passage); a GR scores its best passage,
            normalised so the top GR scores 1.0
  date      the question names a date that is a GR's date (exact), or a
            month/year it falls in (weaker)
  number    the question contains a GR number whose key matches a GR's
  cites     the question names a date that no GR in the corpus has, and a GR
            cites a GR of that date: the citing GR is the right result, and the
            answer must say the asked-for GR is not in the corpus

Twins are returned as one result (the group), so they do not take two slots.
"""
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .dates import MONTHS, date_key, find_dates
from .normalize import normalize, to_ascii_digits
from .orders import find_order_keys, key_str

INDEX_DIR = Path("data/index")

# Score weights
W_EXACT_DATE = 1.0
W_ORDER = 1.0
W_CITES_MISSING = 0.9
W_MONTH = 0.35
W_YEAR = 0.1

DISTINCTIVE_MAX_DF = 0.2  # for topic checks: ignore words in more than 20% of passages

PASSAGE_TOKENS = 120
PASSAGE_STRIDE = 80

STOPWORDS = set("""
a an the of and or to in on for from by with at as is are was were be been being this that these those
it its which what who whom whose when where how why will would can could should shall may might must do
does did has have had not no any all there their them they he she his her i my me we our you your
still current currently latest new newer old earlier later than about regarding regards gr grs govt
government resolution resolutions circular show find tell say said given give get
""".split())

# Abbreviations written both ways across GR titles and texts.
ABBREVIATIONS = {
    "ai": ["artificial", "intelligence"],
    "dbt": ["direct", "benefit", "transfer"],
    "nhm": ["national", "health", "mission"],
    "dit": ["directorate", "information", "technology"],
    "it": ["information", "technology"],
    "rfp": ["request", "proposal"],
    "sdc": ["state", "data", "centre", "center"],
}


def _stem(tok: str) -> str:
    """Very light English stemming; Devanagari tokens are left as they are."""
    if not tok.isascii() or tok.isdigit() or len(tok) <= 3:
        return tok
    if tok.endswith("ies") and len(tok) > 5:
        tok = tok[:-3] + "y"
    elif tok.endswith(("sses", "xes", "zes", "ches", "shes")):
        tok = tok[:-2]
    else:
        for suf in ("ing", "ed", "s"):
            if tok.endswith(suf) and not tok.endswith("ss") and len(tok) - len(suf) >= 3:
                tok = tok[: -len(suf)]
                break
    # drop a final "e" so date / dated / dates and rate / rates meet
    if tok.endswith("e") and len(tok) >= 4:
        tok = tok[:-1]
    return tok


def analyze(text: str, expand: bool = False) -> list[str]:
    text = normalize(text).lower().replace("centre", "center")
    toks = re.findall(r"[a-z0-9]+|[ऀ-ॿ]+", text)
    out = []
    for t in toks:
        if t in STOPWORDS:
            continue
        out.append(_stem(t))
        if expand and t in ABBREVIATIONS:
            out.extend(_stem(x) for x in ABBREVIATIONS[t])
    return out


@dataclass
class Passage:
    code: str
    page: int
    which: str  # "orig" or "en"
    text: str   # original text of the passage (for quotes)
    tokens: list[str] = field(default_factory=list)


@dataclass
class Hit:
    group: str
    codes: list[str]
    score: float
    reasons: dict[str, float]
    passages: list[dict]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(1, len(docs))
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        q = Counter(query)
        out = []
        for tf, ln in zip(self.tf, self.len):
            s = 0.0
            for t in q:
                f = tf.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / self.avg))
            out.append(s)
        return out


def _windows(text: str, size: int, stride: int) -> list[str]:
    words = text.split()
    if len(words) <= size:
        return [text]
    return [" ".join(words[i:i + size]) for i in range(0, max(1, len(words) - size + stride), stride)]


class Retriever:
    def __init__(self, index_dir: Path = INDEX_DIR):
        index_dir = Path(index_dir)
        if not (index_dir / "grs.json").exists():
            raise FileNotFoundError(f"{index_dir}/grs.json not found. Run: python -m grengine.build_index")
        meta = json.loads((index_dir / "grs.json").read_text(encoding="utf-8"))
        self.grs = {g["code"]: g for g in meta["grs"]}
        self.group_of = {c: g["group"] for c, g in self.grs.items()}
        self.members = defaultdict(list)
        for c, g in self.grs.items():
            self.members[g["group"]].append(c)
        self.graph = json.loads((index_dir / "citation_graph.json").read_text(encoding="utf-8"))

        self.by_date = defaultdict(list)
        self.by_key = defaultdict(list)
        for c, g in self.grs.items():
            self.by_date[g["date"]].append(c)
            if g["order_key"]:
                self.by_key[g["order_key"]].append(c)
        # missing cited date -> {citing code: tokens of its title + the citation snippet}
        self.citers_of_date = defaultdict(dict)
        for u in self.graph["unresolved"]:
            toks = self.citers_of_date[u["cited_date"]].setdefault(u["from"], set())
            toks.update(analyze(self.grs[u["from"]]["title"] + " " + u["snippet"]))

        self.passages: list[Passage] = []
        with (index_dir / "pages.jsonl").open(encoding="utf-8") as f:
            for line in f:
                p = json.loads(line)
                title = self.grs[p["code"]]["title"]
                for which in ("orig", "en"):
                    if which == "en" and self.grs[p["code"]]["original_lang"] == "en":
                        continue  # English originals: the .en.txt is a near copy
                    for w in _windows(p[f"text_{which}"], PASSAGE_TOKENS, PASSAGE_STRIDE):
                        self.passages.append(Passage(p["code"], p["page"], which, w,
                                                     analyze(title + " " + w)))
        self.bm25 = BM25([p.tokens for p in self.passages])
        # a token in more than this share of passages is too common to show topic
        n = len(self.passages)
        df_cut = DISTINCTIVE_MAX_DF * n
        self.min_distinctive_idf = math.log(1 + (n - df_cut + 0.5) / (df_cut + 0.5))

    # ---- direct lookup -------------------------------------------------
    def parse_query(self, q: str) -> dict:
        ascii_q = to_ascii_digits(q)
        dates = [d.date for d in find_dates(q)]
        keys = [key_str(k) for k, _, _ in find_order_keys(q)]
        months = []
        month_alt = "|".join(sorted(MONTHS, key=len, reverse=True))
        for m in re.finditer(rf"(?<![\w])({month_alt})\s*,?\s*((?:19|20)\d{{2}})", ascii_q, re.IGNORECASE):
            months.append((MONTHS[m.group(1).lower()], int(m.group(2))))
        years = [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)", ascii_q)]
        return {"dates": dates, "order_keys": keys, "months": months, "years": years}

    @staticmethod
    def strip_dates_numbers(q: str) -> str:
        spans = [(d.start, d.end) for d in find_dates(q)]
        ascii_q = to_ascii_digits(q)
        for m in re.finditer(r"\S*\d+/\S*", ascii_q):  # GR numbers like 3814/प्र.क्र.174/39
            spans.append(m.span())
        merged: list[list[int]] = []
        for a, b in sorted(spans):
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        for a, b in reversed(merged):
            q = q[:a] + " " + q[b:]
        return q

    def search(self, query: str, k: int = 5) -> list[Hit]:
        parsed = self.parse_query(query)
        reasons: dict[str, dict[str, float]] = defaultdict(dict)  # group -> reason -> score
        best_passages: dict[str, list[tuple[float, Passage]]] = defaultdict(list)

        # text (dates and GR numbers removed: digits like "19", "01", "2018"
        # match nearly every GR and are handled by direct lookup below)
        qtok = analyze(self.strip_dates_numbers(query), expand=True)
        scores = self.bm25.scores(qtok) if qtok else [0.0] * len(self.passages)
        per_group: dict[str, float] = {}
        for s, p in zip(scores, self.passages):
            if s <= 0:
                continue
            gid = self.group_of[p.code]
            per_group[gid] = max(per_group.get(gid, 0.0), s)
            best_passages[gid].append((s, p))
        top = max(per_group.values(), default=0.0)
        for gid, s in per_group.items():
            reasons[gid]["text"] = s / top if top else 0.0

        # dates
        for d in parsed["dates"]:
            if d in self.by_date:
                for c in self.by_date[d]:
                    reasons[self.group_of[c]]["date"] = W_EXACT_DATE
            else:
                # The asked-for GR is not in the corpus. A GR that cites that date is the
                # right result, but only if the citation is on the question's topic: the
                # same date can be cited for unrelated GRs (or misdated).
                topic = {t for t in qtok if self.bm25.idf.get(t, 0) >= self.min_distinctive_idf}
                for c, toks in self.citers_of_date.get(d, {}).items():
                    if topic & toks:
                        reasons[self.group_of[c]]["cites_missing"] = W_CITES_MISSING
        for mo, yr in parsed["months"]:
            for c, g in self.grs.items():
                dd, mm, yy = (int(x) for x in g["date"].split("-"))
                if (mm, yy) == (mo, yr):
                    reasons[self.group_of[c]].setdefault("month", W_MONTH)
        for yr in parsed["years"]:
            for c, g in self.grs.items():
                if int(g["date"][-4:]) == yr:
                    reasons[self.group_of[c]].setdefault("year", W_YEAR)

        # GR numbers
        for key in parsed["order_keys"]:
            for c in self.by_key.get(key, ()):
                reasons[self.group_of[c]]["number"] = W_ORDER

        hits = []
        for gid, r in reasons.items():
            if not any(x in r for x in ("text", "date", "number", "cites_missing")):
                continue  # month/year alone is not a match
            ps = sorted(best_passages.get(gid, []), key=lambda x: -x[0])[:3]
            hits.append(Hit(
                group=gid,
                codes=sorted(self.members[gid]),
                score=round(sum(r.values()), 4),
                reasons={k2: round(v, 3) for k2, v in r.items()},
                passages=[{"code": p.code, "page": p.page, "which": p.which,
                           "score": round(s, 3), "text": p.text} for s, p in ps],
            ))
        # ties broken by date, newest first
        hits.sort(key=lambda h: (-h.score, tuple(-x for x in date_key(self.grs[h.group]["date"]))))
        return hits[:k]

    def lookup_date(self, ddmmyyyy: str) -> list[str]:
        return list(self.by_date.get(ddmmyyyy, []))

    def lookup_number(self, text: str) -> list[str]:
        return [c for k, _, _ in find_order_keys(text) for c in self.by_key.get(key_str(k), [])]
