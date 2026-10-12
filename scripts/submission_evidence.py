#!/usr/bin/env python3
"""Preserve and inspect signed submission evidence without inferring score credit.

Offline by default. --seq collects public, read-only native/host snapshots.
No private key is loaded and no message is posted or replayed.
"""

import argparse
import collections
import concurrent.futures
import datetime
import hashlib
import json
import math
import pathlib
import re
import sys
import urllib.parse
import urllib.request

from verify_tape import verify_record


SCHEMA = "flop-submission-evidence-v1"
ROOM = re.compile(r"[A-Za-z0-9_-]+\Z")
EVENT = re.compile(r"^(JOB|CLAIM|RESULT|ATTEST) v1 \| (k[0-9a-f]{10})(?: \| |$)")
SIGNED_FIELDS = ("from", "text", "sig")
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_EXPORT_BYTES = 32 * 1024 * 1024
MAX_PACKET_BYTES = 8 * 1024 * 1024


def strict_json(raw):
    # Ambiguous duplicate fields can be interpreted differently by reviewers.
    # Nonfinite numbers are not JSON and must not leak into an evidence report.
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result
    def reject_constant(value):
        raise ValueError("nonfinite JSON number")
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def integer(value):
    return value if type(value) is int else None


def same_signed_content(left, right):
    return (isinstance(left, dict) and isinstance(right, dict)
            and all(left.get(key) == right.get(key) for key in SIGNED_FIELDS)
            and str(left.get("nonce")) == str(right.get("nonce")))


def inspect_readback(room, record, snapshot):
    if snapshot is None:
        return {"state": "not_supplied"}
    if (not isinstance(snapshot, dict) or snapshot.get("room") != room
            or not isinstance(snapshot.get("messages"), list)):
        return {"state": "malformed_or_wrong_room"}
    messages = snapshot["messages"]
    counts = collections.Counter(verify_record(room, item)[0] for item in messages)
    matching = [item for item in messages if same_signed_content(record, item)
                and verify_record(room, item)[0] == "verified"]
    seqs = [integer(item.get("seq")) if isinstance(item, dict) else None for item in messages]
    contiguous = (bool(seqs) and all(seq is not None and seq >= 1 for seq in seqs)
                  and all(b == a + 1 for a, b in zip(seqs, seqs[1:])))
    target_seq = integer(record.get("seq"))
    if len(matching) > 1:
        state = "ambiguous_duplicate_signed_content"
    elif len(matching) == 1:
        state = ("exact_fields_match_in_supplied_snapshot" if target_seq is not None and target_seq >= 1
                 and target_seq == integer(matching[0].get("seq"))
                 else "signed_content_at_different_or_missing_sequence")
    elif target_seq is not None and any(isinstance(item, dict) and item.get("seq") == target_seq for item in messages):
        state = "sequence_content_conflict"
    else:
        state = "not_observed_in_supplied_window"
    head = integer(snapshot.get("last_seq"))
    return {
        "state": state, "signed_content_matches": len(matching),
        "signature_counts": dict(counts), "records": len(messages),
        "stored_sequence_contiguous": contiguous,
        "window_floor": seqs[0] if seqs else None,
        "window_tip": seqs[-1] if seqs else None,
        "reported_head": head, "reported_generation": snapshot.get("generation"),
        "window_reaches_reported_head": bool(contiguous and head is not None and seqs[-1] >= head),
        "metadata_binding": "sequence, timestamps, generation and head are unsigned server metadata",
    }


def inspect_board(board, job_id):
    if board is None:
        return {"state": "not_supplied"}
    if not isinstance(board, dict) or board.get("ok", True) is not True or not isinstance(board.get("jobs"), list):
        return {"state": "unavailable_or_malformed"}
    origin = board.get("origin") if isinstance(board.get("origin"), dict) else {}
    matches = [row for row in board["jobs"] if isinstance(row, dict)
               and job_id is not None and row.get("id") == job_id]
    return {
        "state": "matching_row_observed" if len(matches) == 1 else
                 "ambiguous_duplicate_rows" if len(matches) > 1 else
                 "not_observed_in_supplied_board" if job_id else "no_job_id_in_submission",
        "matching_rows": matches,
        "engine_seq": integer(board.get("engine_seq")),
        "origin_engine_seq": integer(origin.get("stats_engine_seq")),
        "origin_tape_last_seq": integer(origin.get("tape_last_seq")),
        "origin_ok": origin.get("ok"),
        "coverage": "not_established_across_native_and_host_ledgers",
    }


