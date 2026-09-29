"""Offline archive and signed-referee checks for the Close Call auditor."""

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
import audit_close_call as audit  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class CloseCallAuditTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + public)
        self.sweep = 917
        self.full_hash = "a" * 64
        self.record = {
            "input": {"t": "sweep", "n": self.sweep, "owners": [self.did],
                      "trades": [{"id": "trade-1", "maker": self.did, "qty": "1.00"}]},
            "output": {"sweep": self.sweep, "minted": [self.did],
                       "trades": [{"id": "trade-1", "outcome": "settled"}]},
        }
        self.raw = json.dumps(self.record, separators=(",", ":")).encode()
        self.entry = {"n": self.sweep, "file": self.full_hash, "status": "redacted",
                      "path": f"redacted/{self.full_hash}.json", "bytes": len(self.raw),
                      "sha256": hashlib.sha256(self.raw).hexdigest()}
        text = json.dumps({"t": "flow", "n": self.sweep, "file": self.full_hash},
                          separators=(",", ":"))
        nonce = 1790000000000
        sig = self.private.sign(f"d-close1-flow|{nonce}|{text}".encode())
        self.flow = {"seq": self.sweep, "from": self.did, "nonce": nonce, "text": text,
                     "sig": base64.urlsafe_b64encode(sig).decode().rstrip("=")}
        self.export = json.dumps(self.flow).encode() + b"\n"

    def test_index_path_and_record_checksum(self):
        entry = audit.find_entry({"sweeps": [self.entry]}, self.sweep)
        self.assertEqual(audit.verify_archive_record(entry, self.raw), self.record)
        with self.assertRaisesRegex(ValueError, "do not match index"):
            audit.verify_archive_record(entry, self.raw + b" ")
        with self.assertRaisesRegex(ValueError, "unsafe or malformed"):
            audit.find_entry({"sweeps": [{**self.entry, "path": "../secret"}]}, self.sweep)
        with self.assertRaisesRegex(ValueError, "not uniquely indexed"):
            audit.find_entry({"sweeps": [self.entry, self.entry]}, self.sweep)

    def test_full_record_requires_signed_hash(self):
        full = {key: value for key, value in self.entry.items() if key != "sha256"}
        full.update({"status": "full", "path": f"sweeps/{self.full_hash}.json"})
        audit.find_entry({"sweeps": [full]}, self.sweep)
        with self.assertRaisesRegex(ValueError, "do not match index"):
            audit.verify_archive_record(full, self.raw)
        full["file"] = hashlib.sha256(self.raw).hexdigest()
        full["path"] = f"sweeps/{full['file']}.json"
        audit.find_entry({"sweeps": [full]}, self.sweep)
        self.assertEqual(audit.verify_archive_record(full, self.raw), self.record)
        with self.assertRaisesRegex(ValueError, "unsafe or malformed"):
            audit.find_entry({"sweeps": [{**full, "sha256": self.full_hash}]}, self.sweep)

    def test_signed_flow_binds_expected_referee_and_file(self):
        self.assertEqual(audit.verify_flow(self.export, self.sweep, self.full_hash, self.did),
                         self.sweep)
        with self.assertRaisesRegex(ValueError, "signature, referee DID, or file hash mismatch"):
            audit.verify_flow(self.export, self.sweep, "b" * 64, self.did)
        with self.assertRaisesRegex(ValueError, "signature, referee DID, or file hash mismatch"):
            audit.verify_flow(self.export, self.sweep, self.full_hash, audit.REFEREE_DID)
        tampered = {**self.flow, "text": self.flow["text"].replace("flow", "price")}
        with self.assertRaisesRegex(ValueError, "absent or ambiguous"):
            audit.verify_flow(json.dumps(tampered).encode(), self.sweep, self.full_hash, self.did)
        tampered = {**self.flow, "nonce": self.flow["nonce"] + 1}
        with self.assertRaisesRegex(ValueError, "signature, referee DID, or file hash mismatch"):
            audit.verify_flow(json.dumps(tampered).encode(), self.sweep, self.full_hash, self.did)
        with self.assertRaisesRegex(ValueError, "absent or ambiguous"):
            audit.verify_flow(b"", self.sweep, self.full_hash, self.did)

    def test_trade_and_mint_lookup(self):
        trades, owner = audit.inspect_record(self.record, "trade-1", self.did)
        self.assertEqual(trades[0]["outcome"]["outcome"], "settled")
        self.assertEqual(owner, {"in_input": True, "minted_this_sweep": True})
        self.assertEqual(audit.inspect_record(self.record, "other")[0], [])
        broken = json.loads(json.dumps(self.record))
        broken["output"]["trades"][0]["id"] = "wrong"
        with self.assertRaisesRegex(ValueError, "trade ID mismatch"):
            audit.inspect_record(broken, "trade-1")

    def test_end_to_end_read_only_audit(self):
        index = json.dumps({"sweeps": [self.entry]}).encode()
        with patch.object(audit, "REFEREE_DID", self.did), patch.object(
                audit, "fetch_bytes", side_effect=[index, self.raw, self.export]) as fetch:
            result = audit.audit(self.sweep, "trade-1", self.did)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(result["signed_flow_seq"], self.sweep)
        self.assertEqual(result["trade_matches"][0]["outcome"]["outcome"], "settled")
        self.assertEqual(result["owner_result"]["minted_this_sweep"], True)
        self.assertIn("unsigned_archive_index_only", result["provenance"])


if __name__ == "__main__":
    unittest.main()
