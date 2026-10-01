#!/usr/bin/env python3
"""Read-only coverage check for the Close Call archive and signed referee flow.

This checks the *latest indexed* sweep's file and signature, then compares it
with the latest signed flow. It cannot determine a participant's balance or the
outcome of any trade in the unarchived gap.
"""

import argparse
import json
import sys
import urllib.error

from audit_close_call import (ARCHIVE, FLOW_EXPORT, MAX_FLOW_BYTES,
                              MAX_INDEX_BYTES, MAX_RECORD_BYTES, REFEREE_DID,
                              HASH, fetch_bytes, find_entry,
                              verify_archive_record, verify_flow)
from verify_tape import verify_record


FLOW_TAIL = "https://technocore.chat/r/d-close1-flow?format=json&limit=1"
MAX_TAIL_BYTES = 1_000_000


def latest_signed_flow(snapshot, referee_did=REFEREE_DID):
    if (not isinstance(snapshot, dict) or snapshot.get("room") != "d-close1-flow" or
            not isinstance(snapshot.get("messages"), list) or
            len(snapshot["messages"]) != 1):
        raise ValueError("latest flow snapshot has the wrong room or message count")
    message = snapshot["messages"][0]
    if (not isinstance(message, dict) or type(message.get("seq")) is not int or
            message["seq"] != snapshot.get("last_seq")):
        raise ValueError("latest flow sequence does not match room head")
    status, reason = verify_record("d-close1-flow", message)
    if status != "verified" or message.get("from") != referee_did:
        raise ValueError(f"latest flow signature or referee DID mismatch: {reason}")
    try:
        body = json.loads(message["text"])
    except (ValueError, TypeError) as exc:
        raise ValueError("latest flow text is not JSON") from exc
    if (not isinstance(body, dict) or body.get("t") != "flow" or
            type(body.get("n")) is not int or body["n"] < 1 or
            not isinstance(body.get("file"), str) or not HASH.fullmatch(body["file"])):
        raise ValueError("latest signed flow has malformed sweep or file hash")
    return message, body


def assess_coverage(index, tip_raw, flow_export, tail, referee_did=REFEREE_DID):
    entries = index.get("sweeps") if isinstance(index, dict) else None
    if (not isinstance(index, dict) or index.get("contest") != "close-1" or
            not isinstance(entries, list) or not entries):
        raise ValueError("archive index has the wrong contest or no sweeps")
    numbers = [entry.get("n") if isinstance(entry, dict) and
               type(entry.get("n")) is int else None for entry in entries]
    if numbers != list(range(1, len(entries) + 1)):
        raise ValueError("archive index has missing, duplicate, or out-of-order sweeps")
    tip = len(entries)
    entry = find_entry(index, tip)
    verify_archive_record(entry, tip_raw)
    signed_tip_seq = verify_flow(flow_export, tip, entry["file"], referee_did)
    latest_message, latest_body = latest_signed_flow(tail, referee_did)
    gap = latest_body["n"] - tip
    if gap < 0:
        raise ValueError("archive tip is ahead of latest signed referee flow")
    return {
        "status": "caught_up" if gap == 0 else "lagging",
        "archive_tip_sweep": tip,
        "archive_tip_status": entry["status"],
        "archive_tip_signed_flow_seq": signed_tip_seq,
        "archive_tip_record_checksum_verified": True,
        "archive_tip_full_hash_matches_signed_flow": True,
        "archive_tip_provenance": ("full_record_matches_signed_hash" if entry["status"] == "full"
                                   else "redacted_record_matches_unsigned_archive_index_only"),
        "latest_signed_sweep": latest_body["n"],
        "latest_signed_flow_seq": latest_message["seq"],
        "latest_signed_flow_ts": latest_message.get("ts"),
        "unarchived_sweep_count": gap,
        "caution": ("This is archive coverage, not an account statement. The latest signed flow "
                    "omits many per-trade outcomes; do not infer fills, expiry, balances, or score "
                    "from an unarchived gap."),
    }


def check(timeout=15):
    index = json.loads(fetch_bytes(ARCHIVE + "index.json", MAX_INDEX_BYTES, timeout))
    entries = index.get("sweeps") if isinstance(index, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("archive index has no sweeps")
    entry = find_entry(index, len(entries))
    tip_raw = fetch_bytes(ARCHIVE + entry["path"], MAX_RECORD_BYTES, timeout)
    export = fetch_bytes(FLOW_EXPORT, MAX_FLOW_BYTES, timeout)
    tail = json.loads(fetch_bytes(FLOW_TAIL, MAX_TAIL_BYTES, timeout))
    return assess_coverage(index, tip_raw, export, tail)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=15, help="seconds per public GET")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        result = check(args.timeout)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"close-call coverage unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "caught_up" else 1


if __name__ == "__main__":
    sys.exit(main())
