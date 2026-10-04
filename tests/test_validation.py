"""Input normalization / validation tests."""

import unittest

from app.utils.validation import InputError, normalize_raw


class TestNormalization(unittest.TestCase):
    def test_decimal_integer(self):
        n = normalize_raw("1716201234")
        self.assertEqual(n.kind, "int")
        self.assertEqual(n.base if hasattr(n, "base") else n.interpretations[0][1], "dec")
        self.assertEqual(n.canonical, "1716201234")
        self.assertFalse(n.is_hex_notation)
        self.assertEqual(n.interpretations[0][0], 1716201234)

    def test_decimal_with_sign(self):
        n = normalize_raw("-978307200")
        self.assertEqual(n.interpretations[0][0], -978307200)
        self.assertTrue(n.negative)

    def test_explicit_hex(self):
        n = normalize_raw("0x01D71F0E96F4EBF0")
        self.assertTrue(n.is_hex_notation)
        self.assertEqual(n.interpretations[0][1], "hex")
        self.assertEqual(n.interpretations[0][0], 0x01D71F0E96F4EBF0)

    def test_bare_hex_with_letters(self):
        n = normalize_raw("ABCDEF")
        self.assertTrue(n.is_hex_notation)
        self.assertEqual(n.interpretations[0][0], 0xABCDEF)

    def test_all_digits_get_hex_alternative(self):
        n = normalize_raw("1716201234567")
        bases = {b for _v, b, _h in n.interpretations}
        self.assertIn("dec", bases)
        self.assertIn("hex", bases)

    def test_float(self):
        n = normalize_raw("45221.5")
        self.assertEqual(n.kind, "float")
        self.assertEqual(n.interpretations[0][1], "float")
        self.assertEqual(float(n.interpretations[0][0]), 45221.5)

    def test_whitespace_is_stripped(self):
        n = normalize_raw("  1716201234  ")
        self.assertEqual(n.canonical, "1716201234")

    def test_empty_raises(self):
        with self.assertRaises(InputError):
            normalize_raw("   ")

    def test_invalid_characters_raise(self):
        for bad in ("12abc.xx", "1716,2012", "17/12/2020", "hello"):
            with self.assertRaises(InputError):
                normalize_raw(bad)

    def test_malformed_hex_raises(self):
        with self.assertRaises(InputError):
            normalize_raw("0x")
        with self.assertRaises(InputError):
            normalize_raw("0x12GG")

    def test_huge_integer_is_accepted_as_number(self):
        n = normalize_raw("9" * 40)
        self.assertEqual(n.kind, "int")


if __name__ == "__main__":
    unittest.main()