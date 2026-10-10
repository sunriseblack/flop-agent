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
