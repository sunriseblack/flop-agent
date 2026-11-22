"""Compare event-list visibility for one transaction in two saved explorer responses."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from submission_evidence import MAX_JSON_BYTES, strict_json


HASH = re.compile(r"0x[0-9a-fA-F]{64}")
HASH_KEYS = ("hash", "extrinsicHash", "extrinsic_hash", "txHash", "tx_hash", "transactionHash", "transaction_hash")


def hash_of(row):
    if not isinstance(row, dict):
        raise ValueError("transaction row must be an object")
    values = [row[key] for key in HASH_KEYS if key in row]
    if not values or any(not isinstance(value, str) or not HASH.fullmatch(value) for value in values):
        raise ValueError("transaction row needs a full transaction hash")
    if len({value.lower() for value in values}) != 1:
        raise ValueError("conflicting transaction hashes on the same row")
    return values[0].lower()


def unwrap(value, *, account):
    """Accept a saved row or common response envelopes, never search nested event data."""
    wrapper = "transactions" if account else "transaction"
    for _ in range(3):
        if not isinstance(value, dict):
            return value
        if "error" in value and value["error"] is not None:
            raise ValueError("explorer returned an error instead of a transaction view")
        if any(key in value for key in HASH_KEYS):
            return value
        keys = [key for key in ("data", wrapper) if key in value]
        if "events" in value:
            raise ValueError("events outside the transaction row need a documented binding")
        if len(keys) != 1:
            raise ValueError("unsupported or ambiguous response envelope")
        value = value[keys[0]]
    raise ValueError("response envelope is too deeply nested")


def event_field(row):
    if "events" not in row:
        return {"state": "absent", "count": None}
    events = row["events"]
    if events is None:
        return {"state": "null", "count": None}
    if not isinstance(events, list):
        raise ValueError("events must be a list, null or absent")
    return {"state": "populated" if events else "empty", "count": len(events)}


def compare(tx, account, detail):
    if not isinstance(tx, str) or not HASH.fullmatch(tx):
        raise ValueError("expected a full transaction hash")
    tx = tx.lower()
    detail_row = unwrap(detail, account=False)
    if hash_of(detail_row) != tx:
        raise ValueError("detail belongs to a different transaction")
    listing = unwrap(account, account=True)
    rows = listing if isinstance(listing, list) else [listing]
    matches = [row for row in rows if hash_of(row) == tx]
    if len(matches) != 1:
        raise ValueError("expected exactly one matching transaction on the supplied account page")
    account_view, detail_view = event_field(matches[0]), event_field(detail_row)
    return {"schema": "flop-explorer-event-views-v1", "transaction_hash": tx,
            "account_events": account_view, "detail_events": detail_view,
            "field_state_or_count_differs": account_view != detail_view,
            "event_contents_compared": False, "chain_events_verified": False}


def read_view(path):
    with path.open("rb") as source:
        raw = source.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("saved response exceeds 4 MiB")
    return strict_json(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transaction_hash")
    parser.add_argument("account", type=Path, help="saved account transaction page or its exact transaction row")
    parser.add_argument("detail", type=Path, help="saved transaction detail response or its exact transaction row")
    args = parser.parse_args()
    try:
        account, account_hash = read_view(args.account)
        detail, detail_hash = read_view(args.detail)
        report = compare(args.transaction_hash, account, detail)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"comparison unavailable: {exc}", file=sys.stderr)
        return 2
    report["source_sha256"] = {"account": account_hash, "detail": detail_hash}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
