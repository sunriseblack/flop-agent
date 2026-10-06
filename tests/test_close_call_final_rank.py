"""Offline boundary and integrity checks for the full final-rank reader."""

import gzip
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_final_rank as final_rank  # noqa: E402


def sample_record():
    owners = ["did:key:zAAA", "did:key:zBBB", "did:key:zCCC"]
    rows = [
        {"fees": "1.000000", "key": owner, "places": [], "position": "0.00",
         "score": str(3 - n), "sharing": 0}
        for n, owner in enumerate(owners)
    ]
    return json.dumps(
        {"input": {"px": "234.69", "t": "final"},
         "output": {"S": "234.69", "fees": "3.000000", "owners": 3,
                    "standings": rows, "zero_sum": "0.000000"}},
        sort_keys=True, separators=(",", ":")).encode("ascii")


class FinalRankTests(unittest.TestCase):
    def test_every_byte_boundary_gives_same_count_and_rank(self):
        record = sample_record()
        for chunk_size in (1, 2, 3, 7, 17, 43, 1024):
            with self.subTest(chunk_size=chunk_size):
                scanner = final_rank.FinalScanner("did:key:zBBB")
                for offset in range(0, len(record), chunk_size):
                    scanner.feed(record[offset:offset + chunk_size])
                result = scanner.finish()
                self.assertEqual(result["owners_counted"], 3)
                self.assertEqual(result["owner"]["rank"], 2)
                self.assertEqual(result["owner"]["row"]["score"], "2")
                self.assertEqual(result["decompressed_bytes"], len(record))

    def test_missing_and_duplicate_owner_rejected(self):
        record = sample_record()
        scanner = final_rank.FinalScanner("did:key:zDDD")
        scanner.feed(record)
        with self.assertRaisesRegex(ValueError, "not found"):
            scanner.finish()
        duplicate = record.replace(b"did:key:zCCC", b"did:key:zBBB")
        scanner = final_rank.FinalScanner("did:key:zBBB")
        with self.assertRaisesRegex(ValueError, "more than once"):
            scanner.feed(duplicate)
            scanner.finish()

    def test_gzip_stream_and_truncation(self):
        compressed = gzip.compress(sample_record())
        chunks = [compressed[i:i + 5] for i in range(0, len(compressed), 5)]
        result = final_rank.scan_gzip(chunks, "did:key:zCCC")
        self.assertEqual(result["owner"]["rank"], 3)
        self.assertEqual(result["owners_counted"], 3)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            final_rank.scan_gzip([compressed[:-4]], "did:key:zCCC")


if __name__ == "__main__":
    unittest.main()
