"""Offline regression cases for the read-only Kibble doctor."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from doctor import DEFAULT_KIBBLE_URL, assess  # noqa: E402


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

    def test_cursor_below_retained_floor_cannot_catch_up_from_live_room(self):
        data = baseline()
        data["floor"][0]["seq"] = 998
        result = assess(data, 1000)
        self.assertFalse(result["healthy"])
        self.assertTrue(any("2 messages have fallen before retained floor" in p for p in result["problems"]))

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
