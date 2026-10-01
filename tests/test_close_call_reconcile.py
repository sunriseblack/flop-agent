"""Offline multi-sweep reconciliation checks; no network or real identity key."""

import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_reconcile as reconcile  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def did_from_private(private):
    raw = b"\xed\x01" + private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    value = int.from_bytes(raw, "big")
    encoded = ""
    while value:
        value, digit = divmod(value, 58)
        encoded = ALPHABET[digit] + encoded
    return "did:key:z" + encoded


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.did = did_from_private(self.private)
        self.entries = []
        self.files = {}
        flows = []
        for n, status, rows in (
                (5, "full", [("trade-a", "settled")]),
                (6, "redacted", [("trade-a", "void"), ("trade-b", "void")])):
            record = {"input": {"n": n, "owners": [],
                                "trades": [{"id": key} for key, _ in rows]},
                      "output": {"sweep": n, "minted": [],
                                 "trades": [{"id": key, "outcome": outcome}
                                            for key, outcome in rows]}}
            raw = json.dumps(record, separators=(",", ":")).encode()
            digest = hashlib.sha256(raw).hexdigest() if status == "full" else "b" * 64
            path = f"{'sweeps' if status == 'full' else 'redacted'}/{digest}.json"
            entry = {"n": n, "file": digest, "status": status,
                     "path": path, "bytes": len(raw)}
            if status == "redacted":
                entry["sha256"] = hashlib.sha256(raw).hexdigest()
            self.entries.append(entry)
            self.files[reconcile.ARCHIVE + path] = raw
            text = json.dumps({"t": "flow", "n": n, "file": digest}, separators=(",", ":"))
            nonce = 1000 + n
            signature = self.private.sign(f"d-close1-flow|{nonce}|{text}".encode())
            flows.append({"seq": n, "from": self.did, "nonce": nonce, "text": text,
                          "sig": base64.urlsafe_b64encode(signature).decode().rstrip("=")})
        self.files[reconcile.ARCHIVE + "index.json"] = json.dumps(
            {"sweeps": self.entries}).encode()
        self.files[reconcile.FLOW_EXPORT] = (
            "\n".join(json.dumps(row) for row in flows) + "\n").encode()

    def fetch(self, url, limit, timeout):
        return self.files[url]

    def test_complete_range_preserves_settled_and_void_duplicates(self):
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch) as fetch:
            result = reconcile.reconcile(5, 6, ["trade-a", "trade-b", "trade-c"],
                                         referee_did=self.did)
        self.assertEqual(result["status"], "complete_range")
        self.assertEqual(result["missing_sweeps"], [])
        self.assertEqual(fetch.call_count, 4)
        self.assertEqual(result["trade_ids"]["trade-a"]["classification"],
                         "published_settled")
        self.assertEqual(len(result["trade_ids"]["trade-a"]["published_outcomes"]), 2)
        self.assertEqual(result["trade_ids"]["trade-b"]["classification"],
                         "published_void_only")
        self.assertEqual(result["trade_ids"]["trade-c"]["classification"],
                         "not_observed")
        self.assertEqual(result["checked_sweeps"][0]["provenance"], "signed_full_hash")
        self.assertIn("unsigned_index", result["checked_sweeps"][1]["provenance"])

    def test_missing_sweep_is_incomplete_not_negative_evidence(self):
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch):
            result = reconcile.reconcile(5, 7, ["trade-c"], referee_did=self.did)
        self.assertEqual(result["status"], "partial_range")
        self.assertEqual(result["missing_sweeps"], [7])
        self.assertEqual(result["trade_ids"]["trade-c"]["classification"],
                         "not_observed")

    def test_rejects_corrupt_records_and_wrong_referee(self):
        redacted_url = reconcile.ARCHIVE + self.entries[1]["path"]
        self.files[redacted_url] += b" "
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, "do not match index"):
                reconcile.reconcile(5, 6, ["trade-a"], referee_did=self.did)
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, "signature, referee DID"):
                reconcile.reconcile(5, 5, ["trade-a"])

    def test_rejects_ambiguous_or_unbounded_inputs(self):
        for first, last, ids in ((0, 1, ["x"]), (5, 69, ["x"]),
                                 (5, 5, []), (5, 5, ["bad id"]),
                                 (5, 5, ["x", "x"])):
            with self.assertRaisesRegex(ValueError, "invalid sweep range"):
                reconcile.reconcile(first, last, ids)
        index = json.dumps({"sweeps": self.entries + [self.entries[0]]}).encode()
        self.files[reconcile.ARCHIVE + "index.json"] = index
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, "not uniquely indexed"):
                reconcile.reconcile(5, 5, ["trade-a"], referee_did=self.did)

    def test_rejects_two_published_settlements_of_one_id(self):
        entry = self.entries[1]
        url = reconcile.ARCHIVE + entry["path"]
        record = json.loads(self.files[url])
        record["output"]["trades"][0]["outcome"] = "settled"
        raw = json.dumps(record, separators=(",", ":")).encode()
        entry["bytes"] = len(raw)
        entry["sha256"] = hashlib.sha256(raw).hexdigest()
        self.files[url] = raw
        self.files[reconcile.ARCHIVE + "index.json"] = json.dumps(
            {"sweeps": self.entries}).encode()
        with patch.object(reconcile, "fetch_bytes", side_effect=self.fetch):
            with self.assertRaisesRegex(ValueError, "multiple published settlements"):
                reconcile.reconcile(5, 6, ["trade-a"], referee_did=self.did)


if __name__ == "__main__":
    unittest.main()
