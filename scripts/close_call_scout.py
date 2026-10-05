#!/usr/bin/env python3
"""Read-only, signed Close Call leaderboard and price-sensitivity scout.

The live PnL mark is the paper-trade VWAP, not the Hyperliquid reference or
the final settlement price. Score/mark sensitivity is observational; trades,
fees and changing positions can alter it. This tool neither signs nor trades.
"""

import argparse
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
FINAL_PRICE = re.compile(r"[0-9]{1,7}(?:\.[0-9]{1,2})?\Z")
FINAL_CUTOFF = dt.datetime(2026, 10, 4, 10, tzinfo=dt.timezone.utc)
LOCK_SWEEP = 2556


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


def parse_snapshot(room, snapshot, referee_did=REFEREE_DID, now=None, allow_stale=False):
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
            if type(body.get("age_s")) is not int or body["age_s"] < 0:
                raise ValueError("price record lacks a nonnegative signed reference age")
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
    if now.tzinfo is None:
        raise ValueError(f"{room}: comparison time lacks timezone")
    age = (now - stamp).total_seconds()
    if age < -30 or (not allow_stale and age > 600):
        raise ValueError(f"{room}: latest signed record is stale or future-dated")
    return result


def split_final_price_snapshot(snapshot, referee_did=REFEREE_DID,
                               expected_lock_sweep=LOCK_SWEEP):
    """Verify the referee's separate final-price post, retaining pre-lock sweeps.

    The final-price post fixes S but is not itself an account or standings post.
    """
    if (not isinstance(snapshot, dict) or snapshot.get("room") != "d-close1-price" or
            not isinstance(snapshot.get("messages"), list) or not snapshot["messages"]):
        raise ValueError("d-close1-price: malformed or empty snapshot")
    message = snapshot["messages"][-1]
    try:
        body = json.loads(message["text"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("d-close1-price: invalid final JSON") from exc
    if not isinstance(body, dict) or body.get("t") != "final":
        return snapshot, None
    if (len(snapshot["messages"]) < 2 or
            not isinstance(snapshot["messages"][-2], dict) or
            type(message.get("seq")) is not int or
            message["seq"] != snapshot.get("last_seq") or
            message["seq"] != snapshot["messages"][-2].get("seq", -2) + 1 or
            message.get("from") != referee_did or
            verify_record("d-close1-price", message)[0] != "verified" or
            body.get("season") != "close-1" or
            not isinstance(body.get("price"), str) or
            not FINAL_PRICE.fullmatch(body["price"]) or
            amount(body["price"]) <= 0 or
            not isinstance(body.get("trade"), dict) or
            type(body["trade"].get("tid")) is not int or
            body["trade"]["tid"] < 0):
        raise ValueError("d-close1-price: invalid signed final record")
    try:
        trade_time = dt.datetime.fromisoformat(body["trade"]["time"].replace("Z", "+00:00"))
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        raise ValueError("d-close1-price: invalid final trade time") from exc
    if (trade_time.tzinfo is None or
            not FINAL_CUTOFF - dt.timedelta(hours=1) <= trade_time < FINAL_CUTOFF):
        raise ValueError("d-close1-price: final trade time is outside closing window")
    previous = json.loads(snapshot["messages"][-2]["text"])
    if previous.get("n") != expected_lock_sweep or previous.get("t") != "price":
        raise ValueError("d-close1-price: final post does not follow lock sweep")
    prelock = dict(snapshot)
    prelock["messages"] = snapshot["messages"][:-1]
    prelock["last_seq"] = prelock["messages"][-1]["seq"]
    return prelock, {"S": body["price"], "trade": body["trade"],
                     "signed_room": "d-close1-price", "signed_seq": message["seq"],
                     "caution": "A signed final price is not a final standings or owner account statement."}


def split_final_standings_snapshot(snapshot, final_price, referee_did=REFEREE_DID,
                                   expected_lock_sweep=LOCK_SWEEP,
                                   owner_did=OWNER_DID):
    """Verify a separate signed top-25 final standings post, if present.

    The published leaders do not establish the exact rank or score of an owner
    outside that list; a complete owner-row artifact is still required.
    """
    if (not isinstance(snapshot, dict) or snapshot.get("room") != "d-close1-pnl" or
            not isinstance(snapshot.get("messages"), list) or not snapshot["messages"]):
        raise ValueError("d-close1-pnl: malformed or empty snapshot")
    message = snapshot["messages"][-1]
    try:
        body = json.loads(message["text"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("d-close1-pnl: invalid final standings JSON") from exc
    if not isinstance(body, dict) or body.get("t") != "standings":
        return snapshot, None
    if (len(snapshot["messages"]) < 2 or
            not isinstance(snapshot["messages"][-2], dict) or
            type(message.get("seq")) is not int or
            message["seq"] != snapshot.get("last_seq") or
            message["seq"] != snapshot["messages"][-2].get("seq", -2) + 1 or
            message.get("from") != referee_did or
            verify_record("d-close1-pnl", message)[0] != "verified" or
            body.get("season") != "close-1" or
            not isinstance(body.get("S"), str) or
            not FINAL_PRICE.fullmatch(body["S"]) or
            body["S"] != final_price or
            not isinstance(body.get("file"), str) or
            not HASH.fullmatch(body["file"]) or
            type(body.get("owners")) is not int or body["owners"] < 25 or
            amount(body.get("fees")) < 0 or
            amount(body.get("zero_sum")) != 0):
        raise ValueError("d-close1-pnl: invalid signed final standings")
    try:
        previous = json.loads(snapshot["messages"][-2]["text"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("d-close1-pnl: invalid prior sweep") from exc
    if previous.get("n") != expected_lock_sweep or previous.get("t") != "pnl":
        raise ValueError("d-close1-pnl: standings do not follow lock sweep")
    places, following = body.get("places"), body.get("next")
    if (not isinstance(places, list) or len(places) != 3 or
            not isinstance(following, list) or len(following) != 22):
        raise ValueError("d-close1-pnl: incomplete published final top 25")
    leaders = []
    for rank, row in enumerate(places, 1):
        if (not isinstance(row, list) or len(row) != 4 or
                not isinstance(row[2], list) or row[2] != [rank] or
                type(row[3]) is not int or row[3] < 1):
            raise ValueError("d-close1-pnl: malformed final podium")
        leaders.append(row[:2])
    leaders.extend(following)
    if (any(not isinstance(row, list) or len(row) != 2 or
            not isinstance(row[0], str) or not row[0].startswith("did:key:z") or
            not isinstance(row[1], str) for row in leaders) or
            len({row[0] for row in leaders}) != 25):
        raise ValueError("d-close1-pnl: malformed final top 25")
    scores = [amount(row[1]) for row in leaders]
    if scores != sorted(scores, reverse=True):
        raise ValueError("d-close1-pnl: unsorted final top 25")
    prelock = dict(snapshot)
    prelock["messages"] = snapshot["messages"][:-1]
    prelock["last_seq"] = prelock["messages"][-1]["seq"]
    owner_row = next(((rank, score) for rank, (did, score) in enumerate(leaders, 1)
                      if did == owner_did), None)
    return prelock, {"S": body["S"], "published_count": len(leaders),
                     "reported_owner_count": body["owners"],
                     "podium": [{"rank": rank, "did": did, "score": score}
                                for rank, (did, score) in enumerate(leaders[:3], 1)],
                     "owner_in_published_top_25": owner_row is not None,
                     "owner_published_rank": owner_row[0] if owner_row else None,
                     "owner_published_score": owner_row[1] if owner_row else None,
                     "signed_room": "d-close1-pnl", "signed_seq": message["seq"],
                     "full_file_hash": body["file"],
                     "caution": "Only 25 final rows are published here; an absent owner has no certified "
                                "exact rank, score, or account statement in this post."}


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


def aligned_rows(price, pnl, positions):
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
    return rows


def assess(price, pnl, positions, owner_did=OWNER_DID):
    rows = aligned_rows(price, pnl, positions)
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
    stale_sweeps = [row["n"] for row in rows if row["price"]["age_s"] >= 300]
    return {"status": "signed_live_scout", "sweep": last["n"],
            "observed_window_sweeps": [rows[0]["n"], last["n"]],
            "reference": str(latest_ref), "paper_vwap_mark": last["pnl"]["mark"],
            "signed_reference_age_seconds_at_sweep": last["price"]["age_s"],
            "reference_at_least_5min_stale_at_sweep": last["price"]["age_s"] >= 300,
            "observed_stale_reference_sweep_count": len(stale_sweeps),
            "last_observed_stale_reference_sweep": stale_sweeps[-1] if stale_sweeps else None,
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


def project_podium(price, pnl, positions, final_prices, optimistic_score, max_abs_position):
    """Stress-test a hypothetical static board, never predict the final standings.

    The owner gets a hindsight-perfect direction and pays no new fee. This is an
    upper bound for one static position, not an executable trading strategy.
    """
    rows = aligned_rows(price, pnl, positions)
    last = rows[-1]
    mark = amount(last["pnl"]["mark"])
    optimistic_score = amount(optimistic_score)
    max_abs_position = amount(max_abs_position)
    if max_abs_position <= 0 or not final_prices or len(final_prices) > 50:
        raise ValueError("projection needs 1-50 prices and a positive position bound")
    cohort = []
    for did, score in last["pnl"]["top"]:
        observed = sensitivity(rows, did, last["n"])
        if observed is None:
            raise ValueError("insufficient signed score/mark movements for every visible leader")
        cohort.append((amount(score), amount(observed["score_per_mark_unit"])))
    if len(cohort) < 3:
        raise ValueError("projection needs at least three visible leaders")
    scenarios = []
    for raw_price in final_prices:
        final_price = amount(raw_price)
        if final_price <= 0:
            raise ValueError("projected final price must be positive")
        change = final_price - mark
        projected_third = sorted((score + slope * change for score, slope in cohort),
                                 reverse=True)[2]
        optimistic_owner = optimistic_score + max_abs_position * abs(change)
        scenarios.append({"final_price": str(final_price),
                          "static_visible_third": str(projected_third.quantize(Decimal("0.01"))),
                          "optimistic_owner": str(optimistic_owner.quantize(Decimal("0.01"))),
                          "gap_to_third": str((projected_third - optimistic_owner).quantize(Decimal("0.01")))})
    return {"signed_sweep": last["n"], "board_mark": str(mark),
            "visible_cohort": len(cohort), "assumed_owner_score": str(optimistic_score),
            "assumed_max_abs_position": str(max_abs_position), "scenarios": scenarios,
            "caution": "Conditional static-board stress test only. Slopes are recent observed score/mark "
                       "sensitivities, not certified positions; all agents may trade. The owner score and "
                       "position bound are caller assumptions. The owner gets hindsight-perfect direction "
                       "with no new fees, so this is not an executable strategy or a forecast."}


def fetch(room, timeout=15):
    url = f"https://technocore.chat/r/{room}?format=json&limit=200"
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                  "User-Agent": "flop-agent-close-call-scout/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"{room}: snapshot exceeds bounded read limit")
    return json.loads(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-price", action="append", default=[],
                        help="sample a hypothetical final price; repeat up to 50 times")
    parser.add_argument("--optimistic-score", help="caller-assumed current score upper bound")
    parser.add_argument("--max-abs-position", help="caller-assumed static position bound")
    args = parser.parse_args(argv)
    if bool(args.final_price) != bool(args.optimistic_score and args.max_abs_position):
        parser.error("projections require --final-price, --optimistic-score and --max-abs-position")
    try:
        snapshots = [fetch(room) for room in ROOMS]
        snapshots[0], final = split_final_price_snapshot(snapshots[0])
        snapshots[1], standings = split_final_standings_snapshot(
            snapshots[1], final["S"] if final is not None else None)
        if standings is not None and final is None:
            raise ValueError("signed final standings lack a matching final-price post")
        parsed = [parse_snapshot(room, snapshot, allow_stale=final is not None)
                  for room, snapshot in zip(ROOMS, snapshots)]
        report = assess(*parsed)
        if final is not None:
            report["status"] = "signed_final_price_with_prelock_board"
            report["final"] = final
            report["caution"] += (" This board is the last pre-lock VWAP-marked top 25, "
                                  "not final standings.")
        if standings is not None:
            report["status"] = "signed_final_top25_with_prelock_board"
            report["final_standings"] = standings
            report["caution"] += (" The separate signed final standings post lists 25 owners; "
                                  "an owner outside it has no published exact score or place.")
        if args.final_price:
            if final is not None:
                raise ValueError("hypothetical projection is unavailable after the signed final")
            report["podium_projection"] = project_podium(
                *parsed, args.final_price, args.optimistic_score, args.max_abs_position)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"close-call scout unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
