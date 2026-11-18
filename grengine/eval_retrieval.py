"""E2 retrieval check on the 37 eval questions. No model calls.

A question is a hit when any of its gold_grs codes (or a twin of one) is in the
top 5 retrieved results. Twins share one result slot.

Usage:
    python -m grengine.eval_retrieval [--k 5] [--out eval/results]
Writes <out>/e2_retrieval.md and <out>/e2_retrieval.json.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from .citations import newer_candidates
from .dates import date_key
from .search import Retriever

QUESTIONS = Path("eval/questions.jsonl")
MISSING_GR_IDS = [9, 16, 36, 37]
CONTROL_IDS = [30, 31, 32, 33, 34, 35]
CLOUD_IDS = [1, 2, 3, 4, 5, 6]


def load_questions(path: Path = QUESTIONS) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def run(retriever: Retriever, questions: list[dict], k: int) -> list[dict]:
    rows = []
    for q in questions:
        hits = retriever.search(q["question"], k=k)
        gold_groups = {retriever.group_of[c] for c in q["gold_grs"] if c in retriever.group_of}
        rank = next((i + 1 for i, h in enumerate(hits) if h.group in gold_groups), None)
        rows.append({
            "id": q["id"], "question": q["question"], "task": q["task"], "case": q["case"],
            "lang": q["lang"], "gold_grs": q["gold_grs"],
            "unknown_gold": [c for c in q["gold_grs"] if c not in retriever.group_of],
            "parsed": retriever.parse_query(q["question"]),
            "hit": rank is not None, "rank": rank,
            "results": [{"group": h.group, "codes": h.codes, "score": h.score,
                         "reasons": h.reasons} for h in hits],
        })
    return rows


def _rate(rows):
    n = len(rows)
    h = sum(r["hit"] for r in rows)
    return f"{h}/{n} ({100 * h / n:.0f}%)" if n else "-"


def _gr_line(rt: Retriever, code: str) -> str:
    g = rt.grs[code]
    return f"{g['date']} `{code}` {g['title'][:70].strip()}"


def _candidates_table(rt: Retriever, code: str) -> list[str]:
    cands = newer_candidates(code, rt.graph, rt.group_of)
    if not cands:
        return ["  - none (no GR in the corpus cites it)"]
    out = []
    for c in cands:
        flag = " (candidate only)" if c["candidate_only"] else ""
        hop = "" if c["hops"] == 1 else f", {c['hops']} hops"
        out.append(f"  - {c['from_date']} `{c['from']}` {rt.grs[c['from']]['title'][:60].strip()} "
                   f"— **{c['best_evidence']}**{flag}{hop}")
    return out


def report(rt: Retriever, rows: list[dict], k: int) -> str:
    L = []
    L.append(f"# E2 retrieval check (top {k})\n")
    L.append("No model calls. Hit = a gold GR (or its twin) is in the top 5; twins share one slot.\n")
    L.append(f"**Overall: {_rate(rows)}**\n")

    def split(label, keyf):
        groups = defaultdict(list)
        for r in rows:
            for v in keyf(r):
                groups[v].append(r)
        L.append(f"| {label} | hit rate |\n|---|---|")
        for v in sorted(groups):
            L.append(f"| {v} | {_rate(groups[v])} |")
        L.append("")

    L.append("## By split\n")
    L.append("`lang` is the language of the gold GRs (EN,MR = both, e.g. twins). "
             "Questions with two case tags count under each.\n")
    split("lang", lambda r: [r["lang"]])
    split("task", lambda r: [r["task"]])
    split("case", lambda r: r["case"].split(","))

    ranks = defaultdict(int)
    for r in rows:
        ranks[r["rank"]] += 1
    L.append("Rank of first gold GR: " + ", ".join(
        f"{'miss' if k2 is None else f'#{k2}'}: {v}" for k2, v in sorted(ranks.items(), key=lambda x: (x[0] is None, x[0] or 0))) + "\n")

    L.append("## Misses\n")
    misses = [r for r in rows if not r["hit"]]
    if not misses:
        L.append("None.\n")
    for r in misses:
        L.append(f"### Q{r['id']} ({r['task']}, {r['case']}, {r['lang']}): {r['question']}\n")
        L.append("Gold:")
        for c in r["gold_grs"]:
            L.append(f"- {_gr_line(rt, c)}")
        L.append("\nReturned instead:")
        for i, h in enumerate(r["results"], 1):
            L.append(f"{i}. {_gr_line(rt, h['group'])} — score {h['score']} {h['reasons']}")
        L.append("")

    L.append("## Hits not at rank 1\n")
    L.append("| Q | gold rank | ranked above it |\n|---|---|---|")
    for r in rows:
        if r["hit"] and r["rank"] > 1:
            above = "; ".join(_gr_line(rt, h["group"]) for h in r["results"][: r["rank"] - 1])
            L.append(f"| {r['id']} | {r['rank']} | {above} |")
    L.append("")

    L.append("## Missing-GR questions (9, 16, 36, 37)\n")
    L.append("The asked-for GR is not in the corpus. The right result is a GR that cites it; "
             "the answer must say the asked-for GR isn't in the corpus.\n")
    for r in [r for r in rows if r["id"] in MISSING_GR_IDS]:
        p = r["parsed"]
        missing_dates = [d for d in p["dates"] if not rt.lookup_date(d)]
        L.append(f"### Q{r['id']}: {r['question']}\n")
        L.append(f"- Hit: {'yes, rank ' + str(r['rank']) if r['hit'] else 'NO'}")
        if missing_dates:
            for d in missing_dates:
                citers = sorted(rt.citers_of_date.get(d, ()), key=lambda c: date_key(rt.grs[c]["date"]))
                L.append(f"- Asked-for date {d}: no GR in the corpus has this date. "
                         f"Cited by: " + (", ".join(f"{rt.grs[c]['date']} `{c}`" for c in citers) or "none"))
        else:
            L.append("- No full date in the question" + (f" (year {p['years']})" if p["years"] else "")
                     + ": the missing-GR signal has to come from the answer step (no exact match).")
        L.append("- Top 5:")
        for i, h in enumerate(r["results"], 1):
            L.append(f"  {i}. {_gr_line(rt, h['group'])} {h['reasons']}")
        L.append("")

    for title, ids in (("Controls (30 to 35)", CONTROL_IDS), ("Cloud chain (1 to 6)", CLOUD_IDS)):
        L.append(f"## Newer-GR candidates: {title}\n")
        L.append("For the top retrieved GR, and for each gold GR not already shown. Ranked by evidence: "
                 "date+order, order, date, same_file. *Candidate only* = only a shared file number; "
                 "never proof of a newer GR.\n")
        for r in [r for r in rows if r["id"] in ids]:
            L.append(f"### Q{r['id']}: {r['question']}\n")
            anchors = []
            if r["results"]:
                anchors.append(("top result", r["results"][0]["group"]))
            for c in sorted(r["gold_grs"], key=lambda c: date_key(rt.grs[c]["date"])):
                if rt.group_of[c] not in [a for _, a in anchors]:
                    anchors.append(("gold", rt.group_of[c]))
            for label, code in anchors:
                L.append(f"- {label}: {_gr_line(rt, code)}")
                L.extend(_candidates_table(rt, code))
            L.append("")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--out", type=Path, default=Path("eval/results"))
    args = ap.parse_args()
    rt = Retriever()
    rows = run(rt, load_questions(), args.k)
    args.out.mkdir(parents=True, exist_ok=True)
    md = report(rt, rows, args.k)
    (args.out / "e2_retrieval.md").write_text(md + "\n", encoding="utf-8")
    (args.out / "e2_retrieval.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Overall hit@{args.k}: {_rate(rows)}")
    for r in rows:
        if not r["hit"]:
            print(f"  MISS Q{r['id']}: {r['question']}")
    print(f"Report: {args.out}/e2_retrieval.md")


if __name__ == "__main__":
    main()
