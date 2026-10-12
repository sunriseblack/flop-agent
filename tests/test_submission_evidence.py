"""Offline positive and adversarial checks for submission evidence packets."""

import base64
import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from submission_evidence import SCHEMA, assess_packet, collect_packet, inspect_artifact, main  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def did_from_private(private):
    raw = b"\xed\x01" + private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    value, encoded = int.from_bytes(raw, "big"), ""
    while value:
        value, digit = divmod(value, 58)
        encoded = ALPHABET[digit] + encoded
    return "did:key:z" + encoded


class SubmissionEvidenceTests(unittest.TestCase):
    def setUp(self):
        # Test-only ephemeral identity; never posted and no private fixture stored.
        self.private = Ed25519PrivateKey.generate()
        self.did = did_from_private(self.private)
        self.record = self.sign("RESULT v1 | k0123456789 | Verified artifact and tests.")
        self.packet = {"schema": SCHEMA, "room": "kibble", "submission": self.record,
                       "native_readback": {"room": "kibble", "generation": 0,
                                           "last_seq": 100, "messages": [self.record]},
                       "host_board": {"jobs": [{"id": "k0123456789", "status": "delivered"}],
                                      "engine_seq": 99},
                       "host_score": {"ok": True, "did": self.did, "found": True,
                                      "score": 7, "engine_warm": True, "engine_seq": 99}}

    def sign(self, text, nonce=1000000000000000015):
        sig = self.private.sign(f"kibble|{nonce}|{text}".encode())
        return {"seq": 100, "from": self.did, "text": text, "nonce": nonce,
                "sig": base64.urlsafe_b64encode(sig).decode().rstrip("=")}

    def assess(self, packet=None):
        return assess_packet(self.packet if packet is None else packet, self.did)

    def test_valid_receipt_board_and_score_do_not_assert_credit(self):
        result = self.assess()
        self.assertTrue(result["evidence_verified"])
        self.assertEqual(result["native_readback"]["state"], "exact_fields_match_in_supplied_snapshot")
        self.assertEqual(result["host_board"]["state"], "matching_row_observed")
        self.assertEqual(result["host_score"]["state"], "account_snapshot_observed")
        self.assertEqual(result["credit_for_submission"], "not_determined")
        self.assertEqual(result["submission"]["job_id"], "k0123456789")

    def test_changed_text_nonce_room_signature_fail(self):
        for key, value in (("text", self.record["text"] + "!"), ("nonce", 1),
                           ("sig", "A" * 86), ("from", "did:key:z123")):
            packet = copy.deepcopy(self.packet)
            packet["submission"][key] = value
            self.assertFalse(self.assess(packet)["evidence_verified"], key)
        packet = {**self.packet, "room": "lobby"}
        self.assertFalse(self.assess(packet)["evidence_verified"])

    def test_wrong_expected_owner_cannot_attach_host_views(self):
        result = assess_packet(self.packet, "did:key:z123")
        self.assertFalse(result["evidence_verified"])
        self.assertNotIn("host_score", result)
        self.assertNotIn("native_readback", result)

    def test_missing_signature_is_unverifiable(self):
        packet = copy.deepcopy(self.packet)
        del packet["submission"]["sig"]
        self.assertEqual(self.assess(packet)["submission"]["signature_status"], "unverifiable")

    def test_sequence_and_timestamp_are_not_signed(self):
        packet = copy.deepcopy(self.packet)
        packet["submission"] = {**packet["submission"], "seq": 777, "ts": "fictional"}
        result = self.assess(packet)
        self.assertTrue(result["evidence_verified"])
        self.assertEqual(result["native_readback"]["state"], "signed_content_at_different_or_missing_sequence")
        self.assertEqual(result["submission"]["signed_payload_sha256"], self.assess()["submission"]["signed_payload_sha256"])

    def test_decimal_string_nonce_has_same_exact_signed_bytes(self):
        packet = copy.deepcopy(self.packet)
        packet["submission"]["nonce"] = str(self.record["nonce"])
        self.assertEqual(self.assess(packet)["native_readback"]["state"], "exact_fields_match_in_supplied_snapshot")

    def test_duplicate_signed_content_is_ambiguous(self):
        packet = copy.deepcopy(self.packet)
        packet["native_readback"]["messages"].append({**self.record, "seq": 101})
        self.assertEqual(self.assess(packet)["native_readback"]["state"], "ambiguous_duplicate_signed_content")

    def test_conflicting_content_at_same_sequence_is_not_readback(self):
        packet = copy.deepcopy(self.packet)
        packet["native_readback"]["messages"] = [self.sign("A different signed message.")]
        self.assertEqual(self.assess(packet)["native_readback"]["state"], "sequence_content_conflict")

    def test_absence_and_wrong_room_do_not_mean_rejection(self):
        packet = copy.deepcopy(self.packet)
        packet["native_readback"]["messages"] = []
        self.assertEqual(self.assess(packet)["native_readback"]["state"], "not_observed_in_supplied_window")
        packet["native_readback"]["room"] = "lobby"
        self.assertEqual(self.assess(packet)["native_readback"]["state"], "malformed_or_wrong_room")
        self.assertEqual(self.assess(packet)["credit_for_submission"], "not_determined")

    def test_gap_and_partial_snapshot_are_visible(self):
        packet = copy.deepcopy(self.packet)
        packet["native_readback"]["messages"].append({**self.record, "seq": 102})
        packet["native_readback"]["last_seq"] = 200
        result = self.assess(packet)["native_readback"]
        self.assertFalse(result["stored_sequence_contiguous"])
        self.assertFalse(result["window_reaches_reported_head"])

    def test_duplicate_board_ids_are_ambiguous(self):
        packet = copy.deepcopy(self.packet)
        packet["host_board"]["jobs"] *= 2
        self.assertEqual(self.assess(packet)["host_board"]["state"], "ambiguous_duplicate_rows")

    def test_missing_board_row_and_zero_score_do_not_prove_rejection(self):
        packet = copy.deepcopy(self.packet)
        packet["host_board"]["jobs"] = []
        packet["host_score"].update(found=False, score=0, engine_warm=False)
        result = self.assess(packet)
        self.assertEqual(result["host_board"]["state"], "not_observed_in_supplied_board")
        self.assertEqual(result["credit_for_submission"], "not_determined")

    def test_host_cursors_never_infer_native_ingestion(self):
        for seq in (1, 100000000):
            packet = copy.deepcopy(self.packet)
            packet["host_board"]["engine_seq"] = seq
            packet["host_score"]["engine_seq"] = seq
            self.assertEqual(self.assess(packet)["host_board"]["coverage"], "not_established_across_native_and_host_ledgers")

    def test_score_wrong_or_missing_identity_is_not_attached(self):
        for did in (None, "did:key:z123"):
            packet = copy.deepcopy(self.packet)
            packet["host_score"]["did"] = did
            self.assertEqual(self.assess(packet)["host_score"]["state"], "wrong_or_missing_did")

    def test_unavailable_host_and_non_job_submission(self):
        packet = copy.deepcopy(self.packet)
        packet["host_board"] = {"ok": False}
        packet["host_score"] = {"ok": False}
        result = self.assess(packet)
        self.assertEqual(result["host_board"]["state"], "unavailable_or_malformed")
        self.assertEqual(result["host_score"]["state"], "unavailable_or_malformed")
        packet["submission"] = self.sign("A useful public protocol answer.")
        packet["host_board"] = {"jobs": []}
        self.assertEqual(self.assess(packet)["host_board"]["state"], "no_job_id_in_submission")

    def test_collection_failure_is_distinct_from_no_snapshot(self):
        packet = copy.deepcopy(self.packet)
        packet["host_board"] = None
        packet["collection"] = {"host_board": {"error": "TimeoutError: timed out"}}
        self.assertEqual(self.assess(packet)["host_board"]["state"], "collection_failed")
        self.assertEqual(self.assess(packet)["host_board"]["error"], "TimeoutError: timed out")

    def test_invalid_packet_schema_and_room_raise(self):
        for packet in ([], {}, {**self.packet, "room": "../secrets"}):
            with self.assertRaises(ValueError):
                assess_packet(packet)

    def test_public_fixture_verifies_and_has_no_credit_claim(self):
        fixture = Path(__file__).resolve().parents[1] / "examples/submission-evidence-flop-327293.json"
        result = assess_packet(json.loads(fixture.read_text()))
        self.assertTrue(result["evidence_verified"])
        self.assertEqual(result["submission"]["signed_payload_sha256"], "bd994047a99ca37fc157c8a967dc72dd3f0ea6bc246a51cb04048fa649e3b9ff")
        self.assertEqual(result["credit_for_submission"], "not_determined")

    def test_nonfinite_timeout_is_rejected_before_network(self):
        for value in ("nan", "inf"):
            with mock.patch("submission_evidence.collect_packet") as collect, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main(["--seq", "100", "--timeout", value])
                collect.assert_not_called()

    def test_artifact_hash_only_binds_when_mentioned(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "artifact.txt"
            path.write_bytes(b"public example")
            digest = hashlib.sha256(b"public example").hexdigest()
            result = inspect_artifact(path, self.record, digest)
            self.assertTrue(result["expected_hash_matches"])
            self.assertFalse(result["hash_mentioned_in_signed_text"])
            self.assertTrue(inspect_artifact(path, self.sign("RESULT v1 | k0123456789 | sha256:" + digest))["hash_mentioned_in_signed_text"])
            self.assertFalse(inspect_artifact(path, self.sign("hex:" + digest + "a"))["hash_mentioned_in_signed_text"])
            self.assertFalse(inspect_artifact(path, self.record, "0" * 64)["expected_hash_matches"])
            with self.assertRaises(ValueError):
                inspect_artifact(path, self.record, "not a hash")

    def test_collect_retained_record_is_read_only(self):
        with mock.patch("submission_evidence.get_json", side_effect=[self.packet["native_readback"],
                                                                    self.packet["host_board"], self.packet["host_score"]]):
            packet = collect_packet("kibble", 100, 1)
        self.assertTrue(assess_packet(packet)["evidence_verified"])

    def test_collect_native_export_fallback(self):
        snapshot = {"room": "flop", "messages": [], "generation": 0, "last_seq": 200}
        text = "Public answer."
        sig = self.private.sign(f"flop|1|{text}".encode())
        record = {"seq": 100, "from": self.did, "nonce": 1, "text": text,
                  "sig": base64.urlsafe_b64encode(sig).decode().rstrip("=")}
        with mock.patch("submission_evidence.get_json", return_value=snapshot), mock.patch(
                "submission_evidence.get_export", return_value=([record], "0")):
            packet = collect_packet("flop", 100, 1)
        self.assertTrue(packet["collection"]["export_fallback_used"])
        self.assertTrue(assess_packet(packet)["evidence_verified"])
        self.assertFalse(assess_packet(packet)["native_readback"]["window_reaches_reported_head"])

    def test_collect_generation_change_or_expired_record_fails(self):
        snapshot = {"room": "kibble", "messages": [], "generation": 0}
        for generation in ("1", "0", None):
            with mock.patch("submission_evidence.get_json", return_value=snapshot), mock.patch(
                    "submission_evidence.get_export", return_value=([], generation)):
                with self.assertRaises(ValueError):
                    collect_packet("kibble", 100, 1)

    def test_existing_output_is_never_overwritten_or_refetched(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.json"
            path.write_text("preserved")
            with mock.patch("submission_evidence.collect_packet") as collect, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--seq", "100", "--output", str(path)]), 2)
                collect.assert_not_called()
            self.assertEqual(path.read_text(), "preserved")

    def test_save_and_offline_verification_do_not_use_network(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.json"
            with mock.patch("submission_evidence.collect_packet", return_value=self.packet), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--seq", "100", "--output", str(path)]), 0)
            with mock.patch("submission_evidence.get_json") as fetch, contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(["--file", str(path), "--did", self.did]), 0)
                fetch.assert_not_called()
            self.assertEqual(json.loads(out.getvalue())["credit_for_submission"], "not_determined")

    def test_wrong_owner_does_not_save_packet(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.json"
            with mock.patch("submission_evidence.collect_packet", return_value=self.packet), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--seq", "100", "--did", "did:key:z123", "--output", str(path)]), 1)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
