"""Offline signature and cursor tests for the read-only offer watcher."""

import base64
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_watch_offer as watcher  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def did_for(key):
    raw = b"\xed\x01" + key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    value = int.from_bytes(raw, "big")
    encoded = ""
    while value:
        value, digit = divmod(value, 58)
        encoded = ALPHABET[digit] + encoded
    return "did:key:z" + encoded


def sign(key, payload):
    return base64.urlsafe_b64encode(key.sign(payload.encode())).decode().rstrip("=")


class WatchOfferTests(unittest.TestCase):
    def setUp(self):
        self.maker_key = Ed25519PrivateKey.generate()
        self.taker_key = Ed25519PrivateKey.generate()
        self.maker = did_for(self.maker_key)
        self.taker = did_for(self.taker_key)
        self.terms = {"id": "bounded-1", "maker": self.maker, "px": "229.00",
                      "qty": "40", "side": "buy", "taker": "any", "until": 1770}
        self.maker_sig = sign(
            self.maker_key, "close-1|terms|" + watcher.canonical_terms(self.terms))

    def message(self, seq, body, key, did):
        text = json.dumps(body, sort_keys=True, separators=(",", ":"))
        nonce = 1790868000000 + seq
        return {"seq": seq, "from": did, "nonce": nonce, "text": text,
                "sig": sign(key, f"close1|{nonce}|{text}"), "ts": "2026-10-01T15:20:00Z"}

    def offer_message(self, seq=100):
        body = {"t": "offer", "season": "close-1", "terms": self.terms,
                "maker_sig": self.maker_sig}
        return self.message(seq, body, self.maker_key, self.maker)

    def trade_message(self, seq=101):
        payload = f"close-1|accept|{watcher.canonical_terms(self.terms)}|{self.taker}"
        body = {"t": "trade", "season": "close-1", "terms": self.terms,
                "taker": self.taker, "maker_sig": self.maker_sig,
                "taker_sig": sign(self.taker_key, payload)}
        return self.message(seq, body, self.taker_key, self.taker)

    def snapshot(self, first, *messages):
        return {"room": "close1", "first_seq": first, "messages": list(messages)}

    def test_offer_and_both_nested_trade_signatures(self):
        offer = watcher.offer_at(self.snapshot(100, self.offer_message()), "close1", 100)
        trade = watcher.matching_trade("close1", self.trade_message(), offer)
        self.assertEqual(trade["seq"], 101)
        self.assertEqual(trade["taker"], self.taker)
        self.assertTrue(trade["outer_and_both_nested_signatures_verified"])
        cursor, found = watcher.scan_snapshot(
            self.snapshot(100, self.trade_message()), "close1", 100, offer)
        self.assertEqual(cursor, 101)
        self.assertEqual(found, trade)
        with patch.object(watcher, "read_snapshot",
                          return_value=self.snapshot(100, self.trade_message())):
            live = watcher.watch_cursor("close1", 100, 0, offer)
        self.assertEqual(live["status"], "signed_public_trade_observed")
        self.assertEqual(live["receipt"]["seq"], 101)

    def test_bad_signatures_and_wrong_terms_are_not_receipts(self):
        offer = watcher.offer_at(self.snapshot(100, self.offer_message()), "close1", 100)
        bad_outer = self.trade_message()
        bad_outer["text"] += " "
        self.assertIsNone(watcher.matching_trade("close1", bad_outer, offer))
        bad_taker = self.trade_message()
        body = json.loads(bad_taker["text"])
        body["taker_sig"] = self.maker_sig
        bad_taker = self.message(101, body, self.taker_key, self.taker)
        self.assertIsNone(watcher.matching_trade("close1", bad_taker, offer))
        wrong_terms = self.trade_message()
        body = json.loads(wrong_terms["text"])
        body["terms"] = {**self.terms, "px": "229.01"}
        wrong_terms = self.message(101, body, self.taker_key, self.taker)
        self.assertIsNone(watcher.matching_trade("close1", wrong_terms, offer))

    def test_rejects_missing_offer_and_retention_gap(self):
        with self.assertRaisesRegex(ValueError, "rolled past"):
            watcher.offer_at(self.snapshot(101), "close1", 100)
        with self.assertRaisesRegex(ValueError, "not available"):
            watcher.offer_at(self.snapshot(100), "close1", 100)
        offer = watcher.offer_at(self.snapshot(100, self.offer_message()), "close1", 100)
        with self.assertRaisesRegex(ValueError, "rolled past"):
            watcher.scan_snapshot(self.snapshot(102, self.trade_message(102)),
                                  "close1", 100, offer)

    def test_cursor_tail_gap_recovers_from_retained_export(self):
        skipped = self.snapshot(102, self.trade_message(102))
        recovered = self.snapshot(100, self.offer_message(), self.trade_message())
        with patch.object(watcher, "read_snapshot", return_value=skipped), \
                patch.object(watcher, "read_export_snapshot", return_value=recovered):
            result = watcher.read_catching_up("close1", 99)
        self.assertEqual(result, recovered)
        self.assertEqual(watcher.offer_at(result, "close1", 100)["offer_seq"], 100)

    def test_bounded_export_recovers_only_contiguous_sequences(self):
        raw = b"\n".join(json.dumps(m).encode() for m in
                         (self.offer_message(), self.trade_message())) + b"\n"
        with patch.object(watcher.urllib.request, "urlopen", return_value=io.BytesIO(raw)):
            result = watcher.read_export_snapshot("close1", 99)
        self.assertEqual(result["first_seq"], 100)
        self.assertEqual(result["last_seq"], 101)
        self.assertEqual(len(result["messages"]), 2)
        bad = b"\n".join(json.dumps(m).encode() for m in
                         (self.offer_message(), self.trade_message(102))) + b"\n"
        with patch.object(watcher.urllib.request, "urlopen", return_value=io.BytesIO(bad)):
            with self.assertRaisesRegex(ValueError, "gapped"):
                watcher.read_export_snapshot("close1", 99)

    def test_zero_second_snapshot_watch_never_claims_unfilled(self):
        snapshots = [self.snapshot(100, self.offer_message()), self.snapshot(100)]
        with patch.object(watcher, "read_snapshot", side_effect=snapshots):
            result = watcher.watch("close1", 100, 0)
        self.assertEqual(result["status"], "no_signed_public_trade_observed")
        self.assertIn("Not proof", result["caution"])


if __name__ == "__main__":
    unittest.main()
