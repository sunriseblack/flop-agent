#!/usr/bin/env python3
"""Prepare or post one bounded Close Call paper offer with the existing DID.

Dry-run is the default. Posting requires --post and an explicit unique trade ID.
Supply either a conservative cash floor assuming the entire offer opens,
cash/position lower-bound scenarios that all fund the maker, or bounded
conditional scenarios that prove the maker funds or lacks funds in each branch. The
redacted, lagging archive cannot certify a live balance. This tool never loads
a wallet or trades real assets.
"""

import argparse
import base64
import datetime as dt
import json
import re
import sys
from decimal import Decimal, InvalidOperation

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from audit_close_call import REFEREE_DID, audit
from say import PROJECT_ROOT, fetch_json, post_and_verify
from verify_tape import public_key_from_did, verify_record


PRICE_URL = "https://technocore.chat/r/d-close1-price?format=json&limit=1"
AMOUNT = re.compile(r"[0-9]{1,7}(?:\.[0-9]{1,2})?\Z")
SCENARIO = re.compile(r"([0-9]{1,7}(?:\.[0-9]{1,2})?):(-?[0-9]{1,7}(?:\.[0-9]{1,2})?)\Z")
CONDITIONAL_SCENARIO = re.compile(
    r"([0-9]{1,7}(?:\.[0-9]{1,2})?):([0-9]{1,7}(?:\.[0-9]{1,2})?):"
    r"(-?[0-9]{1,7}(?:\.[0-9]{1,2})?)\Z")
TRADE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
LOCK_SWEEP = 2556


