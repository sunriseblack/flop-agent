#!/usr/bin/env python3
"""Read-only, signed Close Call leaderboard and price-sensitivity scout.

The live PnL mark is the paper-trade VWAP, not the Hyperliquid reference or
the final settlement price. Score/mark sensitivity is observational; trades,
fees and changing positions can alter it. This tool neither signs nor trades.
"""

import datetime as dt
import json
import re
import statistics
import sys
import urllib.request
from decimal import Decimal, InvalidOperation

from audit_close_call import REFEREE_DID
from verify_tape import verify_record


ROOMS = ("d-close1-price", "d-close1-pnl", "d-close1-positions")
OWNER_DID = "did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv"
MAX_BYTES = 2_000_000
HASH = re.compile(r"[0-9a-f]{64}\Z")


def amount(value):
    if not isinstance(value, str):
        raise ValueError("amount is not a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal amount") from exc
    if not result.is_finite():
        raise ValueError("nonfinite decimal amount")
    return result


def parse_snapshot(room, snapshot, referee_did=REFEREE_DID, now=None):
    if (room not in ROOMS or not isinstance(snapshot, dict) or
            snapshot.get("room") != room or
            not isinstance(snapshot.get("messages"), list) or
            type(snapshot.get("last_seq")) is not int or
            not snapshot["messages"]):
        raise ValueError(f"{room}: malformed or empty snapshot")
    expected = room.removeprefix("d-close1-")
    result = {}
    previous_seq = None
    previous_n = None
    for message in snapshot["messages"]:
        if (not isinstance(message, dict) or
                type(message.get("seq")) is not int or
                (previous_seq is not None and message["seq"] != previous_seq + 1) or
                message.get("from") != referee_did or
                verify_record(room, message)[0] != "verified"):
            raise ValueError(f"{room}: unsigned, wrong-author, or gapped record")
        try:
            body = json.loads(message["text"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{room}: invalid JSON body") from exc
        if (not isinstance(body, dict) or body.get("t") != expected or
                type(body.get("n")) is not int or body["n"] < 1 or
                not isinstance(body.get("file"), str) or
                not HASH.fullmatch(body["file"]) or
                (previous_n is not None and body["n"] != previous_n + 1) or
                body["n"] in result):
            raise ValueError(f"{room}: malformed or gapped sweep")
        if room == "d-close1-price":
            if not isinstance(body.get("ref"), dict):
                raise ValueError("price record lacks reference")
            if amount(body["ref"].get("px")) <= 0 or amount(body.get("global")) <= 0:
                raise ValueError("price record contains a nonpositive price")
        else:
            top = body.get("top")
            if (not isinstance(top, list) or
                    any(not isinstance(pair, list) or len(pair) != 2 or
                        not isinstance(pair[0], str) or
                        not pair[0].startswith("did:key:z") or
                        not isinstance(pair[1], str) for pair in top) or
                    len({pair[0] for pair in top}) != len(top)):
                raise ValueError(f"{room}: malformed top list")
            for _, value in top:
                amount(value)
            if room == "d-close1-pnl":
                amount(body.get("mark"))
        try:
            stamp = dt.datetime.fromisoformat(message["ts"].replace("Z", "+00:00"))
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ValueError(f"{room}: malformed timestamp") from exc
        if stamp.tzinfo is None:
            raise ValueError(f"{room}: timestamp lacks timezone")
        result[body["n"]] = body
        previous_seq = message["seq"]
        previous_n = body["n"]
    if previous_seq != snapshot.get("last_seq"):
        raise ValueError(f"{room}: last sequence does not match room head")
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    if now.tzinfo is None or not -30 <= (now - stamp).total_seconds() <= 600:
        raise ValueError(f"{room}: latest signed record is stale or future-dated")
    return result


def score_for(body, did):
    for key, value in body["top"]:
        if key == did:
            return amount(value)
    return None


def sensitivity(rows, did, end_n, sample_count=12):
    """Median adjacent signed score/mark changes; never an account statement."""
    samples = []
    for earlier, later in zip(rows, rows[1:]):
        if later["n"] > end_n:
            break
        first = score_for(earlier["pnl"], did)
        second = score_for(later["pnl"], did)
        delta_mark = amount(later["pnl"]["mark"]) - amount(earlier["pnl"]["mark"])
        if first is None or second is None or abs(delta_mark) < Decimal("0.25"):
            continue
        samples.append((later["n"], (second - first) / delta_mark))
    recent = samples[-sample_count:]
    if len(recent) < 3:
        return None
    return {"from_sweep": recent[0][0], "through_sweep": recent[-1][0],
            "samples": len(recent), "score_per_mark_unit":
                str(statistics.median(value for _, value in recent).quantize(Decimal("0.01")))}


def assess(price, pnl, positions, owner_did=OWNER_DID):
    shared = sorted(set(price) & set(pnl) & set(positions))
    if len(shared) < 4 or shared[-1] < max(max(price), max(pnl), max(positions)) - 1:
        raise ValueError("price, PnL, and positions have no fresh common sweep")
    rows = []
    for n in shared:
        records = (price[n], pnl[n], positions[n])
        if len({record["file"] for record in records}) != 1:
            raise ValueError(f"sweep {n}: referee file hashes disagree")
        if amount(price[n]["global"]) != amount(pnl[n]["mark"]):
            raise ValueError(f"sweep {n}: PnL mark differs from global VWAP")
        rows.append({"n": n, "price": price[n], "pnl": pnl[n], "positions": positions[n]})
    last = rows[-1]
    leaders = last["pnl"]["top"]
    if len(leaders) < 3:
        raise ValueError("latest signed board has fewer than three owners")
    long_top = {did: qty for did, qty in last["positions"]["top"]}
    leader_rows = []
    for did, score in leaders[:4]:
        leader_rows.append({"did": did, "score": score,
                            "signed_top_long_qty": long_top.get(did),
                            "observed_score_mark_sensitivity": sensitivity(rows, did, last["n"])})
    transitions = []
    for did, _ in leaders[:4]:
        for earlier, later in zip(rows, rows[1:]):
            earlier_long = dict(earlier["positions"]["top"]).get(did)
            later_long = dict(later["positions"]["top"]).get(did)
            if earlier_long is not None and later_long is None:
                transitions.append({"did": did, "after_sweep": earlier["n"],
                                    "first_absent_sweep": later["n"],
                                    "previous_signed_top_long_qty": earlier_long,
                                    "caution": "Leaving the top-long list does not by itself prove a short."})
    refs = [amount(row["price"]["ref"]["px"]) for row in rows]
    latest_ref = refs[-1]
    return {"status": "signed_live_scout", "sweep": last["n"],
            "observed_window_sweeps": [rows[0]["n"], last["n"]],
            "reference": str(latest_ref), "paper_vwap_mark": last["pnl"]["mark"],
            "owner_in_top_25": any(did == owner_did for did, _ in leaders),
            "owner_visible_score": next((score for did, score in leaders if did == owner_did), None),
            "visible_board_count": len(leaders),
            "visible_board_floor_score": leaders[-1][1],
            "leaders": leader_rows,
            "recent_top_long_exits": transitions[-6:],
            "observed_ref_range": str(max(refs) - min(refs)),
            "round_trip_base_fee_per_contract_at_ref": str((latest_ref * Decimal("0.02")).quantize(Decimal("0.01"))),
            "caution": "Top lists are truncated; observed score/mark sensitivity is not a certified position, "
                       "cash balance, settlement, or forecast. Historical range is not a future profit opportunity."}


def fetch(room, timeout=15):
    url = f"https://technocore.chat/r/{room}?format=json&limit=200"
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                  "User-Agent": "flop-agent-close-call-scout/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"{room}: snapshot exceeds bounded read limit")
    return json.loads(raw)


def main():
    try:
        parsed = [parse_snapshot(room, fetch(room)) for room in ROOMS]
        report = assess(*parsed)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"close-call scout unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
