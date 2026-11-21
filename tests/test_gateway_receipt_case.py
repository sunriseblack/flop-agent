import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gateway_receipt_case as case


class GatewayReceiptCaseTests(unittest.TestCase):
    def setUp(self):
        self.receipt = {"request_id": case.REQUEST, "channel_id": case.CHANNEL, "state": "estimated",
                        "response_status": 503, "settled_spend_raw": None}

    def test_estimate_can_reference_paid_channel(self):
        r = case.compare(self.receipt)
        self.assertEqual(r["receipt_state"], "estimated")
        self.assertEqual(r["referenced_channel_settlement"]["block_event_index"], 9)
        self.assertIsNone(r["receipt_settled_spend_raw"])
        self.assertEqual(r["per_request_chain_payment"], "unknown")
        self.assertEqual(r["current_quota"], "unknown")

    def test_release_and_zero_are_preserved_without_deducing_a_refund(self):
        r = case.compare(dict(self.receipt, state="released", settled_spend_raw="0"))
        self.assertEqual(r["receipt_settled_spend_raw"], "0")
        self.assertEqual(r["referenced_channel_settlement"]["event"], "computeChannel.Settled")
        self.assertEqual(r["beneficiary_credit"], "unknown")

    def test_different_or_missing_channel_cannot_borrow_the_terminal_event(self):
        for cid, expected in [(None, "missing"), ("0x" + "a1" * 32, "different")]:
            r = case.compare(dict(self.receipt, channel_id=cid))
            self.assertIsNone(r["referenced_channel_settlement"])
            self.assertEqual(r["channel_reference"], expected)

    def test_unknown_request_and_malformed_claims(self):
        for change in [{"request_id": "different"}, {"channel_id": "partial"}, {"state": "pending-new"},
                       {"settled_spend_raw": True}, {"settled_spend_raw": 0.5}, {"response_status": True}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                case.compare(dict(self.receipt, **change))
