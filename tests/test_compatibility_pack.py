"""Actual CLI parity plus explicit missing-transport and metadata limits."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import compatibility_pack as pack
import inference_readiness as private
import test_submission_evidence as fixtures


def fake_node(raw):
    cases = json.loads(raw)["cases"]
    return {"node": "test-seam-not-real-execution", "input_sha256": hashlib.sha256(raw).hexdigest(),
            "results": [{"id": c["id"], "status": pack.verify_record(c["room"], c["record"])[0],
                         "ordinary_parse_unsafe_nonce": False, "ordinary_parse_status": None} for c in cases]}


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        helper = fixtures.SubmissionEvidenceTests()
        helper.setUp()
        self.packet = copy.deepcopy(helper.packet)
        self.record = helper.sign("Already signed synthetic control: café e\u0301 🐕", nonce=1000000000000000001)
        self.packet["submission"] = self.record
        self.packet["native_readback"]["messages"] = [self.record]
        self.snapshot = self.packet["native_readback"]

    def test_json_export_and_mcp_json_use_exact_fields(self):
        raw = json.dumps(self.snapshot, ensure_ascii=False).encode()
        export = json.dumps(self.record).encode() + b"\n"
        mcp = json.dumps({"content": [{"type": "text", "text": raw.decode()}]}).encode()
        result = pack.check(self.packet, {"json": raw, "export": export, "mcp": mcp}, fake_node)
        self.assertTrue(result["python_node_classifications_match"])
        self.assertEqual(result["unicode_signed_records"], 1)
        self.assertFalse(result["untested_transports"])
        for row in result["transports"]:
            self.assertTrue(row["target_signed_content_present"])
        self.assertEqual(result["credit_for_submission"], "not_determined")

    def test_missing_history_plain_mcp_and_generations_stay_distinct(self):
        snap = {**self.snapshot, "generation": 999, "messages": []}
        mcp = json.dumps({"content": [{"type": "text", "text": "# room kibble\n[100] display only\nnext: /r/kibble?since=100"}]}).encode()
        report = pack.check(self.packet, {"json": json.dumps(snap).encode(), "mcp": mcp}, fake_node)
        self.assertEqual(report["transports"][0]["readback"]["state"], "not_observed_in_supplied_window")
        self.assertEqual(report["transports"][1]["parse_state"], "text_projection_not_reverifiable")
        self.assertEqual(report["unverifiable_transports"], ["mcp"])
        self.assertEqual(report["live_mcp_protocol"], "not_established")
        self.assertEqual(report["untested_transports"], ["export"])
        self.assertFalse(report["derived_metadata_controls"]["derived_internal_gap_contiguous"])
        self.assertEqual(report["derived_metadata_controls"]["generation_authenticity"], "not_established_by_message_signature")

    def test_duplicate_nonfinite_mcp_errors_and_ambiguous_blocks_rejected(self):
        cases = [(b'{"room":"kibble","room":"other","messages":[]}', "json"),
                 (b'{"room":"kibble","messages":[],"n":NaN}', "json"),
                 (b'{"room":"other","messages":[]}', "json"),
                 (b'{"isError":true,"content":[]}', "mcp"),
                 (json.dumps({"content": [{"type": "text", "text": '{"room":"kibble","room":"other","messages":[]}'}]}).encode(), "mcp"),
                 (b'{"content":[{"type":"text","text":"{}"},{"type":"text","text":"{}"}]}', "mcp")]
        for raw, kind in cases:
            with self.assertRaises(ValueError):
                pack.parse_transport(raw, kind, "kibble")

    def test_invalid_packet_parity_hash_and_unsafe_acceptance_fail(self):
        wrong = copy.deepcopy(self.packet)
        wrong["submission"]["text"] += " changed"
        with self.assertRaises(ValueError):
            pack.check(wrong, {}, fake_node)
        def mismatch(raw):
            value = fake_node(raw)
            value["results"][0]["status"] = "invalid"
            return value
        def wrong_hash(raw):
            return {**fake_node(raw), "input_sha256": "0" * 64}
        def unsafe(raw):
            value = fake_node(raw)
            value["results"][0].update(ordinary_parse_unsafe_nonce=True, ordinary_parse_status="verified")
            return value
        for runner in (mismatch, wrong_hash, unsafe):
            with self.assertRaises(ValueError):
                pack.check(self.packet, {}, runner)

    def test_widest_nonce_control_remains_inside_signed_nonce_grammar(self):
        helper = fixtures.SubmissionEvidenceTests()
        helper.setUp()
        widest = helper.sign("widest nonce", nonce=9999999999999999999)
        cases = pack.cases_for("kibble", [widest])
        altered = next(c for c in cases if c["id"].endswith("/nonce-tamper"))
        self.assertEqual(altered["record"]["nonce"], "9999999999999999998")
        self.assertEqual(pack.verify_record("kibble", altered["record"])[0], "invalid")

    @unittest.skipUnless(shutil.which("node"), "Node required for cross-client execution")
    def test_actual_node_preserves_unicode_and_rejects_rounded_numbers(self):
        report = pack.check(self.packet, {})
        self.assertTrue(report["python_node_classifications_match"])
        self.assertGreater(report["ordinary_parse_unsafe_nonce_cases"], 0)
        self.assertEqual(report["unicode_signed_records"], 1)
        self.assertEqual(report["derived_cases"], 6)

    def test_real_cli_output_exclusive_and_private(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(private, "ROOT", Path(directory)):
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(self.packet))
            output = Path(directory) / ".private/readiness/report.json"
            with mock.patch.object(pack, "check", return_value={"supplied_signed_records_checked": 1,
                                   "python_node_classifications_match": True, "untested_transports": ["mcp"]}):
                self.assertEqual(pack.main(["--packet", str(path), "--output", str(output)]), 0)
                before = output.read_bytes()
                self.assertEqual(pack.main(["--packet", str(path), "--output", str(output)]), 2)
                self.assertEqual(output.read_bytes(), before)
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
