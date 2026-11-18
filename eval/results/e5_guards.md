# E5: key handling, spend cap, rate limit (18-11-2026)

All guards are in `grengine/sarvam.py` and `grengine/run.py`. The offline tests are in
`tests/test_sarvam.py` (a fake transport, so no network and no spend).

| Guard | Behaviour | Shown by |
|---|---|---|
| Key | Read only from `SARVAM_API_KEY`; sent only as the `api-subscription-key` header; never printed, logged or stored. If missing, the run fails with a clear message before any call. | live (below), tests |
| 402 | Credits exhausted: stop, no retry | **live** on the first E3 call (`runs/2026-11-18-e3-check.jsonl`), tests |
| 429 / 500 / 502 / 503 | Up to 5 retries with exponential backoff (2, 4, 8… s, plus jitter, max 60 s), honouring `Retry-After`. `seat_budget_exhausted_error` (429) is not retried. | tests |
| Our rate limit | 30 calls a minute, below Sarvam's 60 (a limit of 60 or more is refused) | tests |
| Daily cap | `DAILY_SPEND_CAP_INR` (default 50), tracked per IST day in `runs/spend/` (not committed). Checked before every call, including whether the call's worst case would pass the cap. | live (below), tests |
| Run cap | `RUN_SPEND_CAP_INR` (default 20). A preflight estimates the worst case from prompt sizes before any call. During the run it stops when the projected cost passes the cap. | live (below) |
| Any other error | Stops the run; the reason is in `run_end.stopped` | n/a |
| Cost tracking | From `usage` on every call: uncached input × Rs 10, cached input × Rs 0.25, completion (including reasoning) × Rs 25, per 1M tokens | tests, every run log |

## Live runs (no paid call was made in any of them)

**Missing key:**

```
$ (SARVAM_API_KEY unset) python -m grengine.run --name e5-missing-key --ids 1
STOP: SARVAM_API_KEY is not set. Put your Sarvam API key in the SARVAM_API_KEY environment variable (for example in a local .env you source; .env is git-ignored). No API call was made.
exit 2
```

**Daily cap already reached** (Rs 0.39 spent today, cap set to Rs 0.30):

```
$ DAILY_SPEND_CAP_INR=0.30 python -m grengine.run --name e5-cap --ids 1
"stopped": "Q1: SpendCapReachedError: Daily spend cap reached: Rs 0.3916 spent of Rs 0.30 (2026-11-18, IST). No call made."
```

**Next call could pass the daily cap** (cap Rs 0.45):

```
$ DAILY_SPEND_CAP_INR=0.45 python -m grengine.run --name e5-cap-worstcase --ids 1
"stopped": "Q1: SpendCapReachedError: Next call could cost up to Rs 0.3809; with Rs 0.3916 already spent that would pass the daily cap of Rs 0.45. No call made."
```

**Run cap preflight** (all 37 questions, cap Rs 5):

```
$ RUN_SPEND_CAP_INR=5 python -m grengine.run --name e5-runcap
Preflight: 37 questions, ~509862 prompt tokens, worst case Rs 8.89 (run cap Rs 5.00)
STOP: worst-case cost Rs 8.89 is over the run cap Rs 5.00. No call made.
exit 3
```

The spend ledger was unchanged after all four (Rs 0.391629 in 6 calls).

**Worst case for one run of 37: Rs 8.89.** That is under the Rs 20 stop line. It assumes
3.5 characters per token (the measured figure is 3.9) and every reply using the full 4,096
tokens. On Q7, replies used about 500 tokens.
