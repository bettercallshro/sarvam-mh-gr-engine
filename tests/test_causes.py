"""eval/causes.csv has exactly one row for each scored answer that isn't fully correct."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAUSES = {"layout", "reply", "oldfirst", "unlinked", "samedate", "yes", "notfound", "opener",
          "splitdate", "madeup", "other"}
ENDINGS = {"fixed": "Fixed: right in both final runs.", "other_run": "Right in the other run.",
           "one_final": "Right in one final run, not the other.", "open": "Still open."}


def read(name):
    with (ROOT / "eval" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestCauses(unittest.TestCase):
    def test_one_row_per_answer_not_fully_correct(self):
        causes = read("causes.csv")
        self.assertEqual(len(causes), 55)
        pairs = [(r["run"], int(r["question_id"])) for r in causes]
        self.assertEqual(len(pairs), len(set(pairs)))
        not_fully = {(r["run"], int(r["question_id"])) for r in read("scores.csv") if r["fully_correct"] == "no"}
        self.assertEqual(set(pairs), not_fully)

    def test_codes_and_status_match_the_line(self):
        for r in read("causes.csv"):
            self.assertIn(r["cause"], CAUSES)
            self.assertIn(r["status"], ENDINGS)
            self.assertTrue(r["why"].endswith(ENDINGS[r["status"]]), r)


if __name__ == "__main__":
    unittest.main()
