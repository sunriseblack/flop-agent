"""Offline regression cases for the read-only Kibble doctor."""

import sys
import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from doctor import DEFAULT_KIBBLE_URL, assess, fetch, main  # noqa: E402


def baseline():
    return {
        "room": ({"last_seq": 1000, "generation": 0}, None),
        "status": ({"ok": True, "origin": {"ok": True}}, None),
        "stats": ({"ok": True, "origin": {"ok": True, "stats_engine_warm": True, "stats_engine_seq": 995, "tape_head_seq": 1000}}, None),
        "board": ({"ok": True, "jobs": [], "engine_seq": 995}, None),
        "score": ({"ok": True, "found": False, "score": 0, "engine_warm": True, "engine_seq": 995}, None),
        "floor": ({"seq": 900, "ts": "2026-09-27T12:00:00Z"}, None),
    }


class DoctorTests(unittest.TestCase):
    def test_default_kibble_host_is_current_public_board(self):
        self.assertEqual(DEFAULT_KIBBLE_URL, "https://kibble.world")

    def test_healthy_snapshot(self):
        self.assertTrue(assess(baseline(), 1000)["healthy"])

    def test_rewind_even_when_since_cursor_would_be_echoed(self):
        data = baseline()
        data["stats"][0]["origin"].update(stats_engine_seq=1200, tape_head_seq=1200)
        data["score"][0]["engine_seq"] = 1200
        data["board"][0]["engine_seq"] = 1200
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("possible rewind" in p for p in result["problems"]))

    def test_stalled_engine_and_board_timeout(self):
        data = baseline()
        data["room"][0]["last_seq"] = 2000000
        data["stats"][0]["origin"]["stats_engine_warm"] = False
        data["score"][0]["engine_warm"] = False
        data["board"] = (None, "TimeoutError: timed out")
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("scoring engine is not warm" in p for p in result["problems"]))
        self.assertTrue(any("board: TimeoutError" in p for p in result["problems"]))

    def test_score_projection_mismatch(self):
        data = baseline()
        data["score"][0]["engine_seq"] = 990
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("differs from stats" in p for p in result["problems"]))

    def test_board_must_have_jobs(self):
        data = baseline()
        data["board"] = ({"ok": True, "jobs": None}, None)
        self.assertFalse(assess(data, 1000)["healthy"])

    def test_board_cursor_can_be_in_origin_when_top_level_is_absent(self):
        data = baseline()
        data["board"] = ({"jobs": [{"seq": 994}], "origin": {
            "ok": True, "stats_engine_warm": True, "stats_engine_seq": 995, "tape_last_seq": 1000,
        }}, None)
        result = assess(data, 1000)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["observations"]["board_engine_seq_source"], "origin")
        self.assertEqual(result["observations"]["board_tape_last_seq"], 1000)

    def test_board_job_above_reported_cursor_is_explicit_ambiguity(self):
        data = baseline()
        data["board"] = ({"jobs": [{"seq": 999}], "origin": {
            "ok": True, "stats_engine_seq": 995,
        }}, None)
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertEqual(result["observations"]["board_max_job_seq"], 999)
        self.assertTrue(any("cursor coverage is ambiguous" in p for p in result["problems"]))

    def test_board_missing_cursor_or_conflicting_sources_is_unhealthy(self):
        data = baseline()
        data["board"] = ({"jobs": []}, None)
        self.assertTrue(any("missing integer engine sequence" in p for p in assess(data, 1000)["problems"]))
        data["board"] = ({"jobs": [], "engine_seq": 995, "origin": {"stats_engine_seq": 994}}, None)
        self.assertTrue(any("differs from origin" in p for p in assess(data, 1000)["problems"]))

    def test_board_origin_failure_is_unhealthy(self):
        data = baseline()
        data["board"] = ({"jobs": [], "origin": {
            "ok": False, "stats_engine_warm": False, "stats_engine_seq": 995,
        }}, None)
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("board: origin is not healthy" in p for p in result["problems"]))
        self.assertTrue(any("origin scoring engine is not warm" in p for p in result["problems"]))

    def test_cursor_below_retained_floor_has_only_conditional_replay_interpretation(self):
        data = baseline()
        data["floor"][0]["seq"] = 998
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("2 intervening sequences" in p and "if it is a native cursor" in p
                            for p in result["problems"]))
        self.assertEqual(result["evidence_scope"]["native_to_host_cursor_mapping"], "not_established")
        self.assertFalse(any("messages have fallen" in p for p in result["problems"]))

    def test_equal_cursors_and_healthy_diagnostic_do_not_bind_ledgers_or_credit(self):
        result = assess(baseline(), 1000)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["evidence_scope"]["native_to_host_cursor_mapping"], "not_established")
        self.assertEqual(result["evidence_scope"]["credit_for_submission"], "not_determined")

    def test_arithmetic_differences_are_not_labelled_verified_processing_lag(self):
        data = baseline()
        data["room"][0]["last_seq"] = 2000000
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertEqual(result["observations"]["scoring_engine_gap"], 2000000 - 995)
        self.assertTrue(any("numeric difference" in p and "stale or non-comparable" in p
                            for p in result["problems"]))
        self.assertFalse(any("messages behind" in p for p in result["problems"]))

    def test_inventory_keeps_qualified_cursor_paths_without_merging_ledgers(self):
        data = baseline()
        data["status"][0]["origin"]["engine_seq"] = 11
        data["status"][0]["origin"]["nested"] = {"host_cursor": 12}
        data["board"][0]["jobs"] = [{"seq": 999}]
        result = assess(data, 1000)
        values = result["observations"]["reported_cursor_metadata"]
        self.assertEqual(values["status.origin.engine_seq"], 11)
        self.assertEqual(values["status.origin.nested.host_cursor"], 12)
        self.assertEqual(values["stats.origin.stats_engine_seq"], 995)
        self.assertEqual(values["board.engine_seq"], 995)
        self.assertEqual(values["room.last_seq"], 1000)
        self.assertFalse(any("jobs" in key for key in values))
        self.assertEqual(result["evidence_scope"]["native_to_host_cursor_mapping"], "not_established")

    def test_inventory_structural_bound_is_visible_and_unhealthy(self):
        data = baseline()
        data["status"][0]["origin"].update({f"field_{i}_cursor": i for i in range(130)})
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(result["observations"]["cursor_inventory_truncated"])
        self.assertLessEqual(len(result["observations"]["reported_cursor_metadata"]), 128)

    def test_missing_or_wrong_requested_score_identity_is_not_accepted(self):
        data = baseline()
        expected = "did:example:owner"
        for value in (None, "did:example:other"):
            data["score"][0]["did"] = value
            result = assess(data, 1000, expected_did=expected)
            self.assertFalse(result["healthy"])
            self.assertFalse(result["observations"]["score_identity_matches"])
        data["score"][0]["did"] = expected
        self.assertTrue(assess(data, 1000, expected_did=expected)["healthy"])

    def test_score_and_breakdown_mismatch_is_visible_without_summing_role_boards(self):
        data = baseline()
        data["score"][0]["breakdown"] = {"score": 1}
        self.assertFalse(assess(data, 1000)["healthy"])
        data["score"][0]["breakdown"]["score"] = 0
        data["score"][0]["role_scores"] = {"miner": 999, "agent": 999}
        self.assertTrue(assess(data, 1000)["healthy"])

    def test_nonfinite_timeout_fails_before_any_network_call(self):
        for value in ("nan", "inf"):
            with mock.patch("doctor.fetch") as network, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main(["--timeout", value])
                network.assert_not_called()

    def test_fetch_rejects_oversized_json_instead_of_unbounded_read(self):
        with mock.patch("urllib.request.urlopen") as network, mock.patch("doctor.MAX_JSON_BYTES", 4):
            response = network.return_value.__enter__.return_value
            response.read.return_value = b"xxxxx"
            payload, error = fetch("https://example.test/score", 1)
            response.read.assert_called_once_with(5)
            self.assertIsNone(payload)
            self.assertIn("exceeds byte bound", error)

    def test_fetch_reads_valid_json_and_catches_excessive_nesting(self):
        with mock.patch("urllib.request.urlopen") as network:
            response = network.return_value.__enter__.return_value
            response.read.return_value = b'{"ok": true}'
            self.assertEqual(fetch("https://example.test/status", 1), ({"ok": True}, None))
            # CPython versions differ in parser depth limits. A parsed root
            # array is still not a valid API object; parser denial is also safe.
            response.read.return_value = b"[" * 2000 + b"0" + b"]" * 2000
            payload, error = fetch("https://example.test/status", 1)
            self.assertIsNone(payload)
            self.assertTrue("RecursionError" in error or "expected a JSON object" in error)
            with mock.patch("doctor.json.loads", side_effect=RecursionError("parser limit")):
                payload, error = fetch("https://example.test/status", 1)
                self.assertIsNone(payload)
                self.assertIn("RecursionError", error)

    def test_cursor_immediately_before_retained_floor_can_replay(self):
        data = baseline()
        data["floor"][0]["seq"] = 996
        self.assertTrue(assess(data, 1000)["healthy"])

    def test_failed_floor_probe_is_explicit(self):
        data = baseline()
        data["floor"] = (None, "TimeoutError: timed out")
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("floor: TimeoutError" in p for p in result["problems"]))


if __name__ == "__main__":
    unittest.main()
