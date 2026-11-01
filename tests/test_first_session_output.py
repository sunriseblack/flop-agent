"""Saved-answer boundaries, not a live client or semantic accuracy evaluation."""

import contextlib
import copy
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import docs_workload as docs
import first_session_output as output
import inference_readiness as readiness
from review_exporter_review import fixture


class FirstSessionOutputTests(unittest.TestCase):
    def setUp(self):
        self.bundle, self.answer = fixture()
        self.job_hash = self.answer["job_sha256"]

    def review(self, answer=None, raw=None):
        raw = json.dumps(self.answer if answer is None else answer).encode() if raw is None else raw
        return output.review(self.bundle, raw, self.job_hash)

    def test_positive_binds_raw_bytes_but_keeps_semantics_and_execution_unknown(self):
        result = self.review()
        self.assertTrue(result["mechanical_pass"])
        self.assertEqual(result["semantic_review"], "required")
        self.assertEqual(result["output_token_limit"], "not_verified")
        self.assertEqual(result["proof_and_settlement"], "not_verified")
        self.assertFalse(result["live_session_authorized"])

    def test_exact_byte_cap_and_one_byte_over_including_utf8(self):
        raw = json.dumps(self.answer, ensure_ascii=False).encode()
        exact = raw + b" " * (8192 - len(raw))
        self.assertTrue(self.review(raw=exact)["mechanical_pass"])
        with self.assertRaises(ValueError):
            self.review(raw=exact + b" ")
        answer = {**self.answer, "answer": "\u00e9" * 4096}
        with self.assertRaises(ValueError):
            self.review(raw=json.dumps(answer, ensure_ascii=False).encode())

    def test_oversized_input_is_rejected_before_json_parser(self):
        with mock.patch.object(output, "strict_json", side_effect=AssertionError("parsed")):
            with self.assertRaises(ValueError):
                self.review(raw=b"{" * 8193)

    def test_duplicate_nonfinite_and_non_utf8_rejected(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff', b'{'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.review(raw=raw)

    def test_independent_job_hash_and_answer_binding(self):
        with self.assertRaises(ValueError):
            output.review(self.bundle, b"{}", "0" * 64)
        result = self.review({**self.answer, "job_sha256": "0" * 64})
        self.assertIn("task_or_version_mismatch", result["errors"])

    def test_fabricated_citation_and_action_fields_fail(self):
        answer = copy.deepcopy(self.answer)
        answer["claims"][0]["evidence"][0]["quote"] = "fabricated quote"
        self.assertIn("citation_not_in_pinned_excerpt", self.review(answer)["errors"])
        self.assertIn("response_schema_mismatch", self.review({**self.answer, "action": "spend"})["errors"])
        self.assertIn("response_schema_mismatch", self.review({"choices": [self.answer]})["errors"])

    def test_false_entitlement_with_real_quote_still_needs_human_rejection(self):
        answer = copy.deepcopy(self.answer)
        answer["answer"] = answer["claims"][0]["text"] = "The owner is guaranteed a token award."
        result = self.review(answer)
        self.assertTrue(result["mechanical_pass"])
        self.assertEqual(result["semantic_review"], "required")
        self.assertEqual(result["airdrop_credit"], "not_determined")

    def test_abstention_requirement_is_preserved(self):
        self.bundle["jobs"][0]["evaluation"]["must_abstain"] = True
        self.bundle["jobs_sha256"] = docs.digest(self.bundle["jobs"])
        self.assertIn("abstention_policy_failed", self.review()["errors"])

    def test_multiple_jobs_cannot_be_reviewed_as_single_session(self):
        other = copy.deepcopy(self.bundle["jobs"][0])
        other["request"]["task_id"] = "another"
        other["request"]["job_sha256"] = docs.digest({k: v for k, v in other["request"].items() if k != "job_sha256"})
        self.bundle["jobs"].append(other)
        self.bundle["jobs_sha256"] = docs.digest(self.bundle["jobs"])
        with self.assertRaises(ValueError):
            self.review()

    def test_cli_exclusive_private_output_and_invalid_answer_exit(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(docs, "ROOT", Path(tmp)), \
                mock.patch.object(readiness, "ROOT", Path(tmp)), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            directory = Path(tmp) / ".private" / "readiness"
            directory.mkdir(parents=True)
            jobs, answer, report = (directory / name for name in ("jobs.json", "answer.json", "report.json"))
            jobs.write_text(json.dumps(self.bundle))
            answer.write_text(json.dumps(self.answer))
            args = ["--jobs", str(jobs), "--answer", str(answer), "--expected-job-sha256", self.job_hash,
                    "--output", str(report)]
            self.assertEqual(output.main(args), 0)
            previous = report.read_bytes()
            self.assertEqual(stat.S_IMODE(report.stat().st_mode), 0o600)
            self.assertEqual(output.main(args), 2)
            self.assertEqual(report.read_bytes(), previous)
            report.unlink()
            answer.write_text(json.dumps({**self.answer, "action": "spend"}))
            self.assertEqual(output.main(args), 1)
            report.unlink()
            answer.write_bytes(b"x" * 8193)
            self.assertEqual(output.main(args), 2)
            self.assertFalse(report.exists())

    def test_public_files_symlinks_and_directory_escapes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(docs, "ROOT", Path(tmp)):
            base = Path(tmp) / ".private"
            base.mkdir()
            public = Path(tmp) / "public.json"
            public.write_text("{}")
            link = base / "link.json"
            link.symlink_to(public)
            linkdir = base / "redirect"
            linkdir.symlink_to(Path(tmp), target_is_directory=True)
            for path in (public, link, linkdir / "public.json", base):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    output.read_private(path, 8192)


if __name__ == "__main__":
    unittest.main()
