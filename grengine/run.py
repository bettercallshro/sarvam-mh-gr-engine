"""Run the engine on eval questions and log everything (E4), with the run guards (E5).

Usage:
    python -m grengine.run --name smoke --ids 1,7,11,30,36
    python -m grengine.run --name baseline            # all 37, also writes the scoring CSV

One JSONL per run in runs/: a run_start line, one line per question, and a
run_end line. Each question line has: question, retrieved GRs and the exact
prompt (which holds the passages and candidate texts), prompt version, raw
response, parsed answer, latency, tokens (incl. reasoning and cached) and cost.

The run stops (and says why in run_end) on:
  - any API error, a missing key, exhausted credits, or the daily cap
  - an unparseable model reply
  - a projected cost for this run above RUN_SPEND_CAP_INR (default 20)
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from .answer import Answerer, answer_question
from .sarvam import IST, SarvamClient, SarvamError, SpendTracker

QUESTIONS = Path("eval/questions.jsonl")
RUNS_DIR = Path("runs")
DEFAULT_RUN_CAP_INR = 20.0


def run_cap() -> float:
    raw = os.environ.get("RUN_SPEND_CAP_INR", "").strip()
    return float(raw) if raw else DEFAULT_RUN_CAP_INR


def question_record(q: dict, out: dict) -> dict:
    ctx = out["context"]
    return {
        "type": "question",
        "id": q["id"],
        "question": q["question"],
        "gold_answer": q.get("gold_answer"),
        "gold_grs": q.get("gold_grs"),
        "prompt_version": out["settings"]["prompt_version"],
        "settings": out["settings"],
        "retrieved": ctx.retrieved,
        "candidates": ctx.candidates,
        "date_facts": ctx.date_facts,
        "messages": out["messages"],
        "raw_response": out["raw_response"],
        "parsed_model_output": out["parsed_model_output"],
        "answer": out["result"],
        "issues": out["issues"],
        "latency_s": out["latency_s"],
        "attempts": out["attempts"],
        "retries": out["retries"],
        "usage": out["usage"],
        "cost_inr": out["usage"]["cost_inr"],
    }


def write_csv(path: Path, records: list[dict]) -> None:
    cols = ["id", "question", "gold_answer", "model_answer", "cited", "newer", "status",
            "answer_score", "citation", "latest", "confident_wrong", "notes"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            a = r.get("answer") or {}
            w.writerow({
                "id": r["id"], "question": r["question"], "gold_answer": r.get("gold_answer", ""),
                "model_answer": a.get("answer", ""),
                "cited": "; ".join(f"{c['date']} {c['code']} p{c['page']}"
                                   + ("" if c.get("quote_verified") else " [quote not verified]")
                                   for c in a.get("cited", [])),
                "newer": "; ".join(f"{n['date']} {n['code']}: {n['what_changed']}" for n in a.get("newer", [])),
                "status": a.get("status", ""),
                "answer_score": "", "citation": "", "latest": "", "confident_wrong": "",
                "notes": "; ".join(r.get("issues", [])),
            })


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="run name, e.g. smoke or baseline")
    ap.add_argument("--ids", help="comma-separated question ids (default: all)")
    ap.add_argument("--csv", action="store_true", help="also write the hand-scoring CSV")
    args = ap.parse_args(argv)

    questions = [json.loads(l) for l in QUESTIONS.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.ids:
        wanted = [int(x) for x in args.ids.split(",")]
        questions = [q for q in questions if q["id"] in wanted]

    try:
        client = SarvamClient(spend=SpendTracker())
    except SarvamError as e:
        print(f"STOP: {e}", file=sys.stderr)
        return 2

    answerer = Answerer()
    cap = run_cap()
    day = datetime.now(IST).strftime("%Y-%m-%d")
    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / f"{day}-{args.name}.jsonl"
    n = 1
    while path.exists():
        n += 1
        path = RUNS_DIR / f"{day}-{args.name}-{n}.jsonl"

    records, spent, stop_reason = [], 0.0, None
    with path.open("w", encoding="utf-8") as f:
        def log(obj):
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            f.flush()

        log({"type": "run_start", "name": args.name, "started": datetime.now(IST).isoformat(),
             "question_ids": [q["id"] for q in questions], "run_cap_inr": cap,
             "daily_cap_inr": client.spend.cap, "daily_spent_before_inr": client.spend.spent()})
        for i, q in enumerate(questions, 1):
            try:
                out = answer_question(answerer, client, q["question"])
            except SarvamError as e:
                stop_reason = f"Q{q['id']}: {type(e).__name__}: {e}"
                break
            except Exception as e:  # any other error also stops the run
                stop_reason = f"Q{q['id']}: unexpected {type(e).__name__}: {e}"
                break
            rec = question_record(q, out)
            log(rec)
            records.append(rec)
            spent += rec["cost_inr"]
            u = rec["usage"]
            print(f"Q{q['id']:>2}  {rec['latency_s']:>6.1f}s  in {u['prompt_tokens']:>6} out {u['completion_tokens']:>5} "
                  f"(reasoning {u['reasoning_tokens']:>5})  Rs {rec['cost_inr']:.4f}  "
                  f"{(rec['answer'] or {}).get('status', 'PARSE FAILED')}  issues: {len(rec['issues'])}", flush=True)
            if rec["answer"] is None:
                stop_reason = f"Q{q['id']}: model reply could not be parsed"
                break
            projected = spent / i * len(questions)
            if projected > cap:
                stop_reason = (f"projected cost for this run Rs {projected:.2f} is over the run cap Rs {cap:.2f} "
                               f"(after {i} of {len(questions)} questions, Rs {spent:.4f} spent)")
                break
        summary = {
            "type": "run_end", "finished": datetime.now(IST).isoformat(),
            "completed": len(records), "planned": len(questions), "stopped": stop_reason,
            "cost_inr": round(spent, 6),
            "prompt_tokens": sum(r["usage"]["prompt_tokens"] for r in records),
            "completion_tokens": sum(r["usage"]["completion_tokens"] for r in records),
            "reasoning_tokens": sum(r["usage"]["reasoning_tokens"] for r in records),
            "cached_tokens": sum(r["usage"]["cached_tokens"] for r in records),
            "daily_spent_after_inr": client.spend.spent(),
        }
        log(summary)

    if args.csv:
        write_csv(path.with_suffix(".csv"), records)
    print(f"\nLog: {path}")
    print(json.dumps({k: v for k, v in summary.items() if k != "type"}, indent=1))
    return 1 if stop_reason else 0


if __name__ == "__main__":
    sys.exit(main())
