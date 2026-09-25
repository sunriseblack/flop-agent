"""Offline signature and snapshot checks for Technocore tape verification."""

import base64
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_tape import ALPHABET, assess_snapshot, verify_record  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class TapeVerificationTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        raw_public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + raw_public)
        self.room = "kibble"
        self.text = "RESULT v1 | k0123456789 | Provenance caf\u00e9"
        self.nonce = 1790341500000
        signed = self.private.sign(f"{self.room}|{self.nonce}|{self.text}".encode())
        self.record = {"seq": 123, "from": self.did, "nonce": self.nonce,
                       "text": self.text, "sig": base64.urlsafe_b64encode(signed).decode().rstrip("=")}

    def test_valid_record_and_snapshot(self):
        self.assertEqual(verify_record(self.room, self.record)[0], "verified")
        result = assess_snapshot(self.room, {"room": self.room, "messages": [self.record]})
        self.assertEqual(result["counts"], {"verified": 1, "unverifiable": 0, "invalid": 0})

    def test_tampered_text_or_room_is_invalid(self):
        self.assertEqual(verify_record("lobby", self.record)[0], "invalid")
        self.assertEqual(verify_record(self.room, {**self.record, "text": self.text + "!"})[0], "invalid")

    def test_absent_signature_is_unverifiable_not_invalid(self):
        self.assertEqual(verify_record(self.room, {"from": self.did, "text": self.text})[0], "unverifiable")

    def test_noncanonical_signature_and_bad_did_are_invalid(self):
        self.assertEqual(verify_record(self.room, {**self.record, "sig": self.record["sig"][:-1] + "B"})[0], "invalid")
        self.assertEqual(verify_record(self.room, {**self.record, "from": "did:key:z123"})[0], "invalid")

    def test_bool_nonce_and_wrong_snapshot_room_are_rejected(self):
        self.assertEqual(verify_record(self.room, {**self.record, "nonce": True})[0], "invalid")
        with self.assertRaises(ValueError):
            assess_snapshot(self.room, {"room": "lobby", "messages": [self.record]})


if __name__ == "__main__":
    unittest.main()
