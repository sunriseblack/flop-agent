import unittest

from research.escrow_turnover_replay import profile, replay


def row(cid, lo, hi, opened, settled, paid=100):
    return {"channelId": cid, "openedBlock": lo, "statusBlockNumber": hi, "openedAt": opened,
            "settlement": {"timestamp": settled}, "minerPaid": str(paid)}


class EscrowTurnoverTests(unittest.TestCase):
    def test_duration_weighted_quantile_and_same_height_handoff(self):
        # A high balance for one of twenty blocks is outside the nearest-rank p95.
        p = profile([(-1, 19, 3), (19, 21, 9), (19, 19, 100)], 0, 20)
        self.assertEqual((p["area_raw"], p["p95_raw"], p["peak_raw"], p["first_peak"]),
                         ("66", "3", "9", 19))

    def test_two_clocks_fixed_flow_and_clipped_edges(self):
        rows = [row("pre", 1, 4, 10, 40), row("in", 8, 12, 80, 120, 5),
                row("a", 10, 11, 100, 110), row("b", 11, 19, 110, 290),
                row("out", 18, 21, 280, 310, 8), row("future", 20, 23, 300, 330)]
        r = replay(rows, (10, 20), (100, 300))
        self.assertEqual((r["contained_channels"], r["contained_miner_paid_raw"]), (2, "200"))
        self.assertEqual(r["contained_by_block"]["area_raw"], "900")
        self.assertEqual(r["contained_by_timestamp"]["area_raw"], "19000")
        self.assertEqual(r["overlapping_by_block"]["area_raw"], str(900 + 2*5 + 2*8))
        self.assertEqual(r["peak_channel_ids"], ["b", "out"])
        self.assertEqual(r["contained_by_timestamp"]["turnovers_per_utc_day"], "909473.68421053")

    def test_zero_duration_and_uncovered_or_inconsistent_capture(self):
        before, after = row("pre", 0, 1, 0, 1), row("post", 10, 11, 10, 11)
        r = replay([before, row("a", 3, 3, 3, 3), after], (2, 9), (2, 9))
        self.assertEqual(r["contained_miner_paid_raw"], "100")
        self.assertIsNone(r["contained_by_timestamp"]["turnovers_per_utc_day"])
        for rows in ([before, after], [row("a", 3, 6, 3, 6), after],
                     [before, row("a", 3, 6, 3, 10), after],
                     [before, row("a", 3, 6, 5, 4), after]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                replay(rows, (2, 9), (2, 9))
