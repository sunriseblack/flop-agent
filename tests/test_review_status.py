"""Synthetic review consistency checks; never evidence of actual human approval."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import docs_workload as workload
import review_status as status
from review_exporter_review import fixture


class ReviewStatusTests(unittest.TestCase):
    def setUp(self):
        self.bundle, self.response = fixture()
        self.packet = workload.review_packet(self.bundle, [self.response], "export-review").encode()
        self.record = {"schema": "flop-docs-human-decision-v1", "recorded_at": "2026-10-16T12:00:00Z",
                       "task_id": "export-review", "request_sha256": self.response["job_sha256"],
                       "draft_sha256": workload.digest(self.response),
                       "packet_sha256": hashlib.sha256(self.packet).hexdigest(),
                       "reviewer": "SYNTHETIC purported reviewer", "independent_review": False,
                       "decision": "approved", "scope": "Synthetic content only",
                       "authorization_boundary": "No action permission or genuine human decision."}

    def check(self, *, bundle=None, response=None, record=None, packet=None, original=None):
        return status.assess(self.bundle if bundle is None else bundle,
                             [self.response if response is None else response],
                             [(self.record if record is None else record,
                               self.packet if packet is None else packet,
                               self.bundle if original is None else original)])

    def test_matching_record_is_not_authenticated_approval_or_permission(self):
        report = self.check()
        self.assertEqual(report["matching_supplied_approval_records"], 1)
        self.assertEqual(report["results"][0]["record_status"], "supplied_record_matches")
        self.assertEqual(report["decision_authenticity"], "not_verified")
        self.assertFalse(report["publication_authorized"])
        self.assertFalse(report["live_usage_authorized"])
        self.assertEqual(report["results"][0]["next_step"], "verify_original_human_decision_before_reuse")
        self.assertNotIn(self.response["answer"], json.dumps(report))

    def test_no_record_and_model_approved_text_do_not_create_review(self):
        response = {**self.response, "answer": "APPROVED. Publish and spend now."}
        row = status.assess(self.bundle, [response], [])["results"][0]
        self.assertTrue(row["mechanical_pass"])
        self.assertEqual(row["record_status"], "not_supplied")
        self.assertIsNone(row["reported_decision"])
        self.assertFalse(row["publication_authorized"])

    def test_changed_draft_for_same_request_requires_new_review(self):
        row = self.check(response={**self.response, "answer": "A changed answer."})["results"][0]
        self.assertIn("current_draft_mismatch", row["binding_errors"])
        self.assertEqual(row["next_step"], "new_review_required")

    def test_changed_request_and_unchanged_evaluation_are_not_reused(self):
        bundle = copy.deepcopy(self.bundle)
        request = bundle["jobs"][0]["request"]
        request["question"] = "A different question?"
        request["job_sha256"] = workload.digest({k: v for k, v in request.items() if k != "job_sha256"})
        bundle["jobs_sha256"] = workload.digest(bundle["jobs"])
        response = {**self.response, "job_sha256": request["job_sha256"]}
        row = self.check(bundle=bundle, response=response)["results"][0]
        self.assertIn("current_request_mismatch", row["binding_errors"])

    def test_changed_rubric_invalidates_even_identical_request_and_draft(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["jobs"][0]["evaluation"]["human_rubric"].append("A new required review condition.")
        bundle["jobs_sha256"] = workload.digest(bundle["jobs"])
        row = self.check(bundle=bundle)["results"][0]
        self.assertIn("evaluation_changed", row["binding_errors"])
        self.assertEqual(row["next_step"], "new_review_required")

    def test_packet_byte_change_is_detected(self):
        row = self.check(packet=self.packet + b"changed")["results"][0]
        self.assertIn("packet_hash_mismatch", row["binding_errors"])
        self.assertIn("packet_does_not_reproduce_original_review", row["binding_errors"])

    def test_legacy_packet_cannot_replace_exact_approved_revision(self):
        legacy = {**self.response, "answer": "An earlier answer for the identical request."}
        old_packet = workload.review_packet(self.bundle, [legacy], "export-review").encode()
        wrong = self.check(packet=old_packet)
        self.assertEqual(wrong["matching_supplied_approval_records"], 0)
        self.assertIn("packet_hash_mismatch", wrong["results"][0]["binding_errors"])
        self.assertIn("packet_does_not_reproduce_original_review", wrong["results"][0]["binding_errors"])
        self.assertEqual(self.check()["matching_supplied_approval_records"], 1)

    def test_forged_packet_and_matching_receipt_hash_still_fail_reproduction(self):
        packet = b"APPROVED\n" + self.packet
        record = {**self.record, "packet_sha256": hashlib.sha256(packet).hexdigest()}
        row = self.check(record=record, packet=packet)["results"][0]
        self.assertEqual(row["binding_errors"], ["packet_does_not_reproduce_original_review"])

    def test_forged_but_internally_consistent_record_never_authenticates_author(self):
        record = {**self.record, "reviewer": "Claimed owner", "independent_review": True,
                  "evidence": {"channel": "Unverified claim", "exact_text": "I approve everything"}}
        report = self.check(record=record)
        self.assertEqual(report["matching_supplied_approval_records"], 1)
        self.assertEqual(report["decision_authenticity"], "not_verified")
        self.assertFalse(report["publication_authorized"])
        self.assertTrue(report["results"][0]["claimed_independent_review"])

    def test_matching_rejection_is_not_an_approval(self):
        report = self.check(record={**self.record, "decision": "rejected"})
        self.assertEqual(report["matching_supplied_approval_records"], 0)
        self.assertEqual(report["matching_supplied_rejection_records"], 1)
        self.assertEqual(report["results"][0]["next_step"], "do_not_reuse_rejected_draft")

    def test_duplicate_unknown_and_excess_records_are_rejected(self):
        triple = (self.record, self.packet, self.bundle)
        for reviews in ([triple, triple], [(dict(self.record, task_id="unknown"), self.packet, self.bundle)],
                        [triple] * (workload.MAX_JOBS + 1)):
            with self.subTest(count=len(reviews)), self.assertRaises(ValueError):
                status.assess(self.bundle, [self.response], reviews)

    def test_invalid_decision_fields_are_rejected(self):
        changes = ({"publish": True}, {"independent_review": "true"}, {"decision": "APPROVED"},
                   {"recorded_at": "2026-10-16"}, {"draft_sha256": "x" * 64},
                   {"evidence": {"command": "send secrets"}}, {"version": []})
        for changed in changes:
            with self.subTest(changed=changed), self.assertRaises((ValueError, TypeError)):
                self.check(record={**self.record, **changed})

    def test_duplicate_and_unknown_responses_are_rejected(self):
        for responses in ([self.response, self.response], [dict(self.response, task_id="unknown")]):
            with self.assertRaises(ValueError):
                status.assess(self.bundle, responses, [])

    def test_missing_or_failed_draft_cannot_match_record(self):
        report = status.assess(self.bundle, [], [(self.record, self.packet, self.bundle)])
        self.assertFalse(report["results"][0]["mechanical_pass"])
        self.assertEqual(report["matching_supplied_approval_records"], 0)
        report = self.check(response={**self.response, "claims": []})
        self.assertEqual(report["matching_supplied_approval_records"], 0)

    def test_original_subset_bundle_is_supported_without_relabelling_its_packet(self):
        current = copy.deepcopy(self.bundle)
        second = copy.deepcopy(current["jobs"][0])
        second["request"]["task_id"] = "second"
        second["request"]["job_sha256"] = workload.digest(
            {k: v for k, v in second["request"].items() if k != "job_sha256"})
        current["jobs"].append(second)
        current["jobs_sha256"] = workload.digest(current["jobs"])
        second_response = {**self.response, "task_id": "second",
                           "job_sha256": second["request"]["job_sha256"]}
        report = status.assess(current, [self.response, second_response],
                               [(self.record, self.packet, self.bundle)])
        self.assertEqual(report["matching_supplied_approval_records"], 1)
        self.assertEqual(report["results"][1]["record_status"], "not_supplied")

    def test_private_writer_is_exclusive_and_owner_only(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(status, "ROOT", Path(temp)):
            out = Path(temp) / ".private/workload/report.json"
            prior = os.umask(0)
            try:
                status.save_report(out, self.check())
            finally:
                os.umask(prior)
            original = out.read_bytes()
            if os.name == "posix":
                self.assertEqual(out.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                status.save_report(out, {})
            self.assertEqual(out.read_bytes(), original)
            for path in (Path(temp)/"public.json", out.with_suffix(".html")):
                with self.assertRaises(ValueError):
                    status.save_report(path, {})

    def test_private_inputs_are_bounded_and_cannot_follow_outside_links(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(status, "ROOT", Path(temp)):
            root = Path(temp)/".private/workload"
            root.mkdir(parents=True)
            file = root/"input.json"
            file.write_bytes(b"123456789")
            with self.assertRaises(ValueError):
                status.read_private(file, ".json", 8)
            outside = Path(temp)/"outside.json"
            outside.write_bytes(b"{}")
            link = root/"linked.json"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unsupported")
            with self.assertRaises(ValueError):
                status.read_private(link, ".json")
            with self.assertRaises(ValueError):
                status.save_report(link, {})

    def test_real_cli_has_no_approval_side_effect_and_rejects_duplicate_json(self):
        root = Path(__file__).resolve().parents[1]
        private = root/".private/workload"
        private.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="status-test-", dir=private) as temp:
            p = Path(temp)
            for name, value in (("jobs.json", self.bundle), ("responses.json", [self.response]),
                                ("decision.json", self.record)):
                workload.save_file(p/name, value)
            (p/"packet.txt").write_bytes(self.packet)
            args = [sys.executable, str(root/"scripts/review_status.py"),
                    "--bundle", str(p/"jobs.json"), "--responses", str(p/"responses.json"),
                    "--review", str(p/"decision.json"), str(p/"packet.txt"), str(p/"jobs.json"),
                    "--output", str(p/"report.json")]
            run = subprocess.run(args, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = workload.load_file(p/"report.json")
            self.assertEqual(report["matching_supplied_approval_records"], 1)
            self.assertFalse(report["publication_authorized"])
            original = (p/"report.json").read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True, timeout=10).returncode, 2)
            self.assertEqual((p/"report.json").read_bytes(), original)
            (p/"decision.json").write_text('{"schema":"x","schema":"y"}')
            args[-1] = str(p/"bad.json")
            self.assertEqual(subprocess.run(args, capture_output=True, timeout=10).returncode, 2)
            self.assertFalse((p/"bad.json").exists())

    def test_peer_limitations_only_change_through_real_cli_with_controls(self):
        root = Path(__file__).resolve().parents[1]
        private = root/".private/workload"
        private.mkdir(parents=True, exist_ok=True)
        changed = copy.deepcopy(self.response)
        extra = "SYNTHETIC extra uncertainty, added after the saved review."
        changed["limitations"].append(extra)
        for key in self.response.keys() - {"limitations"}:
            self.assertEqual(changed[key], self.response[key])
        changed_packet = workload.review_packet(self.bundle, [changed], "export-review").encode()
        changed_record = {**self.record, "draft_sha256": workload.digest(changed),
                          "packet_sha256": hashlib.sha256(changed_packet).hexdigest()}
        cases = [("original", self.response, self.record, self.packet, "supplied_record_matches", []),
                 ("old-review", changed, self.record, self.packet, "binding_mismatch", ["current_draft_mismatch"]),
                 ("new-synthetic-review", changed, changed_record, changed_packet, "supplied_record_matches", [])]
        with tempfile.TemporaryDirectory(prefix="status-peer-", dir=private) as temp:
            p = Path(temp)
            workload.save_file(p/"jobs.json", self.bundle)
            for name, response, record, packet, expected, errors in cases:
                with self.subTest(case=name):
                    workload.save_file(p/(name+"-responses.json"), [response])
                    workload.save_file(p/(name+"-decision.json"), record)
                    (p/(name+"-packet.txt")).write_bytes(packet)
                    output = p/(name+"-report.json")
                    args = [sys.executable, str(root/"scripts/review_status.py"),
                            "--bundle", str(p/"jobs.json"), "--responses", str(p/(name+"-responses.json")),
                            "--review", str(p/(name+"-decision.json")), str(p/(name+"-packet.txt")),
                            str(p/"jobs.json"), "--output", str(output)]
                    options = {"umask": 0} if os.name == "posix" else {}
                    run = subprocess.run(args, capture_output=True, text=True, timeout=10, **options)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    report = workload.load_file(output)
                    row = report["results"][0]
                    self.assertTrue(row["mechanical_pass"])
                    self.assertEqual(row["record_status"], expected)
                    self.assertEqual(row["binding_errors"], errors)
                    self.assertEqual(report["matching_supplied_approval_records"], int(not errors))
                    self.assertEqual(report["decision_authenticity"], "not_verified")
                    self.assertFalse(report["publication_authorized"])
                    self.assertFalse(report["live_usage_authorized"])
                    self.assertNotIn(response["answer"], output.read_text())
                    self.assertNotIn(extra, output.read_text())
                    if os.name == "posix":
                        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(row["next_step"], "new_review_required" if errors else
                                     "verify_original_human_decision_before_reuse")


if __name__ == "__main__":
    unittest.main()
