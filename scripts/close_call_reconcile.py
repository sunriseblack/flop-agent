#!/usr/bin/env python3
"""Read-only, bounded lookup of trade outcomes in indexed Close Call sweeps.

An archived redacted record is checked against the organizer's index checksum,
not against the referee's signed full-file hash. Missing IDs never prove that a
private-room acceptance or a trade outside the selected sweeps did not occur.
"""

import argparse
import json
import re
import sys
import urllib.error

from audit_close_call import (ARCHIVE, FLOW_EXPORT, MAX_FLOW_BYTES,
                              MAX_INDEX_BYTES, MAX_RECORD_BYTES, REFEREE_DID,
                              fetch_bytes, find_entry, inspect_record,
                              verify_archive_record, verify_flow)


TRADE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
MAX_SPAN = 64


def reconcile(first, last, trade_ids, timeout=15, referee_did=REFEREE_DID):
    if (type(first) is not int or type(last) is not int or first < 1 or
            last < first or last - first + 1 > MAX_SPAN or
            not isinstance(trade_ids, list) or not trade_ids or
            len(trade_ids) != len(set(trade_ids)) or
            any(not isinstance(value, str) or not TRADE_ID.fullmatch(value)
                for value in trade_ids) or timeout <= 0):
        raise ValueError("invalid sweep range, trade IDs, or timeout")

    index = json.loads(fetch_bytes(ARCHIVE + "index.json", MAX_INDEX_BYTES, timeout))
    sweeps = index.get("sweeps") if isinstance(index, dict) else None
    if not isinstance(sweeps, list):
        raise ValueError("archive index has no sweeps list")
    by_n = {}
    for entry in sweeps:
        if not isinstance(entry, dict) or type(entry.get("n")) is not int:
            raise ValueError("archive index contains a malformed sweep entry")
        by_n.setdefault(entry["n"], []).append(entry)
    tip = max(by_n, default=0)
    available = []
    missing = []
    for n in range(first, last + 1):
        if n not in by_n:
            missing.append(n)
        else:
            available.append((n, find_entry(index, n)))

    flow = fetch_bytes(FLOW_EXPORT, MAX_FLOW_BYTES, timeout) if available else b""
    outcomes = {trade_id: [] for trade_id in trade_ids}
    checked = []
    for n, entry in available:
        raw = fetch_bytes(ARCHIVE + entry["path"], MAX_RECORD_BYTES, timeout)
        record = verify_archive_record(entry, raw)
        flow_seq = verify_flow(flow, n, entry["file"], referee_did)
        provenance = ("signed_full_hash" if entry["status"] == "full" else
                      "unsigned_index_checksum_for_redacted_copy")
        checked.append({"sweep": n, "signed_flow_seq": flow_seq,
                        "provenance": provenance})
        for trade_id in trade_ids:
            matches, _ = inspect_record(record, trade_id)
            for match in matches:
                outcomes[trade_id].append({"sweep": n, "provenance": provenance,
                                           **match})

    results = {}
    for trade_id, matches in outcomes.items():
        settled = sum(row["outcome"].get("outcome") == "settled" for row in matches)
        if settled > 1:
            raise ValueError(f"{trade_id}: multiple published settlements contradict the rules")
        results[trade_id] = {
            "published_outcomes": matches,
            "classification": ("published_settled" if settled else
                               "published_void_only" if matches else "not_observed"),
        }
    return {
        "status": "complete_range" if not missing else "partial_range",
        "requested_sweeps": [first, last], "archive_tip": tip,
        "checked_sweeps": checked, "missing_sweeps": missing,
        "trade_ids": results,
        "caution": ("Published outcomes are not an account statement or final score. "
                    "Redacted record contents are organizer-indexed but not cryptographically "
                    "bound to the referee's signed full-file hash. A missing ID does not "
                    "exclude private-room redaction or a settlement outside this range."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", type=int, required=True, help="first sweep to inspect")
    parser.add_argument("--last", type=int, required=True, help="last sweep to inspect")
    parser.add_argument("--trade-id", action="append", required=True,
                        help="exact trade ID; repeat for multiple IDs")
    parser.add_argument("--timeout", type=float, default=15, help="seconds per public GET")
    args = parser.parse_args(argv)
    try:
        report = reconcile(args.first, args.last, args.trade_id, args.timeout)
    except (OSError, ValueError, TypeError, urllib.error.URLError) as exc:
        print(f"close-call reconciliation unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "complete_range" else 1


if __name__ == "__main__":
    sys.exit(main())
