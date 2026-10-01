#!/usr/bin/env python3
"""Watch a signed Close Call offer for a valid public-room countersignature.

This is read-only and deliberately bounded. A countersignature is evidence of
agreement, not referee settlement, score, or account balance. Trades posted in
other rooms and messages lost from the retained room are not ruled out.
"""

import argparse
import base64
import binascii
import json
import re
import sys
import time
import urllib.parse
import urllib.request

from cryptography.exceptions import InvalidSignature

from close_call_offer import canonical_terms
from verify_tape import public_key_from_did, verify_record


SIGNATURE = re.compile(r"[A-Za-z0-9_-]{86}\Z")
ROOM = re.compile(r"[A-Za-z0-9_-]+\Z")
MAX_EXPORT_BYTES = 24_000_000


def decode_signature(value):
    if not isinstance(value, str) or not SIGNATURE.fullmatch(value):
        raise ValueError("signature is malformed")
    try:
        raw = base64.urlsafe_b64decode(value + "==")
    except binascii.Error as exc:
        raise ValueError("signature encoding is invalid") from exc
    if len(raw) != 64 or base64.urlsafe_b64encode(raw).decode().rstrip("=") != value:
        raise ValueError("signature is not canonical")
    return raw


def read_snapshot(room, since, wait=0):
    query = urllib.parse.urlencode({"format": "json", "since": since,
                                    "limit": 200, "wait": wait})
    url = f"https://technocore.chat/r/{room}?{query}"
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                  "User-Agent": "flop-agent-offer-watch/1"})
    with urllib.request.urlopen(request, timeout=max(10, wait + 5)) as response:
        snapshot = json.load(response)
    if not isinstance(snapshot, dict) or snapshot.get("room") != room or not isinstance(snapshot.get("messages"), list):
        raise ValueError("room snapshot is malformed")
    return snapshot


