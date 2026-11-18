"""Detect GRs issued as both an English and a Marathi PDF (different codes, one GR).

Rule: same metadata date, different original language, same order-number key,
and English-version text cosine similarity >= TWIN_MIN_SIMILARITY.
Titles are not compared: the two versions are often titled differently.
"""
import itertools
import math
from collections import Counter, defaultdict

from .corpus import GR
from .normalize import tokens

TWIN_MIN_SIMILARITY = 0.8


def cosine(a: str, b: str) -> float:
    A, B = Counter(tokens(a)), Counter(tokens(b))
    dot = sum(A[k] * B[k] for k in A)
    na = math.sqrt(sum(v * v for v in A.values()))
    nb = math.sqrt(sum(v * v for v in B.values()))
    return dot / (na * nb) if na and nb else 0.0


def find_twins(grs: list[GR]) -> list[dict]:
    by_date = defaultdict(list)
    for g in grs:
        by_date[g.date].append(g)
    pairs = []
    for date, group in sorted(by_date.items()):
        for a, b in itertools.combinations(group, 2):
            if a.original_lang == b.original_lang:
                continue
            if a.order_key is None or a.order_key != b.order_key:
                continue
            sim = cosine(a.text_en, b.text_en)
            if sim >= TWIN_MIN_SIMILARITY:
                en, mr = (a, b) if a.original_lang == "en" else (b, a)
                pairs.append({"date": date, "en_code": en.code, "mr_code": mr.code,
                              "similarity": round(sim, 3)})
    return pairs


def group_ids(grs: list[GR], twins: list[dict]) -> dict[str, str]:
    """Map every code to a group id. Twins share a group id (the earlier code)."""
    gid = {g.code: g.code for g in grs}
    for t in twins:
        lead = min(t["en_code"], t["mr_code"])
        gid[t["en_code"]] = gid[t["mr_code"]] = lead
    return gid
