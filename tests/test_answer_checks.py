"""Post-answer checks: they correct the product answer, and every change is logged."""
import unittest

from grengine.answer import Answerer, Context, validate
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


class TestValidate(unittest.TestCase):
    GOOD = {"asked_for_code": None, "candidates_reviewed": [], "newer": [], "cited": [],
            "answer": "x", "status": "answered"}

    def test_good(self):
        self.assertEqual(validate(dict(self.GOOD), []), [])

    def test_bad_status_missing_fields_and_dups(self):
        bad = dict(self.GOOD, status=" ")
        del bad["cited"]
        errs = validate(bad, ["cited"])
        self.assertTrue(any("bad status" in e for e in errs))
        self.assertTrue(any("missing field: cited" in e for e in errs))
        self.assertTrue(any("duplicate keys" in e for e in errs))

    def test_echoed_document_is_invalid(self):
        self.assertTrue(validate({"code": "1", "text": "..."}, []))

    def test_none(self):
        self.assertEqual(validate(None, []), ["not a JSON object"])


@unittest.skipUnless((INDEX_DIR / "grs.json").exists(), "index not built")
class TestFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = Answerer()

    def test_date_in_answer_matching_no_gr_is_flagged(self):
        ctx = Context("q", [], [], [], [CLOUD], "text mentions 31.03.2020")
        parsed = {"status": "answered", "asked_for_code": CLOUD, "candidates_reviewed": [], "newer": [],
                  "cited": [{"code": CLOUD, "date": "29-01-2018", "title": "t", "quote": "q", "page": 1}],
                  "answer": "The 29-01-2018 circular; deadline 31-03-2020; see 11-05-2011."}
        _, _, flags = self.a.finalize(ctx, parsed)
        date_flags = [f for f in flags if f.startswith("date in answer")]
        self.assertEqual(len(date_flags), 2)
        self.assertTrue(any("11-05-2011" in f and "nowhere" in f for f in date_flags))
        self.assertTrue(any("31-03-2020" in f and "in the texts given" in f for f in date_flags))

    def test_only_candidates_of_asked_for_gr_must_be_reviewed(self):
        cands = [{"code": "201906191741481211", "of_code": CLOUD, "already_retrieved": False},
                 {"code": "202304131657547811", "of_code": LAPTOP, "already_retrieved": False}]
        ctx = Context("q", [], cands, [], [CLOUD, LAPTOP, "201906191741481211", "202304131657547811"], "")
        base = {"status": "answered", "answer": "x", "newer": [], "cited": [], "candidates_reviewed": []}
        _, _, flags = self.a.finalize(ctx, dict(base, asked_for_code=CLOUD))
        self.assertTrue(any("201906191741481211" in f and "202304131657547811" not in f for f in flags))
        _, _, flags = self.a.finalize(ctx, dict(base, asked_for_code=None))
        self.assertFalse(any("not reviewed" in f for f in flags))


class TestRepair(TestChecks):
    def test_mistyped_code_repaired_by_date(self):
        parsed = {"status": "answered", "answer": "x", "cited": [], "candidates_reviewed": [],
                  "newer": [{"code": "202304131657523211", "date": "12-04-2023", "what_changed": "x"}]}
        result, corrections, _ = self.a.finalize(self.ctx([LAPTOP, "202304131657547811"]), parsed)
        self.assertEqual(result["newer"][0]["code"], "202304131657547811")
        self.assertEqual(corrections[0]["check"], "repair_code_by_date")

    def test_unknown_code_with_unmatched_date_dropped(self):
        parsed = {"status": "answered", "answer": "x", "cited": [], "candidates_reviewed": [],
                  "newer": [{"code": "202304131657523211", "date": "01-01-2023", "what_changed": "x"}]}
        result, corrections, _ = self.a.finalize(self.ctx([LAPTOP]), parsed)
        self.assertEqual(result["newer"], [])
        self.assertEqual(corrections[0]["check"], "drop_unknown_code")


if __name__ == "__main__":
    unittest.main()


class TestRepairsAndCoverage(unittest.TestCase):
    def test_missing_asked_for_code_becomes_null(self):
        from grengine.answer import repair_reply
        p, reps = repair_reply({"status": "answered", "answer": "x"})
        self.assertIsNone(p["asked_for_code"])
        self.assertEqual(len(reps), 1)

    def test_code_keyed_review_flattened(self):
        from grengine.answer import repair_reply
        p, reps = repair_reply({"asked_for_code": None, "candidates_reviewed": [
            {"202403051249430211": {"effect": "clarifies", "reason": "r"}}]})
        self.assertEqual(p["candidates_reviewed"][0],
                         {"code": "202403051249430211", "effect": "clarifies", "reason": "r"})
        self.assertEqual(len(reps), 1)

    def test_review_coverage(self):
        from grengine.answer import review_coverage
        parsed = {"candidates_reviewed": [{"code": "A", "effect": "cites_only", "reason": ""}]}
        self.assertEqual(review_coverage(parsed, ["A", "B"], {}), ["B"])


@unittest.skipUnless((INDEX_DIR / "grs.json").exists(), "index not built")
class TestLayoutAndAnswerFirst(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = Answerer()

    def test_retrieved_candidate_gets_its_own_block(self):
        # Q18: the 19-03-2021 corrigendum is retrieved AND a candidate of 20-03-2018
        ctx = self.a.build_context("Whose concurrence is needed for a consultant's scope of work?")
        self.assertIn("202103191753279311", ctx.listed_candidates)
        block = ctx.user_message.split("NEWER-GR CANDIDATES", 1)[1]
        self.assertIn("code: 202103191753279311", block)
        self.assertIn("Also RETRIEVED #", block)

    def test_number_facts(self):
        ctx = self.a.build_context("मातंस ३८१४/प्र.क्र.१७४/३९: what is the current limit?")
        self.assertIn("NUMBER FACTS", ctx.user_message)
        self.assertIn("202304131657547811", ctx.user_message.split("NUMBER FACTS", 1)[1].split("RETRIEVED", 1)[0])

    def test_compact_context_is_shorter(self):
        q = "Which university is responsible for the Academic module of the IUMS project?"
        self.assertLess(len(self.a.build_context(q, compact=True).user_message),
                        len(self.a.build_context(q).user_message))

    def test_answer_first_flags(self):
        ctx = Context("q", [], [], [], [CLOUD], "")
        base = {"asked_for_code": CLOUD, "candidates_reviewed": [], "newer": [],
                "cited": [{"code": CLOUD, "date": "29-01-2018", "title": "t", "quote": "q", "page": 1}]}
        _, _, flags = self.a.finalize(ctx, dict(base, status="not_found",
                                                answer="The circular sets a deadline. I couldn't find a GR on this in the corpus."))
        self.assertTrue(any("first sentence does not say" in f for f in flags))
        self.assertTrue(any("while citing the asked-for GR" in f for f in flags))
        _, _, flags = self.a.finalize(ctx, dict(base, status="answered", answer="Yes. It is amended."))
        self.assertFalse(any(f.startswith("answer-first") for f in flags))


@unittest.skipUnless((INDEX_DIR / "grs.json").exists(), "index not built")
class TestOddShapes(unittest.TestCase):
    def test_raw_answer_tolerates_strings_in_lists(self):
        a = Answerer()
        raw = a.raw_answer({"status": "answered", "answer": "x", "cited": ["201801291824268911"],
                            "newer": "none"})
        self.assertEqual(raw["cited"], [{"raw": "201801291824268911"}])
        self.assertEqual(raw["newer"], [{"raw": "none"}])