def inspect_score(score, did):
    if score is None:
        return {"state": "not_supplied"}
    if not isinstance(score, dict) or score.get("ok") is not True:
        return {"state": "unavailable_or_malformed"}
    if score.get("did") != did:
        return {"state": "wrong_or_missing_did"}
    return {
        "state": "account_snapshot_observed", "did": did,
        "found": score.get("found"), "score": score.get("score"),
        "breakdown": score.get("breakdown"), "drops": score.get("drops"),
        "engine_warm": score.get("engine_warm"),
        "engine_seq": integer(score.get("engine_seq")),
        "attribution": "aggregate account snapshot does not identify credit for this submission",
    }


def assess_packet(packet, expected_did=None):
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise ValueError("unsupported evidence packet schema")
    room = packet.get("room")
    if not isinstance(room, str) or not ROOM.fullmatch(room):
        raise ValueError("invalid room")
    record = packet.get("submission")
    status, reason = verify_record(room, record)
    identity_matches = expected_did is None or (isinstance(record, dict) and record.get("from") == expected_did)
    verified = status == "verified" and identity_matches
    event = EVENT.match(record.get("text", "")) if verified else None
    job_id = event.group(2) if event else None
    digest = (hashlib.sha256(f"{room}|{record['nonce']}|{record['text']}".encode()).hexdigest()
              if verified else None)
    result = {
        "schema": SCHEMA, "room": room,
        "submission": {"signature_status": status, "reason": reason,
                       "expected_did_matches": identity_matches,
                       "signed_payload_sha256": digest,
                       "unsigned_sequence": record.get("seq") if isinstance(record, dict) else None,
                       "event": event.group(1) if event else None, "job_id": job_id},
        "evidence_verified": verified,
        "credit_for_submission": "not_determined",
        "cautions": [
            "A signature proves the exact room/nonce/text and key possession, not delivery, useful work or credit.",
            "Supplied snapshots and collection URLs are not cryptographic attestations by the server.",
            "No native-to-host cursor mapping is assumed; an absent row or zero score is not rejection.",
            "A matching board row or aggregate score is not per-submission credit or a FLOP allocation.",
            "If a write was uncertain, inspect existing records; this tool never reposts it.",
        ],
    }
    # Do not attach another account's score/board to an invalid or wrong-owner receipt.
    if verified:
        result["native_readback"] = inspect_readback(room, record, packet.get("native_readback"))
        result["host_board"] = inspect_board(packet.get("host_board"), job_id)
        result["host_score"] = inspect_score(packet.get("host_score"), record["from"])
        result["collection"] = packet.get("collection")
        collection = packet.get("collection")
        if isinstance(collection, dict):
            for name in ("host_board", "host_score"):
                source = collection.get(name)
                if packet.get(name) is None and isinstance(source, dict) and source.get("error"):
                    result[name] = {"state": "collection_failed", "error": source["error"]}
    return result


def inspect_artifact(path, record, expected_hash=None):
    if expected_hash is not None and not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ValueError("expected artifact hash must be 64 lowercase hexadecimal digits")
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    text = record.get("text", "") if isinstance(record, dict) else ""
    mentioned = bool(re.search(r"(?<![0-9a-fA-F])" + actual + r"(?![0-9a-fA-F])", text))
    return {"sha256": actual, "expected_hash_matches": None if expected_hash is None else actual == expected_hash,
            "hash_mentioned_in_signed_text": mentioned,
            "caution": "A matching hash identifies bytes, not artifact safety, quality, or scorer acceptance."}


def get_json(url, timeout):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "flop-submission-evidence/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("JSON response exceeds byte bound")
    return strict_json(raw)


def get_export(room, timeout):
    url = "https://technocore.chat/r/" + room + "/export"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "flop-submission-evidence/1"}), timeout=timeout) as response:
        raw = response.read(MAX_EXPORT_BYTES + 1)
        generation = response.headers.get("X-Room-Generation")
    if len(raw) > MAX_EXPORT_BYTES:
        raise ValueError("export exceeds byte bound")
    return [strict_json(line) for line in raw.splitlines() if line.strip()], generation


