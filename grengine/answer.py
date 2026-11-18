"""E3 answer step: retrieved GRs + newer-GR candidates -> sarvam-105b -> answer contract.

The model gets full texts. What it returns is kept twice:
  raw_answer      the model's own output in the contract shape, untouched
                  (the eval scores this)
  answer          after the post-answer checks (what the product shows)
and every change the checks make is logged as a correction:
  - cited/newer codes must be GRs that were given to it; a mistyped code whose
    stated date matches exactly one given GR is repaired, others are dropped
  - date, title and url always come from the metadata (model values replaced)
  - each quote is searched in the GR's original text; its page is taken from
    where it is found (quotes not found are flagged, not removed)
Wording rules (bare "in force", "does not exist") are flagged, not rewritten.
"""
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from .citations import newer_candidates
from .corpus import COVERAGE
from .dates import date_key, find_dates
from .normalize import to_ascii_digits
from .orders import find_order_keys, key_str
from .search import INDEX_DIR, Retriever

PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_VERSION = "answer_v4"

TOP_K = 5                 # retrieved GRs given in full
CANDIDATE_SOURCES = 3     # newer-GR candidates are collected for the top 3 retrieved GRs
MAX_CANDIDATE_BLOCKS = 12   # candidate blocks, including ones that are also retrieved GRs
COMPACT_ORIG_CHARS = 4500   # per GR, in the compact retry after a length-limit reply
MAX_ORIG_CHARS = 9000     # per GR; longer texts are cut (and marked)
MAX_EN_CHARS = 5000       # English machine translation of Marathi GRs, for reference
MAX_TOKENS = 4096
REASONING_EFFORT = "low"
TEMPERATURE = 0.2
CHARS_PER_TOKEN_ESTIMATE = 2.0  # conservative (measured ~3.9 on Q7), for the pre-call spend check only

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "asked_for_code": {"type": ["string", "null"]},
        "candidates_reviewed": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"},
                           "effect": {"type": "string", "enum": ["amends", "replaces", "stays", "extends",
                                                                  "clarifies", "cites_only", "unrelated"]},
                           "reason": {"type": "string"}},
            "required": ["code", "effect"], "additionalProperties": False}},
        "newer": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"}, "date": {"type": "string"},
                           "what_changed": {"type": "string"}},
            "required": ["code", "date", "what_changed"], "additionalProperties": False}},
        "cited": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"}, "date": {"type": "string"}, "title": {"type": "string"},
                           "quote": {"type": "string"}, "page": {"type": "integer"}},
            "required": ["code", "date", "title", "quote", "page"], "additionalProperties": False}},
        "answer": {"type": "string"},
        "status": {"type": "string", "enum": ["answered", "not_found"]},
    },
    "required": ["asked_for_code", "candidates_reviewed", "newer", "cited", "answer", "status"],
    "additionalProperties": False,
}

COULDNT_FIND = re.compile(r"could(?:n't| not) find", re.I)


def first_sentence(text: str) -> str:
    """Up to the first sentence end, ignoring abbreviations like Rs. and No."""
    m = re.search(r"(?<!\bRs)(?<!\bNo)(?<!\bDr)(?<!\b[A-Z])[.!?](?=\s|$)", text or "")
    return (text or "")[: m.end()] if m else (text or "")


BARE_IN_FORCE = re.compile(r"\b(?:is|are|remains?|still)\s+(?:currently\s+)?in\s+force\b", re.I)
DOES_NOT_EXIST = re.compile(r"\b(?:does not|doesn't|did not|never)\s+exist|\bno such (?:GR|government resolution)\b", re.I)


def load_prompt(version: str = PROMPT_VERSION) -> str:
    return (PROMPT_DIR / f"{version}.md").read_text(encoding="utf-8")


@dataclass
class Context:
    question: str
    retrieved: list[dict]     # [{code, date, title, score, reasons}]
    candidates: list[dict]    # [{code, date, title, of_code, evidence, hops, candidate_only}]
    date_facts: list[dict]
    given_codes: list[str]
    user_message: str


