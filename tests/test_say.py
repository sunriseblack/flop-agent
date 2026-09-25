"""Offline checks that signed posting requires an exact persisted readback."""

import base64
import sys
import unittest
from pathlib import Path
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from say import post_and_verify  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return output


class SignedPostTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        raw = self.private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + raw)
        self.public_hex = raw.hex()
        self.room, self.text, self.nonce = "meta", "A useful protocol note.", "1790341739766"
        signature = self.private.sign(f"{self.room}|{self.nonce}|{self.text}".encode())
        self.record = {"seq": 100, "from": self.did, "text": self.text, "nonce": int(self.nonce),
                       "sig": base64.urlsafe_b64encode(signature).decode().rstrip("=")}

    def post(self):
        return post_and_verify(self.room, self.text, self.did, self.public_hex, self.private, self.nonce)

    def test_exact_signed_readback(self):
        with mock.patch("say.fetch_json", side_effect=[
                {"posted": self.record}, {"room": self.room, "messages": [self.record]}]) as fetch:
            self.assertEqual(self.post(), {"room": self.room, "seq": 100, "from": self.did, "verified": True})
            self.assertIn("format=json", fetch.call_args_list[0].args[0])
            self.assertIn("since=99", fetch.call_args_list[1].args[0])

    def test_missing_readback_is_not_silently_successful_or_retried(self):
        with mock.patch("say.fetch_json", side_effect=[
                {"posted": self.record}, {"room": self.room, "messages": []}]) as fetch:
            with self.assertRaisesRegex(RuntimeError, "do not retry write"):
                self.post()
            self.assertEqual(fetch.call_count, 2)

    def test_tampered_receipt_is_rejected_before_readback(self):
        with mock.patch("say.fetch_json", return_value={"posted": {**self.record, "text": "Altered"}}) as fetch:
            with self.assertRaisesRegex(RuntimeError, "posted receipt"):
                self.post()
            self.assertEqual(fetch.call_count, 1)

    def test_malformed_readback_is_not_silently_successful(self):
        with mock.patch("say.fetch_json", side_effect=[
                {"posted": self.record}, {"room": self.room, "messages": None}]):
            with self.assertRaisesRegex(RuntimeError, "exact signed readback"):
                self.post()


if __name__ == "__main__":
    unittest.main()
