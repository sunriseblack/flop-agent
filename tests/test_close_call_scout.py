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
                    body.update({"ref": {"px": marks[n - 1]}, "global": marks[n - 1],
                                 "age_s": (1, 2, 301, 600, 4)[n - 1]})
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
        self.assertEqual(report["signed_reference_age_seconds_at_sweep"], 4)
        self.assertFalse(report["reference_at_least_5min_stale_at_sweep"])
        self.assertEqual(report["observed_stale_reference_sweep_count"], 2)
        self.assertEqual(report["last_observed_stale_reference_sweep"], 4)
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

    def test_reference_age_is_signed_nonnegative_integer(self):
        room = "d-close1-price"
        message = self.snapshots[room]["messages"][-1]
        for invalid in (-1, True, "300"):
            body = json.loads(message["text"])
            body["age_s"] = invalid
            message["text"] = json.dumps(body, separators=(",", ":"))
            signature = self.private.sign(
                f"{room}|{message['nonce']}|{message['text']}".encode())
            message["sig"] = base64.urlsafe_b64encode(signature).decode().rstrip("=")
            with self.assertRaisesRegex(ValueError, "nonnegative signed reference age"):
                self.parsed()

    def test_podium_projection_is_explicitly_hypothetical(self):
        report = scout.project_podium(*self.parsed(), ["90", "100", "110"], "0", "5")
        self.assertEqual(report["signed_sweep"], 5)
        self.assertEqual(report["visible_cohort"], 3)
        self.assertEqual([row["gap_to_third"] for row in report["scenarios"]],
                         ["-10.00", "50.00", "0.00"])
        self.assertIn("hindsight-perfect direction", report["caution"])
        with self.assertRaisesRegex(ValueError, "must be positive"):
            scout.project_podium(*self.parsed(), ["0"], "0", "5")
        with self.assertRaisesRegex(ValueError, "positive position bound"):
            scout.project_podium(*self.parsed(), ["110"], "0", "0")

    def test_projection_fails_closed_without_observed_sensitivity(self):
        price, pnl, positions = self.parsed()
        for n in price:
            price[n]["global"] = "100.00"
            pnl[n]["mark"] = "100.00"
        with self.assertRaisesRegex(ValueError, "insufficient signed score/mark"):
            scout.project_podium(price, pnl, positions, ["110"], "0", "5")

    def test_signed_final_is_not_the_prelock_vwap_or_owner_score(self):
        for room in scout.ROOMS:
            snapshot = self.snapshots[room]
            for message in snapshot["messages"]:
                body = json.loads(message["text"])
                body["n"] += 2551
                message["seq"] += 2551
                message["ts"] = "2026-10-04T09:00:28Z"
                message["text"] = json.dumps(body, separators=(",", ":"))
                signature = self.private.sign(
                    f"{room}|{message['nonce']}|{message['text']}".encode())
                message["sig"] = base64.urlsafe_b64encode(signature).decode().rstrip("=")
            snapshot["last_seq"] = 2556
        room = "d-close1-price"
        final_body = {"t": "final", "season": "close-1", "price": "234.69",
                      "trade": {"time": "2026-10-04T09:59:40.596000Z",
                                "tid": 868189527772348}}
        text = json.dumps(final_body, separators=(",", ":"))
        nonce = 1790870000010
        signature = self.private.sign(f"{room}|{nonce}|{text}".encode())
        final_message = {"seq": 2557, "from": self.did, "nonce": nonce, "text": text,
                         "sig": base64.urlsafe_b64encode(signature).decode().rstrip("="),
                         "ts": "2026-10-04T10:00:28Z"}
        self.snapshots[room]["messages"].append(final_message)
        self.snapshots[room]["last_seq"] = 2557
        prelock, final = scout.split_final_price_snapshot(self.snapshots[room], self.did)
        self.assertEqual(final["S"], "234.69")
        self.assertEqual(final["signed_seq"], 2557)
        self.assertEqual(prelock["last_seq"], 2556)
        now = dt.datetime(2026, 10, 4, 11, 30, tzinfo=dt.timezone.utc)
        parsed = [scout.parse_snapshot(name, prelock if name == room else self.snapshots[name],
                                       self.did, now, allow_stale=True)
                  for name in scout.ROOMS]
        report = scout.assess(*parsed, owner_did=self.third)
        self.assertEqual(report["sweep"], 2556)
        self.assertEqual(report["paper_vwap_mark"], "100.00")
        self.assertNotEqual(report["paper_vwap_mark"], final["S"])
        with self.assertRaisesRegex(ValueError, "stale"):
            scout.parse_snapshot(room, prelock, self.did, now)
        final_message["text"] += " "
        with self.assertRaisesRegex(ValueError, "invalid signed final"):
            scout.split_final_price_snapshot(self.snapshots[room], self.did)

    def test_signed_final_standings_list_only_published_top_25(self):
        room = "d-close1-pnl"

        def signed(seq, nonce, body):
            text = json.dumps(body, separators=(",", ":"))
            signature = self.private.sign(f"{room}|{nonce}|{text}".encode())
            return {"seq": seq, "from": self.did, "nonce": nonce, "text": text,
                    "sig": base64.urlsafe_b64encode(signature).decode().rstrip("="),
                    "ts": "2026-10-04T17:33:04Z"}

        before = signed(2556, 1790870000011,
                        {"t": "pnl", "n": 2556, "file": "a" * 64,
                         "mark": "234.31", "top": []})
        leaders = [[f"did:key:zleader{i:02d}", str(1000 - i)] for i in range(25)]
        body = {"t": "standings", "season": "close-1", "S": "234.69",
                "file": "b" * 64, "owners": 100, "fees": "100.00",
                "zero_sum": "0.000000",
                "places": [[did, score, [rank], 1]
                           for rank, (did, score) in enumerate(leaders[:3], 1)],
                "next": leaders[3:]}
        final = signed(2557, 1790870000012, body)
        snapshot = {"room": room, "last_seq": 2557, "messages": [before, final]}
        prelock, report = scout.split_final_standings_snapshot(
            snapshot, "234.69", self.did, owner_did=self.third)
        self.assertEqual(prelock["last_seq"], 2556)
        self.assertEqual(report["published_count"], 25)
        self.assertEqual(report["podium"][0]["score"], "1000")
        self.assertFalse(report["owner_in_published_top_25"])
        self.assertIsNone(report["owner_published_rank"])
        self.assertIn("no certified exact rank", report["caution"])
        with self.assertRaisesRegex(ValueError, "invalid signed final standings"):
            scout.split_final_standings_snapshot(snapshot, "234.70", self.did)
        final["text"] += " "
        with self.assertRaisesRegex(ValueError, "invalid signed final standings"):
            scout.split_final_standings_snapshot(snapshot, "234.69", self.did)


if __name__ == "__main__":
    unittest.main()
