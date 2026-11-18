# E4: run logging (18-11-2026)

`python -m grengine.run --name <name> [--ids 1,2] [--csv]` writes one JSONL file per run:
`runs/<yyyy-mm-dd>-<name>.jsonl`, using the IST date. A second run with the same name gets
`-2`, `-3`, and so on. Nothing is overwritten.

## Lines

| type | Fields |
|---|---|
| `run_start` | name, start time, question ids, prompt version, model settings, git commit, run cap, daily cap, amount spent today before the run |
| `question` | see below, one line per question |
| `run_end` | completed vs planned, stop reason (null if none), total cost, prompt, completion, reasoning and cached tokens, amount spent today after the run, corrections by check type, number of questions with corrections |

## Question line

| Brief asks for | Field |
|---|---|
| question | `id`, `question` (plus `gold_answer`, `gold_grs` for scoring) |
| retrieved passages | `retrieved`: each GR's code, date, title, score, score reasons and top BM25 `passages`. `candidates`: newer-GR candidates with their evidence. `date_facts`. `messages`: the exact prompt sent, with the full texts. |
| prompt version | `prompt_version`, `settings` |
| raw response | `raw_response` (the full API JSON), `model_content` |
| parsed answer | `parsed_model_output`, `raw_answer` (contract shape, no checks; this is what is scored), `answer` (after the checks; the product) |
| latency | `latency_s`, `attempts`, `retries` |
| tokens | `usage`: `prompt_tokens`, `cached_tokens`, `completion_tokens`, `reasoning_tokens`, `total_tokens` |
| cost | `cost_inr` (also in `usage`) |
| what the checks did | `corrections` (each with check, where, before, after), `issues` (flags left in place) |

The API key is never logged: it is sent only as a request header and is not part of
`raw_response`.

## Example

`runs/2026-11-18-e3-check-4.jsonl`, Q7:

- **Usage:** 8,879 prompt tokens (800 cached), 491 completion tokens, 0 reasoning tokens.
- **Cost and latency:** Rs 0.0933, 2.87 s.
- **Corrections:** one, `drop_unknown_code` on `newer[0]` (the mistyped code
  `202304131657523211`).

That run predates the explicit `passages` field and the `run_start` settings; both are
logged from now on.
