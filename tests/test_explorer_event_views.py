from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from explorer_event_views import compare, read_view


TX = "0x" + "ab" * 32
OTHER = "0x" + "bc" * 32


class ExplorerEventViewTests(unittest.TestCase):
    def test_exact_hash_not_row_position_and_field_shape(self):
        rows = {"data": {"transactions": [{"hash": OTHER, "events": [1]}, {"hash": TX, "events": []}]}}
        detail = {"data": {"transaction": {"extrinsicHash": TX, "events": list(range(5))}}}
        report = compare(TX, rows, detail)
        self.assertEqual(report["account_events"], {"state": "empty", "count": 0})
        self.assertEqual(report["detail_events"], {"state": "populated", "count": 5})
        self.assertTrue(report["field_state_or_count_differs"])
        self.assertFalse(report["chain_events_verified"])

    def test_absent_null_empty_and_equal_length_different_events(self):
        detail = {"hash": TX, "events": ["a"]}
        for update, state in (({}, "absent"), ({"events": None}, "null"), ({"events": []}, "empty")):
            report = compare(TX, {"hash": TX, **update}, detail)
            self.assertEqual(report["account_events"]["state"], state)
            self.assertTrue(report["field_state_or_count_differs"])
        report = compare(TX, {"hash": TX, "events": ["b"]}, detail)
        self.assertFalse(report["field_state_or_count_differs"])
        self.assertFalse(report["event_contents_compared"])

    def test_refuse_missing_duplicate_conflicting_or_unrelated_hash(self):
        row = {"hash": TX, "events": []}
        for account, detail in (([], row), ([row, row], row), (row, {"hash": OTHER}),
                                ([{"hash": OTHER}], row), (dict(row, txHash=OTHER), row),
                                ({"error": "Writer unavailable"}, row), (row, {"events": [row]}),
                                (row, {"transaction": {"hash": TX}, "events": [1]}),
                                (dict(row, events="[]"), row), ({"transactions": [row], "data": [row]}, row)):
            with self.subTest(account=account, detail=detail), self.assertRaises(ValueError):
                compare(TX, account, detail)

    def test_refuse_duplicate_json_fields_and_http_error_body_via_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "saved.json"
            path.write_text('{"events":[],"events":null}')
            with self.assertRaises(ValueError):
                read_view(path)
            path.write_text('{"error":"Writer unavailable"}')
            cli = Path(__file__).resolve().parents[1] / "scripts" / "explorer_event_views.py"
            run = subprocess.run([sys.executable, cli, TX, str(path), str(path)], capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, b"")
