"""Offline checks for the read-only, signed Close Call leaderboard scout."""

import base64
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_scout as scout  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def base58(raw):
    value = int.from_bytes(raw, "big")
    result = ""
    while value:
        value, digit = divmod(value, 58)
        result = ALPHABET[digit] + result
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + result


class CloseCallScoutTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + base58(b"\xed\x01" + public)
        self.long = "did:key:zlong"
        self.third = "did:key:zthird"
        self.now = dt.datetime(2026, 10, 1, 16, 10, tzinfo=dt.timezone.utc)
        marks = ("100.00", "101.00", "102.00", "101.00", "100.00")
        leader_scores = ("120", "125", "130", "134", "138")
        long_scores = ("100", "106", "112", "106", "100")
        self.snapshots = {}
        for room in scout.ROOMS:
            messages = []
            for n in range(1, 6):
                body = {"t": room.removeprefix("d-close1-"), "n": n, "file": f"{n:064x}"}
                if room == "d-close1-price":
                    body.update({"ref": {"px": marks[n - 1]}, "global": marks[n - 1]})
                elif room == "d-close1-pnl":
                    body.update({"mark": marks[n - 1], "top": [
                        [self.did, leader_scores[n - 1]],
                        [self.long, long_scores[n - 1]], [self.third, "50"]]})
                else:
                    body["top"] = ([[self.did, "5.00"]] if n <= 3 else []) + [[self.long, "6.00"]]
                text = json.dumps(body, separators=(",", ":"))
                nonce = 1790870000000 + n
                sig = self.private.sign(f"{room}|{nonce}|{text}".encode())
                messages.append({"seq": n, "from": self.did, "nonce": nonce,
                                 "text": text, "sig": base64.urlsafe_b64encode(sig).decode().rstrip("="),
                                 "ts": "2026-10-01T16:09:00Z"})
            self.snapshots[room] = {"room": room, "last_seq": 5, "messages": messages}

    def parsed(self):
        return [scout.parse_snapshot(room, self.snapshots[room], self.did, self.now)
                for room in scout.ROOMS]

    def test_signed_scout_observes_exit_without_claiming_short(self):
        report = scout.assess(*self.parsed(), owner_did=self.third)
        self.assertEqual(report["sweep"], 5)
        self.assertEqual(report["observed_window_sweeps"], [1, 5])
        self.assertEqual(report["leaders"][0]["score"], "138")
        self.assertIsNone(report["leaders"][0]["signed_top_long_qty"])
        self.assertEqual(report["recent_top_long_exits"][0]["first_absent_sweep"], 4)
        self.assertIn("does not by itself prove a short", report["recent_top_long_exits"][0]["caution"])
        self.assertEqual(report["round_trip_base_fee_per_contract_at_ref"], "2.00")
        self.assertEqual(report["observed_ref_range"], "2.00")
        self.assertTrue(report["owner_in_top_25"])
        self.assertEqual(report["visible_board_count"], 3)
        self.assertEqual(report["visible_board_floor_score"], "50")

    def test_tampering_wrong_author_and_stale_head_fail_closed(self):
        room = "d-close1-pnl"
        self.snapshots[room]["messages"][2]["text"] += " "
        with self.assertRaisesRegex(ValueError, "unsigned"):
            self.parsed()
        self.snapshots[room]["messages"][2]["text"] = self.snapshots[room]["messages"][2]["text"].rstrip()
        self.snapshots[room]["messages"][2]["from"] = self.long
        with self.assertRaisesRegex(ValueError, "wrong-author"):
            self.parsed()
        self.snapshots[room]["messages"][2]["from"] = self.did
        with self.assertRaisesRegex(ValueError, "stale"):
            scout.parse_snapshot(room, self.snapshots[room], self.did,
                                 self.now + dt.timedelta(minutes=11))

    def test_cross_room_hash_and_mark_mismatch_fail_closed(self):
        price, pnl, positions = self.parsed()
        positions[5]["file"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "hashes disagree"):
            scout.assess(price, pnl, positions)
        positions[5]["file"] = price[5]["file"]
        pnl[5]["mark"] = "99.00"
        with self.assertRaisesRegex(ValueError, "mark differs"):
            scout.assess(price, pnl, positions)

    def test_gapped_sweep_fails_closed(self):
        room = "d-close1-positions"
        self.snapshots[room]["messages"].pop(2)
        with self.assertRaisesRegex(ValueError, "gapped record"):
            self.parsed()
        self.snapshots[room]["messages"].insert(2, self.snapshots[room]["messages"][1])
        with self.assertRaisesRegex(ValueError, "gapped record"):
            self.parsed()

    def test_bool_room_head_is_not_a_sequence(self):
        room = "d-close1-price"
        self.snapshots[room]["last_seq"] = True
        with self.assertRaisesRegex(ValueError, "malformed or empty snapshot"):
            self.parsed()


if __name__ == "__main__":
    unittest.main()
