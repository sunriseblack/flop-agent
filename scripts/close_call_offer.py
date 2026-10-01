#!/usr/bin/env python3
"""Prepare or post one bounded Close Call paper offer with the existing DID.

Dry-run is the default. Posting requires --post and an explicit unique trade ID.
The caller must supply a conservative cash floor from current account evidence;
the redacted, lagging archive cannot certify a live balance. This tool never
loads a wallet or trades real assets.
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


def validate_offer(offer_id, side, qty_text, px_text, until, cash_floor_text, did, price):
    if (not TRADE_ID.fullmatch(offer_id) or side not in ("buy", "sell") or
            not AMOUNT.fullmatch(qty_text) or not AMOUNT.fullmatch(px_text) or
            not AMOUNT.fullmatch(cash_floor_text)):
        raise ValueError("offer ID, side, quantity, price, or cash floor is malformed")
    qty, px, cash_floor = (Decimal(value) for value in (qty_text, px_text, cash_floor_text))
    if qty < Decimal("0.1") or px <= 0 or cash_floor <= 0:
        raise ValueError("quantity, price, or cash floor is out of range")
    if not price["lower"] <= px <= price["upper"]:
        raise ValueError("offer price is outside signed next-sweep limits")
    if type(until) is not int or not price["sweep"] <= until <= min(price["sweep"] + 2, LOCK_SWEEP):
        raise ValueError("offer expiry must be within two sweeps and before lock")
    # Reserve as though the entire quantity opens a position and the reference
    # moves five percent in one sweep. This is conservative, not a cash proof.
    fee_per_contract = max(px * Decimal("0.01"), price["reference"] * Decimal("0.05"))
    worst_reserve = qty * (px + fee_per_contract)
    if worst_reserve > cash_floor:
        raise ValueError("conservative collateral and fee reserve exceeds supplied cash floor")
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
    parser.add_argument("--cash-floor", required=True, help="conservative POLF cash lower bound")
    parser.add_argument("--post", action="store_true", help="post one signed offer, then verify exact readback")
    args = parser.parse_args(argv)
    try:
        meta = json.loads((PROJECT_ROOT / "agent-did.json").read_text())
        did = meta["did"]
        price = read_price(fetch_json(PRICE_URL))
        mint = audit(915, owner=did)
        if mint["owner_result"] != {"in_input": True, "minted_this_sweep": True}:
            raise ValueError("owner mint was not found in the verified archived sweep")
        terms, reserve = validate_offer(args.id, args.side, args.qty, args.px,
                                        args.until, args.cash_floor, did, price)
        result = {"mode": "dry_run", "terms": terms, "signed_price_seq": price["signed_seq"],
                  "next_sweep": price["sweep"], "cash_floor_assumed": args.cash_floor,
                  "conservative_reserve": str(reserve),
                  "mint_provenance": mint["provenance"],
                  "caution": "This is only a negotiation offer, not a referee-settled trade. Cash floor and exposure are caller assumptions; archive redactions do not prove live balance."}
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
        print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        print(f"close-call offer unavailable: {exc}; do not retry an uncertain post", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