class Answerer:
    def __init__(self, retriever: Retriever | None = None, index_dir: Path = INDEX_DIR):
        self.rt = retriever or Retriever(index_dir)
        self.pages = {}  # code -> {"orig": {page: text}, "en": {page: text}}
        with (Path(index_dir) / "pages.jsonl").open(encoding="utf-8") as f:
            for line in f:
                p = json.loads(line)
                d = self.pages.setdefault(p["code"], {"orig": {}, "en": {}})
                d["orig"][p["page"]] = p["text_orig"]
                d["en"][p["page"]] = p["text_en"]
        # JSON mode (response_format json_object) with the schema stated in the prompt.
        # Strict json_schema mode was tried first: on Q7 it returned an empty
        # "not_found" without reading the texts (runs/experiments/2026-11-18-q7-format.json).
        self.system_prompt = load_prompt() + "\n\nJSON schema of the reply:\n" + json.dumps(ANSWER_SCHEMA)

    # ---- context ------------------------------------------------------------
    def _doc(self, code: str, header: str, compact: bool = False) -> str:
        g = self.rt.grs[code]
        limit = COMPACT_ORIG_CHARS if compact else MAX_ORIG_CHARS
        orig = "\n".join(f"# Page {p}\n{t}" for p, t in sorted(self.pages[code]["orig"].items()))
        if len(orig) > limit:
            orig = orig[:limit] + "\n[... text cut here for length ...]"
        twins = [c for c in self.rt.members[g["group"]] if c != code]
        lines = [
            f"=== {header} ===",
            f"code: {code}" + (f"   (same GR as {', '.join(twins)}: English/Marathi copies)" if twins else ""),
            f"date: {g['date']}",
            f"title: {g['title']}",
            f"GR number: {g['order_number']}",
            f"original language: {'Marathi' if g['original_lang'] == 'mr' else 'English'}",
            "--- original text ---",
            orig,
        ]
        if g["original_lang"] == "mr" and not compact:
            en = "\n".join(t for _, t in sorted(self.pages[code]["en"].items()))
            if len(en) > MAX_EN_CHARS:
                en = en[:MAX_EN_CHARS] + " [...]"
            lines += ["--- English machine translation (for reference only; never quote it) ---", en]
        return "\n".join(lines)

    def _date_facts(self, question: str) -> list[dict]:
        facts = []
        for d in dict.fromkeys(m.date for m in find_dates(question)):
            codes = self.rt.lookup_date(d)
            fact = {"date": d, "corpus_grs": [{"code": c, "title": self.rt.grs[c]["title"]} for c in codes]}
            if not codes:
                fact["cited_by"] = [
                    {"code": u["from"], "date": u["from_date"], "cited_number": u["cited_order"],
                     "snippet": u["snippet"].split("] ", 1)[-1]}
                    for u in self.rt.graph["unresolved"] if u["cited_date"] == d]
            facts.append(fact)
        return facts

    def _number_facts(self, question: str) -> list[dict]:
        out = []
        for key, _, _ in find_order_keys(question):
            ks = key_str(key)
            out.append({"number_key": ks, "corpus_grs": [
                {"code": c, "date": self.rt.grs[c]["date"], "title": self.rt.grs[c]["title"]}
                for c in sorted(self.rt.by_key.get(ks, []), key=lambda c: date_key(self.rt.grs[c]["date"]))]})
        return out

    def build_context(self, question: str, compact: bool = False) -> Context:
        """Prompt context. Every newer-GR candidate of the top retrieved GRs gets its
        own block with full text in the candidates section, even when it is also a
        retrieved GR. compact=True (used after a length-limit reply) drops the
        English translations and cuts each text shorter."""
        hits = self.rt.search(question, k=TOP_K)
        retrieved = [{"code": h.group, "date": self.rt.grs[h.group]["date"], "title": self.rt.grs[h.group]["title"],
                      "score": h.score, "reasons": h.reasons, "passages": h.passages} for h in hits]
        rank_of = {h.group: i for i, h in enumerate(hits, 1)}

        # candidate code -> its links (one per retrieved GR it cites)
        links: dict[str, list[dict]] = {}
        for h in hits[:CANDIDATE_SOURCES]:
            for c in newer_candidates(h.group, self.rt.graph, self.rt.group_of):
                gid = self.rt.group_of[c["from"]]
                if gid == h.group:
                    continue
                links.setdefault(gid, []).append({
                    "code": gid, "of_code": h.group, "evidence": c["evidence"],
                    "best_evidence": c["best_evidence"], "hops": c["hops"],
                    "candidate_only": c["candidate_only"], "already_retrieved": gid in rank_of})
        listed = list(links)[:MAX_CANDIDATE_BLOCKS]
        cands = [l for code in listed for l in links[code]]
        for c in cands:
            c["date"], c["title"] = self.rt.grs[c["code"]]["date"], self.rt.grs[c["code"]]["title"]
        given = [h.group for h in hits] + [c for c in listed if c not in rank_of]

        facts = self._date_facts(question)
        numbers = self._number_facts(question)
        parts = [f"QUESTION: {question}", "", "DATE FACTS:"]
        if not facts:
            parts.append("(no full date in the question)")
        for f in facts:
            if f["corpus_grs"]:
                parts.append(f"- {f['date']}: corpus GR(s) with this date: "
                             + "; ".join(f"{g['code']} ({g['title']})" for g in f["corpus_grs"]))
            else:
                parts.append(f"- {f['date']}: NO GR in the corpus has this date.")
                for c in f.get("cited_by", []):
                    parts.append(f"  - cited in {c['code']} (dated {c['date']}): \"{c['snippet']}\"")
                if not f.get("cited_by"):
                    parts.append("  - no corpus GR cites this date.")
        if numbers:
            parts += ["", "NUMBER FACTS (GR numbers in the question):"]
            for n in numbers:
                if n["corpus_grs"]:
                    parts.append(f"- file/case {n['number_key']}: corpus GRs issued on this number: "
                                 + "; ".join(f"{g['code']} ({g['date']}, {g['title']})" for g in n["corpus_grs"]))
                else:
                    parts.append(f"- file/case {n['number_key']}: no corpus GR has this number.")
        parts += ["", "RETRIEVED GRS (search rank order):"]
        for i, h in enumerate(hits, 1):
            parts.append(self._doc(h.group, f"RETRIEVED #{i}", compact))
        parts += ["", f"NEWER-GR CANDIDATES ({len(listed)} listed; leads only; read each text and decide; "
                      "candidates_reviewed must have one entry for EACH code below):"]
        if not listed:
            parts.append("(none: no corpus GR cites the top retrieved GRs)")
        for k, code in enumerate(listed, 1):
            lines = []
            for l in links[code]:
                note = " Only a shared file number links them; this alone proves nothing." if l["candidate_only"] else ""
                lines.append(f"cites {l['of_code']} [{self.rt.grs[l['of_code']]['date']}]; "
                             f"evidence: {', '.join(l['evidence'])}; hops: {l['hops']}.{note}")
            also = f" Also RETRIEVED #{rank_of[code]} above (same text)." if code in rank_of else ""
            parts.append(self._doc(code, f"CANDIDATE {k} of {len(listed)}: " + " | ".join(lines) + also, compact))
        ctx = Context(question, retrieved, cands, facts, given, "\n".join(parts))
        ctx.listed_candidates = listed
        ctx.number_facts = numbers
        ctx.compact = compact
        return ctx

    # ---- validation ---------------------------------------------------------
    def _find_quote(self, code: str, quote: str) -> tuple[int | None, bool]:
        """Page where `quote` occurs in the original text (whitespace-insensitive)."""
        def norm(s):
            return re.sub(r"\s+", " ", to_ascii_digits(s)).strip().strip('"“”\'').lower()
        q = norm(quote)
        if not q:
            return None, False
        pages = self.pages.get(code, {}).get("orig", {})
        for p, t in sorted(pages.items()):
            if q in norm(t):
                return p, True
        # quote spanning a page break
        whole = norm(" ".join(t for _, t in sorted(pages.items())))
        return (None, q in whole)

    def _given_dates(self, ctx: Context) -> set[str]:
        if not hasattr(ctx, "_dates"):
            ctx._dates = {m.date for m in find_dates(ctx.question + "\n" + ctx.user_message)}
        return ctx._dates

    def raw_answer(self, parsed: dict) -> dict:
        """The model's output in the contract shape, with no checks applied.
        Works on any reply shape: list items that are not objects are kept as {"raw": item}."""
        def items(key):
            val = parsed.get(key)
            return val if isinstance(val, list) else ([] if val is None else [val])

        def cited(c):
            if not isinstance(c, dict):
                return {"raw": c}
            return {"code": c.get("code"), "date": c.get("date"), "title": c.get("title"), "url": None,
                    "quote": c.get("quote", ""), "page": c.get("page")}

        def newer(n):
            if not isinstance(n, dict):
                return {"raw": n}
            return {"code": n.get("code"), "date": n.get("date"), "what_changed": n.get("what_changed", "")}

        ans = parsed.get("answer")
        return {
            "status": parsed.get("status"),
            "answer": ans.strip() if isinstance(ans, str) else ("" if ans is None else str(ans)),
            "cited": [cited(c) for c in items("cited")],
            "newer": [newer(n) for n in items("newer")],
            "coverage": COVERAGE,
        }

    def finalize(self, ctx: Context, parsed: dict) -> tuple[dict, list[dict], list[str]]:
        """Apply the post-answer checks. Returns (checked answer, corrections, flags).

        corrections: every change made to the model's output, as
            {"check", "where", "before", "after"}
        flags: problems found but left in place (quote not found, wording, ...)
        """
        corrections, flags = [], []
        given_groups = {self.rt.group_of[c] for c in ctx.given_codes}

        def fix(check, where, before, after):
            corrections.append({"check": check, "where": where, "before": before, "after": after})

        given_by_date: dict[str, set] = {}
        for c in ctx.given_codes:
            for m in self.rt.members[self.rt.group_of[c]]:
                given_by_date.setdefault(self.rt.grs[m]["date"], set()).add(self.rt.group_of[m])

        def resolve(code, date=None, where=None) -> str | None:
            code = (code or "").strip()
            if code in self.rt.group_of and self.rt.group_of[code] in given_groups:
                return code
            # A mistyped code whose stated date matches exactly one GR given to the
            # model is repaired to that GR (logged as a correction).
            groups = given_by_date.get((date or "").strip(), set())
            if code not in self.rt.group_of and len(groups) == 1:
                fixed = next(iter(groups))
                fix("repair_code_by_date", f"{where}.code", code, fixed)
                return fixed
            return None

        cited = []
        for i, c in enumerate(parsed.get("cited", [])):
            where = f"cited[{i}]"
            code = resolve(c.get("code"), c.get("date"), where)
            if code is None:
                known = (c.get("code") or "").strip() in self.rt.group_of
                fix("drop_unknown_code", where,
                    {"code": c.get("code"), "date": c.get("date")},
                    "dropped (" + ("in corpus but not given to the model" if known else "not a corpus GR code") + ")")
                continue
            quote = c.get("quote", "")
            page, found = self._find_quote(code, quote)
            if not found:
                for twin in self.rt.members[self.rt.grs[code]["group"]]:
                    if twin != code:
                        page, found = self._find_quote(twin, quote)
                        if found:
                            fix("move_quote_to_twin", f"{where}.code", code, twin)
                            code = twin
                            break
            g = self.rt.grs[code]
            if (c.get("date") or "").strip() != g["date"]:
                fix("date_from_metadata", f"{where}.date", c.get("date"), g["date"])
            if (c.get("title") or "").strip() != g["title"].strip():
                fix("title_from_metadata", f"{where}.title", c.get("title"), g["title"].strip())
            if not found:
                flags.append(f"{where}: quote not found in the original text of {code}")
            elif page is not None and page != c.get("page"):
                fix("page_from_quote", f"{where}.page", c.get("page"), page)
            cited.append({"code": code, "date": g["date"], "title": g["title"].strip(), "url": g["url"],
                          "quote": quote, "page": page if page is not None else c.get("page"),
                          "quote_verified": found})

        newer = []
        for i, n in enumerate(parsed.get("newer", [])):
            where = f"newer[{i}]"
            code = resolve(n.get("code"), n.get("date"), where)
            if code is None:
                known = (n.get("code") or "").strip() in self.rt.group_of
                fix("drop_unknown_code", where, {"code": n.get("code"), "date": n.get("date")},
                    "dropped (" + ("in corpus but not given to the model" if known else "not a corpus GR code") + ")")
                continue
            d = self.rt.grs[code]["date"]
            if (n.get("date") or "").strip() != d:
                fix("date_from_metadata", f"{where}.date", n.get("date"), d)
            newer.append({"code": code, "date": d, "what_changed": n.get("what_changed", "")})
        order = sorted(range(len(newer)), key=lambda k: date_key(newer[k]["date"]))
        if order != list(range(len(newer))):
            fix("sort_newer_by_date", "newer", [n["code"] for n in newer], [newer[k]["code"] for k in order])
            newer = [newer[k] for k in order]

        # Only candidates of the asked-for GR must be reviewed. If the model names no
        # asked-for GR (or one not given to it), nothing is checked.
        asked = (parsed.get("asked_for_code") or "").strip()
        asked_group = self.rt.group_of.get(asked) if asked else None
        if asked_group in given_groups:
            reviewed = {self.rt.group_of.get(r.get("code", ""), r.get("code"))
                        for r in parsed.get("candidates_reviewed", [])}
            owed = list(dict.fromkeys(c["code"] for c in ctx.candidates if c["of_code"] == asked_group))
            unreviewed = [c for c in owed if c not in reviewed]
            if unreviewed:
                flags.append(f"candidates of the asked-for GR not reviewed: {', '.join(unreviewed)}")

        # A date in the answer text that is no cited or newer GR's date is flagged
        # (not corrected). The flag says whether the date occurs in the given texts.
        gr_dates = {c.get("date") for c in cited} | {n.get("date") for n in newer}
        for d in dict.fromkeys(m.date for m in find_dates(parsed.get("answer") or "")):
            if d not in gr_dates:
                where = ("occurs in the texts given" if d in self._given_dates(ctx)
                         else "occurs nowhere in the question or the texts given")
                flags.append(f"date in answer matches no cited or newer GR: {d} ({where})")

        # Answer-first rule (flags only)
        answer_text = (parsed.get("answer") or "").strip()
        first = first_sentence(answer_text)
        says_not_found = bool(COULDNT_FIND.search(first))
        if parsed.get("status") == "not_found" and not says_not_found:
            flags.append("answer-first: status not_found but first sentence does not say it couldn't find")
        if parsed.get("status") == "answered" and says_not_found:
            flags.append("answer-first: status answered but first sentence says it couldn't find")
        if COULDNT_FIND.search(answer_text) and asked_group and asked_group in {self.rt.group_of.get(c["code"]) for c in cited}:
            flags.append("answer-first: says it couldn't find the GR while citing the asked-for GR")

        answer = (parsed.get("answer") or "").strip()
        if BARE_IN_FORCE.search(answer):
            flags.append("wording: bare 'in force'")
        if DOES_NOT_EXIST.search(answer):
            flags.append("wording: says a GR does not exist")
        if parsed.get("status") not in ("answered", "not_found"):
            flags.append(f"bad status {parsed.get('status')!r}")

        result = {"status": parsed.get("status"), "answer": answer, "cited": cited, "newer": newer,
                  "coverage": COVERAGE}
        return result, corrections, flags


