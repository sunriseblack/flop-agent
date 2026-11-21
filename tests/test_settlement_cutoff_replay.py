import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.settlement_cutoff_replay import read_settlements, summarize


class CutoffReplayTests(unittest.TestCase):
    def test_open_and_terminal_boundaries_and_overlapping_cutoffs(self):
        # Inclusive open, exclusive settlement. A terminal exactly at H+G is covered.
        rows = [(10, 12, 7, True, 0), (10, 10, 41, False, 0),
                (13, 14, 11, False, 0), (9, 13, 5, False, 0)]
        result = summarize(rows, heights=[10, 12], grace=[0, 1, 2, 3])
        self.assertEqual(result["median_crossing_channels"], 1.5)
        self.assertEqual(result["cohorts"]["other_opener"]["crossing_channels"], 1)
        self.assertEqual([(g["channel_cutoff_pairs"], g["distinct_channels"],
                           g["miner_paid_raw_across_pairs"]) for g in result["outside_grace"]],
                         [(3, 2, "17"), (2, 2, "12"), (1, 1, "5"), (0, 0, "0")])

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.row = {"channelId": "0x" + "01" * 32, "status": "settled", "paymentStatus": "PAID",
                    "observationHead": "finalized", "openedBlock": 10, "statusBlockNumber": 12,
                    "minerPaid": "12370493928571277405", "agent": "example-opener",
                    "settlement": {"event": "computeChannel.Settled", "blockNumber": 12, "timestamp": 1500}}

    def page(self, data, **changes):
        meta = {"total": len(data), "limit": 100, "offset": 0, "hasMore": False, **changes}
        (self.folder / "0.json").write_text(json.dumps({"pagination": meta, "data": data}))
        return read_settlements(self.folder)

    def test_exact_amount_and_missing_event_remains_unknown(self):
        missing = dict(self.row, channelId="0x" + "02" * 32)
        del missing["settlement"]
        rows, excluded = self.page([self.row, missing])
        self.assertEqual(rows, [(10, 12, 12370493928571277405, False, 1500)])
        self.assertEqual(excluded, [missing["channelId"]])

    def test_reject_inconsistent_rows_or_pagination(self):
        for change in [{"status": "refunded"}, {"settlement": dict(self.row["settlement"], blockNumber=13)},
                       {"observationHead": "best"}, {"minerPaid": 12.5}, {"openedBlock": 14}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.page([dict(self.row, **change)])
        with self.assertRaises(ValueError):
            self.page([self.row, self.row])
        with self.assertRaises(ValueError):
            self.page([self.row], total=2)
