"""Before/after table across runs, using automatic measures only (no hand scores).

Usage:
    python -m grengine.compare_runs --out eval/results/v3_before_after \\
        F1=runs/2026-11-18-baseline.jsonl run1=runs/... run2=runs/...

Measures per question and run, on the RAW model answer and on the CHECKED
(product) answer where it differs:
  format        ok / repaired / retried_ok / failed
  status_ok     status matches the expected status (not_found for the
                missing-GR questions, case MI; answered otherwise)
  gold_any      at least one gold GR is among cited or newer codes
  gold_all      every gold GR is among cited or newer codes
  gold_unrev    gold GRs that were candidates of the asked-for GR but got no review
  first         the first sentence of the answer
These are proxies. They do not replace the hand scores in the CSVs.
"""
import argparse
import csv
import json
from pathlib import Path

from .answer import first_sentence


def load(path):
    lines = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return {r["id"]: r for r in lines if r.get("type") == "question"}, lines[-1]


def codes(ans):
    if not ans:
        return set()
    out = set()
    for key in ("cited", "newer"):
        for it in ans.get(key) or []:
            if isinstance(it, dict) and it.get("code"):
                out.add(str(it["code"]).strip())
    return out


def measures(r):
    raw, chk = r.get("raw_answer") or {}, r.get("answer") or {}
    gold = set(r["gold_grs"])
    expected = "not_found" if "MI" in r.get("case", "") else "answered"
    p = r.get("parsed_model_output") or {}
    asked = (p.get("asked_for_code") or "") if isinstance(p, dict) else ""
    reviewed = set()
    if isinstance(p, dict):
        for it in p.get("candidates_reviewed") or []:
            if isinstance(it, dict):
                reviewed.add(str(it.get("code", "")).strip())
    owed = {c["code"] for c in r.get("candidates", []) if c.get("of_code") == asked}
    raw_codes, chk_codes = codes(raw), codes(chk)
    return {
        "format": r.get("format", "ok"),
        "status": raw.get("status"),
        "status_ok": raw.get("status") == expected,
        "gold_any_raw": bool(gold & raw_codes), "gold_any_checked": bool(gold & chk_codes),
        "gold_all_raw": gold <= raw_codes, "gold_all_checked": gold <= chk_codes,
        "gold_unreviewed": sorted((gold & owed) - reviewed),
        "answer_first_flags": sum(1 for f in r.get("issues", []) if f.startswith("answer-first")),
        "quote_not_found": sum(1 for f in r.get("issues", []) if "quote not found" in f),
        "corrections": len(r.get("corrections", [])),
        "product_shown": bool(chk) and bool((chk or {}).get("answer")),
        "format_repaired": bool((chk or {}).get("format_repaired")),
        "rule_flag": any(f.startswith("current-rule-first") for f in r.get("issues", [])),
        "cost": r.get("cost_inr", 0.0),
        "first": first_sentence(raw.get("answer") or ""),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("runs", nargs="+", help="label=path")
    args = ap.parse_args(argv)
    runs = []
    for spec in args.runs:
        label, path = spec.split("=", 1)
        q, end = load(path)
        runs.append((label, path, q, end))
    ids = sorted(set().union(*(set(q) for _, _, q, _ in runs)))
    case = {}
    for _, _, q, _ in runs:
        for i, r in q.items():
            case[i] = r
    with open("eval/questions.jsonl", encoding="utf-8") as f:
        meta = {json.loads(l)["id"]: json.loads(l) for l in f if l.strip()}
    for _, _, q, _ in runs:
        for i, r in q.items():
            r.setdefault("case", meta[i]["case"])

    M = {(label, i): measures(q[i]) for label, _, q, _ in runs for i in ids if i in q}

    # The current-rule-first code check, applied the same way to every run's scored
    # reply (offline), so older runs that predate the check can be compared.
    from .answer import Answerer, current_rule_check
    answerer = Answerer()
    ctx_cache = {}
    for label, _, q, _ in runs:
        for i in ids:
            if i not in q:
                continue
            p = q[i].get("parsed_model_output")
            res = {"applies": False, "ok": True}
            if isinstance(p, dict):
                if i not in ctx_cache:
                    ctx_cache[i] = answerer.build_context(q[i]["question"])
                try:
                    res = current_rule_check(answerer, ctx_cache[i], p)
                except Exception:
                    pass
            M[(label, i)]["rule_applies"] = res["applies"]
            M[(label, i)]["rule_ok"] = res["ok"]
    labels = [l for l, _, _, _ in runs]
    n = len(ids)

    def agg(label, key):
        vals = [M[(label, i)][key] for i in ids if (label, i) in M]
        return sum(bool(v) for v in vals)

    L = ["# Before/after across runs\n",
         "Automatic measures only; they are proxies, not the hand scores. \"Raw\" is the model's "
         "own output; \"checked\" is after the product checks (repairs, drops, metadata).\n",
         "| Run | Log | Prompt |", "|---|---|---|"]
    for label, path, q, end in runs:
        pv = next(iter(q.values())).get("prompt_version")
        L.append(f"| {label} | `{path}` | {pv} |")
    L += ["", "## Totals (37 questions)\n", "| Measure | " + " | ".join(labels) + " |",
          "|---|" + "---|" * len(labels)]

    def row(name, fn):
        L.append(f"| {name} | " + " | ".join(fn(l) for l in labels) + " |")

    def fmt_counts(l):
        c = {}
        for i in ids:
            if (l, i) in M:
                c[M[(l, i)]["format"]] = c.get(M[(l, i)]["format"], 0) + 1
        return ", ".join(f"{k} {v}" for k, v in sorted(c.items()))
    row("Format", fmt_counts)
    row("Format failures", lambda l: str(sum(1 for i in ids if M.get((l, i), {}).get("format") == "failed")))
    row("Product answer shown (checked)", lambda l: f"{agg(l, 'product_shown')}/{n}")
    row("…of which format repaired", lambda l: str(agg(l, "format_repaired")))
    row("Status as expected (raw)", lambda l: f"{agg(l, 'status_ok')}/{n}")
    row("Any gold GR cited or newer (raw)", lambda l: f"{agg(l, 'gold_any_raw')}/{n}")
    row("Any gold GR cited or newer (checked)", lambda l: f"{agg(l, 'gold_any_checked')}/{n}")
    row("All gold GRs cited or newer (raw)", lambda l: f"{agg(l, 'gold_all_raw')}/{n}")
    row("All gold GRs cited or newer (checked)", lambda l: f"{agg(l, 'gold_all_checked')}/{n}")
    row("Questions with a gold GR left unreviewed", lambda l: str(agg(l, "gold_unreviewed")))
    row("Current rule first: holds / applies (code check, all runs)",
        lambda l: f"{sum(1 for i in ids if M.get((l, i), {}).get('rule_applies') and M[(l, i)]['rule_ok'])}"
                  f"/{agg(l, 'rule_applies')}")
    row("Current-rule-first flags in the log (round 2 only)", lambda l: str(agg(l, "rule_flag")))
    row("Answer-first flags", lambda l: str(sum(M[(l, i)]["answer_first_flags"] for i in ids if (l, i) in M)))
    row("Quotes not found", lambda l: str(sum(M[(l, i)]["quote_not_found"] for i in ids if (l, i) in M)))
    row("Corrections by checks", lambda l: str(sum(M[(l, i)]["corrections"] for i in ids if (l, i) in M)))
    row("Calls", lambda l: str(next(e.get("calls", "-") for lb, _, _, e in runs if lb == l)))
    row("Cost (Rs)", lambda l: f"{next(e['cost_inr'] for lb, _, _, e in runs if lb == l):.2f}")

    def mark(v):
        return "✓" if v else "✗"

    L += ["", "## Per question\n",
          "Each cell: format · status as expected · any gold GR (raw/checked) · gold GR left unreviewed.\n",
          "| Q | case | " + " | ".join(labels) + " |", "|---|---|" + "---|" * len(labels)]
    for i in ids:
        cells = []
        for l in labels:
            m = M.get((l, i))
            if not m:
                cells.append("-")
                continue
            cells.append(f"{m['format']} · {mark(m['status_ok'])} · {mark(m['gold_any_raw'])}/{mark(m['gold_any_checked'])}"
                         + (f" · unreviewed {', '.join(m['gold_unreviewed'])}" if m["gold_unreviewed"] else ""))
        L.append(f"| {i} | {meta[i]['case']} | " + " | ".join(cells) + " |")

    L += ["", "## First sentence of the raw answer\n"]
    for i in ids:
        L.append(f"**Q{i}.** {meta[i]['question']}  \n*Gold:* {meta[i]['gold_answer']}")
        for l in labels:
            m = M.get((l, i))
            L.append(f"- {l}: {m['first'] if m and m['first'] else '(no answer)'}")
        L.append("")
    out = Path(args.out)
    out.with_suffix(".md").write_text("\n".join(L) + "\n", encoding="utf-8")

    with out.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["id", "case", "question", "gold_answer"]
        for l in labels:
            cols += [f"{l}_format", f"{l}_status", f"{l}_status_ok", f"{l}_gold_any_raw", f"{l}_gold_any_checked",
                     f"{l}_gold_all_raw", f"{l}_gold_all_checked", f"{l}_gold_unreviewed", f"{l}_first_sentence"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i in ids:
            row_ = {"id": i, "case": meta[i]["case"], "question": meta[i]["question"],
                    "gold_answer": meta[i]["gold_answer"]}
            for l in labels:
                m = M.get((l, i)) or {}
                row_.update({f"{l}_format": m.get("format"), f"{l}_status": m.get("status"),
                             f"{l}_status_ok": m.get("status_ok"), f"{l}_gold_any_raw": m.get("gold_any_raw"),
                             f"{l}_gold_any_checked": m.get("gold_any_checked"),
                             f"{l}_gold_all_raw": m.get("gold_all_raw"),
                             f"{l}_gold_all_checked": m.get("gold_all_checked"),
                             f"{l}_gold_unreviewed": " ".join(m.get("gold_unreviewed", [])),
                             f"{l}_first_sentence": m.get("first")})
            w.writerow(row_)
    print("\n".join(L[: L.index("## Per question\n") + 0]))


if __name__ == "__main__":
    main()
