"""Offline regression checks for the Kibble payment-splitter answer."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "contributions"))
from kibble_k0072571c57_payment_splitter import split_cents  # noqa: E402


class SplitCentsTests(unittest.TestCase):
    def test_remainder_is_deterministic_and_no_cents_are_lost(self):
        self.assertEqual(split_cents(10, 3), [4, 3, 3])
        self.assertEqual(split_cents(1, 3), [1, 0, 0])
        self.assertEqual(split_cents(0, 3), [0, 0, 0])

    def test_share_invariants_over_many_small_inputs(self):
        for total in range(101):
            for recipients in range(1, 21):
                shares = split_cents(total, recipients)
                self.assertEqual(len(shares), recipients)
                self.assertEqual(sum(shares), total)
                self.assertLessEqual(max(shares) - min(shares), 1)

    def test_invalid_inputs_are_rejected(self):
        for total, recipients in ((10, 0), (10, -1), (-1, 3), (0.1, 3),
                                  (10, 2.5), (True, 3), (10, False)):
            with self.subTest(total=total, recipients=recipients):
                with self.assertRaises(ValueError):
                    split_cents(total, recipients)


if __name__ == "__main__":
    unittest.main()
