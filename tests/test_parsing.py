import unittest

from grengine.corpus import split_pages
from grengine.dates import find_dates
from grengine.normalize import compact_numbers, to_ascii_digits
from grengine.orders import find_order_keys, order_key


class TestDigits(unittest.TestCase):
    def test_devanagari_to_ascii(self):
        self.assertEqual(to_ascii_digits("दि. २४.०२.२०१५"), "दि. 24.02.2015")

    def test_length_preserved(self):
        s = "रु. १,२०,०००"
        self.assertEqual(len(to_ascii_digits(s)), len(s))

    def test_compact_joins_ocr_split_digits(self):
        self.assertEqual(compact_numbers("से-२/३ ९"), "से-2/39")


class TestDates(unittest.TestCase):
    def dates(self, s):
        return [d.date for d in find_dates(s)]

    def test_numeric_marathi(self):
        self.assertEqual(self.dates("वाचा- दि. २४.१२.२०१९"), ["24-12-2019"])

    def test_marathi_month(self):
        self.assertEqual(self.dates("दिनांक - २७ नोव्हेंबर, २०२०."), ["27-11-2020"])

    def test_english_forms(self):
        self.assertEqual(self.dates("Dated - 29th January 2018"), ["29-01-2018"])
        self.assertEqual(self.dates("January 29, 2018"), ["29-01-2018"])
        self.assertEqual(self.dates("approved on 17.1.2018."), ["17-01-2018"])

    def test_two_digit_year(self):
        self.assertEqual(self.dates("dt 24.12.19"), ["24-12-2019"])

    def test_glued_list_number(self):
        self.assertEqual(self.dates("दिनांक 29.01.20183.सामान्य"), ["29-01-2018"])

    def test_invalid_ignored(self):
        self.assertEqual(self.dates("version 45.67.2018"), [])


class TestOrderKeys(unittest.TestCase):
    def test_marathi_and_english_forms_match(self):
        mr = order_key("मातंसं २०१८/प्र.क्र . २५/से-३/३ ९")
        en = order_key("GAD-2018/CR 25/Sect3/39")
        self.assertEqual(mr, en)
        self.assertEqual(mr, ("F", 2018, 25))

    def test_file_case_year(self):
        self.assertEqual(order_key("GAD-IT-060/3/2017"), ("F", 60, 3))
        self.assertEqual(order_key("मातंसं-००८८/२७/२०१६-DIR IT ( MH )"), ("F", 88, 27))

    def test_short_file_with_marker(self):
        self.assertEqual(order_key("मातंसं ०६५/प्र.क्र .१/२०१८"), ("F", 65, 1))

    def test_ocr_case_marker_without_halant(self):
        self.assertEqual(order_key("मातसं-२०२२/प्र.क . १ ९/से-२/३ ९"), ("F", 2022, 19))

    def test_machine_translation_markers(self):
        self.assertEqual(order_key("1717/ PR No. 111/39"), ("F", 1717, 111))
        self.assertEqual(order_key("Mattsam065/ P.No. 1/2018"), ("F", 65, 1))

    def test_slash_date_is_not_an_order_number(self):
        self.assertEqual(find_order_keys("dated 24/12/2019"), [])


class TestPages(unittest.TestCase):
    def test_split(self):
        pages = split_pages("# Page 1\nfirst\n# Page 2\nsecond\n")
        self.assertEqual(pages, {1: "first", 2: "second"})


if __name__ == "__main__":
    unittest.main()