def parse_json(text: str | None) -> tuple[dict, list[str]]:
    """Parse the model's JSON. Returns (object, duplicate top-level keys).

    With a duplicated key the last value wins (as json.loads does); the
    duplicate is reported so it shows in the run log."""
    if not text:
        raise ValueError("empty content")
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in content")
    dups: list[str] = []

    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                dups.append(k)
            seen.add(k)
        return dict(pairs)
    obj = json.loads(text[start:end + 1], object_pairs_hook=hook)
    return obj, dups


def validate(parsed: dict | None, dups: list[str]) -> list[str]:
    """Problems that make a reply invalid against the answer schema."""
    if parsed is None:
        return ["not a JSON object"]
    errs = []
    if dups:
        errs.append(f"duplicate keys: {', '.join(sorted(set(dups)))}")
    props = ANSWER_SCHEMA["properties"]
    for key in ANSWER_SCHEMA["required"]:
        if key not in parsed:
            errs.append(f"missing field: {key}")
    extra = set(parsed) - set(props)
    if extra:
        errs.append(f"unexpected fields: {', '.join(sorted(extra))}")
    if parsed.get("status") not in ("answered", "not_found"):
        errs.append(f"bad status: {parsed.get('status')!r}")
    if not isinstance(parsed.get("answer"), str) or not parsed.get("answer", "").strip():
        errs.append("empty or non-string answer")
    afc = parsed.get("asked_for_code")
    if "asked_for_code" in parsed and afc is not None and not isinstance(afc, str):
        errs.append("asked_for_code is not a string or null")
    for arr, item_req in (("candidates_reviewed", ("code", "effect")),
                          ("newer", ("code", "date", "what_changed")),
                          ("cited", ("code", "date", "title", "quote", "page"))):
        val = parsed.get(arr)
        if arr in parsed and not isinstance(val, list):
            errs.append(f"{arr} is not a list")
            continue
        for i, it in enumerate(val or []):
            if not isinstance(it, dict):
                errs.append(f"{arr}[{i}] is not an object")
                continue
            miss = [k for k in item_req if k not in it]
            if miss:
                errs.append(f"{arr}[{i}] missing {', '.join(miss)}")
            if arr == "cited" and "page" in it and not isinstance(it["page"], int):
                errs.append(f"cited[{i}].page is not an integer")
            if arr == "candidates_reviewed" and it.get("effect") not in props[arr]["items"]["properties"]["effect"]["enum"]:
                errs.append(f"candidates_reviewed[{i}] bad effect: {it.get('effect')!r}")
    return errs


