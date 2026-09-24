"""Offline regression cases for the read-only Kibble doctor."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from doctor import assess  # noqa: E402


def baseline():
    return {
        "room": ({"last_seq": 1000, "generation": 0}, None),
        "status": ({"ok": True, "origin": {"ok": True}}, None),
        "stats": ({"ok": True, "origin": {"ok": True, "stats_engine_warm": True, "stats_engine_seq": 995, "tape_head_seq": 1000}}, None),
        "board": ({"ok": True, "jobs": [], "engine_seq": 995}, None),
        "score": ({"ok": True, "found": False, "score": 0, "engine_warm": True, "engine_seq": 995}, None),
    }


class DoctorTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
