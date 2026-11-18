import json
import unittest
from pathlib import Path

from grengine.citations import EVIDENCE_RANK, best_evidence, newer_candidates
from grengine.search import INDEX_DIR, Retriever, analyze


class TestQueryHandling(unittest.TestCase):
    def test_dates_and_numbers_removed_from_text_query(self):
        q = Retriever.strip_dates_numbers("A file cites the State cloud policy dated 19/01/2018. Is that current?")
        self.assertNotIn("2018", q)
        self.assertIn("Is that current?", q)
        q = Retriever.strip_dates_numbers("मातंस ३८१४/प्र.क्र.१७४/३९: what is the current limit?")
        self.assertNotIn("३८१४", q)
        q = Retriever.strip_dates_numbers("Is the 29 January 2018 cloud computing circular still current?")
        self.assertNotIn("January", q)

    def test_analyze_stems_and_drops_stopwords(self):
        self.assertEqual(analyze("the Consultants rates"), ["consultant", "rat"])
        self.assertEqual(analyze("date dated dates"), ["dat", "dat", "dat"])
        self.assertEqual(analyze("rate rates"), ["rat", "rat"])

    def test_evidence_order(self):
        self.assertEqual(best_evidence(["same_file", "date", "order"]), "order")
        self.assertLess(EVIDENCE_RANK["date+order"], EVIDENCE_RANK["same_file"])


@unittest.skipUnless((INDEX_DIR / "grs.json").exists(), "index not built")
class TestRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = Retriever()

    def top(self, q, k=5):
        return [h.group for h in self.rt.search(q, k=k)]

    def test_exact_date_lookup(self):
        self.assertEqual(self.top("Is the 26 November 2020 GR on the computer qualification certificate in force?")[0],
                         "202011261535430611")

    def test_number_lookup(self):
        self.assertIn("202304131657547811", self.top("मातंस ३८१४/प्र.क्र.१७४/३९: what is the current limit?"))

    def test_missing_gr_returns_citing_gr(self):
        self.assertIn("201912241451082111", self.top("Show me the 24 February 2015 GR on laptops for officers."))

    def test_off_topic_citers_of_missing_date_not_boosted(self):
        # 19-01-2018 is cited by CSC GRs (a different, missing GR) and, misdated, by the
        # Fintech GR for the cloud policy. Only the cloud-related citation should count.
        hits = self.rt.search("A file cites the State cloud policy dated 19/01/2018. Is that current?")
        boosted = {h.group for h in hits if "cites_missing" in h.reasons}
        self.assertNotIn("201909111829110711", boosted)
        self.assertIn("201801291824268911", [h.group for h in hits])

    def test_same_file_is_candidate_only(self):
        cands = newer_candidates("202105111646307611", self.rt.graph, self.rt.group_of)
        self.assertTrue(all(c["candidate_only"] for c in cands))


if __name__ == "__main__":
    unittest.main()