def collect_packet(room, seq, timeout):
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    base = "https://technocore.chat/r/" + room
    url = base + "?format=json&limit=200"
    snapshot = get_json(url, timeout)
    if (not isinstance(snapshot, dict) or snapshot.get("room") != room
            or not isinstance(snapshot.get("messages"), list)):
        raise ValueError("malformed native snapshot")
    matches = [r for r in snapshot["messages"] if isinstance(r, dict) and r.get("seq") == seq]
    used_export = False
    if not matches:
        records, generation = get_export(room, timeout)
        if str(snapshot.get("generation")) != generation:
            raise ValueError("native generation changed or export generation is missing")
        indexes = [i for i, r in enumerate(records) if isinstance(r, dict) and r.get("seq") == seq]
        if len(indexes) == 1:
            index = indexes[0]
            snapshot = {**snapshot, "messages": records[max(0, index - 99):index + 101]}
            matches = [records[index]]
            used_export = True
    if len(matches) != 1 or verify_record(room, matches[0])[0] != "verified":
        raise ValueError("exact signed receipt unavailable in retained native window; use a previously saved packet, never repost")
    record = matches[0]
    packet = {"schema": SCHEMA, "room": room, "submission": record,
              "native_readback": snapshot,
              "collection": {"native_url": base + "/export" if used_export else url,
                             "export_fallback_used": used_export,
                             "started_at": started_at}}
    if room == "kibble":
        urls = {"host_board": "https://kibble.world/api/board?limit=1",
                "host_score": "https://kibble.world/api/score?" + urllib.parse.urlencode({"did": record["from"]})}
        def read(item):
            name, host_url = item
            try:
                return name, get_json(host_url, timeout), None
            except (OSError, ValueError) as exc:
                return name, None, f"{type(exc).__name__}: {exc}"
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for name, payload, error in pool.map(read, urls.items()):
                packet[name] = payload
                packet["collection"][name] = {"url": urls[name], "error": error}
    packet["collection"]["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="inspect a saved packet entirely offline")
    source.add_argument("--seq", type=int, help="collect an existing native room record, read-only")
    parser.add_argument("--room", default="kibble")
    parser.add_argument("--did", help="require this submitter DID")
    parser.add_argument("--output", help="save the collected packet exclusively; never overwrite")
    parser.add_argument("--artifact", help="hash a local artifact without including its contents")
    parser.add_argument("--expected-artifact-sha256")
    parser.add_argument("--timeout", type=float, default=12)
    args = parser.parse_args(argv)
    if (not ROOM.fullmatch(args.room) or not math.isfinite(args.timeout) or args.timeout <= 0
            or (args.seq is not None and args.seq < 1)
            or (args.expected_artifact_sha256 and not args.artifact)
            or (args.output and args.file)):
        parser.error("invalid room, sequence, timeout, artifact options or output with offline input")
    try:
        if args.output and pathlib.Path(args.output).exists():
            raise ValueError("output already exists; refusing to overwrite preserved evidence")
        if args.file:
            with open(args.file, "rb") as source_file:
                raw = source_file.read(MAX_PACKET_BYTES + 1)
            if len(raw) > MAX_PACKET_BYTES:
                raise ValueError("saved packet exceeds byte bound")
            packet = strict_json(raw)
        else:
            packet = collect_packet(args.room, args.seq, args.timeout)
        result = assess_packet(packet, args.did)
        if args.artifact:
            if not result["evidence_verified"]:
                raise ValueError("cannot associate artifact with an unverified or wrong-owner submission")
            result["artifact"] = inspect_artifact(args.artifact, packet["submission"], args.expected_artifact_sha256)
        if args.output and result["evidence_verified"]:
            with open(args.output, "x", encoding="utf-8") as output:
                json.dump(packet, output, indent=2, ensure_ascii=False)
                output.write("\n")
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
        artifact_bad = result.get("artifact", {}).get("expected_hash_matches") is False
        return 0 if result["evidence_verified"] and not artifact_bad else 1
    except (OSError, ValueError) as exc:
        print(f"Submission evidence unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
