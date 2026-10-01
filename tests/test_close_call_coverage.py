"""Offline checks for signed Close Call archive coverage."""

import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_coverage as coverage  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class CloseCallCoverageTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + public)
        self.digest = "a" * 64
        record = {"input": {"n": 2, "trades": []},
                  "output": {"sweep": 2, "trades": []}}
        self.raw = json.dumps(record).encode()
        entry = {"n": 2, "file": self.digest, "status": "redacted",
                 "path": f"redacted/{self.digest}.json", "bytes": len(self.raw),
                 "sha256": hashlib.sha256(self.raw).hexdigest()}
        self.index = {"contest": "close-1", "sweeps": [{"n": 1}, entry]}
        self.tip_flow = self.signed_flow(2)
        self.latest = self.signed_flow(4)
        self.export = (json.dumps(self.tip_flow) + "\n" + json.dumps(self.latest)).encode()
        self.tail = {"room": "d-close1-flow", "last_seq": 4,
                     "messages": [self.latest]}

    def signed_flow(self, sweep, digest=None):
        text = json.dumps({"t": "flow", "n": sweep, "file": digest or self.digest},
                          separators=(",", ":"))
        nonce = 1790000000000 + sweep
        sig = self.private.sign(f"d-close1-flow|{nonce}|{text}".encode())
        return {"seq": sweep, "from": self.did, "nonce": nonce, "text": text,
                "sig": base64.urlsafe_b64encode(sig).decode().rstrip("="),
                "ts": "2026-10-01T13:00:00Z"}

    def assess(self):
        return coverage.assess_coverage(self.index, self.raw, self.export,
                                        self.tail, self.did)

    def test_lagging_coverage_is_not_a_balance_claim(self):
        result = self.assess()
        self.assertEqual(result["status"], "lagging")
        self.assertEqual(result["unarchived_sweep_count"], 2)
        self.assertTrue(result["archive_tip_record_checksum_verified"])
        self.assertIn("unsigned_archive_index_only", result["archive_tip_provenance"])
        self.assertIn("not an account statement", result["caution"])

    def test_caught_up(self):
        self.tail = {"room": "d-close1-flow", "last_seq": 2,
                     "messages": [self.tip_flow]}
        result = self.assess()
        self.assertEqual(result["status"], "caught_up")
        self.assertEqual(result["unarchived_sweep_count"], 0)

    def test_rejects_malformed_archive_and_record(self):
        self.index["sweeps"][0]["n"] = 2
        with self.assertRaisesRegex(ValueError, "missing, duplicate"):
            self.assess()
        self.index["sweeps"][0]["n"] = 1
        self.index["sweeps"][0]["n"] = True
        with self.assertRaisesRegex(ValueError, "missing, duplicate"):
            self.assess()
        self.index["sweeps"][0]["n"] = 1
        self.raw += b" "
        with self.assertRaisesRegex(ValueError, "do not match index"):
            self.assess()

    def test_rejects_wrong_or_tampered_flow(self):
        self.export = json.dumps(self.signed_flow(2, "b" * 64)).encode()
        with self.assertRaisesRegex(ValueError, "file hash mismatch"):
            self.assess()
        self.export = json.dumps(self.tip_flow).encode()
        self.tail["messages"][0] = {**self.latest, "nonce": self.latest["nonce"] + 1}
        with self.assertRaisesRegex(ValueError, "signature or referee DID mismatch"):
            self.assess()

    def test_rejects_archive_ahead_of_signed_flow(self):
        older = self.signed_flow(1)
        self.tail = {"room": "d-close1-flow", "last_seq": 1, "messages": [older]}
        with self.assertRaisesRegex(ValueError, "ahead of latest"):
            self.assess()


if __name__ == "__main__":
    unittest.main()
