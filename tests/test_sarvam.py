"""E5 guards, tested with a fake transport (no network, no spend)."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from grengine import sarvam
from grengine.sarvam import (CreditsExhaustedError, MissingKeyError, RateLimiter, SarvamClient,
                             SpendCapReachedError, SpendTracker, cost_inr)

OK_BODY = json.dumps({
    "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "{}"}}],
    "usage": {"prompt_tokens": 10000, "completion_tokens": 2000, "total_tokens": 12000,
              "completion_tokens_details": {"reasoning_tokens": 1500},
              "prompt_tokens_details": {"cached_tokens": 4000}},
}).encode()


def err(status, code):
    return status, {}, json.dumps({"error": {"code": code, "message": "x"}}).encode()


class FakePost:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, url, headers, body, timeout):
        self.calls.append(headers)
        return self.replies.pop(0)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"SARVAM_API_KEY": "test-key"}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def client(self, replies, cap=50.0):
        self.post = FakePost(replies)
        self.sleeps = []
        spend = SpendTracker(cap_inr=cap, spend_dir=Path(self.tmp.name), today="2026-11-18")
        limiter = RateLimiter(rpm=30, clock=lambda: 0.0, sleep=lambda s: None)
        return SarvamClient(spend=spend, limiter=limiter, post=self.post, sleep=self.sleeps.append)

    def chat(self, c):
        return c.chat([{"role": "user", "content": "hi"}], max_tokens=100, reasoning_effort="low", temperature=0.2)


class TestKey(Base):
    def test_missing_key_fails_clearly_before_any_call(self):
        with mock.patch.dict(os.environ, {"SARVAM_API_KEY": ""}):
            with self.assertRaises(MissingKeyError) as cm:
                SarvamClient(post=FakePost([]))
        self.assertIn("SARVAM_API_KEY is not set", str(cm.exception))

    def test_key_sent_in_header_and_not_in_errors(self):
        c = self.client([err(400, "invalid_request_error")])
        with self.assertRaises(sarvam.APIError) as cm:
            self.chat(c)
        self.assertEqual(self.post.calls[0]["api-subscription-key"], "test-key")
        self.assertNotIn("test-key", str(cm.exception))


class TestCost(Base):
    def test_cost_includes_cached_and_reasoning(self):
        u = cost_inr(json.loads(OK_BODY)["usage"])
        # 6000 uncached * 10 + 4000 cached * 0.25 + 2000 output * 25, per 1M
        self.assertAlmostEqual(u["cost_inr"], (60000 + 1000 + 50000) / 1e6)
        self.assertEqual(u["reasoning_tokens"], 1500)

    def test_spend_recorded(self):
        c = self.client([(200, {}, OK_BODY)])
        r = self.chat(c)
        self.assertAlmostEqual(c.spend.spent(), r.usage["cost_inr"])


class TestStops(Base):
    def test_402_stops_without_retry(self):
        c = self.client([err(402, "insufficient_quota_error"), (200, {}, OK_BODY)])
        with self.assertRaises(CreditsExhaustedError):
            self.chat(c)
        self.assertEqual(len(self.post.calls), 1)

    def test_cap_reached_blocks_call(self):
        c = self.client([(200, {}, OK_BODY)], cap=0.05)
        c.spend.add(0.05)
        with self.assertRaises(SpendCapReachedError):
            self.chat(c)
        self.assertEqual(self.post.calls, [])

    def test_call_that_could_pass_cap_is_blocked(self):
        c = self.client([(200, {}, OK_BODY)], cap=0.05)
        with self.assertRaises(SpendCapReachedError):
            c.chat([{"role": "user", "content": "x"}], max_tokens=4096, reasoning_effort="low",
                   temperature=0.2, prompt_tokens_estimate=10000)  # worst case Rs 0.2024
        self.assertEqual(self.post.calls, [])

    def test_seat_budget_429_not_retried(self):
        c = self.client([err(429, "seat_budget_exhausted_error")])
        with self.assertRaises(sarvam.APIError):
            self.chat(c)
        self.assertEqual(len(self.post.calls), 1)


class TestRetry(Base):
    def test_429_and_503_retried_with_backoff(self):
        c = self.client([err(429, "rate_limit_exceeded_error"), err(503, "model_overloaded"), (200, {}, OK_BODY)])
        r = self.chat(c)
        self.assertEqual(r.attempts, 3)
        self.assertEqual(len(self.sleeps), 2)
        self.assertLess(self.sleeps[0], self.sleeps[1] + 1)  # exponential: ~2s then ~4s

    def test_gives_up_after_max_retries(self):
        c = self.client([err(503, "model_overloaded")] * (sarvam.MAX_RETRIES + 1))
        with self.assertRaises(sarvam.APIError):
            self.chat(c)
        self.assertEqual(len(self.post.calls), sarvam.MAX_RETRIES + 1)


class TestRateLimiter(unittest.TestCase):
    def test_waits_when_window_full(self):
        t = [0.0]
        slept = []

        def sleep(s):
            slept.append(s)
            t[0] += s
        rl = RateLimiter(rpm=3, clock=lambda: t[0], sleep=sleep)
        for _ in range(3):
            self.assertEqual(rl.wait(), 0.0)
        self.assertGreater(rl.wait(), 59)  # 4th call in the same minute waits

    def test_must_be_below_sarvam_limit(self):
        with self.assertRaises(ValueError):
            RateLimiter(rpm=60)


if __name__ == "__main__":
    unittest.main()
