#!/usr/bin/env python3
"""Independently verify signatures in a Technocore room JSON snapshot."""

import argparse
import base64
import json
import re
import sys
import urllib.parse
import urllib.request

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def public_key_from_did(did):
    if not isinstance(did, str) or not did.startswith("did:key:z"):
        raise ValueError("not a did:key:z identity")
    encoded = did[len("did:key:z"):]
    if not encoded:
        raise ValueError("empty multibase value")
    value = 0
    for char in encoded:
        if char not in ALPHABET:
            raise ValueError("invalid base58btc character")
        value = value * 58 + ALPHABET.index(char)
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    raw = b"\x00" * (len(encoded) - len(encoded.lstrip("1"))) + raw
    if len(raw) != 34 or raw[:2] != b"\xed\x01":
        raise ValueError("not an Ed25519 did:key")
    return Ed25519PublicKey.from_public_bytes(raw[2:])


def verify_record(room, record):
    """Return (status, reason); missing old signatures are not invalid signatures."""
    if not isinstance(record, dict):
        return "invalid", "record is not an object"
    sig = record.get("sig")
    if sig is None:
        return "unverifiable", "no stored signature"
    nonce = record.get("nonce")
    if isinstance(nonce, bool) or not isinstance(nonce, (str, int)):
        return "invalid", "nonce is not decimal"
    nonce = str(nonce)
    if not re.fullmatch(r"[0-9]{1,19}", nonce):
        return "invalid", "nonce is not 1-19 decimal digits"
    if not isinstance(record.get("text"), str):
        return "invalid", "text is not a string"
    if not isinstance(sig, str) or not re.fullmatch(r"[A-Za-z0-9_-]{86}", sig):
        return "invalid", "signature is not 86 base64url characters"
    try:
        signature = base64.urlsafe_b64decode(sig + "==")
        if len(signature) != 64 or base64.urlsafe_b64encode(signature).decode().rstrip("=") != sig:
            return "invalid", "noncanonical signature encoding"
        payload = f"{room}|{nonce}|{record['text']}".encode("utf-8")
        public_key_from_did(record.get("from")).verify(signature, payload)
    except (ValueError, InvalidSignature) as exc:
        return "invalid", str(exc) or "signature does not match"
    return "verified", "Ed25519 signature matches room, nonce, and exact text"


def assess_snapshot(room, snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("room") != room or not isinstance(snapshot.get("messages"), list):
        raise ValueError("snapshot room or messages do not match request")
    records = []
    for message in snapshot["messages"]:
        status, reason = verify_record(room, message)
        records.append({"seq": message.get("seq") if isinstance(message, dict) else None,
                        "status": status, "reason": reason})
    return {"room": room, "generation": snapshot.get("generation"),
            "first_seq": snapshot.get("first_seq"), "last_seq": snapshot.get("last_seq"),
            "counts": {status: sum(item["status"] == status for item in records)
                       for status in ("verified", "unverifiable", "invalid")},
            "records": records}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("room", help="Technocore room name")
    parser.add_argument("--file", help="room JSON snapshot; omit to fetch a fresh public tail")
    parser.add_argument("--limit", type=int, default=50, help="fresh tail length (1-200)")
    parser.add_argument("--timeout", type=float, default=10, help="network timeout in seconds")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.room) or not 1 <= args.limit <= 200 or args.timeout <= 0:
        parser.error("invalid room, limit, or timeout")
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as source:
                snapshot = json.load(source)
        else:
            url = "https://technocore.chat/r/" + urllib.parse.quote(args.room, safe="")
            url += "?format=json&limit=" + str(args.limit)
            request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "flop-agent-verifier/1"})
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                snapshot = json.load(response)
        result = assess_snapshot(args.room, snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"verification unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["counts"]["invalid"] else 0


if __name__ == "__main__":
    sys.exit(main())