def canonical_terms(terms):
    return json.dumps(terms, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_price(snapshot, now=None):
    if (not isinstance(snapshot, dict) or snapshot.get("room") != "d-close1-price" or
            not isinstance(snapshot.get("messages"), list) or
            len(snapshot["messages"]) != 1):
        raise ValueError("price tail has the wrong room or message count")
    message = snapshot["messages"][0]
    if (not isinstance(message, dict) or type(message.get("seq")) is not int or
            message["seq"] != snapshot.get("last_seq") or
            message.get("from") != REFEREE_DID or
            verify_record("d-close1-price", message)[0] != "verified"):
        raise ValueError("price tail signature, referee DID, or sequence is invalid")
    try:
        body = json.loads(message["text"])
        stamp = dt.datetime.fromisoformat(message["ts"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("price tail body or timestamp is malformed") from exc
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    if stamp.tzinfo is None or now.tzinfo is None:
        raise ValueError("price timestamp or current time lacks a timezone")
    age = (now - stamp).total_seconds()
    if (not -30 <= age <= 600 or
            not isinstance(body, dict) or body.get("t") != "price" or
            type(body.get("n")) is not int or type(body.get("for")) is not int or
            body["for"] != body["n"] + 1 or
            not isinstance(body.get("limits"), list) or len(body["limits"]) != 2 or
            not isinstance(body.get("ref"), dict)):
        raise ValueError("price tail is stale or malformed")
    try:
        lower, upper = (Decimal(value) for value in body["limits"])
        reference = Decimal(body["ref"]["px"])
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        raise ValueError("price limits or reference are malformed") from exc
    if (not all(value.is_finite() for value in (lower, upper, reference)) or
            lower <= 0 or upper <= lower or reference <= 0):
        raise ValueError("price limits or reference are invalid")
    return {"sweep": body["for"], "lower": lower, "upper": upper,
            "reference": reference, "signed_seq": message["seq"], "timestamp": message["ts"]}


def fee_ceiling_per_contract(px, reference):
    """Upper fee if the next closing reference is within 5% of the signed one."""
    return max(px * Decimal("0.01"),
               abs(px - reference) + reference * Decimal("0.05"))


def conditional_analysis(side, qty, px, price, scenarios, max_abs_position_text):
    """Prove maker funding or maker-funds-void for every supplied account state.

    The cash interval must describe free cash *when this trade is applied*. The
    fee ceiling shares the existing offer tool's five-percent close-move
    assumption; a larger move may void a supposedly funded branch.
    """
    if not scenarios or not max_abs_position_text or not AMOUNT.fullmatch(max_abs_position_text):
        raise ValueError("conditional funding needs scenarios and a position cap")
    cap = Decimal(max_abs_position_text)
    if cap <= 0:
        raise ValueError("conditional position cap must be positive")
    min_fee = qty * px * Decimal("0.01")
    max_fee = qty * fee_ceiling_per_contract(px, price["reference"])
    branches = []
    for index, scenario in enumerate(scenarios, 1):
        match = CONDITIONAL_SCENARIO.fullmatch(scenario)
        if not match:
            raise ValueError(f"conditional scenario {index} is malformed")
        cash_min, cash_max, position = (Decimal(value) for value in match.groups())
        if cash_min < 0 or cash_max < cash_min:
            raise ValueError(f"conditional scenario {index} has invalid cash bounds")
        if abs(position) > cap:
            raise ValueError(f"conditional scenario {index} starts beyond position cap")
        closing = min(qty, max(Decimal(0), -position if side == "buy" else position))
        opening = qty - closing
        reserve_min = opening * px + min_fee
        reserve_max = opening * px + max_fee
        if cash_min >= reserve_max:
            outcome = "maker_funded_within_fee_bound"
            next_position = position + (qty if side == "buy" else -qty)
        elif cash_max < reserve_min:
            outcome = "maker_funds_void_if_reached"
            next_position = position
        else:
            raise ValueError(f"conditional scenario {index} has ambiguous funding")
        if abs(next_position) > cap:
            raise ValueError(f"conditional scenario {index} exceeds position cap")
        branches.append({"scenario": scenario, "outcome": outcome,
                         "reserve_min": str(reserve_min), "reserve_max": str(reserve_max),
                         "position_after": str(next_position)})
    if not any(branch["outcome"] == "maker_funded_within_fee_bound" for branch in branches):
        raise ValueError("conditional offer has no funded account scenario")
    return branches


def validate_offer(offer_id, side, qty_text, px_text, until, cash_floor_text, did, price,
                   scenarios=None, conditional_scenarios=None, max_abs_position=None):
    if (not TRADE_ID.fullmatch(offer_id) or side not in ("buy", "sell") or
            not AMOUNT.fullmatch(qty_text) or not AMOUNT.fullmatch(px_text)):
        raise ValueError("offer ID, side, quantity, or price is malformed")
    modes = sum(value is not None for value in
                (cash_floor_text, scenarios, conditional_scenarios))
    if modes != 1:
        raise ValueError("supply either a cash floor or one type of account scenarios")
    if conditional_scenarios is None and max_abs_position is not None:
        raise ValueError("position cap applies only to conditional scenarios")
    qty, px = (Decimal(value) for value in (qty_text, px_text))
    if qty < Decimal("0.1") or px <= 0:
        raise ValueError("quantity or price is out of range")
    if not price["lower"] <= px <= price["upper"]:
        raise ValueError("offer price is outside signed next-sweep limits")
    if type(until) is not int or not price["sweep"] <= until <= min(price["sweep"] + 2, LOCK_SWEEP):
        raise ValueError("offer expiry must be within two sweeps and before lock")
    # Include the quote's offset from the signed reference as well as a
    # five-percent closing-reference move. A larger jump can still void the
    # trade; scenarios are caller assumptions, not a certified cash balance.
    fee_per_contract = fee_ceiling_per_contract(px, price["reference"])
    if conditional_scenarios is not None:
        branches = conditional_analysis(side, qty, px, price,
                                        conditional_scenarios, max_abs_position)
        worst_reserve = max(Decimal(branch["reserve_max"]) for branch in branches
                            if branch["outcome"] == "maker_funded_within_fee_bound")
    elif scenarios is None:
        if not AMOUNT.fullmatch(cash_floor_text):
            raise ValueError("cash floor is malformed")
        cash_floor = Decimal(cash_floor_text)
        if cash_floor <= 0:
            raise ValueError("cash floor is out of range")
        worst_reserve = qty * (px + fee_per_contract)
        if worst_reserve > cash_floor:
            raise ValueError("conservative collateral and fee reserve exceeds supplied cash floor")
    else:
        if not scenarios:
            raise ValueError("at least one account scenario is required")
        reserves = []
        for index, scenario in enumerate(scenarios, 1):
            match = SCENARIO.fullmatch(scenario)
            if not match or Decimal(match[1]) <= 0:
                raise ValueError(f"account scenario {index} is malformed")
            cash_floor, position = Decimal(match[1]), Decimal(match[2])
            closing = min(qty, max(Decimal(0), -position if side == "buy" else position))
            reserve = (qty - closing) * px + qty * fee_per_contract
            if reserve > cash_floor:
                raise ValueError(f"account scenario {index} reserve exceeds its cash floor")
            reserves.append(reserve)
        worst_reserve = max(reserves)
    terms = {"id": offer_id, "maker": did, "px": px_text, "qty": qty_text,
             "side": side, "taker": "any", "until": until}
    return terms, worst_reserve


def signed_offer(terms, private_key):
    canonical = canonical_terms(terms)
    signature = private_key.sign(f"close-1|terms|{canonical}".encode("ascii"))
    public_key_from_did(terms["maker"]).verify(signature,
                                                f"close-1|terms|{canonical}".encode("ascii"))
    body = {"t": "offer", "season": "close-1", "terms": terms,
            "maker_sig": base64.urlsafe_b64encode(signature).decode().rstrip("=")}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="new, unique paper trade ID")
    parser.add_argument("--side", choices=("buy", "sell"), required=True)
    parser.add_argument("--qty", required=True, help="paper contracts, max two decimal places")
    parser.add_argument("--px", required=True, help="POLF per contract, max two decimal places")
    parser.add_argument("--until", type=int, required=True, help="last valid sweep")
    funding = parser.add_mutually_exclusive_group(required=True)
    funding.add_argument("--cash-floor", help="POLF cash floor if the entire offer opens")
    funding.add_argument("--scenario", action="append", metavar="CASH_FLOOR:POSITION",
                         help="repeat for every unresolved-fill state; signed position, POLF cash floor")
    funding.add_argument("--conditional-scenario", action="append",
                         metavar="CASH_MIN:CASH_MAX:POSITION",
                         help="repeat for every unresolved-fill state; each must prove funded or funds-void")
    parser.add_argument("--max-abs-position",
                        help="required for conditional scenarios; cap the position after each branch")
    parser.add_argument("--post", action="store_true", help="post one signed offer, then verify exact readback")
    parser.add_argument("--watch-seconds", type=int, default=0,
                        help="after --post, watch this public room for a verified countersignature (0-600)")
    args = parser.parse_args(argv)
    if not 0 <= args.watch_seconds <= 600 or (args.watch_seconds and not args.post):
        parser.error("--watch-seconds requires --post and a duration of 0-600 seconds")
    try:
        meta = json.loads((PROJECT_ROOT / "agent-did.json").read_text())
        did = meta["did"]
        price = read_price(fetch_json(PRICE_URL))
        mint = audit(915, owner=did)
        if mint["owner_result"] != {"in_input": True, "minted_this_sweep": True}:
            raise ValueError("owner mint was not found in the verified archived sweep")
        terms, reserve = validate_offer(args.id, args.side, args.qty, args.px,
                                        args.until, args.cash_floor, did, price,
                                        scenarios=args.scenario,
                                        conditional_scenarios=args.conditional_scenario,
                                        max_abs_position=args.max_abs_position)
        result = {"mode": "dry_run", "terms": terms, "signed_price_seq": price["signed_seq"],
                  "next_sweep": price["sweep"],
                  "conservative_reserve": str(reserve),
                  "mint_provenance": mint["provenance"],
                  "caution": "This is only a negotiation offer, not a referee-settled trade. Funding scenarios are caller assumptions; archive redactions do not prove live balance."}
        if args.scenario:
            result["account_scenarios_assumed"] = args.scenario
        elif args.conditional_scenario:
            result["conditional_branches"] = conditional_analysis(
                args.side, Decimal(args.qty), Decimal(args.px), price,
                args.conditional_scenario, args.max_abs_position)
            result["max_abs_position_assumed"] = args.max_abs_position
            result["caution"] += (" A funds-void branch is a deliberate possible no-fill, "
                                  "not proof of exposure or settlement; cash intervals "
                                  "must bound free cash at application time. The fee bound "
                                  "assumes no more than a five-percent reference move. "
                                  "Maker funding does not prove the taker's funding, "
                                  "countersignature, ingestion, or settlement.")
        else:
            result["cash_floor_assumed"] = args.cash_floor
        if args.post:
            fresh = read_price(fetch_json(PRICE_URL))
            if fresh["signed_seq"] != price["signed_seq"]:
                raise ValueError("signed price advanced since preflight; re-evaluate the offer")
            identity_dir = PROJECT_ROOT / ".private" / "identity"
            private_key = load_pem_private_key(
                (identity_dir / "agent-ed25519.pem").read_bytes(), password=None)
            raw_public = private_key.public_key().public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            if raw_public.hex() != meta["public_key_raw_hex"]:
                raise ValueError("private key does not match existing public DID")
            message = signed_offer(terms, private_key)
            receipt = post_and_verify("close1", message, did, meta["public_key_raw_hex"], private_key)
            result.update({"mode": "posted", "receipt": receipt})
            if args.watch_seconds:
                # The busy room may discard an offer before a separate process
                # can fetch it again. The exact posting receipt above already
                # authenticated this text and sequence, so watch from there.
                from close_call_watch_offer import offer_from_text, watch_cursor
                try:
                    watched = offer_from_text(message, did, receipt["seq"])
                    result["watch"] = watch_cursor("close1", receipt["seq"],
                                                  args.watch_seconds, watched)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    result["watch"] = {"status": "unavailable", "error": str(exc),
                                       "caution": "Offer was posted; do not retry the write. Counterparty and referee outcomes remain unknown."}
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        print(f"close-call offer unavailable: {exc}; do not retry an uncertain post", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
