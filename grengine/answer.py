"""E3 answer step: retrieved GRs + newer-GR candidates -> sarvam-105b -> answer contract.

The model gets full texts. Everything it returns is checked before it reaches
the answer contract:
  - cited/newer codes must be GRs that were given to it (others are dropped and flagged)
  - date, title and url always come from the metadata, never from the model
  - each quote is searched in the GR's original text; its page is taken from
    where it is found (flagged if not found)
  - wording rules are checked (bare "in force", "does not exist")
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
from .search import INDEX_DIR, Retriever

PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_VERSION = "answer_v1"

TOP_K = 5                 # retrieved GRs given in full
CANDIDATE_SOURCES = 3     # newer-GR candidates are collected for the top 3 retrieved GRs
MAX_CANDIDATES = 10
MAX_ORIG_CHARS = 9000     # per GR; longer texts are cut (and marked)
MAX_EN_CHARS = 5000       # English machine translation of Marathi GRs, for reference
MAX_TOKENS = 4096
REASONING_EFFORT = "low"
TEMPERATURE = 0.2
CHARS_PER_TOKEN_ESTIMATE = 2.0  # conservative, for the pre-call spend check only

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["answered", "not_found"]},
        "answer": {"type": "string"},
        "asked_for_code": {"type": ["string", "null"]},
        "cited": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"}, "quote": {"type": "string"}, "page": {"type": "integer"}},
            "required": ["code", "quote", "page"], "additionalProperties": False}},
        "candidates_reviewed": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"},
                           "effect": {"type": "string", "enum": ["amends", "replaces", "stays", "extends",
                                                                  "clarifies", "cites_only", "unrelated"]},
                           "reason": {"type": "string"}},
            "required": ["code", "effect", "reason"], "additionalProperties": False}},
        "newer": {"type": "array", "items": {
            "type": "object",
            "properties": {"code": {"type": "string"}, "what_changed": {"type": "string"}},
            "required": ["code", "what_changed"], "additionalProperties": False}},
    },
    "required": ["status", "answer", "asked_for_code", "cited", "candidates_reviewed", "newer"],
    "additionalProperties": False,
}

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
        self.system_prompt = load_prompt()

    # ---- context ------------------------------------------------------------
    def _doc(self, code: str, header: str) -> str:
        g = self.rt.grs[code]
        orig = "\n".join(f"# Page {p}\n{t}" for p, t in sorted(self.pages[code]["orig"].items()))
        if len(orig) > MAX_ORIG_CHARS:
            orig = orig[:MAX_ORIG_CHARS] + "\n[... text cut here for length ...]"
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
        if g["original_lang"] == "mr":
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

    def build_context(self, question: str) -> Context:
        hits = self.rt.search(question, k=TOP_K)
        retrieved = [{"code": h.group, "date": self.rt.grs[h.group]["date"], "title": self.rt.grs[h.group]["title"],
                      "score": h.score, "reasons": h.reasons} for h in hits]
        given = [h.group for h in hits]

        cands, seen = [], set(given)
        for h in hits[:CANDIDATE_SOURCES]:
            for c in newer_candidates(h.group, self.rt.graph, self.rt.group_of):
                gid = self.rt.group_of[c["from"]]
                if gid in seen:
                    # already given (retrieved); still record the link
                    cands.append({"code": gid, "of_code": h.group, "evidence": c["evidence"],
                                  "best_evidence": c["best_evidence"], "hops": c["hops"],
                                  "candidate_only": c["candidate_only"], "already_retrieved": True})
                    continue
                seen.add(gid)
                cands.append({"code": gid, "of_code": h.group, "evidence": c["evidence"],
                              "best_evidence": c["best_evidence"], "hops": c["hops"],
                              "candidate_only": c["candidate_only"], "already_retrieved": False})
        new_cands = [c for c in cands if not c["already_retrieved"]][:MAX_CANDIDATES]
        kept = {c["code"] for c in new_cands}
        cands = [c for c in cands if c["already_retrieved"] or c["code"] in kept]
        for c in cands:
            c["date"], c["title"] = self.rt.grs[c["code"]]["date"], self.rt.grs[c["code"]]["title"]
        given += [c["code"] for c in new_cands]

        facts = self._date_facts(question)
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
        parts += ["", "RETRIEVED GRS (search rank order):"]
        for i, h in enumerate(hits, 1):
            parts.append(self._doc(h.group, f"RETRIEVED #{i}"))
        parts += ["", "NEWER-GR CANDIDATES (leads only; read each text and decide):"]
        if not cands:
            parts.append("(none: no corpus GR cites the top retrieved GRs)")
        for c in cands:
            ev = ", ".join(c["evidence"])
            note = " Only a shared file number links them; this alone proves nothing." if c["candidate_only"] else ""
            line = (f"- {c['code']} ({c['date']}) cites {c['of_code']} "
                    f"[{self.rt.grs[c['of_code']]['date']}]; evidence: {ev}; hops: {c['hops']}.{note}")
            if c["already_retrieved"]:
                parts.append(line + " Its text is above among the retrieved GRs.")
        for c in new_cands:
            ev = ", ".join(c["evidence"])
            note = " Only a shared file number links them; this alone proves nothing." if c["candidate_only"] else ""
            parts.append(self._doc(
                c["code"], f"CANDIDATE: cites {c['of_code']} [{self.rt.grs[c['of_code']]['date']}]; "
                           f"evidence: {ev}; hops: {c['hops']}.{note}"))
        return Context(question, retrieved, cands, facts, given, "\n".join(parts))

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

    def finalize(self, ctx: Context, parsed: dict) -> tuple[dict, list[str]]:
        issues = []
        given = set(ctx.given_codes)

        def resolve(code: str) -> str | None:
            code = (code or "").strip()
            if code in self.rt.group_of and self.rt.group_of[code] in {self.rt.group_of[c] for c in given}:
                return code
            return None

        cited = []
        for c in parsed.get("cited", []):
            code = resolve(c.get("code"))
            if code is None:
                issues.append(f"cited code not given to model, dropped: {c.get('code')}")
                continue
            g = self.rt.grs[code]
            page, found = self._find_quote(code, c.get("quote", ""))
            if not found:
                # the quote may be from the twin copy
                for twin in self.rt.members[g["group"]]:
                    if twin != code:
                        page, found = self._find_quote(twin, c.get("quote", ""))
                        if found:
                            issues.append(f"quote for {code} found in its twin {twin}")
                            code, g = twin, self.rt.grs[twin]
                            break
            if not found:
                issues.append(f"quote not found in original text of {code}")
            elif page is not None and page != c.get("page"):
                issues.append(f"page for {code} corrected {c.get('page')} -> {page}")
            cited.append({"code": code, "date": g["date"], "title": g["title"], "url": g["url"],
                          "quote": c.get("quote", ""), "page": page if page is not None else c.get("page"),
                          "quote_verified": found})

        newer = []
        for n in parsed.get("newer", []):
            code = resolve(n.get("code"))
            if code is None:
                issues.append(f"newer code not given to model, dropped: {n.get('code')}")
                continue
            newer.append({"code": code, "date": self.rt.grs[code]["date"], "what_changed": n.get("what_changed", "")})
        newer.sort(key=lambda n: date_key(n["date"]))

        reviewed = {self.rt.group_of.get(r.get("code", ""), r.get("code")) for r in parsed.get("candidates_reviewed", [])}
        unreviewed = [c["code"] for c in ctx.candidates if not c["already_retrieved"] and c["code"] not in reviewed]
        if unreviewed:
            issues.append(f"candidates not reviewed by model: {', '.join(unreviewed)}")

        answer = (parsed.get("answer") or "").strip()
        if BARE_IN_FORCE.search(answer):
            issues.append("wording: bare 'in force'")
        if DOES_NOT_EXIST.search(answer):
            issues.append("wording: says a GR does not exist")
        if parsed.get("status") not in ("answered", "not_found"):
            issues.append(f"bad status {parsed.get('status')!r}")

        result = {
            "status": parsed.get("status"),
            "answer": answer,
            "cited": cited,
            "newer": newer,
            "coverage": COVERAGE,
        }
        return result, issues


def parse_json(text: str | None) -> dict:
    if not text:
        raise ValueError("empty content")
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in content")
    return json.loads(text[start:end + 1])


def answer_question(answerer: Answerer, client, question: str) -> dict:
    """One full answer, with everything E4 logs."""
    ctx = answerer.build_context(question)
    messages = [{"role": "system", "content": answerer.system_prompt},
                {"role": "user", "content": ctx.user_message}]
    est_tokens = int(sum(len(m["content"]) for m in messages) / CHARS_PER_TOKEN_ESTIMATE)
    t0 = time.monotonic()
    call = client.chat(messages, max_tokens=MAX_TOKENS, reasoning_effort=REASONING_EFFORT,
                       temperature=TEMPERATURE,
                       response_format={"type": "json_schema",
                                        "json_schema": {"name": "gr_answer", "strict": True, "schema": ANSWER_SCHEMA}},
                       prompt_tokens_estimate=est_tokens)
    choice = (call.response.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    issues, parsed, result, parse_error = [], None, None, None
    try:
        parsed = parse_json(msg.get("content"))
        result, issues = answerer.finalize(ctx, parsed)
    except (ValueError, json.JSONDecodeError) as e:
        parse_error = f"{type(e).__name__}: {e}"
        issues.append(f"could not parse model output: {parse_error}")
    if choice.get("finish_reason") != "stop":
        issues.append(f"finish_reason={choice.get('finish_reason')}")
    return {
        "context": ctx,
        "messages": messages,
        "raw_response": call.response,
        "parsed_model_output": parsed,
        "result": result,
        "issues": issues,
        "usage": call.usage,
        "latency_s": round(call.latency_s, 2),
        "total_s": round(time.monotonic() - t0, 2),
        "attempts": call.attempts,
        "retries": call.retries,
        "settings": {"model": "sarvam-105b", "max_tokens": MAX_TOKENS, "reasoning_effort": REASONING_EFFORT,
                     "temperature": TEMPERATURE, "prompt_version": PROMPT_VERSION},
    }