def repair_reply(parsed: dict | None) -> tuple[dict | None, list[str]]:
    """Two harmless format slips, fixed and logged (never content):
      - asked_for_code missing -> null
      - a review entry keyed by its code, {"<code>": {"effect", "reason"}} -> flattened
    """
    if not isinstance(parsed, dict):
        return parsed, []
    repairs = []
    if "asked_for_code" not in parsed and "status" in parsed:
        parsed["asked_for_code"] = None
        repairs.append("asked_for_code missing -> null")
    items = parsed.get("candidates_reviewed")
    if isinstance(items, list):
        for k, it in enumerate(items):
            if isinstance(it, dict) and "effect" not in it:
                inner = [(key, v) for key, v in it.items() if isinstance(v, dict) and "effect" in v]
                if len(inner) == 1:
                    key, v = inner[0]
                    items[k] = {"code": v.get("code", key), "effect": v.get("effect"), "reason": v.get("reason", "")}
                    repairs.append(f"candidates_reviewed[{k}] keyed by code -> flattened")
    return parsed, repairs


def review_coverage(parsed: dict | None, listed: list[str], group_of: dict) -> list[str]:
    """Listed candidate codes with no review entry."""
    if not isinstance(parsed, dict) or not isinstance(parsed.get("candidates_reviewed"), list):
        return list(listed)
    seen = {group_of.get(str(r.get("code", "")).strip(), str(r.get("code", "")).strip())
            for r in parsed["candidates_reviewed"] if isinstance(r, dict)}
    return [c for c in listed if c not in seen]


