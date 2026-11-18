# E3: stopped on the first model call (18-11-2026)

## What happened

The first `sarvam-105b` call (question 7, run log `runs/2026-11-18-e3-check.jsonl`) returned:

```
HTTP 402 insufficient_quota_error: No credits available.
```

A 402 means the Sarvam account's credit balance is empty. The key was accepted: a bad key
returns 403. As the brief requires, the client stopped and did not retry. Nothing was
charged, and no answer was produced.

## State of the code (no model output yet)

| Step | Code | Checked against the live API |
|---|---|---|
| E3 | `grengine/answer.py`, prompt in `grengine/prompts/answer_v1.md` | No: blocked by 402 |
| E4 | `grengine/run.py`, one JSONL per run in `runs/` | Run start/end logged; no question lines yet |
| E5 | `grengine/sarvam.py`: key from env only, 402 stop, 429/5xx backoff, own 30 rpm limit, daily cap | 402 stop shown live; other paths not yet tested |

## Pricing used (docs.sarvam.ai pricing page, read 18-11-2026)

| sarvam-105b | Rs per 1M tokens (excl. GST) |
|---|---|
| Input | 10 |
| Cached input | 0.25 |
| Output (reasoning tokens billed as output) | 25 |

This is introductory pricing through the end of 2026. The pay-as-you-go limit is 60 requests
a minute; the engine limits itself to 30.

## Cost estimate for one run of 37 (offline, before any call)

- Prompt text across the 37 questions: 1.71M characters (the largest is 82k).
- Worst case: Rs 12.35. This assumes 2 characters per token and every reply using the
  full 4,096 output tokens.
- That is under the Rs 20 stop line. The first successful call will calibrate the real
  tokens per character.

## To resume

Add credits on the Sarvam dashboard (Billing), then rerun:

```bash
SARVAM_API_KEY=... python -m grengine.run --name e3-check --ids 7
```
