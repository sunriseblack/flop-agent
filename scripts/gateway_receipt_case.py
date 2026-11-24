"""Inspect a saved gateway receipt and optionally compare it with a pinned devnet event."""

import argparse
from decimal import Decimal, DecimalException
import hashlib
import json
from pathlib import Path
import re
import sys

from submission_evidence import strict_json


REQUEST = "e7892382-fcc9-420b-b2a0-c7e971c23f17"
CHANNEL = "0x625606bb24f0e82fa235bce993504fde776c4879b84a37bae92decba2c71aea3"
SETTLEMENT = {
    "block": 4014811,
    "block_hash": "0x638595fcc512fd29abd4c4f85cae5990d24eae72a2c27dad19f5e37770419d72",
    "extrinsic_index": 2,
    "extrinsic_hash": "0x370697667d0e04119711a88166e2a8dc9a5069afc14af1e94316975f76e4eabc",
    "block_event_index": 9,
    "event": "computeChannel.Settled",
    "miner_paid_raw": "60971428571391361",
}


def receipt_fields(receipt, request_id, expected_channel):
    if not isinstance(receipt, dict) or receipt.get("request_id") != request_id:
        raise ValueError("receipt does not match the expected request ID")
    channel = receipt.get("channel_id")
    if channel is not None and (not isinstance(channel, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", channel)):
        raise ValueError("invalid channel_id")
    if expected_channel is None:
        reference = "supplied_unverified"
        if channel is None:
            reference = "null" if "channel_id" in receipt else "absent"
    elif channel is None:
        reference = "missing"
    elif channel.lower() == expected_channel:
        reference = "matches"
    else:
        reference = "different"

    state = receipt.get("state")
    if state not in ("reserved", "estimated", "settled", "released"):
        raise ValueError("unsupported or missing receipt state")
    response_status = receipt.get("response_status")
    if response_status is not None and (type(response_status) is not int or not 100 <= response_status <= 599):
        raise ValueError("invalid HTTP response_status")
    raw = receipt.get("settled_spend_raw")
    if raw is not None and not ((type(raw) is int and raw >= 0)
                                or (isinstance(raw, str) and re.fullmatch(r"[0-9]+", raw))):
        raise ValueError("invalid settled_spend_raw")
    return {"request_id": request_id, "receipt_state": state,
            "recorded_response_status": response_status, "channel_reference": reference,
            "settled_spend_raw_field_present": "settled_spend_raw" in receipt,
            "receipt_settled_spend_raw": str(raw) if raw is not None else None,
            "chain_source": "previously decoded public devnet RPC observation" if expected_channel else None,
            "receipt_authentication": "not_checked", "observation_time": "not_supplied",
            "per_request_chain_payment": "unknown", "current_quota": "unknown",
            "beneficiary_credit": "unknown"}


def compare(receipt):
    report = receipt_fields(receipt, REQUEST, CHANNEL)
    report["schema"] = "flop-receipt-308-v1"
    report["referenced_channel_settlement"] = SETTLEMENT if report["channel_reference"] == "matches" else None
    return report


def field_report(receipt, request_id, channel_id=None):
    if request_id in (".", "..") or not re.fullmatch(r"[!-~]{1,128}", request_id):
        raise ValueError("expected a nonempty request identifier of at most 128 characters")
    witness = None
    if channel_id is not None:
        channel_id = channel_id.lower()
        witnesses = json.loads(Path(__file__).with_name("gateway_588_events.json").read_bytes())
        witness = witnesses.get(channel_id)
        if witness is None:
            raise ValueError("channel is outside the pinned issue-588 observations")
    report = receipt_fields(receipt, request_id, channel_id)
    value = receipt.get("settled_spend")
    if value is None:
        spend_state = "null" if "settled_spend" in receipt else "absent"
    else:
        if isinstance(value, str) and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
            value = Decimal(value)
        if type(value) not in (int, Decimal) or not Decimal(value).is_finite() or value < 0:
            raise ValueError("invalid nonnegative settled_spend")
        spend_state = "zero" if value == 0 else "positive"
    if "terminal_event" not in receipt:
        event_reference = "absent"
    elif receipt["terminal_event"] is None:
        event_reference = "null"
    elif not isinstance(receipt["terminal_event"], str):
        raise ValueError("invalid terminal_event")
    elif report["channel_reference"] != "matches":
        event_reference = "unbound_channel"
    else:
        references = {f"{witness['block_hash']}:{witness['extrinsic_index']}"}
        if witness["event"] == "computeChannel.TimedOutRefunded":
            references.add("timeout:" + witness["extrinsic_hash"])
        event_reference = "matches" if receipt["terminal_event"].lower() in references else "different"
    report.update({
        "receipt_terminal_event_reference": event_reference,
        "schema": "flop-receipt-588-v1" if witness else "flop-gateway-request-observation-v1",
        "expected_channel": channel_id,
        "receipt_settled_spend_state": spend_state,
        "referenced_channel_event": witness if report["channel_reference"] == "matches" else None,
        "answered_turn_verified": False,
    })
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="one saved, redacted JSON receipt")
    parser.add_argument("--field-channel", help="channel from network issue 588 to compare")
    parser.add_argument("--request-id", help="expected identifier from your existing request record")
    args = parser.parse_args(argv)
    if args.field_channel is not None and args.request_id is None:
        parser.error("--field-channel requires --request-id from the saved request record")
    try:
        with args.receipt.open("rb") as source:
            data = source.read(65537)
        if len(data) > 65536:
            raise ValueError("receipt exceeds 64 KiB")
        if args.request_id is None:
            report = compare(strict_json(data.decode("utf-8")))
        else:
            receipt = strict_json(data.decode("utf-8"), parse_float=Decimal)
            report = field_report(receipt, args.request_id, args.field_channel)
            report["receipt_sha256"] = hashlib.sha256(data).hexdigest()
    except (OSError, ValueError, DecimalException, RecursionError) as exc:
        print(f"receipt unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
