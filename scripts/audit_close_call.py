#!/usr/bin/env python3
"""Read-only audit of one archived Close Call sweep and its signed flow post.

The referee signs the hash of the *full* sweep. A redacted archive copy has
different bytes; its contents are validated against the archive index, not
cryptographically proved by the referee signature. Do not confuse the two.
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request

from verify_tape import verify_record


ARCHIVE = "https://challenges.technocore.chat/close-1/"
FLOW_EXPORT = "https://technocore.chat/r/d-close1-flow/export"
REFEREE_DID = "did:key:z6MkowHQwsx9xr84WbWN3YCnKutyBnBXkT1ChKY4uEAAMzte"
HASH = re.compile(r"[0-9a-f]{64}\Z")
MAX_INDEX_BYTES = 2_000_000
MAX_RECORD_BYTES = 32_000_000
MAX_FLOW_BYTES = 16_000_000


def fetch_bytes(url, limit, timeout):
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "flop-agent-close-call-audit/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"response exceeds {limit} bytes: {url}")
    return data


def find_entry(index, sweep):
    entries = index.get("sweeps") if isinstance(index, dict) else None
    if not isinstance(entries, list):
        raise ValueError("archive index has no sweeps list")
    matches = [entry for entry in entries if isinstance(entry, dict) and
               type(entry.get("n")) is int and entry["n"] == sweep]
    if len(matches) != 1:
        latest = max((entry.get("n", 0) for entry in entries
                      if isinstance(entry, dict) and type(entry.get("n")) is int), default=0)
        raise ValueError(f"sweep {sweep} is not uniquely indexed (latest: {latest})")
    entry = matches[0]
    digest = entry.get("file")
    status = entry.get("status")
    checksum = entry.get("sha256") if status == "redacted" else entry.get("sha256", digest)
    directory = {"full": "sweeps", "redacted": "redacted"}.get(status)
    if (not isinstance(digest, str) or not HASH.fullmatch(digest) or
            not isinstance(checksum, str) or not HASH.fullmatch(checksum) or
            (status == "full" and checksum != digest) or
            directory is None or entry.get("path") != f"{directory}/{digest}.json" or
            type(entry.get("bytes")) is not int or not 0 < entry["bytes"] <= MAX_RECORD_BYTES):
        raise ValueError(f"sweep {sweep} has unsafe or malformed archive metadata")
    return entry


def verify_archive_record(entry, raw):
    checksum = entry.get("sha256", entry["file"])
    if len(raw) != entry["bytes"] or hashlib.sha256(raw).hexdigest() != checksum:
        raise ValueError(f"sweep {entry['n']} archive bytes do not match index")
    record = json.loads(raw)
    if (not isinstance(record, dict) or not isinstance(record.get("input"), dict) or
            not isinstance(record.get("output"), dict) or
            record["input"].get("n") != entry["n"] or
            record["output"].get("sweep") != entry["n"]):
        raise ValueError(f"sweep {entry['n']} record shape or number does not match index")
    return record


def verify_flow(export, sweep, digest, referee_did=REFEREE_DID):
    matches = []
    for line in export.splitlines():
        try:
            message = json.loads(line)
            body = json.loads(message["text"])
        except (ValueError, KeyError, TypeError):
            continue
        if isinstance(body, dict) and body.get("t") == "flow" and body.get("n") == sweep:
            matches.append((message, body))
    if len(matches) != 1:
        raise ValueError(f"sweep {sweep} signed flow is absent or ambiguous in retained export")
    message, body = matches[0]
    status, reason = verify_record("d-close1-flow", message)
    if status != "verified" or message.get("from") != referee_did or body.get("file") != digest:
        raise ValueError(f"sweep {sweep} flow signature, referee DID, or file hash mismatch: {reason}")
    return message["seq"]


def inspect_record(record, trade_id=None, owner=None):
    rows = record["input"].get("trades")
    outcomes = record["output"].get("trades")
    if not isinstance(rows, list) or not isinstance(outcomes, list) or len(rows) != len(outcomes):
        raise ValueError("input and output trade lists are not aligned")
    found = []
    if trade_id:
        for position, (terms, outcome) in enumerate(zip(rows, outcomes)):
            if not isinstance(terms, dict) or not isinstance(outcome, dict):
                raise ValueError("trade entry is not an object")
            if terms.get("id") == trade_id or outcome.get("id") == trade_id:
                if terms.get("id") != outcome.get("id"):
                    raise ValueError(f"trade ID mismatch at index {position}")
                found.append({"index": position, "input": terms, "outcome": outcome})
    owner_result = None
    if owner:
        owners = record["input"].get("owners")
        minted = record["output"].get("minted")
        if not isinstance(owners, list) or not isinstance(minted, list):
            raise ValueError("owner and mint lists are not arrays")
        owner_result = {"in_input": owner in owners, "minted_this_sweep": owner in minted}
    return found, owner_result


def audit(sweep, trade_id=None, owner=None, timeout=15):
    index = json.loads(fetch_bytes(ARCHIVE + "index.json", MAX_INDEX_BYTES, timeout))
    entry = find_entry(index, sweep)
    raw = fetch_bytes(ARCHIVE + entry["path"], MAX_RECORD_BYTES, timeout)
    record = verify_archive_record(entry, raw)
    flow_seq = verify_flow(fetch_bytes(FLOW_EXPORT, MAX_FLOW_BYTES, timeout),
                           sweep, entry["file"], referee_did=REFEREE_DID)
    trades, owner_result = inspect_record(record, trade_id, owner)
    return {
        "sweep": sweep,
        "signed_flow_seq": flow_seq,
        "referee_did": REFEREE_DID,
        "signed_full_file_hash": entry["file"],
        "archive_path": ARCHIVE + entry["path"],
        "archive_sha256_verified": entry.get("sha256", entry["file"]),
        "provenance": ("full_record_matches_signed_hash" if entry["status"] == "full" else
                       "redacted_record_matches_unsigned_archive_index_only"),
        "trade_id": trade_id,
        "trade_matches": trades,
        "owner": owner,
        "owner_result": owner_result,
        "caution": (("An absent trade ID proves only absence from this published sweep; "
                     "private trade redaction and other sweeps can conceal activity.") if trade_id else
                    ("An absent mint here does not prove this owner was never minted; "
                     "check earlier sweeps or obtain a signed owner statement.")),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", type=int, required=True, help="referee sweep number")
    parser.add_argument("--trade-id", help="exact trade ID to look up")
    parser.add_argument("--owner", help="exact owner DID to check in mint lists")
    parser.add_argument("--timeout", type=float, default=15, help="seconds per public GET")
    args = parser.parse_args(argv)
    if args.sweep < 1 or args.timeout <= 0 or not (args.trade_id or args.owner):
        parser.error("positive sweep and timeout, plus --trade-id or --owner, are required")
    try:
        result = audit(args.sweep, args.trade_id, args.owner, args.timeout)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"close-call audit unavailable: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
