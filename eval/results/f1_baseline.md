# F1: baseline run of all 37 (18-11-2026)

- **Run log:** `runs/2026-11-18-baseline.jsonl`
- **Scoring sheet:** `runs/2026-11-18-baseline.csv`
- **Prompt and settings:** `answer_v2`, sarvam-105b, JSON mode, temperature 0.2,
  max_tokens 4096, reasoning_effort "low" (0 reasoning tokens used).
- **Code:** commit `2b41877`.

Not scored yet. The CSV's `model_answer`, `cited`, `newer` and `status` columns are the
**raw** model output, before the post-answer checks. The empty columns `answer_score`,
`citation`, `latest`, `confident_wrong` and `notes` are for hand scoring. Extra columns:
`format` (ok, retried_ok or failed), `check_corrections` (what the checks changed),
`checked_cited` and `checked_newer` (after the checks), and `flags`.

## Run

| | |
|---|---|
| Completed | 37 of 37, no stop |
| Cost | Rs 4.66, including format retries (preflight worst case Rs 8.89; stop line Rs 20) |
| Tokens | 616,923 prompt (261,760 cached), 41,854 completion, 0 reasoning |
| Spent today | Rs 5.76 |

## Format (schema validation, one retry)

- First reply valid: 25
- Valid after the retry: 7
- **Format failures (invalid after the retry): 5**, in Q4, Q10, Q12, Q17, Q27

| Q | Format | Schema errors (first reply / retry) |
|---|---|---|
| 1 | retried_ok | missing field: newer; missing field: cited / valid |
| 4 | failed | candidates_reviewed[2] missing code, effect, reason; candidates_reviewed[2] bad effect: None / duplicate keys: 202407191742379111; cited[1] missing code, date, title, quote, page |
| 8 | retried_ok | missing field: asked_for_code / valid |
| 10 | failed | missing field: asked_for_code / missing field: newer; missing field: cited |
| 12 | failed | missing field: asked_for_code / missing field: asked_for_code |
| 13 | retried_ok | cited[1] missing code, date; cited[2] missing code, date / valid |
| 17 | failed | candidates_reviewed[2] missing code / candidates_reviewed[1] missing code, effect, reason; candidates_reviewed[1] bad effect: None |
| 22 | retried_ok | missing field: asked_for_code / valid |
| 27 | failed | empty or non-string answer / could not parse: ValueError: no JSON object in content; not a JSON object |
| 34 | retried_ok | could not parse: JSONDecodeError: Expecting ',' delimiter: line 18 column 6 (char 803); not a JSON object / valid |
| 35 | retried_ok | missing field: asked_for_code; missing field: candidates_reviewed / valid |
| 37 | retried_ok | missing field: answer; missing field: status / valid |

Most first-reply errors are a missing field (often `asked_for_code`) or a list item missing
its keys. Q27 and Q34 hit the 4,096-token limit once each.

## Corrections made by the checks (raw → product)

11 questions had at least one correction.

| Check | Count | Questions |
|---|---|---|
| `title_from_metadata` | 8 | 5, 9, 19, 20, 34 |
| `repair_code_by_date` | 7 | 5, 7, 8, 9, 19, 23, 29 |
| `sort_newer_by_date` | 2 | 13, 14 |
| `page_from_quote` | 1 | 14 |
| `date_from_metadata` | 1 | 19 |
| `drop_unknown_code` | 1 | 20 |

## Flags (left in place)

| Flag | Count | Questions |
|---|---|---|
| date in answer matches no cited or newer GR | 29 | 1, 2, 3, 5, 9, 11, 13, 14, 15, 16, 22, 33, 36, 37 |
| quote not found in original text | 14 | 1, 5, 8, 9, 11, 23, 24, 29, 30, 31 |
| candidates of the asked-for GR not reviewed | 9 | 1, 2, 5, 15, 18, 23, 24, 25, 28 |
| format failure after retry | 5 | 4, 10, 12, 17, 27 |
| finish_reason=length | 1 | 27 |

The date flag fires often because answers rightly mention deadlines and other dates (as
expected from the rule). It says whether the date occurs in the texts given; a date that
occurs nowhere is the one to look at.
