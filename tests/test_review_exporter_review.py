"""Check the peer runner itself, including false-success and root guards."""

import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import docs_workload  # noqa: E402
import review_exporter_review as runner  # noqa: E402


class ReviewExporterRunnerTests(unittest.TestCase):
    def test_fixture_is_deterministic_and_explicitly_synthetic(self):
        bundle, response = runner.fixture()
        self.assertEqual(runner.fixture(), (bundle, response))
        snippets = bundle["jobs"][0]["request"]["snippets"]
        self.assertEqual(len(snippets), 2)
        self.assertTrue(all(item["text"].startswith("SYNTHETIC") for item in snippets))
        self.assertTrue(docs_workload.grade(bundle, [response])["ready_for_human_review"])

    def test_real_cli_checks_pass_and_preserve_evidence_boundaries(self):
        report = runner.run()
        self.assertTrue(report["all_passed"], report)
        self.assertEqual(len(report["cases"]), 13)
        self.assertEqual(sum(case["exit"] == 0 for case in report["cases"]), 4)
        self.assertEqual(sum(case["exit"] == 2 for case in report["cases"]), 9)
        self.assertIn("No source authenticity", report["scope"])

    def test_success_exit_without_a_packet_cannot_pass(self):
        fake = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with mock.patch.object(runner.subprocess, "run", return_value=fake):
            report = runner.run()
        self.assertFalse(report["all_passed"])
        self.assertFalse(next(row for row in report["cases"] if row["case"] == "valid")["passed"])

    def test_redirected_private_root_is_rejected_before_cli(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            private = pathlib.Path(root) / ".private"
            private.mkdir()
            (private / "workload").symlink_to(outside, target_is_directory=True)
            with mock.patch.object(runner, "ROOT", pathlib.Path(root)), \
                    mock.patch.object(runner.subprocess, "run") as child:
                with self.assertRaisesRegex(ValueError, "redirected"):
                    runner.run()
                child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
