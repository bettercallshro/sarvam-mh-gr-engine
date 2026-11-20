# Runs

One line per file. Each `.jsonl` is a full run log (question, retrieved GRs, prompt, raw
reply, parsed answer, checks, tokens, cost). Each `.csv` is the scoring sheet for that run.
Hand scores for the scored runs are in `../eval/scores.csv`.

## Scored runs

- `2026-11-18-baseline.jsonl` / `.csv`: baseline, all 37 questions (commit 2b41877, prompt answer_v2; results added in 835367c).
- `2026-11-18-v4-run1-2.jsonl` / `.csv`: final version, run A, all 37 (commit 767eb54, prompt answer_v4).
- `2026-11-18-v4-run2.jsonl` / `.csv`: final version, run B, all 37 (commit 767eb54, prompt answer_v4).
- `2026-11-20-holdout-old-run1.jsonl` / `.csv`: hold-out, 15 new questions, baseline version, run 1 (835367c, same engine code as 2b41877).
- `2026-11-20-holdout-old-run2.jsonl` / `.csv`: hold-out, baseline version, run 2 (835367c, same engine code as 2b41877).
- `2026-11-20-holdout-final-run1.jsonl` / `.csv`: hold-out, final version, run 1 (49ee4ae).
- `2026-11-20-holdout-final-run2.jsonl` / `.csv`: hold-out, final version, run 2 (49ee4ae).

## Other runs

- `2026-11-18-v3-run1.jsonl` / `.csv`: round 1, run A, all 37 (commit 213c181, prompt answer_v3).
- `2026-11-18-v3-run2-2.jsonl` / `.csv`: round 1, run B, all 37 (commit e8e3e09, prompt answer_v3); full rerun of `partial/2026-11-18-v3-run2`.
- `2026-11-18-smoke.jsonl` / `.csv`: smoke test on questions 1, 7, 11, 30, 36 (commit 1be34ff, prompt answer_v2).
- `2026-11-18-e3-check.jsonl`: first answer-step call on Q7; stopped on HTTP 402 (no credits), the credits-exhausted guard working.
- `2026-11-18-e3-check-2.jsonl`, `-3.jsonl`, `-4.jsonl`: answer-step development calls on Q7 (strict schema mode, then JSON mode, then prompt answer_v2).
- `2026-11-18-e5-cap.jsonl`: guard demo; daily spend cap already reached, no call made.
- `2026-11-18-e5-cap-worstcase.jsonl`: guard demo; next call could pass the daily cap, no call made.
- `experiments/2026-11-18-q7-format.json`: three output-format settings compared on Q7 (JSON mode, no format, strict schema).

## Incomplete runs (`partial/`)

- `partial/2026-11-18-v3-run2.jsonl` / `.csv`: round 1, run B, stopped at Q16 on a reply-shape error in the engine (fixed in e8e3e09); the full rerun is `2026-11-18-v3-run2-2`.
- `partial/2026-11-18-v4-run1.jsonl` / `.csv`: final version, run A, stopped after Q1 by an over-cautious cost estimate (fixed in 767eb54); the full rerun is `2026-11-18-v4-run1-2`.

`spend/` (the daily spend ledger) is local only and not committed.
