"""Export logged runs as replay data for the website. No API calls.

Usage (from the repository root):
    python scripts/export_replay.py [--out replay]

Reads eval/questions.jsonl, eval/holdout_questions.jsonl, eval/scores.csv,
corpus/GRs.json and the run logs listed in RUNS. Writes:
    <out>/index.json              one entry per question (52)
    <out>/questions/<id>.json     every run of that question
Full prompt texts are left out (they are in the run logs).
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (set, version, run label, score label in eval/scores.csv or None, run log)
RUNS = [
    ("main", "Baseline", "run 1", "baseline", "runs/2026-11-18-baseline.jsonl"),
    ("main", "Baseline", "run 2", "baseline-run2", "runs/2026-11-21-baseline-run2.jsonl"),
    ("main", "Round 1", "run 1", None, "runs/2026-11-18-v3-run1.jsonl"),
    ("main", "Round 1", "run 2", None, "runs/2026-11-18-v3-run2-2.jsonl"),
    ("main", "Final", "run 1", "final-A", "runs/2026-11-18-v4-run1-2.jsonl"),
    ("main", "Final", "run 2", "final-B", "runs/2026-11-18-v4-run2.jsonl"),
    ("holdout", "Baseline", "run 1", "holdout-old-run1", "runs/2026-11-20-holdout-old-run1.jsonl"),
    ("holdout", "Baseline", "run 2", "holdout-old-run2", "runs/2026-11-20-holdout-old-run2.jsonl"),
    ("holdout", "Final", "run 1", "holdout-final-run1", "runs/2026-11-20-holdout-final-run1.jsonl"),
    ("holdout", "Final", "run 2", "holdout-final-run2", "runs/2026-11-20-holdout-final-run2.jsonl"),
]

FORMAT = {"ok": "ok", "retried_ok": "retried", "repaired": "repaired", "failed": "failed"}


def read_jsonl(path):
    return [json.loads(l) for l in (ROOT / path).read_text(encoding="utf-8").splitlines() if l.strip()]


def load_meta():
    meta = json.loads((ROOT / "corpus/GRs.json").read_text(encoding="utf-8"))
    return {m.get("code") or k.removesuffix(".pdf"): m for k, m in meta.items()}


def load_scores():
    out = {}
    with (ROOT / "eval/scores.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["answer"].strip():
                out[(r["run"], int(r["question_id"]))] = None  # row present, not scored yet
                continue
            out[(r["run"], int(r["question_id"]))] = {
                "answer": int(r["answer"]),
                "citation": r["citation"],
                "latest": r["latest"],
                "confident_wrong": r["confident_wrong"],
                "fully_correct": r["fully_correct"],
                "note": r["note"] or None,
            }
    return out


def cited_items(items, meta, from_product):
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            out.append({"malformed": it})
            continue
        code = str(it.get("code") or "").strip() or None
        m = meta.get(code) if code else None
        out.append({
            "code": code,
            "date": it.get("date"),
            "title": (it.get("title") or "").strip() or None,
            # the product takes the link from the metadata; for the raw answer it is
            # looked up from the code the model gave (null if that code is not a corpus GR)
            "url": it.get("url") if from_product else (m["url"] if m else None),
            "quote": it.get("quote"),
            "page": it.get("page"),
            **({"quote_verified": it.get("quote_verified")} if from_product else {}),
        })
    return out


def newer_items(items):
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            out.append({"malformed": it})
            continue
        out.append({"code": it.get("code"), "date": it.get("date"), "what_changed": it.get("what_changed")})
    return out


def answer_block(ans, meta, from_product):
    if not ans:
        return None
    block = {
        "status": ans.get("status"),
        "answer": ans.get("answer"),
        "cited": cited_items(ans.get("cited"), meta, from_product),
        "newer": newer_items(ans.get("newer")),
    }
    if from_product:
        block["format_repaired"] = bool(ans.get("format_repaired"))
    return block


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="replay")
    args = ap.parse_args(argv)
    out_dir = ROOT / args.out
    (out_dir / "questions").mkdir(parents=True, exist_ok=True)

    meta, scores = load_meta(), load_scores()
    questions = [("main", q) for q in read_jsonl("eval/questions.jsonl")] + \
                [("holdout", q) for q in read_jsonl("eval/holdout_questions.jsonl")]

    runs_by_q = {}
    for qset, version, run_label, score_label, path in RUNS:
        lines = read_jsonl(path)
        start = lines[0]
        for r in lines:
            if r.get("type") != "question":
                continue
            runs_by_q.setdefault(r["id"], []).append({
                "version": version,
                "run": run_label,
                "commit": start.get("git_commit"),
                "prompt_version": start.get("prompt_version"),
                "format": FORMAT.get(r.get("format", "ok"), r.get("format")),
                "product": answer_block(r.get("answer"), meta, True),
                "raw": answer_block(r.get("raw_answer"), meta, False),
                "scores": scores.get((score_label, r["id"])) if score_label else None,
                "log": path,
            })

    index = []
    for qset, q in questions:
        entry = {
            "id": q["id"],
            "set": qset,
            "question": q["question"],
            "case": q["case"],
            "task": q["task"],
            "lang": q["lang"],
            "gold_answer": q["gold_answer"],
            "gold_grs": q["gold_grs"],
        }
        index.append(entry)
        gold = [{"code": c, "date": meta[c]["date"], "title": meta[c]["text"].strip(), "url": meta[c]["url"]}
                for c in q["gold_grs"] if c in meta]
        doc = {**entry, "gold_grs_detail": gold, "runs": runs_by_q.get(q["id"], [])}
        (out_dir / "questions" / f"{q['id']}.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    size = sum(p.stat().st_size for p in out_dir.rglob("*.json"))
    print(f"{len(index)} questions, {sum(len(v) for v in runs_by_q.values())} runs, "
          f"{size / 1024:.0f} KB of JSON in {out_dir.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
