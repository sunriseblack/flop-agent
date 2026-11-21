import unittest
from fractions import Fraction

from research.period_origin_replay import allocate, compare, replay


class PeriodOriginTests(unittest.TestCase):
    def test_fixed_cohort_half_open_and_partial_edges(self):
        # A supplies all spend in the first bucket. B owns the second. The shifted middle is mixed.
        rows = [(1, "A", 1), (4, "A", 1), (5, "B", 3), (8, "B", 1), (10, "C", 99)]
        base, empty, count = allocate(rows, 0, 10, 5, 0)
        self.assertEqual((base, empty, count), ({"A": Fraction(1, 2), "B": Fraction(1, 2)}, 0, 2))
        shifted, empty, count = allocate(rows, 0, 10, 5, 2)
        self.assertEqual((shifted, empty, count), ({"A": Fraction(13, 40), "B": Fraction(27, 40)}, 0, 3))
        self.assertEqual(compare(base, shifted), (Fraction(7, 40), Fraction(7, 40)))
        for phase in range(5):
            control, _, _ = allocate(rows, 0, 10, 5, phase, proportional=True)
            self.assertEqual(control, {"A": Fraction(1, 3), "B": Fraction(2, 3)})

    def test_empty_edge_goes_to_reserve_once(self):
        rows = [(2, "A", 2), (7, "A", 1)]
        result, empty, count = allocate(rows, 0, 10, 5, 2)
        self.assertEqual((result, empty, count), ({"A": Fraction(4, 5), None: Fraction(1, 5)}, 1, 3))

    def test_constant_composition_is_phase_invariant(self):
        rows = [(b, opener, amount) for b in range(8, 20) for opener, amount in [("A", 7), ("B", 3)]]
        for phase in range(5):
            result, _, _ = allocate(rows, 8, 20, 5, phase)
            self.assertEqual(result, {"A": Fraction(7, 10), "B": Fraction(3, 10)})

    def test_reject_incompatible_input_and_exclude_same_address(self):
        row = dict(statusBlockNumber=2, cooperative=True, agent="A", miner="B", escrow="8", minerPaid="7")
        report = replay([row, dict(row, miner="A")], 0, 4)
        self.assertEqual((report["included_rows"], report["excluded_equal_addresses"], report["openers"]), (1, 1, 1))
        for changes in ({"cooperative": False}, {"miner": ""}, {"escrow": "8.2"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replay([dict(row, **changes)], 0, 4)
