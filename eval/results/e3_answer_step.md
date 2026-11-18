# E3: answer step (18-11-2026)

## Design

- **Prompt:** `grengine/prompts/answer_v2.md`, version `answer_v2`. The reply schema is
  added to it in `grengine/answer.py`.
- **Context per question:**
  - Date facts: whether each date in the question is a corpus GR's date. If no GR has
    that date, every place a corpus GR cites it is listed.
  - Full text of the top 5 retrieved GRs: original language with page markers, plus the
    English machine translation for Marathi GRs.
  - Full text of up to 10 newer-GR candidates, taken from the top 3 retrieved GRs. Each
    shows its evidence type, and same-file-only links say "this alone proves nothing".
- **Model rules:**
  - Review every candidate from its text (amends, replaces, stays, extends, clarifies,
    cites_only, unrelated), and list in `newer` only candidates that change the asked-for GR.
  - Quote the original language word for word, and follow the wording rules from the brief.
  - If the question's date matches no GR but a corpus GR fits the description, say "The
    corpus dates this GR …" (the Q4 rule).
- **Model settings:** `sarvam-105b`, `/v1/chat/completions`, JSON mode, temperature 0.2,
  max_tokens 4096, reasoning_effort "low". Reasoning tokens were 0 on every call with a
  response format.

## Post-answer checks

These run on the product answer. Every change is logged with before and after values; the
eval scores the raw answer.

| Check | What it does |
|---|---|
| `drop_unknown_code` | Drops a code that is not a GR given to the model |
| `repair_code_by_date` | A mistyped code whose stated date matches exactly one given GR is replaced by that GR's code |
| `date_from_metadata`, `title_from_metadata` | Model values replaced by `GRs.json` values. The url always comes from the metadata. |
| `page_from_quote` | Page set to where the quote is found in the original text |
| `move_quote_to_twin` | The quote is in the twin copy, so the citation moves to the twin |
| `sort_newer_by_date` | Orders the newer GRs by date |

Flagged but left unchanged: quote not found, bare "in force", "does not exist", an
unreviewed candidate, a bad status, duplicate JSON keys, or a finish reason other than `stop`.

## Development calls on Q7 (all logged)

| Run | Setting | Result | Cost (Rs) |
|---|---|---|---|
| `runs/2026-11-18-e3-check.jsonl` | strict json_schema | HTTP 402, no credits (stopped, no retry) | 0 |
| `runs/2026-11-18-e3-check-2.jsonl` | strict json_schema, prompt v1 | Empty `not_found`; texts not read; 49 output tokens | 0.0844 |
| `runs/experiments/2026-11-18-q7-format.json` | json_object, low reasoning | Correct (Rs 1,20,000 from 12-04-2023) | 0.0901 |
| (same) | no format, low reasoning | Reasoning used all 4,096 tokens; empty answer | 0.1049 |
| (same) | strict json_schema, medium reasoning | `not_found` again | 0.0067 |
| `runs/2026-11-18-e3-check-3.jsonl` | json_object, prompt v1 | Right analysis, but blank status and answer, and a duplicate `cited` key | 0.0123 |
| `runs/2026-11-18-e3-check-4.jsonl` | json_object, prompt v2 (work fields first) | Correct; both Marathi quotes verified; one `newer` code mistyped | 0.0933 |

Total spent today: Rs 0.39 in 6 calls.

**Q7 with prompt v2:** "The maximum spend on a laptop or tablet for an IAS, IPS or IFS
officer is Rs. 1,20,000, as revised by the GR dated 12-04-2023. The earlier GR dated
24-12-2019 had set the limit at Rs. 85,000." The model wrote the 12-04-2023 code in
`newer` as `202304131657523211`. In that run the check dropped it. The repair check, added
after this run, would restore it from the date.

## Measured cost

- Q7 prompt: 8,879 tokens for about 35,000 characters, so roughly 3.9 characters per token.
- Q7 output: about 400–500 tokens, with no reasoning tokens.
- Extrapolated to all 37 questions (1.71M prompt characters): about 440k input tokens
  (Rs 4.4) plus 37 × 500 output tokens (Rs 0.5), so **about Rs 5 per run of 37**.
  Cached input makes repeat runs cheaper.
