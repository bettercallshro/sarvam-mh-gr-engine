"""Checks against the real corpus in corpus/."""
import unittest

from grengine.citations import build_graph
from grengine.corpus import DEFAULT_CORPUS_DIR, load_corpus
from grengine.twins import find_twins, group_ids


@unittest.skipUnless((DEFAULT_CORPUS_DIR / "GRs.json").exists(), "corpus/ missing")
class TestCorpusIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grs, cls.failures = load_corpus()
        cls.twins = find_twins(cls.grs)
        cls.group_of = group_ids(cls.grs, cls.twins)
        cls.graph = build_graph(cls.grs, cls.group_of)
        cls.edges = {(e["from"], e["to"]) for e in cls.graph["edges"]}

    def test_all_loaded(self):
        self.assertEqual(len(self.grs), 112)
        self.assertEqual(self.failures, [])

    def test_known_twins(self):
        pairs = {frozenset((t["en_code"], t["mr_code"])) for t in self.twins}
        self.assertIn(frozenset(("201810121542077211", "201810161857288711")), pairs)
        self.assertIn(frozenset(("201809281816318011", "201809281811031811")), pairs)

    def test_same_date_different_grs_are_not_twins(self):
        # 30-11-2018 Fintech addendum and corrigendum: same date and number, different GRs
        self.assertNotEqual(self.group_of["201811301239595811"], self.group_of["201811301240117211"])

    def test_amendment_links(self):
        for later, earlier in [
            ("201906191741481211", "201801291824268911"),  # cloud deadline addendum
            ("202104231756150811", "201801291824268911"),  # cloud empanelment ended
            ("202304131657547811", "201912241451082111"),  # laptop cap corrigendum
            ("202011271209526511", "202011261535430611"),  # stay of recovery order
            ("202312151508137711", "202310041905383211"),  # consultant rates clarification
            ("202111301536272711", "201810121542077211"),  # Maha DBT paras 8 and 9
            ("202107191443218111", "202104061557307811"),  # disability reservation corrigendum
        ]:
            self.assertIn((later, earlier), self.edges)

    def test_unrelated_same_date_not_linked(self):
        # "065/प्र.क्र.1/2018, दि.17.02.2018" is a GR not in the corpus, not the
        # 17-02-2018 tender committee GR that shares the date
        self.assertNotIn(("202211041809363311", "201802171427235111"), self.edges)

    def test_missing_grs_are_unresolved(self):
        cited = {u["cited_date"] for u in self.graph["unresolved"]}
        for d in ("24-02-2015", "19-09-2017", "09-05-2019"):
            self.assertIn(d, cited)


if __name__ == "__main__":
    unittest.main()
