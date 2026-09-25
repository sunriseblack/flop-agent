#!/usr/bin/env python3
"""Post a signed Technocore message and independently verify its readback."""

import base64
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from verify_tape import verify_record

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def fetch_json(url):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "flop-agent-say/2"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}; do not blindly retry an uncertain write") from exc
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"{type(exc).__name__}; write outcome may be uncertain, do not blindly retry") from exc


def post_and_verify(room, text, did, public_key_hex, private_key, nonce=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", room):
        raise ValueError("invalid room name")
    if not text or len(text) > 4096 or any(not 32 <= ord(char) < 127 for char in text):
        raise ValueError("text must be 1-4096 sweep-stable ASCII characters")
    nonce = str(int(time.time() * 1000) if nonce is None else nonce)
    if not re.fullmatch(r"[0-9]{1,19}", nonce):
        raise ValueError("nonce must be 1-19 decimal digits")
    payload = f"{room}|{nonce}|{text}".encode()
    signature = base64.urlsafe_b64encode(private_key.sign(payload)).decode().rstrip("=")
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex)).verify(
        base64.urlsafe_b64decode(signature + "=="), payload)
    base = f"https://technocore.chat/r/{room}"
    url = f"{base}/say-signed/{did}/{signature}/{nonce}/" + urllib.parse.quote(text, safe="") + "?format=json"
    if len(url) >= 16000:
        raise ValueError("signed URL exceeds edge budget")

    receipt = fetch_json(url)
    posted = receipt.get("posted") if isinstance(receipt, dict) else None
    seq = posted.get("seq") if isinstance(posted, dict) else None
    if (isinstance(seq, bool) or not isinstance(seq, int) or seq < 1 or
            posted.get("from") != did or posted.get("text") != text or
            str(posted.get("nonce")) != nonce or posted.get("sig") != signature or
            verify_record(room, posted)[0] != "verified"):
        raise RuntimeError("write response lacks an exact verified posted receipt; do not retry without inspection")

    try:
        readback = fetch_json(f"{base}?format=json&since={seq - 1}&limit=200")
    except RuntimeError as exc:
        raise RuntimeError(f"write accepted at seq {seq}, but readback is unavailable; do not retry write") from exc
    messages = readback.get("messages") if isinstance(readback, dict) else None
    matches = [item for item in messages if isinstance(item, dict) and item.get("seq") == seq] if isinstance(messages, list) else []
    if (not isinstance(readback, dict) or readback.get("room") != room or len(matches) != 1 or
            any(matches[0].get(field) != posted.get(field) for field in ("from", "text", "nonce", "sig")) or
            verify_record(room, matches[0])[0] != "verified"):
        raise RuntimeError(f"write accepted at seq {seq}, but exact signed readback was not verified; do not retry write")
    return {"room": room, "seq": seq, "from": did, "verified": True}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        raise SystemExit(f"usage: {pathlib.Path(sys.argv[0]).name} ROOM TEXTFILE")
    room, path = argv
    identity_dir = pathlib.Path(os.environ.get("FLOP_IDENTITY_DIR", PROJECT_ROOT / ".private" / "identity"))
    try:
        meta = json.loads((PROJECT_ROOT / "agent-did.json").read_text())
        private_key = load_pem_private_key((identity_dir / "agent-ed25519.pem").read_bytes(), password=None)
        message = pathlib.Path(path).read_text().strip()
        result = post_and_verify(room, message, meta["did"], meta["public_key_raw_hex"], private_key)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"signed post not verified: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
