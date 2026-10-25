#!/usr/bin/env python3
"""Offline Python/Node and saved-transport checks using existing signed records.

No network, signing, new records or external model commands. Missing transports
stay untested; derived mutations are controls, never original server evidence.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import inference_readiness as private
from submission_evidence import assess_packet, inspect_readback, same_signed_content, strict_json
from verify_tape import verify_record


MAX_BYTES = 32 * 1024 * 1024
MAX_RECORDS = 100000


def read_bytes(path, maximum=MAX_BYTES):
    with Path(path).open("rb") as source:
        raw = source.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("input exceeds byte bound")
    return raw


def parse_transport(raw, kind, room):
    """Read explicit formats only; never scrape missing signed fields from prose."""
    if kind == "export":
        records = []
        for line in raw.splitlines():
            if line.strip():
                if len(records) >= MAX_RECORDS:
                    raise ValueError("export record bound exceeded")
                records.append(strict_json(line))
        if not all(isinstance(r, dict) for r in records):
            raise ValueError("export rows must be objects")
        return {"room": room, "messages": records}, "parsed_jsonl"
    value = strict_json(raw)
    if kind == "mcp":
        if not isinstance(value, dict) or value.get("isError", False) is not False:
            raise ValueError("MCP error or invalid result")
        blocks = value.get("content")
        if (not isinstance(blocks, list) or len(blocks) != 1 or not isinstance(blocks[0], dict)
                or blocks[0].get("type") != "text" or not isinstance(blocks[0].get("text"), str)):
            raise ValueError("require one exact MCP text result, not ambiguous blocks")
        try:
            value = strict_json(blocks[0]["text"])
        except ValueError:
            if blocks[0]["text"].lstrip().startswith(("{", "[")):
                raise ValueError("malformed or ambiguous MCP JSON text") from None
            return None, "text_projection_not_reverifiable"
    if (not isinstance(value, dict) or value.get("room") != room
            or not isinstance(value.get("messages"), list) or len(value["messages"]) > MAX_RECORDS):
        raise ValueError("wrong-room or invalid snapshot")
    return value, "parsed_json"


def cases_for(room, records):
    cases = []
    for i, record in enumerate(records):
        if verify_record(room, record)[0] != "verified":
            raise ValueError("case source must be an existing verifiable record")
        base = {"id": f"record-{i}", "room": room, "record": record}
        cases.append(base)
        nonce = int(record["nonce"])
        changed_nonce = nonce - 1 if nonce == 10**19 - 1 else nonce + 1
        for label, key, value in (("text-tamper", "text", record["text"] + " e\u0301"),
                                  ("nonce-tamper", "nonce", str(changed_nonce)),
                                  ("metadata-relabel", "seq", 777),
                                  ("decimal-string", "nonce", str(record["nonce"]))):
            cases.append({**base, "id": base["id"] + "/" + label, "record": {**record, key: value}})
        cases.append({**base, "id": base["id"] + "/room-tamper", "room": room + "-changed"})
    return cases


def check(packet, transports, node_runner=None):
    base = assess_packet(packet)
    if not base["evidence_verified"]:
        raise ValueError("packet's original signature must verify")
    room, record = packet["room"], packet["submission"]
    records, rows = [record], []
    for kind, raw in transports.items():
        snapshot, state = parse_transport(raw, kind, room)
        row = {"transport": kind, "input_sha256": hashlib.sha256(raw).hexdigest(), "parse_state": state,
               "scope": "caller-supplied capture; collection provenance is not authenticated"}
        if snapshot is not None:
            row["readback"] = inspect_readback(room, record, snapshot)
            matching = [r for r in snapshot["messages"] if same_signed_content(record, r)]
            row["target_signed_content_present"] = bool(matching)
            # Choose at most four extra real signed rows, preferring Unicode and
            # unsafe JavaScript integers. Nothing is signed or posted for coverage.
            candidates = [r for r in snapshot["messages"] if verify_record(room, r)[0] == "verified"]
            candidates.sort(key=lambda r: (not any(ord(c) > 127 for c in r["text"]),
                                           int(r["nonce"]) <= 2**53 - 1))
            for item in candidates:
                if len(records) >= 5:
                    break
                if not any(same_signed_content(item, old) for old in records):
                    records.append(item)
        rows.append(row)
    cases = cases_for(room, records)
    raw = json.dumps({"schema": "flop-cross-client-cases-v1", "cases": cases},
                     ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()
    if len(raw) > private.MAX_BYTES:
        raise ValueError("cross-client case packet exceeds byte bound")
    python = [{"id": c["id"], "status": verify_record(c["room"], c["record"])[0]} for c in cases]
    # Check Python's escaped and raw UTF-8 JSON round trips separately.
    escaped = strict_json(json.dumps({"cases": cases}, ensure_ascii=True))
    if [verify_record(c["room"], c["record"])[0] for c in escaped["cases"]] != [r["status"] for r in python]:
        raise ValueError("Python JSON round-trip changed classifications")
    runner = Path(__file__).resolve().parents[1] / "examples/verify-records-crosscheck.mjs"
    if node_runner is None:
        node = shutil.which("node")
        if node is None:
            raise ValueError("Node is required; no parity result is inferred without it")
        proc = subprocess.run([node, str(runner)], input=raw, capture_output=True, timeout=20)
        if proc.returncode or len(proc.stdout) > private.MAX_BYTES:
            raise ValueError("Node cross-check failed; use a runtime with JSON source-token support")
        other = strict_json(proc.stdout)
    else:
        other = node_runner(raw)  # Unit-test seam, never taken from input/CLI.
    if other.get("input_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("Node checked a different case packet")
    observed = [{"id": r["id"], "status": r["status"]} for r in other["results"]]
    if observed != python:
        raise ValueError("Python/Node signature classification mismatch")
    if any(r["ordinary_parse_status"] != "invalid" for r in other["results"] if r["ordinary_parse_unsafe_nonce"]):
        raise ValueError("unsafe ordinary JSON numeric nonce was not rejected")
    # Reuse original signatures to demonstrate unsigned metadata/recovery limits.
    one = {"room": room, "generation": 0, "last_seq": 100, "messages": [{**record, "seq": 100}]}
    missing = {**one, "messages": []}
    gap = {**one, "last_seq": 102, "messages": [one["messages"][0], {**record, "seq": 102}]}
    limits = {
        "missing_record": inspect_readback(room, record, missing)["state"],
        "derived_internal_gap_contiguous": inspect_readback(room, record, gap)["stored_sequence_contiguous"],
        "relabelled_generation_signature": verify_record(room, record)[0],
        "generation_authenticity": "not_established_by_message_signature",
        "edge_drop_completeness": "not_established_when_returned_bounds_move",
        "recovery": "Expired original fields cannot be reconstructed by a signature or report",
    }
    return {"schema": "flop-cross-client-report-v1", "room": room,
            "source_signed_payload_sha256": base["submission"]["signed_payload_sha256"],
            "python": sys.version.split()[0], "node": other["node"],
            "supplied_signed_records_checked": len(records), "unicode_signed_records": sum(any(ord(c) > 127 for c in r["text"]) for r in records),
            "unsafe_numeric_source_records": sum(type(r["nonce"]) is int and r["nonce"] > 2**53 - 1 for r in records),
            "derived_cases": len(cases), "case_packet_sha256": hashlib.sha256(raw).hexdigest(),
            "python_node_classifications_match": True, "python_escaped_utf8_roundtrip_match": True,
            "ordinary_parse_unsafe_nonce_cases": sum(r["ordinary_parse_unsafe_nonce"] for r in other["results"]),
            "transports": rows, "untested_transports": [k for k in ("json", "export", "mcp") if k not in transports],
            "unverifiable_transports": [r["transport"] for r in rows if r["parse_state"] == "text_projection_not_reverifiable"],
            "live_mcp_protocol": "not_established",
            "derived_metadata_controls": limits, "credit_for_submission": "not_determined",
            "caution": "Our execution is compatibility evidence, not independent adoption, live MCP coverage, trusted generation, complete history, recovery, policy authorization or settlement. Mutated records are offline controls, not captured originals."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--json-view")
    parser.add_argument("--export")
    parser.add_argument("--mcp-result")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        target = private.private_path(args.output)
        if target.exists():
            raise ValueError("output already exists")
        packet = strict_json(read_bytes(args.packet, 8 * 1024 * 1024))
        inputs = {key: read_bytes(path) for key, path in
                  (("json", args.json_view), ("export", args.export), ("mcp", args.mcp_result)) if path}
        report = check(packet, inputs)
        private.save(args.output, report)
        print(json.dumps({"output": args.output, "supplied_signed_records_checked": report["supplied_signed_records_checked"],
                          "python_node_classifications_match": True, "untested_transports": report["untested_transports"]}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"compatibility unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
