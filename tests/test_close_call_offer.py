"""Offline checks for bounded Close Call paper-offer preparation."""

import base64
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import close_call_offer as offer  # noqa: E402
import close_call_watch_offer as watcher  # noqa: E402
from verify_tape import ALPHABET  # noqa: E402


def encode_base58(raw):
    value = int.from_bytes(raw, "big")
    output = ""
    while value:
        value, digit = divmod(value, 58)
        output = ALPHABET[digit] + output
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + output


class CloseCallOfferTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.did = "did:key:z" + encode_base58(b"\xed\x01" + public)
        self.now = dt.datetime(2026, 10, 1, 14, 10, tzinfo=dt.timezone.utc)
        self.price_body = {"t": "price", "n": 1754, "for": 1755,
                           "limits": ["219.00", "242.04"], "ref": {"px": "230.52"}}

    def snapshot(self, body=None, stamp="2026-10-01T14:09:00Z"):
        text = json.dumps(self.price_body if body is None else body,
                          sort_keys=True, separators=(",", ":"))
        nonce = 1790863800000
        signature = self.private.sign(f"d-close1-price|{nonce}|{text}".encode())
        message = {"seq": 1755, "from": self.did, "nonce": nonce, "text": text,
                   "sig": base64.urlsafe_b64encode(signature).decode().rstrip("="),
                   "ts": stamp}
        return {"room": "d-close1-price", "last_seq": 1755,
                "messages": [message]}

    def read(self, snapshot):
        with patch.object(offer, "REFEREE_DID", self.did):
            return offer.read_price(snapshot, now=self.now)

    def test_signed_price_and_bounded_offer(self):
        price = self.read(self.snapshot())
        self.assertEqual(price["sweep"], 1755)
        terms, reserve = offer.validate_offer(
            "test-1", "sell", "40", "230.50", 1756, "9700", self.did, price)
        self.assertEqual(reserve, offer.Decimal("9681.84"))
        body = json.loads(offer.signed_offer(terms, self.private))
        self.assertEqual(body["t"], "offer")
        self.assertEqual(body["season"], "close-1")
        self.assertEqual(body["terms"], terms)
        signature = base64.urlsafe_b64decode(body["maker_sig"] + "==")
        self.private.public_key().verify(
            signature, f"close-1|terms|{offer.canonical_terms(terms)}".encode())

    def test_rejects_unverified_or_stale_price(self):
        with self.assertRaisesRegex(ValueError, "referee DID"):
            offer.read_price(self.snapshot(), now=self.now)
        snapshot = self.snapshot()
        snapshot["messages"][0]["text"] += " "
        with self.assertRaisesRegex(ValueError, "signature"):
            self.read(snapshot)
        with self.assertRaisesRegex(ValueError, "stale"):
            self.read(self.snapshot(stamp="2026-10-01T13:58:00Z"))
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.read(self.snapshot(stamp="2026-10-01T14:09:00"))

    def test_rejects_malformed_limits(self):
        body = {**self.price_body, "limits": ["NaN", "242.04"]}
        with self.assertRaisesRegex(ValueError, "invalid"):
            self.read(self.snapshot(body=body))
        body = {**self.price_body, "limits": ["oops", "242.04"]}
        with self.assertRaisesRegex(ValueError, "malformed"):
            self.read(self.snapshot(body=body))

    def test_fee_ceiling_includes_quote_offset_from_reference(self):
        ref = offer.Decimal("230.52")
        self.assertEqual(offer.fee_ceiling_per_contract(offer.Decimal("227.75"), ref),
                         offer.Decimal("14.2960"))
        self.assertEqual(offer.fee_ceiling_per_contract(offer.Decimal("233.29"), ref),
                         offer.Decimal("14.2960"))

    def test_rejects_expired_or_unfunded_offer(self):
        price = self.read(self.snapshot())
        for until in (1754, 1758, 2557):
            with self.assertRaisesRegex(ValueError, "expiry"):
                offer.validate_offer("test-1", "buy", "1", "230.50", until,
                                     "9700", self.did, price)
        with self.assertRaisesRegex(ValueError, "outside signed"):
            offer.validate_offer("test-1", "buy", "1", "242.05", 1755,
                                 "9700", self.did, price)
        with self.assertRaisesRegex(ValueError, "reserve exceeds"):
            offer.validate_offer("test-1", "buy", "40", "230.50", 1755,
                                 "9681.83", self.did, price)
        with self.assertRaisesRegex(ValueError, "malformed"):
            offer.validate_offer("bad space", "buy", "1", "230.50", 1755,
                                 "9700", self.did, price)

    def test_unresolved_fill_scenarios_cover_both_account_states(self):
        price = self.read(self.snapshot())
        scenarios = ["9700:-0.9", "470:-40.9"]
        terms, reserve = offer.validate_offer(
            "conditional-buy", "buy", "40", "230.50", 1756, None,
            self.did, price, scenarios=scenarios)
        self.assertEqual(terms["side"], "buy")
        self.assertEqual(reserve, offer.Decimal("9474.39"))
        with self.assertRaisesRegex(ValueError, "scenario 1 reserve"):
            offer.validate_offer("conditional-buy", "buy", "40", "230.50",
                                 1756, None, self.did, price,
                                 scenarios=["9400:-0.9", "470:-40.9"])
        with self.assertRaisesRegex(ValueError, "scenario 2 reserve"):
            offer.validate_offer("conditional-buy", "buy", "40", "230.50",
                                 1756, None, self.did, price,
                                 scenarios=["9700:-0.9", "460:-40.9"])
        with self.assertRaisesRegex(ValueError, "scenario 1 is malformed"):
            offer.validate_offer("conditional-buy", "buy", "40", "230.50",
                                 1756, None, self.did, price,
                                 scenarios=["470:--40.9"])
        with self.assertRaisesRegex(ValueError, "either a cash floor"):
            offer.validate_offer("conditional-buy", "buy", "40", "230.50",
                                 1756, "9700", self.did, price,
                                 scenarios=scenarios)

    def test_conditional_buy_proves_funded_or_funds_void_in_each_state(self):
        price = self.read(self.snapshot())
        scenarios = ["9760:9780:-0.9", "470:500:-40.9",
                     "900:950:39.1", "9560:9580:-0.9"]
        terms, reserve = offer.validate_offer(
            "funds-gated-buy", "buy", "39", "230.42", 1755, None,
            self.did, price, conditional_scenarios=scenarios,
            max_abs_position="45")
        self.assertEqual(terms["side"], "buy")
        self.assertGreater(reserve, offer.Decimal("9000"))
        branches = offer.conditional_analysis("buy", offer.Decimal("39"),
                                               offer.Decimal("230.42"), price,
                                               scenarios, "45")
        self.assertEqual([item["outcome"] for item in branches],
                         ["maker_funded_within_fee_bound", "maker_funded_within_fee_bound",
                          "maker_funds_void_if_reached", "maker_funded_within_fee_bound"])
        self.assertEqual([item["position_after"] for item in branches],
                         ["38.1", "-1.9", "39.1", "38.1"])

    def test_conditional_sell_proves_funded_or_funds_void_in_each_state(self):
        price = self.read(self.snapshot())
        scenarios = ["9760:9780:-0.9", "470:500:-40.9",
                     "900:950:39.1", "9560:9580:-0.9"]
        terms, reserve = offer.validate_offer(
            "funds-gated-sell", "sell", "38.5", "233.29", 1755, None,
            self.did, price, conditional_scenarios=scenarios,
            max_abs_position="45")
        self.assertEqual(terms["side"], "sell")
        self.assertGreater(reserve, offer.Decimal("9000"))
        branches = offer.conditional_analysis("sell", offer.Decimal("38.5"),
                                               offer.Decimal("233.29"), price,
                                               scenarios, "45")
        self.assertEqual([item["outcome"] for item in branches],
                         ["maker_funded_within_fee_bound", "maker_funds_void_if_reached",
                          "maker_funded_within_fee_bound", "maker_funded_within_fee_bound"])
        self.assertEqual([item["position_after"] for item in branches],
                         ["-39.4", "-40.9", "0.6", "-39.4"])

    def test_conditional_mode_rejects_ambiguous_or_unbounded_states(self):
        price = self.read(self.snapshot())
        kwargs = {"conditional_scenarios": ["9000:9500:39.1"],
                  "max_abs_position": "45"}
        with self.assertRaisesRegex(ValueError, "ambiguous funding"):
            offer.validate_offer("test", "buy", "40", "230.42", 1755,
                                 None, self.did, price, **kwargs)
        kwargs["conditional_scenarios"] = ["0:100:39.1"]
        with self.assertRaisesRegex(ValueError, "no funded account scenario"):
            offer.validate_offer("test", "buy", "40", "230.42", 1755,
                                 None, self.did, price, **kwargs)
        kwargs["conditional_scenarios"] = ["9760:9780:-0.9"]
        kwargs["max_abs_position"] = "30"
        with self.assertRaisesRegex(ValueError, "exceeds position cap"):
            offer.validate_offer("test", "buy", "40", "230.42", 1755,
                                 None, self.did, price, **kwargs)
        kwargs["conditional_scenarios"] = ["1000:900:-0.9"]
        kwargs["max_abs_position"] = "45"
        with self.assertRaisesRegex(ValueError, "invalid cash bounds"):
            offer.validate_offer("test", "buy", "40", "230.42", 1755,
                                 None, self.did, price, **kwargs)
        with self.assertRaisesRegex(ValueError, "position cap applies only"):
            offer.validate_offer("test", "buy", "1", "230.50", 1755,
                                 "9700", self.did, price, max_abs_position="45")
        with self.assertRaisesRegex(ValueError, "starts beyond position cap"):
            offer.validate_offer("test", "buy", "1", "230.50", 1755,
                                 None, self.did, price,
                                 conditional_scenarios=["900:950:46"],
                                 max_abs_position="45")

    def test_conditional_cli_remains_dry_run_and_reports_every_branch(self):
        fresh_stamp = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        snapshot = self.snapshot(stamp=fresh_stamp)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agent-did.json").write_text(json.dumps({"did": self.did}))
            output = io.StringIO()
            with patch.object(offer, "PROJECT_ROOT", root), \
                    patch.object(offer, "REFEREE_DID", self.did), \
                    patch.object(offer, "fetch_json", return_value=snapshot), \
                    patch.object(offer, "audit", return_value={
                        "owner_result": {"in_input": True, "minted_this_sweep": True},
                        "provenance": "test_full_record"}), \
                    patch.object(offer, "post_and_verify") as posting, \
                    patch("sys.stdout", output):
                code = offer.main([
                    "--id", "conditional-dry", "--side", "buy", "--qty", "39",
                    "--px", "230.42", "--until", "1755",
                    "--conditional-scenario", "9760:9780:-0.9",
                    "--conditional-scenario", "470:500:-40.9",
                    "--conditional-scenario", "900:950:39.1",
                    "--max-abs-position", "45"])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(len(result["conditional_branches"]), 3)
        self.assertEqual(result["conditional_branches"][2]["outcome"],
                         "maker_funds_void_if_reached")
        posting.assert_not_called()

    def test_post_starts_watch_from_verified_receipt_without_refetching_offer(self):
        fresh_stamp = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        snapshot = self.snapshot(stamp=fresh_stamp)
        public = self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = self.private.private_bytes(serialization.Encoding.PEM,
                                         serialization.PrivateFormat.PKCS8,
                                         serialization.NoEncryption())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            identity = root / ".private" / "identity"
            identity.mkdir(parents=True)
            (identity / "agent-ed25519.pem").write_bytes(pem)
            (root / "agent-did.json").write_text(json.dumps({
                "did": self.did, "public_key_raw_hex": public.hex()}))
            output = io.StringIO()
            with patch.object(offer, "PROJECT_ROOT", root), \
                    patch.object(offer, "REFEREE_DID", self.did), \
                    patch.object(offer, "fetch_json", return_value=snapshot), \
                    patch.object(offer, "audit", return_value={
                        "owner_result": {"in_input": True, "minted_this_sweep": True},
                        "provenance": "test_full_record"}), \
                    patch.object(offer, "post_and_verify", return_value={
                        "room": "close1", "seq": 100, "from": self.did, "verified": True}), \
                    patch.object(watcher, "watch_cursor", return_value={
                        "status": "no_signed_public_trade_observed", "through_seq": 120}) as watching, \
                    patch("sys.stdout", output):
                code = offer.main(["--id", "test-watch", "--side", "buy", "--qty", "1",
                                   "--px", "230.50", "--until", "1755",
                                   "--cash-floor", "9700", "--post", "--watch-seconds", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["watch"]["through_seq"], 120)
        args = watching.call_args.args
        self.assertEqual(args[:3], ("close1", 100, 1))
        self.assertEqual(args[3]["terms"]["id"], "test-watch")


if __name__ == "__main__":
    unittest.main()
