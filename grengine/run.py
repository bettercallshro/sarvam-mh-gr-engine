"""Run the engine on eval questions and log everything (E4), with the run guards (E5).

Usage:
    python -m grengine.run --name smoke --ids 1,7,11,30,36
    python -m grengine.run --name baseline            # all 37, also writes the scoring CSV

One JSONL per run in runs/: a run_start line, one line per question, and a
run_end line. Each question line has: question, retrieved GRs and the exact
prompt (which holds the passages and candidate texts), prompt version, raw
response, parsed answer, latency, tokens (incl. reasoning and cached) and cost.

Before any call, a preflight estimates the run's worst-case cost from prompt
sizes and refuses to start above RUN_SPEND_CAP_INR (default 20).
The run stops (and says why in run_end) on:
  - any API error, a missing key, exhausted credits, or the daily cap
  (a reply that is invalid against the schema is retried once; if it is still
   invalid the question is recorded as a format failure and the run continues)
  - a projected cost for this run above RUN_SPEND_CAP_INR (default 20)
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from .answer import (MAX_TOKENS, PROMPT_VERSION, REASONING_EFFORT, TEMPERATURE, Answerer,
                     answer_question)
from .sarvam import IST, SarvamClient, SarvamError, SpendTracker, worst_case_cost_inr

QUESTIONS = Path("eval/questions.jsonl")
RUNS_DIR = Path("runs")
DEFAULT_RUN_CAP_INR = 20.0
PREFLIGHT_CHARS_PER_TOKEN = 3.5


def _git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


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
        "model_content": out["model_content"],
        "parsed_model_output": out["parsed_model_output"],
        "raw_answer": out["raw_answer"],        # model output, no checks (scored in the eval)
        "format": out["format"],                # ok | repaired | retried_ok | failed
        "chosen_attempt": out["chosen_attempt"],
        "format_attempts": out["format_attempts"],  # every reply, with its schema errors
        "answer": out["result"],                # after the post-answer checks (the product)
        "corrections": out["corrections"],      # every change the checks made
        "issues": out["issues"],                # problems flagged but left in place
        "latency_s": out["latency_s"],
        "attempts": out["attempts"],
        "retries": out["retries"],
        "usage": out["usage"],
        "cost_inr": out["usage"]["cost_inr"],
    }


def _fmt_cited(cited):
    return "; ".join(f"{c.get('date')} {c.get('code')} p{c.get('page')}"
                     + ("" if c.get("quote_verified", True) else " [quote not found]") for c in cited)


def _fmt_newer(newer):
    return "; ".join(f"{n.get('date')} {n.get('code')}: {n.get('what_changed')}" for n in newer)


def write_csv(path: Path, records: list[dict]) -> None:
    """Hand-scoring sheet. model_answer, cited, newer and status are the RAW model
    output (before the post-answer checks). check_corrections lists what the
    checks changed, and checked_cited / checked_newer show the result after them,
    so the effect of the checks can be compared."""
    cols = ["id", "question", "gold_answer", "model_answer", "cited", "newer", "status",
            "answer_score", "citation", "latest", "confident_wrong", "notes",
            "format", "check_corrections", "checked_cited", "checked_newer", "flags"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            raw = r.get("raw_answer") or {}
            chk = r.get("answer") or {}
            w.writerow({
                "id": r["id"], "question": r["question"], "gold_answer": r.get("gold_answer", ""),
                "model_answer": raw.get("answer", ""),
                "cited": _fmt_cited(raw.get("cited", [])),
                "newer": _fmt_newer(raw.get("newer", [])),
                "status": raw.get("status", ""),
                "answer_score": "", "citation": "", "latest": "", "confident_wrong": "", "notes": "",
                "format": r.get("format", ""),
                "check_corrections": "; ".join(f"{c['check']} {c['where']}: {c['before']} -> {c['after']}"
                                               for c in r.get("corrections", [])),
                "checked_cited": _fmt_cited(chk.get("cited", [])),
                "checked_newer": _fmt_newer(chk.get("newer", [])),
                "flags": "; ".join(r.get("issues", [])),
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

    # Preflight: worst-case cost of this run from prompt sizes, before any call.
    # 3.5 characters per token is below the 3.9 measured on Q7 (so it overestimates),
    # and every reply is assumed to use the full max_tokens.
    est_prompt_tokens = sum(
        int((len(answerer.system_prompt) + len(answerer.build_context(q["question"]).user_message)) / PREFLIGHT_CHARS_PER_TOKEN)
        for q in questions)
    worst = worst_case_cost_inr(est_prompt_tokens, MAX_TOKENS * len(questions))
    print(f"Preflight: {len(questions)} questions, ~{est_prompt_tokens} prompt tokens, worst case Rs {worst:.2f} "
          f"(run cap Rs {cap:.2f})", flush=True)
    if worst > cap:
        print(f"STOP: worst-case cost Rs {worst:.2f} is over the run cap Rs {cap:.2f}. No call made.", file=sys.stderr)
        return 3

    records, spent, stop_reason = [], 0.0, None
    with path.open("w", encoding="utf-8") as f:
        def log(obj):
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            f.flush()

        log({"type": "run_start", "name": args.name, "started": datetime.now(IST).isoformat(),
             "prompt_version": PROMPT_VERSION,
             "settings": {"model": "sarvam-105b", "max_tokens": MAX_TOKENS, "reasoning_effort": REASONING_EFFORT,
                          "temperature": TEMPERATURE, "response_format": "json_object"},
             "git_commit": _git_commit(),
             "question_ids": [q["id"] for q in questions], "run_cap_inr": cap,
             "preflight_worst_case_inr": round(worst, 4), "preflight_prompt_tokens": est_prompt_tokens,
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
                  f"{(rec['raw_answer'] or {}).get('status')}  format {rec['format']}  corrections: {len(rec['corrections'])}  flags: {len(rec['issues'])}", flush=True)
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
            "corrections_by_check": dict(Counter(c["check"] for r in records for c in r["corrections"])),
            "questions_with_corrections": sum(1 for r in records if r["corrections"]),
            "format": dict(Counter(r["format"] for r in records)),
            "format_failures": sum(1 for r in records if r["format"] == "failed"),
            "format_retries": sum(1 for r in records if len(r["format_attempts"]) > 1),
            "calls": sum(len(r["format_attempts"]) for r in records),
            "retry_reasons": dict(Counter(a["why"] for r in records for a in r["format_attempts"][1:])),
            "missing_review_attempts": sum(1 for r in records for a in r["format_attempts"] if a["missing_reviews"]),
            "repairs": dict(Counter(x.split(" ", 1)[-1] if x.startswith("candidates_reviewed[") else x
                                     for r in records for x in r["format_attempts"][r["chosen_attempt"]]["repairs"])),
        }
        log(summary)

    if args.csv:
        write_csv(path.with_suffix(".csv"), records)
    print(f"\nLog: {path}")
    print(json.dumps({k: v for k, v in summary.items() if k != "type"}, indent=1))
    return 1 if stop_reason else 0


if __name__ == "__main__":
    sys.exit(main())
