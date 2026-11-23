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


class FieldReceiptTests(unittest.TestCase):
    refunded = "0xacc394a9d7b1f1bdc64deb7ae68522086054c5cd86e77a49655b9ebf6e384df0"
    paid = "0xd06de895364d6a4d35c82ca749ff338fe3bfef08ef73f2e1517995cfc34ee89f"

    def report(self, expected, **fields):
        receipt = {"request_id": "saved-request", "state": "settled", "channel_id": expected}
        receipt.update(fields)
        return case.field_report(receipt, "saved-request", expected)

    def test_zero_receipt_and_channel_refund(self):
        report = self.report(self.refunded, settled_spend=0, response_status=200)
        self.assertEqual(report["receipt_settled_spend_state"], "zero")
        self.assertEqual(report["referenced_channel_event"]["event"], "computeChannel.TimedOutRefunded")
        self.assertEqual(report["per_request_chain_payment"], "unknown")
        self.assertFalse(report["answered_turn_verified"])

    def test_channel_payment_does_not_assign_request_spend(self):
        report = self.report(self.paid, settled_spend=None)
        self.assertEqual(report["receipt_settled_spend_state"], "null")
        self.assertEqual(report["referenced_channel_event"]["event"], "computeChannel.Settled")
        self.assertEqual(report["per_request_chain_payment"], "unknown")
        self.assertEqual(self.report(self.paid)["receipt_settled_spend_state"], "absent")

    def test_request_and_channel_must_match_independently(self):
        with self.assertRaises(ValueError):
            self.report(self.paid, request_id="another")
        with self.assertRaises(ValueError):
            self.report("0x" + "00" * 32)
        for channel in [None, self.paid]:
            with self.subTest(channel=channel):
                self.assertIsNone(self.report(self.refunded, channel_id=channel)["referenced_channel_event"])

    def test_saved_decimal_keeps_subnormal_positive_separate_from_zero(self):
        from decimal import Decimal
        receipt = case.strict_json('{"settled_spend":1e-999}', parse_float=Decimal)
        self.assertEqual(self.report(self.refunded, **receipt)["receipt_settled_spend_state"], "positive")
        for value in [False, -1, [], "NaN"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.report(self.refunded, settled_spend=value)

    def test_saved_file_entry_point(self):
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as folder:
            saved = Path(folder) / "receipt.json"
            args = [str(saved), "--request-id", "saved-request", "--field-channel", self.refunded]
            saved.write_text(json.dumps({"request_id": "saved-request", "channel_id": self.refunded,
                                         "state": "settled", "settled_spend": 0}))
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(case.main(args), 0)
            self.assertEqual(json.loads(output.getvalue())["referenced_channel_event"]["block"], 3477375)
            with redirect_stderr(StringIO()):
                for bad in ['{"state":"estimated","state":"settled"}', " " * 65537]:
                    saved.write_text(bad)
                    self.assertEqual(case.main(args), 2)
