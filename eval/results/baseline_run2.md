# Baseline, run 2: run notes (21-11-2026)

A second run of the first version (the baseline) on the 37 main questions, made exactly
as before to measure how much results vary between runs. Nothing that affects answers was
changed.

## Run

| | |
|---|---|
| Date | 21-11-2026 (IST), started 13:29, finished 13:33 |
| Log | `runs/2026-11-21-baseline-run2.jsonl` |
| Scoring sheet | `runs/2026-11-21-baseline-run2.csv` (same columns as the first baseline) |
| Engine | commit `835367c`, the same engine code as `2b41877`, where the first baseline ran. It ran from a separate git worktree with no code changes. |
| Questions | all 37 in `eval/questions.jsonl` (identical at `835367c` and on `main`) |
| Prompt | `answer_v2` |
| Model as sent | `sarvam-105b` (`/v1/chat/completions`) |
| Model as returned | `sarvam-105b` in all 37 logged responses. The old logger keeps the full response only for the reply that is scored, so the 13 first attempts that were retried have their text logged but not the model field. |
| Settings | temperature 0.2, reasoning_effort "low", max_tokens 4096, JSON mode, one retry for an invalid reply (as in the first baseline) |
| Corpus | `corpus/` copied into the worktree's `data/mahGRs/GRs/Information_Technology_Department/`; it is byte-identical to the fetch at `c96e88f`. The old code built its index from it, and the index is byte-identical to the current one. |
| Cost | Rs 6.02 for 50 calls (671,928 prompt tokens, of which 247,648 cached; 68,462 completion tokens, of which 3,381 reasoning) |
| Spend cap | Daily cap set to Rs 15 for this run. The run cap stayed at its default, Rs 20; it did not trip and was not raised. |

The only things set outside the engine:
- The run log was written to the main repository's `runs/` instead of the worktree's.
- The spend ledger was the main repository's.

## Replies

| | Run 1 (18-11-2026) | Run 2 (21-11-2026) |
|---|---|---|
| Calls | 49 | 50 |
| Questions retried once | 12 | 13 (Q2, 3, 4, 5, 6, 12, 13, 14, 16, 21, 24, 28, 30) |
| Empty replies | 0 | 0 |
| Incomplete replies (cut at the 4,096-token limit) | 2 | 8 (Q4, 5, 13, 16 ×2, 24, 30 ×2) |
| Format failures after the retry | 5 | 9 (Q4, 5, 6, 13, 14, 16, 24, 28, 30) |
| Scored replies that are not readable JSON | 1 | 5 |

Every reply is kept in the log as it came back. No question was re-run on its own.

## Hand scores (confirmed)

Scored against the rubric and confirmed row by row (`eval/scores.csv`, run `baseline-run2`).

| | Run 1 | Run 2 |
|---|---|---|
| Fully correct | 25 / 37 | 26 / 37 |
| Confident-wrong | 5 | 1 (Q27) |
| Answer shown (product) | 32 / 37 | 28 / 37 |

13 of 37 questions changed fully-correct status between baseline runs 1 and 2:
- fully correct in run 1 only: Q1, 11, 16, 21, 24, 30;
- fully correct in run 2 only: Q2, 10, 17, 18, 20, 28, 33.

## Automatic counts (proxies)

From `grengine/compare_runs.py`. These are automatic proxies, not hand scores; the hand
scores are above.

| Measure | Run 1 | Run 2 |
|---|---|---|
| Format: ok / retried_ok / failed | 25 / 7 / 5 | 24 / 4 / 9 |
| Product answer shown (after the checks) | 32 / 37 | 28 / 37 |
| Status as expected (raw) | 32 / 37 | 30 / 37 |
| Any gold GR cited or listed as newer (raw / after checks) | 29 / 26 | 28 / 24 |
| All gold GRs cited or listed as newer (raw / after checks) | 20 / 20 | 25 / 21 |
| Questions with a gold GR left unreviewed | 4 | 0 |
| Current rule first: holds / applies (code check) | 8 / 12 | 9 / 13 |
| Quotes not found | 14 | 13 |
| Corrections made by the checks | 20 | 25 |

"Questions with a gold GR left unreviewed" can only be counted where the scored reply is
readable. Run 2 has 5 unreadable scored replies against 1 in run 1, so its 0 is not a
like-for-like comparison.