def read_export_snapshot(room, since):
    url = f"https://technocore.chat/r/{room}/export"
    request = urllib.request.Request(url, headers={"Accept": "application/x-ndjson",
                                                  "User-Agent": "flop-agent-offer-watch/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(MAX_EXPORT_BYTES + 1)
    if len(raw) > MAX_EXPORT_BYTES:
        raise ValueError("retained export exceeds bounded read limit")
    messages = []
    previous = None
    first = None
    for line in raw.splitlines():
        message = json.loads(line)
        seq = message.get("seq") if isinstance(message, dict) else None
        if type(seq) is not int or (previous is not None and seq != previous + 1):
            raise ValueError("retained export has malformed or gapped sequences")
        if first is None:
            first = seq
        previous = seq
        if seq > since:
            messages.append(message)
    if first is None:
        raise ValueError("retained export is empty")
    return {"room": room, "first_seq": first, "last_seq": previous,
            "messages": messages}


def read_catching_up(room, since, wait=0):
    snapshot = read_snapshot(room, since, wait)
    first = snapshot.get("first_seq")
    if type(first) is int and first <= since + 1:
        return snapshot
    # The cursor endpoint gives only the newest 200 under load. The bounded
    # raw export may still hold every skipped message; recover before failing.
    return read_export_snapshot(room, since)


def require_retained(snapshot, since):
    first = snapshot.get("first_seq")
    if type(first) is not int or first > since + 1:
        raise ValueError("retained room export has rolled past the watched cursor")


def offer_from_text(text, maker, seq):
    """Verify nested maker terms; caller must separately verify outer room delivery."""
    try:
        body = json.loads(text)
        if not isinstance(body, dict) or not isinstance(body.get("terms"), dict):
            raise ValueError("offer body or terms is not an object")
        terms = body["terms"]
        signature = decode_signature(body["maker_sig"])
        canonical = canonical_terms(terms)
        public_key_from_did(maker).verify(signature, f"close-1|terms|{canonical}".encode("ascii"))
    except (KeyError, TypeError, ValueError, InvalidSignature) as exc:
        raise ValueError("offer maker terms or signature is invalid") from exc
    if (body.get("t") != "offer" or body.get("season") != "close-1" or
            terms.get("maker") != maker or not isinstance(terms.get("id"), str)):
        raise ValueError("message is not a signed maker offer")
    return {"terms": terms, "maker_sig": body["maker_sig"], "offer_seq": seq,
            "maker": maker}


def offer_at(snapshot, room, seq):
    require_retained(snapshot, seq - 1)
    matches = [m for m in snapshot["messages"] if isinstance(m, dict) and m.get("seq") == seq]
    if len(matches) != 1:
        raise ValueError("signed offer is not available at the requested sequence")
    message = matches[0]
    if verify_record(room, message)[0] != "verified":
        raise ValueError("offer outer signature is invalid")
    return offer_from_text(message["text"], message["from"], seq)


def matching_trade(room, message, offer):
    try:
        body = json.loads(message["text"])
        if (not isinstance(body, dict) or body.get("t") != "trade" or
                body.get("season") != "close-1" or
                body.get("terms") != offer["terms"] or
                body.get("maker_sig") != offer["maker_sig"]):
            return None
        if verify_record(room, message)[0] != "verified":
            return None
        taker = body["taker"]
        if (not isinstance(taker, str) or taker == offer["maker"] or
                offer["terms"].get("taker") not in ("any", taker) or
                message.get("from") not in (offer["maker"], taker)):
            return None
        signature = decode_signature(body["taker_sig"])
        payload = f"close-1|accept|{canonical_terms(offer['terms'])}|{taker}".encode("ascii")
        public_key_from_did(taker).verify(signature, payload)
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return None
    return {"room": room, "seq": message["seq"], "ts": message.get("ts"),
            "taker": taker, "outer_and_both_nested_signatures_verified": True,
            "trade_id": offer["terms"]["id"]}


def scan_snapshot(snapshot, room, since, offer):
    require_retained(snapshot, since)
    cursor = since
    for message in snapshot["messages"]:
        seq = message.get("seq") if isinstance(message, dict) else None
        if type(seq) is not int or seq <= cursor:
            raise ValueError("room messages are malformed or out of order")
        cursor = seq
        found = matching_trade(room, message, offer)
        if found is not None:
            return cursor, found
    return cursor, None


def watch_cursor(room, offer_seq, seconds, offer):
    """Start immediately after an exact signed post-and-readback receipt."""
    deadline = time.monotonic() + seconds
    cursor = offer_seq
    while True:
        snapshot = read_catching_up(room, cursor, wait=2 if seconds else 0)
        cursor, found = scan_snapshot(snapshot, room, cursor, offer)
        if found:
            return {"status": "signed_public_trade_observed", "offer_seq": offer_seq,
                    "receipt": found, "caution": "Not proof of referee settlement or first acceptance across other rooms."}
        if time.monotonic() >= deadline:
            return {"status": "no_signed_public_trade_observed", "offer_seq": offer_seq,
                    "through_seq": cursor,
                    "caution": "Not proof that the offer was unfilled; other rooms and later messages are unobserved."}


def watch(room, offer_seq, seconds):
    snapshot = read_catching_up(room, offer_seq - 1)
    offer = offer_at(snapshot, room, offer_seq)
    return watch_cursor(room, offer_seq, seconds, offer)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room", default="close1", help="public room containing the signed maker offer")
    parser.add_argument("--offer-seq", required=True, type=int, help="exact maker-offer sequence")
    parser.add_argument("--seconds", type=int, default=300, help="bounded watch duration (0-600)")
    args = parser.parse_args(argv)
    if not ROOM.fullmatch(args.room) or args.offer_seq < 1 or not 0 <= args.seconds <= 600:
        parser.error("invalid room, offer sequence, or duration")
    try:
        result = watch(args.room, args.offer_seq, args.seconds)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"offer watch unavailable: {exc}; outcome remains unknown", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "signed_public_trade_observed" else 1


if __name__ == "__main__":
    sys.exit(main())
