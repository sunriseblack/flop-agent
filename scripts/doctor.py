#!/usr/bin/env python3
"""Read-only health check of a Technocore room and its Kibble projection."""

import argparse
import json
import math
import pathlib
import sys
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DID = json.loads((ROOT / "agent-did.json").read_text())["did"]
DEFAULT_KIBBLE_URL = "https://kibble.world"
MAX_JSON_BYTES = 4 * 1024 * 1024


def fetch(url, timeout):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "flop-agent-doctor/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError("JSON response exceeds byte bound")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("expected a JSON object")
        return payload, None
    except (OSError, ValueError, RecursionError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def fetch_floor(url, timeout):
    """Read the oldest retained export record without downloading the whole ring."""
    request = urllib.request.Request(url, headers={"Accept": "application/jsonl", "User-Agent": "flop-agent-doctor/2"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            line = response.readline(65536)
        if not line:
            return None, "empty export"
        return json.loads(line), None
    except (OSError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def number(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def cursor_inventory(responses):
    """Keep qualified metadata paths, never imply a shared cursor domain.

    Message/job arrays are not high-water marks and are intentionally omitted.
    """
    cursors, truncated = {}, False
    def walk(value, path, depth):
        nonlocal truncated
        if not isinstance(value, dict):
            return
        if depth > 8:
            truncated = True
            return
        for key, child in value.items():
            name = str(key)
            child_path = path + "." + name
            if name == "seq" or name.endswith(("_seq", "_cursor")):
                if len(cursors) >= 128:
                    truncated = True
                    return
                cursors[child_path] = number(child)
            if isinstance(child, dict):
                walk(child, child_path, depth + 1)
    for name, (payload, _) in responses.items():
        walk(payload, name, 0)
    return cursors, truncated


def assess(responses, max_lag, expected_did=None):
    """Assess fetched (payload, error) pairs without network access."""
    problems, observations, payloads = [], {}, {}
    for name in ("room", "status", "stats", "board", "score"):
        payload, error = responses[name]
        if error:
            problems.append(f"{name}: {error}")
        elif not isinstance(payload, dict):
            problems.append(f"{name}: expected a JSON object")
        else:
            payloads[name] = payload

    room = payloads.get("room", {})
    head = number(room.get("last_seq"))
    observations["room_head_seq"] = head
    observations["room_generation"] = number(room.get("generation"))
    if "room" in payloads and head is None:
        problems.append("room: missing integer last_seq")

    status = payloads.get("status", {})
    if "status" in payloads and (status.get("ok") is not True or not isinstance(status.get("origin"), dict) or status["origin"].get("ok") is not True):
        problems.append("status: API or origin is not healthy")

    stats = payloads.get("stats", {})
    origin = stats.get("origin") if isinstance(stats.get("origin"), dict) else {}
    engine, tape = number(origin.get("stats_engine_seq")), number(origin.get("tape_head_seq"))
    observations.update(stats_engine_seq=engine, stats_tape_head_seq=tape,
                        stats_engine_warm=origin.get("stats_engine_warm"),
                        agent_census_seq=number(origin.get("agent_census_seq")))
    if "stats" in payloads:
        if stats.get("ok") is not True or origin.get("ok") is not True:
            problems.append("stats: API or origin is not healthy")
        if origin.get("stats_engine_warm") is not True:
            problems.append("stats: scoring engine is not warm")
        if engine is None or tape is None:
            problems.append("stats: missing integer engine or tape cursor")

    if head is not None:
        for label, cursor in (("scoring engine", engine), ("stats tape", tape)):
            if cursor is None:
                continue
            gap = head - cursor
            observations[label.replace(" ", "_") + "_gap"] = gap
            if gap < 0:
                problems.append(f"{label}: cursor {cursor} numerically exceeds room head {head}; possible rewind or different ledger")
            elif gap > max_lag:
                problems.append(f"{label}: numeric difference {gap} exceeds limit {max_lag}; stale or non-comparable cursor metadata")

    if "floor" in responses:
        floor_record, error = responses["floor"]
        floor = number(floor_record.get("seq")) if isinstance(floor_record, dict) else None
        observations["room_retained_floor_seq"] = floor
        observations["room_retained_floor_ts"] = floor_record.get("ts") if isinstance(floor_record, dict) else None
        if error:
            problems.append(f"floor: {error}")
        elif floor is None:
            problems.append("floor: oldest export record lacks integer seq")
        else:
            if head is not None and floor > head:
                problems.append(f"floor: retained floor {floor} is ahead of room head {head}")
            for label, cursor in (("scoring engine", engine), ("stats tape", tape)):
                if cursor is not None and cursor < floor - 1:
                    missing = floor - 1 - cursor
                    problems.append(f"{label}: cursor {cursor} below retained native floor {floor}; if it is a native cursor, "
                                    f"{missing} intervening sequences are outside live replay; cursor domain is not bound")

    board = payloads.get("board", {})
    if "board" in payloads:
        if board.get("ok", True) is not True or not isinstance(board.get("jobs"), list):
            problems.append("board: job list unavailable or API not healthy")
        if board.get("engine_warm", True) is False:
            problems.append("board: engine is not warm")
        board_origin = board.get("origin") if isinstance(board.get("origin"), dict) else {}
        if board_origin.get("ok", True) is False:
            problems.append("board: origin is not healthy")
        if board_origin.get("stats_engine_warm", True) is False:
            problems.append("board: origin scoring engine is not warm")
        top_level_seq = number(board.get("engine_seq"))
        origin_seq = number(board_origin.get("stats_engine_seq"))
        board_seq = top_level_seq if top_level_seq is not None else origin_seq
        observations["board_engine_seq"] = board_seq
        observations["board_engine_seq_source"] = (
            "top_level" if top_level_seq is not None else "origin" if origin_seq is not None else None
        )
        observations["board_tape_last_seq"] = number(board_origin.get("tape_last_seq"))
        if board_seq is None:
            problems.append("board: missing integer engine sequence in board and origin")
        if top_level_seq is not None and origin_seq is not None and top_level_seq != origin_seq:
            problems.append(
                f"board: top-level engine sequence {top_level_seq} differs from origin {origin_seq}"
            )
        if board_seq is not None and engine is not None and board_seq != engine:
            problems.append(f"board: engine sequence {board_seq} differs from stats {engine}")
        if isinstance(board.get("jobs"), list):
            job_seqs = [seq for job in board["jobs"] if isinstance(job, dict)
                        if (seq := number(job.get("seq"))) is not None]
            max_job_seq = max(job_seqs, default=None)
            observations["board_max_job_seq"] = max_job_seq
            if max_job_seq is not None and board_seq is not None and max_job_seq > board_seq:
                problems.append(
                    f"board: published job sequence {max_job_seq} exceeds reported engine sequence {board_seq}; "
                    "cursor coverage is ambiguous"
                )

    score = payloads.get("score", {})
    if "score" in payloads:
        if score.get("ok") is not True or score.get("engine_warm") is not True:
            problems.append("score: API or engine is not healthy")
        score_seq = number(score.get("engine_seq"))
        observations.update(score_engine_seq=score_seq, did_found=score.get("found"), did_score=score.get("score"))
        observations["score_did"] = score.get("did")
        observations["score_identity_matches"] = None if expected_did is None else score.get("did") == expected_did
        if expected_did is not None and score.get("did") != expected_did:
            problems.append("score: wrong or missing requested DID")
        breakdown = score.get("breakdown")
        if (isinstance(breakdown, dict) and number(score.get("score")) is not None
                and number(breakdown.get("score")) is not None and score["score"] != breakdown["score"]):
            problems.append("score: account score differs from breakdown score")
        if score_seq is None:
            problems.append("score: missing integer engine sequence")
        elif engine is not None and score_seq != engine:
            problems.append(f"score: engine sequence {score_seq} differs from stats {engine}")

    cursors, truncated = cursor_inventory(responses)
    observations["reported_cursor_metadata"] = cursors
    observations["cursor_inventory_truncated"] = truncated
    if truncated:
        problems.append("metadata: cursor inventory exceeds structural bound")
    return {"healthy": not problems, "observations": observations, "problems": problems,
            "evidence_scope": {"native_to_host_cursor_mapping": "not_established",
                               "legacy_gap_fields": "numeric differences, not verified processing lag",
                               "credit_for_submission": "not_determined",
                               "healthy_means": "no diagnostic flags observed, not certified coverage or acceptance"}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room-url", default="https://technocore.chat/r/kibble")
    parser.add_argument("--kibble-url", default=DEFAULT_KIBBLE_URL)
    parser.add_argument("--did", default=DEFAULT_DID)
    parser.add_argument("--timeout", type=float, default=8.0, help="seconds per request")
    parser.add_argument("--max-lag", type=int, default=1000, help="maximum message gap")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.max_lag < 0:
        parser.error("--timeout must be finite and positive and --max-lag nonnegative")
    base = args.kibble_url.rstrip("/")
    urls = {
        "status": base + "/api/status",
        "stats": base + "/api/stats",
        "board": base + "/api/board?limit=1",
        "score": base + "/api/score?" + urllib.parse.urlencode({"did": args.did}),
    }
    responses = {name: fetch(url, args.timeout) for name, url in urls.items()}
    responses["floor"] = fetch_floor(args.room_url.rstrip("/") + "/export", args.timeout)
    # Read the independent head last. On a busy room, reading it first can
    # make a later scorer cursor look falsely ahead of the sampled head.
    responses["room"] = fetch(args.room_url.rstrip("/") + "?format=json&limit=1", args.timeout)
    result = assess(responses, args.max_lag, expected_did=args.did)
    result["endpoints"] = {name: {"ok": error is None, "error": error} for name, (_, error) in responses.items()}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Kibble read-only doctor: " + ("HEALTHY" if result["healthy"] else "UNHEALTHY"))
        for key, value in result["observations"].items():
            print(f"  {key}: {value}")
        for problem in result["problems"]:
            print(f"  ! {problem}")
    return 0 if result["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
