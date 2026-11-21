"""Compare a saved gateway receipt with the public channel witness in network issue 308."""

import argparse
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


def compare(receipt):
    if not isinstance(receipt, dict) or receipt.get("request_id") != REQUEST:
        raise ValueError("expected the saved receipt for the issue-308 request")
    channel = receipt.get("channel_id")
    if channel is not None and (not isinstance(channel, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", channel)):
        raise ValueError("invalid channel_id")
    if channel is None:
        reference = "missing"
    elif channel.lower() == CHANNEL:
        reference = "matches"
    else:
        reference = "different"

    state = receipt.get("state")
    if state not in ("estimated", "settled", "released"):
        raise ValueError("unsupported or missing receipt state")
    response_status = receipt.get("response_status")
    if response_status is not None and (type(response_status) is not int or not 100 <= response_status <= 599):
        raise ValueError("invalid HTTP response_status")
    raw = receipt.get("settled_spend_raw")
    if raw is not None and not ((type(raw) is int and raw >= 0)
                                or (isinstance(raw, str) and re.fullmatch(r"[0-9]+", raw))):
        raise ValueError("invalid settled_spend_raw")
    return {"schema": "flop-receipt-308-v1", "request_id": REQUEST, "receipt_state": state,
            "recorded_response_status": response_status, "channel_reference": reference,
            "settled_spend_raw_field_present": "settled_spend_raw" in receipt,
            "receipt_settled_spend_raw": str(raw) if raw is not None else None,
            "referenced_channel_settlement": SETTLEMENT if reference == "matches" else None,
            "chain_source": "previously decoded public devnet RPC observation",
            "receipt_authentication": "not_checked", "observation_time": "not_supplied",
            "per_request_chain_payment": "unknown", "current_quota": "unknown",
            "beneficiary_credit": "unknown"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="one saved, redacted JSON receipt")
    args = parser.parse_args(argv)
    try:
        with args.receipt.open("rb") as source:
            data = source.read(65537)
        if len(data) > 65536:
            raise ValueError("receipt exceeds 64 KiB")
        report = compare(strict_json(data.decode("utf-8")))
    except (OSError, ValueError, RecursionError) as exc:
        print(f"receipt unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
