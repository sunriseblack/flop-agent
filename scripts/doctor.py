#!/usr/bin/env python3
"""Read-only health check of a Technocore room and its Kibble projection."""

import argparse
import json
import pathlib
import sys
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DID = json.loads((ROOT / "agent-did.json").read_text())["did"]


def fetch(url, timeout):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "flop-agent-doctor/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), None
    except (OSError, ValueError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def number(value):
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def assess(responses, max_lag):
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
                problems.append(f"{label}: cursor {cursor} is ahead of room head {head}; possible rewind")
            elif gap > max_lag:
                problems.append(f"{label}: {gap} messages behind room head (limit {max_lag})")

    board = payloads.get("board", {})
    if "board" in payloads:
        if board.get("ok", True) is not True or not isinstance(board.get("jobs"), list):
            problems.append("board: job list unavailable or API not healthy")
        if board.get("engine_warm", True) is False:
            problems.append("board: engine is not warm")
        board_seq = number(board.get("engine_seq"))
        observations["board_engine_seq"] = board_seq
        if board_seq is not None and engine is not None and board_seq != engine:
            problems.append(f"board: engine sequence {board_seq} differs from stats {engine}")

    score = payloads.get("score", {})
    if "score" in payloads:
        if score.get("ok") is not True or score.get("engine_warm") is not True:
            problems.append("score: API or engine is not healthy")
        score_seq = number(score.get("engine_seq"))
        observations.update(score_engine_seq=score_seq, did_found=score.get("found"), did_score=score.get("score"))
        if score_seq is None:
            problems.append("score: missing integer engine sequence")
        elif engine is not None and score_seq != engine:
            problems.append(f"score: engine sequence {score_seq} differs from stats {engine}")

    return {"healthy": not problems, "observations": observations, "problems": problems}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room-url", default="https://technocore.chat/r/kibble")
    parser.add_argument("--kibble-url", default="https://flop-kibble.onrender.com")
    parser.add_argument("--did", default=DEFAULT_DID)
    parser.add_argument("--timeout", type=float, default=8.0, help="seconds per request")
    parser.add_argument("--max-lag", type=int, default=1000, help="maximum message gap")
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.max_lag < 0:
        parser.error("--timeout must be positive and --max-lag nonnegative")
    base = args.kibble_url.rstrip("/")
    urls = {
        "status": base + "/api/status",
        "stats": base + "/api/stats",
        "board": base + "/api/board?limit=1",
        "score": base + "/api/score?" + urllib.parse.urlencode({"did": args.did}),
        # Read the independent head last. On a busy room, reading it first can
        # make a later scorer cursor look falsely ahead of the sampled head.
        "room": args.room_url.rstrip("/") + "?format=json&limit=1",
    }
    responses = {name: fetch(url, args.timeout) for name, url in urls.items()}
    result = assess(responses, args.max_lag)
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