def _attempt(client, messages, est_tokens, listed, group_of, why) -> dict:
    call = client.chat(messages, max_tokens=MAX_TOKENS, reasoning_effort=REASONING_EFFORT,
                       temperature=TEMPERATURE, response_format={"type": "json_object"},
                       prompt_tokens_estimate=est_tokens)
    choice = (call.response.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content")
    parsed, dups, parse_error = None, [], None
    if not (content or "").strip():
        parse_error = "empty reply"
    else:
        try:
            parsed, dups = parse_json(content)
            if not isinstance(parsed, dict):
                parsed = None
        except (ValueError, json.JSONDecodeError) as e:
            parse_error = f"{type(e).__name__}: {e}"
    parsed, repairs = repair_reply(parsed)
    errors = validate(parsed, dups)
    if parse_error:
        errors.insert(0, f"could not parse: {parse_error}")
    missing = review_coverage(parsed, listed, group_of) if parsed is not None else []
    if missing:
        errors.append(f"no review for listed candidates: {', '.join(missing)}")
    return {"call": call, "finish_reason": choice.get("finish_reason"), "content": content, "why": why,
            "parsed": parsed, "dups": dups, "repairs": repairs, "errors": errors, "missing_reviews": missing}


CHANGING_EFFECTS = ("amends", "replaces")
_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _norm_num(x: str) -> str:
    return x.replace(",", "").lstrip("0") or "0"


def _values(text: str) -> set[str]:
    """Dates (as dd-mm-yyyy) and other numbers (commas removed, 2+ digits) in a text."""
    t = to_ascii_digits(text or "")
    found = find_dates(t)
    vals = {d.date for d in found}
    for d in sorted(found, key=lambda d: -d.start):  # numbers inside dates are not values
        t = t[:d.start] + " " + t[d.end:]
    vals |= {_norm_num(n) for n in _NUM.findall(t) if len(_norm_num(n)) >= 2}
    return vals


# Words that describe a change rather than state the rule
_CHANGE_WORDS = set("""amend amended amendment amends replace replaced replaces change changed changes
paragraph para point line add added adds clarify clarified clarifies extend extended extends earlier
new rule govern government resolution circular corrigendum addendum dated date read instead from
require required requires gr grs original first word words supersede supersedes superseded
revoke revokes revoked cancel cancels cancelled withdraw withdrawn stay stayed stays""".split())


def _words(text: str) -> set[str]:
    from .search import _stem, analyze
    stems = {_stem(w) for w in _CHANGE_WORDS}
    return {w for w in analyze(text or "") if len(w) >= 2 and not w.isdigit() and w not in stems}


def current_rule_check(answerer: "Answerer", ctx: "Context", parsed: dict) -> dict:
    """When `newer` holds a GR that amends or replaces the asked-for GR, the first
    sentence must state the rule as it stands after the newest such change. Passes
    if the first sentence names that GR's date, or a value or a distinctive word
    from its change that is in neither the asked-for GR's text nor the question.
    Not applied to not_found answers. Returns {"applies", "ok", "detail"}."""
    if parsed.get("status") == "not_found":
        return {"applies": False, "ok": True, "detail": "status not_found"}
    rt = answerer.rt
    effects = {}
    for r in parsed.get("candidates_reviewed") or []:
        if isinstance(r, dict) and r.get("code"):
            effects[rt.group_of.get(str(r["code"]).strip(), str(r["code"]).strip())] = r.get("effect")
    given_by_date = {}
    for c in ctx.given_codes:
        given_by_date.setdefault(rt.grs[c]["date"], set()).add(rt.group_of[c])
    changing = []
    for n in parsed.get("newer") or []:
        if not isinstance(n, dict):
            continue
        code = str(n.get("code") or "").strip()
        gid = rt.group_of.get(code)
        if gid is None:  # mistyped code: same repair rule as the product check
            g = given_by_date.get(str(n.get("date") or "").strip(), set())
            gid = next(iter(g)) if len(g) == 1 else None
        if gid is None:
            continue
        if effects.get(gid, "amends") in CHANGING_EFFECTS:
            changing.append((gid, n))
    if not changing:
        return {"applies": False, "ok": True, "detail": "no amending or replacing GR in newer"}
    gid, n = max(changing, key=lambda x: date_key(rt.grs[x[0]]["date"]))
    newest_date = rt.grs[gid]["date"]
    first = first_sentence(parsed.get("answer") or "")
    asked = rt.group_of.get(str(parsed.get("asked_for_code") or "").strip())
    old_text = ctx.question
    if asked:
        pg = answerer.pages.get(asked, {})
        old_text += "\n" + "\n".join(pg.get("orig", {}).values()) + "\n" + "\n".join(pg.get("en", {}).values())
    changed = n.get("what_changed") or ""
    if newest_date in _values(first):
        return {"applies": True, "ok": True, "detail": f"first sentence names {newest_date}"}
    new_vals = (_values(changed) - _values(old_text)) & _values(first)
    if new_vals:
        return {"applies": True, "ok": True, "detail": f"first sentence states new value(s) {', '.join(sorted(new_vals))}"}
    new_words = (_words(changed) - _words(old_text) - _CHANGE_WORDS) & _words(first)
    if new_words:
        return {"applies": True, "ok": True, "detail": f"first sentence states new term(s) {', '.join(sorted(new_words))}"}
    return {"applies": True, "ok": False,
            "detail": f"first sentence names neither the newest change's date {newest_date} ({gid}) "
                      f"nor anything new from that change"}


def sanitize_for_product(parsed: dict | None) -> tuple[dict, list[dict]]:
    """Turn a reply that failed format into something the product checks can run on.
    Every change is returned as a correction (check "format_repair")."""
    fixes = []

    def fix(where, before, after):
        fixes.append({"check": "format_repair", "where": where, "before": before, "after": after})
    if not isinstance(parsed, dict):
        fix("reply", "no JSON object", "placeholder not_found answer")
        return ({"status": "not_found", "answer": "No answer could be produced for this question (the model reply "
                 "could not be read).", "asked_for_code": None, "cited": [], "newer": [],
                 "candidates_reviewed": []}, fixes)
    out = dict(parsed)
    ans = out.get("answer")
    if not isinstance(ans, str) or not ans.strip():
        fix("answer", ans, "placeholder")
        out["answer"] = "No answer text was produced for this question."
    if out.get("status") not in ("answered", "not_found"):
        new = "not_found" if COULDNT_FIND.search(out["answer"]) else "answered"
        fix("status", out.get("status"), new)
        out["status"] = new
    for key, need in (("cited", ("code",)), ("newer", ("code",)), ("candidates_reviewed", ("code",))):
        val = out.get(key)
        if not isinstance(val, list):
            if val is not None:
                fix(key, val, [])
            out[key] = []
            continue
        keep = []
        for k, it in enumerate(val):
            if isinstance(it, dict) and all(it.get(x) for x in need):
                keep.append(it)
            else:
                fix(f"{key}[{k}]", it, "dropped (malformed)")
        out[key] = keep
    if "asked_for_code" not in out or not isinstance(out.get("asked_for_code"), (str, type(None))):
        out["asked_for_code"] = None
    return out, fixes


def answer_question(answerer: Answerer, client, question: str) -> dict:
    """One full answer, with everything E4 logs.

    Attempts (at most 3 calls):
      - an invalid reply (schema, empty, a listed candidate without a review) is
        retried once with the same prompt; after a length-limit reply the retry
        uses a compact context (and one further compact try is allowed);
      - a valid reply that fails the current-rule-first check is retried once.
    Every attempt is logged. The scored raw answer is the best attempt: valid and
    passing the rule check, else the last valid one, else the least broken.
    If no attempt is valid, the product still shows the least broken reply's
    answer and status with the checks applied, marked "format repaired".
    """
    ctx = answerer.build_context(question)
    compact_ctx = None
    sys_msg = {"role": "system", "content": answerer.system_prompt}

    def messages_for(c):
        return [sys_msg, {"role": "user", "content": c.user_message}]

    def est(msgs):
        return int(sum(len(m["content"]) for m in msgs) / CHARS_PER_TOKEN_ESTIMATE)

    def run(c, why):
        m = messages_for(c)
        a = _attempt(client, m, est(m), c.listed_candidates, answerer.rt.group_of, why)
        a["rule"] = None
        if not a["errors"]:
            try:
                a["rule"] = current_rule_check(answerer, c, a["parsed"])
            except Exception as e:
                a["rule"] = {"applies": False, "ok": True, "detail": f"check error: {type(e).__name__}: {e}"}
        attempts.append(a)
        used_ctx.append(c)

    t0 = time.monotonic()
    attempts, used_ctx = [], []
    run(ctx, "first")
    format_retry = rule_retry = False
    while len(attempts) < 3:
        last = attempts[-1]
        if last["errors"]:
            if last["finish_reason"] == "length":
                if compact_ctx is None:
                    compact_ctx = answerer.build_context(question, compact=True)
                run(compact_ctx, "length limit: compact context")
            elif not format_retry:
                format_retry = True
                run(used_ctx[-1], "invalid reply: same prompt")
            else:
                break
        elif last["rule"] and not last["rule"]["ok"] and not rule_retry:
            rule_retry = True
            run(used_ctx[-1], "current rule not first: same prompt")
        else:
            break

    valid = [k for k, a in enumerate(attempts) if not a["errors"]]
    passing = [k for k in valid if attempts[k]["rule"] and attempts[k]["rule"]["ok"]]
    if passing:
        chosen = passing[-1]
    elif valid:
        chosen = valid[-1]
    else:
        chosen = min(range(len(attempts)),
                     key=lambda k: (attempts[k]["parsed"] is None, len(attempts[k]["errors"]), -k))
    pick, pick_ctx = attempts[chosen], used_ctx[chosen]
    format_failed_first = bool(attempts[0]["errors"])
    if valid:
        if chosen == 0:
            fmt = "repaired" if pick["repairs"] else "ok"
        else:
            fmt = "retried_ok" if format_failed_first else ("repaired" if pick["repairs"] else "ok")
    else:
        fmt = "failed"

    issues, corrections, raw_answer, result = [], [], None, None
    parsed = pick["parsed"]
    try:
        if parsed is not None:
            raw_answer = answerer.raw_answer(parsed)
        if valid:
            result, corrections, issues = answerer.finalize(pick_ctx, parsed)
        else:
            clean, fixes = sanitize_for_product(parsed)
            result, corrections, issues = answerer.finalize(pick_ctx, clean)
            corrections = fixes + corrections
            result["format_repaired"] = True
            issues.insert(0, "format repaired: the product shows the least broken reply with the checks applied")
    except Exception as e:  # never lose a reply: log it
        result, corrections = None, []
        issues = [f"processing error (reply kept in log): {type(e).__name__}: {e}"]
        fmt = "failed"
    if not valid:
        issues.append("format failure after retry: " + "; ".join(pick["errors"]))
    if pick["rule"] and not pick["rule"]["ok"]:
        issues.append("current-rule-first: " + pick["rule"]["detail"])
    if pick["finish_reason"] != "stop":
        issues.append(f"finish_reason={pick['finish_reason']}")

    usage = _sum_usage([a["call"].usage for a in attempts])
    return {
        "context": pick_ctx,
        "messages": messages_for(pick_ctx),
        "format": fmt,
        "chosen_attempt": chosen,
        "rule_check": pick["rule"],
        "format_attempts": [{"why": a["why"], "model_content": a["content"], "errors": a["errors"],
                             "repairs": a["repairs"], "missing_reviews": a["missing_reviews"],
                             "rule_check": a["rule"],
                             "usage": a["call"].usage, "finish_reason": a["finish_reason"],
                             "latency_s": round(a["call"].latency_s, 2)} for a in attempts],
        "raw_response": pick["call"].response,
        "model_content": pick["content"],
        "parsed_model_output": parsed,
        "raw_answer": raw_answer,
        "result": result,
        "corrections": corrections,
        "issues": issues,
        "usage": usage,
        "latency_s": round(sum(a["call"].latency_s for a in attempts), 2),
        "total_s": round(time.monotonic() - t0, 2),
        "attempts": sum(a["call"].attempts for a in attempts),
        "retries": [r for a in attempts for r in a["call"].retries],
        "settings": {"model": "sarvam-105b", "max_tokens": MAX_TOKENS, "reasoning_effort": REASONING_EFFORT,
                     "temperature": TEMPERATURE, "response_format": "json_object",
                     "prompt_version": PROMPT_VERSION},
    }


def _sum_usage(usages: list[dict]) -> dict:
    keys = ("prompt_tokens", "cached_tokens", "completion_tokens", "reasoning_tokens", "total_tokens")
    out = {k: sum(u[k] for u in usages) for k in keys}
    out["cost_inr"] = round(sum(u["cost_inr"] for u in usages), 6)
    out["calls"] = len(usages)
    return out
