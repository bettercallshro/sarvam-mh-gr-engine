"""Citation graph: which earlier GRs in the corpus each GR refers to.

A later GR often amends an earlier one without naming what it changes; it only
cites the earlier GR's date or number in its references. Edges here are
"cites" links, not "amends" links: whether the later GR changes the earlier
one has to be read from its text.

Evidence for an edge (source -> target, target dated on or before source):
  date        source mentions target's date in a citation context (original text only)
  date+order  ... and the order number just before that date is target's
  order       source mentions target's order number with no date after it
  same_file   the matched number is source's own GR number (issued on the same
              file, e.g. an addendum to a circular); weakest evidence
Mentions of a GR's own date or a twin's are ignored.

Cited dates with no GR in the corpus are kept as "unresolved" references:
these are GRs the corpus does not hold (not GRs that don't exist).
"""
import re
from collections import defaultdict

from .corpus import GR
from .dates import date_key, find_dates
from .normalize import compact_numbers, to_ascii_digits
from .orders import find_order_keys, key_str

ORDER_BEFORE = 90  # characters before a date mention searched for its order number
DATE_AFTER_ORDER = 45  # an order number followed this closely by a date is a dated reference
CONTEXT_BEFORE = 80  # characters before a date mention searched for a citation word

# Words that mark a date as a reference to a GR, circular, letter, etc.
CITATION_WORDS = re.compile(
    r"शासन|निर्णय|परिपत्रक|पत्र|शुध्दिपत्र|शुद्धिपत्र|शुध्दीपत्र|पु[रू]कपत्र|पूरकपत्र|अधिसूचना|आदेश|"
    r"संदर्भ|वाचा|क्रमांक|क्र\.|"
    r"\bG\.?\s?R\b|resolution|circular|corrigendum|addendum|letter|decision|notification|"
    r"order|reference|\bref\b|\bread\b|vide|No\.",
    re.IGNORECASE,
)

# Dates of meetings, cabinet decisions and other departments' circulars that
# happen to share a date with an IT-department GR.
NOT_A_GR = re.compile(
    r"बैठक|मंत्रिमंडळ|वित्त विभाग|नियोजन विभाग|इतिवृत्त|meeting|cabinet|finance department|"
    r"Finance-\d|अर्थसं|व्यय-",
    re.IGNORECASE,
)
NOT_A_GR_BEFORE = 60
NOT_A_GR_AFTER = 40


def _mentions(gr: GR):
    """Yield (which_text, text) for the original-language and English versions."""
    yield "orig", gr.text_orig
    if gr.original_lang != "en":  # for English originals the .en.txt is a near copy
        yield "en", gr.text_en


def _snippet(text: str, start: int, end: int, pad: int = 70) -> str:
    s = text[max(0, start - pad): min(len(text), end + pad)]
    return re.sub(r"\s+", " ", s).strip()


def build_graph(grs: list[GR], group_of: dict[str, str]) -> dict:
    by_code = {g.code: g for g in grs}
    by_date = defaultdict(list)
    by_order = defaultdict(list)
    for g in grs:
        by_date[g.date].append(g)
        if g.order_key:
            by_order[g.order_key].append(g)

    # (source_code, target_code) -> edge
    edges: dict[tuple[str, str], dict] = {}
    unresolved: dict[tuple[str, str], dict] = {}

    def add_edge(src: GR, tgt: GR, evidence: str, which: str, snippet: str):
        if group_of[src.code] == group_of[tgt.code]:
            return
        if date_key(tgt.date) > date_key(src.date):
            return  # a GR cannot cite a later one; a date match like this is noise
        e = edges.setdefault((src.code, tgt.code), {
            "from": src.code, "from_date": src.date,
            "to": tgt.code, "to_date": tgt.date,
            "evidence": set(), "snippets": [],
        })
        e["evidence"].add(evidence)
        if len(e["snippets"]) < 3 and snippet not in e["snippets"]:
            e["snippets"].append(f"[{which}] {snippet}")

    for src in grs:
        own_dates = {g.date for g in grs if group_of[g.code] == group_of[src.code]}
        for which, text in _mentions(src):
            ascii_text = to_ascii_digits(text)

            # 1. dates
            for dm in find_dates(text):
                if dm.date in own_dates:
                    continue
                before = ascii_text[max(0, dm.start - CONTEXT_BEFORE): dm.start]
                if not CITATION_WORDS.search(before):
                    continue  # deadlines, events, etc.
                after = ascii_text[dm.end: dm.end + NOT_A_GR_AFTER]
                if NOT_A_GR.search(before[-NOT_A_GR_BEFORE:]) or NOT_A_GR.search(after):
                    continue  # meeting dates, other departments' circulars
                # References read "No. <order>, dated <date>": the closest order
                # number just before the date is the one this date belongs to.
                preceding = find_order_keys(ascii_text[max(0, dm.start - ORDER_BEFORE): dm.start])
                cited_key = preceding[-1][0] if preceding else None
                snippet = _snippet(text, dm.start, dm.end)
                candidates = by_date.get(dm.date, [])
                if cited_key is not None:
                    matched = [c for c in candidates if c.order_key == cited_key]
                    evidence = "date+order"
                elif which == "en":
                    continue  # machine translation garbles references; need the number too
                else:
                    matched, evidence = candidates, "date"
                if not matched:
                    # Cited GR is not in the corpus (or is another department's).
                    if date_key(dm.date) < date_key(src.date):
                        u = unresolved.setdefault((src.code, dm.date, key_str(cited_key)), {
                            "from": src.code, "from_date": src.date, "cited_date": dm.date,
                            "cited_order": key_str(cited_key), "snippet": f"[{which}] {snippet}"})
                    continue
                for c in matched:
                    add_edge(src, c, evidence, which, snippet)

            # 2. order numbers
            compact = compact_numbers(text)
            for key, s, e in find_order_keys(text):
                if find_dates(compact[e: e + DATE_AFTER_ORDER]):
                    continue  # "No. X, dated D": a dated reference, resolved by step 1
                evidence = "same_file" if key == src.order_key else "order"
                for tgt in by_order.get(key, []):
                    if date_key(tgt.date) < date_key(src.date):
                        add_edge(src, tgt, evidence, which, _snippet(compact, s, e))

    edge_list = []
    for e in edges.values():
        e["evidence"] = sorted(e["evidence"])
        edge_list.append(e)
    edge_list.sort(key=lambda e: (date_key(e["from_date"]), e["from"], date_key(e["to_date"])))

    unresolved_list = []
    for u in unresolved.values():
        unresolved_list.append(u)
    unresolved_list.sort(key=lambda u: (date_key(u["from_date"]), u["from"], date_key(u["cited_date"])))

    return {"edges": edge_list, "unresolved": unresolved_list}


def newer_candidates(code: str, graph: dict, group_of: dict[str, str]) -> list[dict]:
    """GRs that cite `code` (or its twin), directly or through a chain of citations.

    These are candidates for "a newer GR changes this"; the answer step reads
    their text to decide what each one actually does.
    """
    cited_by = defaultdict(list)
    for e in graph["edges"]:
        cited_by[group_of[e["to"]]].append(e)
    seen, out, stack = {group_of[code]}, [], [(group_of[code], 0)]
    while stack:
        gid, depth = stack.pop()
        for e in cited_by.get(gid, []):
            src_gid = group_of[e["from"]]
            if src_gid in seen:
                continue
            seen.add(src_gid)
            out.append({**e, "hops": depth + 1})
            stack.append((src_gid, depth + 1))
    out.sort(key=lambda e: date_key(e["from_date"]))
    return out
