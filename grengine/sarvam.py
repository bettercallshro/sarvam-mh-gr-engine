"""Sarvam chat completions client (sarvam-105b), standard library only.

Endpoint, header, request and response fields follow the Chat Completion V1
reference at docs.sarvam.ai (read 18-11-2026):
  POST https://api.sarvam.ai/v1/chat/completions
  header api-subscription-key
  usage: prompt_tokens, completion_tokens, total_tokens,
         completion_tokens_details.reasoning_tokens (billed as output),
         prompt_tokens_details.cached_tokens (billed at the cached-input rate)

Safety rules (brief section 5):
  - The key is read only from the SARVAM_API_KEY environment variable and is
    never printed, logged or stored.
  - 429 (rate or capacity) and 500/502/503 are retried with exponential backoff.
    429 seat_budget_exhausted_error is not retried.
  - 402 means credits are exhausted: stop, no retry.
  - Our own rate limit (below Sarvam's 60/min) and a daily spend cap
    (DAILY_SPEND_CAP_INR, default 50) are checked before every call.
"""
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

API_URL = "https://api.sarvam.ai/v1/chat/completions"
MODEL = "sarvam-105b"

# Rs per 1M tokens, excluding GST. Introductory pricing through end 2026,
# checked on docs.sarvam.ai/api/getting-started/pricing on 18-11-2026.
PRICE_INPUT_PER_M = 10.0
PRICE_CACHED_INPUT_PER_M = 0.25
PRICE_OUTPUT_PER_M = 25.0  # reasoning tokens are billed as output

SARVAM_RPM_LIMIT = 60          # pay-as-you-go limit for sarvam-105b
OUR_RPM_LIMIT = 30             # ours, well below Sarvam's
DEFAULT_DAILY_CAP_INR = 50.0
MAX_RETRIES = 5

IST = ZoneInfo("Asia/Kolkata")
SPEND_DIR = Path("runs/spend")


class SarvamError(Exception):
    """Any failure that should stop the run."""


class MissingKeyError(SarvamError):
    pass


class CreditsExhaustedError(SarvamError):
    pass


class SpendCapReachedError(SarvamError):
    pass


class APIError(SarvamError):
    def __init__(self, status: int, code: str | None, message: str):
        super().__init__(f"HTTP {status} {code or ''}: {message}".strip())
        self.status, self.code = status, code


def get_api_key() -> str:
    key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not key:
        raise MissingKeyError(
            "SARVAM_API_KEY is not set. Put your Sarvam API key in the SARVAM_API_KEY "
            "environment variable (for example in a local .env you source; .env is git-ignored). "
            "No API call was made."
        )
    return key


