"""Offline safety checks for the retained Kibble JOB/CLAIM audit."""

import base64
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from kibble_tape_audit import assess_records  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class KibbleTapeAuditTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + public)

    def signed(self, seq, text):
        nonce = 1791456463000 + seq
        signature = self.private.sign(f"kibble|{nonce}|{text}".encode())
        return {"seq": seq, "from": self.did, "nonce": nonce, "text": text,
                "sig": base64.urlsafe_b64encode(signature).decode().rstrip("=")}

    def test_signed_claim_blocks_job_and_numeric_id_is_supported(self):
        records = [self.signed(10, "JOB v1 | 1791456463692 | explain | Title | Criteria"),
                   self.signed(11, "CLAIM v1 | 1791456463692 | worker")]
        result = assess_records(records, head=10, generation=0, export_generation=0)
        self.assertTrue(result["coverage_verified"])
        self.assertTrue(result["live_head_covered"])
        self.assertEqual(result["jobs"], 1)
        self.assertEqual(result["signed_claims"], 1)
        self.assertEqual(result["tape_unclaimed_candidates"], [])

    def test_unclaimed_is_only_a_tape_candidate(self):
        result = assess_records([self.signed(10, "JOB v1 | k0123456789 | review | Test | Criteria")],
                                head=10, generation=0, export_generation=0)
        self.assertTrue(result["coverage_verified"])
        self.assertEqual(result["tape_unclaimed_candidates"][0]["id"], "k0123456789")
        self.assertIn("not official open jobs", result["caution"])
        self.assertIsNone(assess_records([self.signed(10, "JOB v1 | k0123456789 | review | Test | Criteria")])["live_head_covered"])

    def test_duplicate_id_is_ambiguous_not_a_candidate(self):
        records = [self.signed(10, "JOB v1 | k0123456789 | build | A | C"),
                   self.signed(11, "JOB v1 | k0123456789 | build | B | C")]
        result = assess_records(records, head=10, generation=0, export_generation=0)
        self.assertTrue(result["coverage_verified"])
        self.assertEqual(result["ambiguous_duplicate_job_ids"], ["k0123456789"])
        self.assertEqual(result["tape_unclaimed_candidates"], [])

    def test_gap_invalid_signature_and_head_lag_fail_closed(self):
        records = [self.signed(10, "JOB v1 | k0123456789 | build | A | C"),
                   self.signed(12, "CLAIM v1 | k0123456789 | worker")]
        records[1]["text"] += " tampered"
        result = assess_records(records, head=13, generation=0, export_generation=0)
        self.assertFalse(result["coverage_verified"])
        self.assertEqual(result["tape_unclaimed_candidates"], [])
        self.assertEqual(len(result["nonverified_sample"]), 1)
        self.assertTrue(any("sequence gap" in problem for problem in result["problems"]))
        self.assertTrue(any("does not cover" in problem for problem in result["problems"]))

    def test_generation_change_and_malformed_prefix_fail_closed(self):
        records = [self.signed(10, "JOB v1 | malformed")]
        result = assess_records(records, head=10, generation=0, export_generation=1)
        self.assertFalse(result["coverage_verified"])
        self.assertEqual(result["malformed_prefix_seq_sample"], [10])
        self.assertEqual(result["tape_unclaimed_candidates"], [])


if __name__ == "__main__":
    unittest.main()
