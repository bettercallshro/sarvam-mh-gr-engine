# Replay data

Logged runs of the engine, exported for the website. **These are recorded answers from
past runs, not live answers.** Nothing here calls the model.

## Files

- `index.json`: one entry per question, 52 in all (37 main, 15 hold-out). Each entry has
  `id`, `set` (`main` or `holdout`), `question`, `case` and `task` tags, `lang`, the short
  right answer (`gold_answer`), and the right GR codes (`gold_grs`).
- `questions/<id>.json`: the same fields, plus `gold_grs_detail` (date, title and official
  PDF link of each right GR) and `runs`: every logged run of that question.

## Runs per question

| Set | Version | Runs | Logs |
|---|---|---|---|
| main (37) | Baseline | run 1, run 2 | `runs/2026-11-18-baseline.jsonl`, `runs/2026-11-21-baseline-run2.jsonl` |
| main | Round 1 | run 1, run 2 | `runs/2026-11-18-v3-run1.jsonl`, `runs/2026-11-18-v3-run2-2.jsonl` |
| main | Final | run 1, run 2 | `runs/2026-11-18-v4-run1-2.jsonl`, `runs/2026-11-18-v4-run2.jsonl` |
| holdout (15) | Baseline | run 1, run 2 | `runs/2026-11-20-holdout-old-run1.jsonl`, `-old-run2.jsonl` |
| holdout | Final | run 1, run 2 | `runs/2026-11-20-holdout-final-run1.jsonl`, `-final-run2.jsonl` |

Each run has:

| Field | Content |
|---|---|
| `version`, `run`, `commit`, `prompt_version` | which engine produced it |
| `format` | `ok`, `retried` (valid after one retry), `repaired` (small format slip fixed), or `failed` (still invalid after the retry) |
| `product` | the answer as the product shows it, after the checks: `status`, `answer`, `cited`, `newer`, `format_repaired`. `null` where the product showed nothing: format failures in the baseline and round 1, before the final version always showed an answer. |
| `raw` | the model's own answer, before the checks: `status`, `answer`, `cited`, `newer`. This is what was scored. `null` where the reply was not readable JSON (its text is in the run log). |
| `scores` | hand scores from `eval/scores.csv`: `answer` (2/1/0), `citation`, `latest`, `confident_wrong`, `fully_correct`, `note`. `null` for round 1, which was not scored, and for runs whose rows in `eval/scores.csv` are not filled in yet. |
| `why` | for an answer scored not fully correct: `cause` (a fixed code such as `layout`, `reply` or `opener`), `status` (`fixed`, `other_run`, `one_final` or `open`) and `text`, the line explaining what went wrong and whether it was fixed, from `eval/causes.csv`. `null` for answers scored fully correct and for round 1. |
| `log` | the run log the entry came from |

`cited` items have `code`, `date`, `title`, `url` (official PDF), `quote` and `page`.
In `product`, date, title, link and page come from the metadata and the text. In `raw`
they are as the model gave them, except `url`, which is looked up from the code the model
gave (`null` if that code is not a corpus GR). `newer` items have `code`, `date` and
`what_changed`. An item the model wrote in the wrong shape is kept as `{"malformed": ...}`.

Full prompt texts are left out; they are in the run logs.

## How it's made

```bash
python scripts/export_replay.py
```

The script reads the question files, `eval/scores.csv`, `eval/causes.csv`, `corpus/GRs.json`
and the run logs above, and rewrites this folder. It makes no API calls.