def cost_inr(usage: dict) -> dict:
    """Cost of one call from its usage block. Returns token counts and Rs."""
    prompt = int(usage.get("prompt_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    cached = int(((usage.get("prompt_tokens_details") or {}).get("cached_tokens")) or 0)
    reasoning = int(((usage.get("completion_tokens_details") or {}).get("reasoning_tokens")) or 0)
    uncached = max(0, prompt - cached)
    inr = (uncached * PRICE_INPUT_PER_M + cached * PRICE_CACHED_INPUT_PER_M
           + completion * PRICE_OUTPUT_PER_M) / 1_000_000
    return {"prompt_tokens": prompt, "cached_tokens": cached, "completion_tokens": completion,
            "reasoning_tokens": reasoning, "total_tokens": int(usage.get("total_tokens") or prompt + completion),
            "cost_inr": round(inr, 6)}


def worst_case_cost_inr(prompt_tokens_estimate: int, max_tokens: int) -> float:
    return (prompt_tokens_estimate * PRICE_INPUT_PER_M + max_tokens * PRICE_OUTPUT_PER_M) / 1_000_000


class SpendTracker:
    """Daily spend ledger (IST day), kept on disk so separate runs add up."""

    def __init__(self, cap_inr: float | None = None, spend_dir: Path = SPEND_DIR, today: str | None = None):
        if cap_inr is None:
            raw = os.environ.get("DAILY_SPEND_CAP_INR", "").strip()
            try:
                cap_inr = float(raw) if raw else DEFAULT_DAILY_CAP_INR
            except ValueError:
                raise SarvamError(f"DAILY_SPEND_CAP_INR is not a number: {raw!r}")
        self.cap = cap_inr
        self.day = today or datetime.now(IST).strftime("%Y-%m-%d")
        self.path = Path(spend_dir) / f"{self.day}.json"
        self._lock = threading.Lock()

    def spent(self) -> float:
        if not self.path.exists():
            return 0.0
        return float(json.loads(self.path.read_text())["spent_inr"])

    def check(self, next_call_worst_case: float = 0.0) -> None:
        spent = self.spent()
        if spent >= self.cap:
            raise SpendCapReachedError(
                f"Daily spend cap reached: Rs {spent:.4f} spent of Rs {self.cap:.2f} ({self.day}, IST). No call made.")
        if spent + next_call_worst_case > self.cap:
            raise SpendCapReachedError(
                f"Next call could cost up to Rs {next_call_worst_case:.4f}; with Rs {spent:.4f} already spent "
                f"that would pass the daily cap of Rs {self.cap:.2f}. No call made.")

    def add(self, inr: float) -> float:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {"day": self.day, "spent_inr": 0.0, "calls": 0}
            if self.path.exists():
                data = json.loads(self.path.read_text())
            data["spent_inr"] = round(data["spent_inr"] + inr, 6)
            data["calls"] += 1
            self.path.write_text(json.dumps(data))
            return data["spent_inr"]


class RateLimiter:
    """At most `rpm` call starts in any 60-second window."""

    def __init__(self, rpm: int = OUR_RPM_LIMIT, clock=time.monotonic, sleep=time.sleep):
        if rpm >= SARVAM_RPM_LIMIT:
            raise ValueError(f"our rate limit must be below Sarvam's {SARVAM_RPM_LIMIT}/min")
        self.rpm, self.clock, self.sleep = rpm, clock, sleep
        self.starts: list[float] = []

    def wait(self) -> float:
        waited = 0.0
        while True:
            now = self.clock()
            self.starts = [t for t in self.starts if now - t < 60]
            if len(self.starts) < self.rpm:
                self.starts.append(now)
                return waited
            pause = 60 - (now - self.starts[0]) + 0.01
            self.sleep(pause)
            waited += pause


def _http_post(url: str, headers: dict, body: bytes, timeout: float) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()


@dataclass
class CallResult:
    response: dict
    usage: dict
    latency_s: float
    attempts: int
    retries: list[dict] = field(default_factory=list)


class SarvamClient:
    def __init__(self, spend: SpendTracker | None = None, limiter: RateLimiter | None = None,
                 post=_http_post, sleep=time.sleep, timeout: float = 180.0):
        self.api_key = get_api_key()  # fail fast, before anything else
        self.spend = spend or SpendTracker()
        self.limiter = limiter or RateLimiter()
        self.post, self.sleep, self.timeout = post, sleep, timeout

    def chat(self, messages: list[dict], *, max_tokens: int, reasoning_effort: str | None,
             temperature: float, response_format: dict | None = None,
             prompt_tokens_estimate: int = 0) -> CallResult:
        payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens,
                   "temperature": temperature, "reasoning_effort": reasoning_effort}
        if response_format:
            payload["response_format"] = response_format
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"api-subscription-key": self.api_key, "Content-Type": "application/json"}

        retries = []
        for attempt in range(1, MAX_RETRIES + 2):
            self.spend.check(worst_case_cost_inr(prompt_tokens_estimate, max_tokens))
            self.limiter.wait()
            t0 = time.monotonic()
            status, resp_headers, raw = self.post(API_URL, headers, body, self.timeout)
            latency = time.monotonic() - t0
            if status == 200:
                data = json.loads(raw)
                usage = cost_inr(data.get("usage") or {})
                self.spend.add(usage["cost_inr"])
                return CallResult(data, usage, latency, attempt, retries)

            code, message = _error_fields(raw)
            if status == 402:
                raise CreditsExhaustedError(f"HTTP 402 {code}: {message}. Credits exhausted; stopping, not retrying.")
            retryable = status in (500, 502, 503) or (status == 429 and code != "seat_budget_exhausted_error")
            if not retryable or attempt > MAX_RETRIES:
                raise APIError(status, code, message)
            delay = _retry_after(resp_headers) or min(60.0, 2 ** attempt + random.uniform(0, 1))
            retries.append({"attempt": attempt, "status": status, "code": code, "sleep_s": round(delay, 2)})
            self.sleep(delay)
        raise AssertionError("unreachable")


def _error_fields(raw: bytes) -> tuple[str | None, str]:
    try:
        err = json.loads(raw).get("error") or {}
        return err.get("code"), str(err.get("message", ""))[:300]
    except Exception:
        return None, raw[:300].decode("utf-8", "replace")


def _retry_after(headers: dict) -> float | None:
    for k, v in headers.items():
        if k.lower() == "retry-after":
            try:
                return min(60.0, float(v))
            except ValueError:
                return None
    return None
