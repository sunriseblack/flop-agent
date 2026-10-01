"""Offline checks for bounded Close Call paper-offer preparation."""

import base64
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_offer as offer  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class CloseCallOfferTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + public)
        self.now = dt.datetime(2026, 10, 1, 14, 10, tzinfo=dt.timezone.utc)
        self.price_body = {"t": "price", "n": 1754, "for": 1755,
                           "limits": ["219.00", "242.04"], "ref": {"px": "230.52"}}

    def snapshot(self, body=None, stamp="2026-10-01T14:09:00Z"):
        text = json.dumps(self.price_body if body is None else body,
                          sort_keys=True, separators=(",", ":"))
        nonce = 1790863800000
        signature = self.private.sign(f"d-close1-price|{nonce}|{text}".encode())
        message = {"seq": 1755, "from": self.did, "nonce": nonce, "text": text,
                   "sig": base64.urlsafe_b64encode(signature).decode().rstrip("="),
                   "ts": stamp}
        return {"room": "d-close1-price", "last_seq": 1755,
                "messages": [message]}

    def read(self, snapshot):
        with patch.object(offer, "REFEREE_DID", self.did):
            return offer.read_price(snapshot, now=self.now)

    def test_signed_price_and_bounded_offer(self):
        price = self.read(self.snapshot())
        self.assertEqual(price["sweep"], 1755)
        terms, reserve = offer.validate_offer(
            "test-1", "sell", "40", "230.50", 1756, "9700", self.did, price)
        self.assertEqual(reserve, offer.Decimal("9681.04"))
        body = json.loads(offer.signed_offer(terms, self.private))
        self.assertEqual(body["t"], "offer")
        self.assertEqual(body["season"], "close-1")
        self.assertEqual(body["terms"], terms)
        signature = base64.urlsafe_b64decode(body["maker_sig"] + "==")
        self.private.public_key().verify(
            signature, f"close-1|terms|{offer.canonical_terms(terms)}".encode())

    def test_rejects_unverified_or_stale_price(self):
        with self.assertRaisesRegex(ValueError, "referee DID"):
            offer.read_price(self.snapshot(), now=self.now)
        snapshot = self.snapshot()
        snapshot["messages"][0]["text"] += " "
        with self.assertRaisesRegex(ValueError, "signature"):
            self.read(snapshot)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.read(self.snapshot(stamp="2026-10-01T13:58:00Z"))
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.read(self.snapshot(stamp="2026-10-01T14:09:00"))

    def test_rejects_malformed_limits(self):
        body = {**self.price_body, "limits": ["NaN", "242.04"]}
        with self.assertRaisesRegex(ValueError, "invalid"):
            self.read(self.snapshot(body=body))
        body = {**self.price_body, "limits": ["oops", "242.04"]}
        with self.assertRaisesRegex(ValueError, "malformed"):
            self.read(self.snapshot(body=body))

    def test_rejects_expired_or_unfunded_offer(self):
        price = self.read(self.snapshot())
        for until in (1754, 1758, 2557):
            with self.assertRaisesRegex(ValueError, "expiry"):
                offer.validate_offer("test-1", "buy", "1", "230.50", until,
                                     "9700", self.did, price)
        with self.assertRaisesRegex(ValueError, "outside signed"):
            offer.validate_offer("test-1", "buy", "1", "242.05", 1755,
                                 "9700", self.did, price)
        with self.assertRaisesRegex(ValueError, "reserve exceeds"):
            offer.validate_offer("test-1", "buy", "40", "230.50", 1755,
                                 "9681.03", self.did, price)
        with self.assertRaisesRegex(ValueError, "malformed"):
            offer.validate_offer("bad space", "buy", "1", "230.50", 1755,
                                 "9700", self.did, price)


if __name__ == "__main__":
    unittest.main()
