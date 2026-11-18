"""Post-answer checks: they correct the product answer, and every change is logged."""
import unittest

from grengine.answer import Answerer, Context
from grengine.search import INDEX_DIR

CLOUD = "201801291824268911"   # 29-01-2018 cloud circular (English original)
LAPTOP = "201912241451082111"  # 24-12-2019 laptop corrigendum (Marathi original)


@unittest.skipUnless((INDEX_DIR / "grs.json").exists(), "index not built")
class TestChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = Answerer()

    def ctx(self, codes):
        return Context("q", [], [], [], list(codes), "")

    def test_raw_answer_is_untouched(self):
        parsed = {"status": "answered", "answer": "x", "cited": [
            {"code": "999", "date": "01-01-2001", "title": "made up", "quote": "q", "page": 9}], "newer": []}
        raw = self.a.raw_answer(parsed)
        self.assertEqual(raw["cited"][0]["code"], "999")
        self.assertEqual(raw["cited"][0]["date"], "01-01-2001")

    def test_corrections_logged(self):
        quote = "Considering the growing adoption of online services by citizens of the State"
        parsed = {"status": "answered", "answer": "The circular is still in force.",
                  "cited": [
                      {"code": CLOUD, "date": "19-01-2018", "title": "Cloud policy", "quote": quote, "page": 3},
                      {"code": "201501010000000000", "date": "24-02-2015", "title": "x", "quote": "y", "page": 1},
                      {"code": LAPTOP, "date": "24-12-2019", "title": "t", "quote": "not in the text", "page": 1},
                  ],
                  "candidates_reviewed": [], "newer": []}
        result, corrections, flags = self.a.finalize(self.ctx([CLOUD, LAPTOP]), parsed)
        checks = {(c["check"], c["where"]) for c in corrections}
        self.assertIn(("date_from_metadata", "cited[0].date"), checks)
        self.assertIn(("title_from_metadata", "cited[0].title"), checks)
        self.assertIn(("page_from_quote", "cited[0].page"), checks)
        self.assertIn(("drop_unknown_code", "cited[1]"), checks)
        # product answer is corrected
        self.assertEqual(result["cited"][0]["date"], "29-01-2018")
        self.assertEqual(result["cited"][0]["page"], 1)
        self.assertEqual(len(result["cited"]), 2)
        # problems that are not corrected are flagged, and the quote is kept
        self.assertTrue(any("quote not found" in f for f in flags))
        self.assertFalse(result["cited"][1]["quote_verified"])
        self.assertTrue(any("in force" in f for f in flags))

    def test_corpus_code_not_given_is_dropped(self):
        parsed = {"status": "answered", "answer": "x", "cited": [], "candidates_reviewed": [],
                  "newer": [{"code": LAPTOP, "date": "24-12-2019", "what_changed": "x"}]}
        result, corrections, _ = self.a.finalize(self.ctx([CLOUD]), parsed)
        self.assertEqual(result["newer"], [])
        self.assertIn("not given to the model", corrections[0]["after"])


if __name__ == "__main__":
    unittest.main()
