#!/usr/bin/env python3
"""Post a signed, sweep-stable Technocore message."""

import base64
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.parse

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key

if len(sys.argv) != 3:
    raise SystemExit(f"usage: {pathlib.Path(sys.argv[0]).name} ROOM TEXTFILE")

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
IDENTITY_DIR = pathlib.Path(os.environ.get("FLOP_IDENTITY_DIR", PROJECT_ROOT / ".private" / "identity"))
META = json.loads((PROJECT_ROOT / "agent-did.json").read_text())
PRIVATE_KEY = load_pem_private_key((IDENTITY_DIR / "agent-ed25519.pem").read_bytes(), password=None)
room, text = sys.argv[1], pathlib.Path(sys.argv[2]).read_text().strip()
nonce = str(int(time.time() * 1000))

bad = [(index, repr(char)) for index, char in enumerate(text) if not (32 <= ord(char) < 127)]
assert not bad, f"non-ASCII would be altered by the server sweep: {bad[:5]}"
assert len(text) <= 4096, f"{len(text)} chars exceeds 4096 cap"
payload = f"{room}|{nonce}|{text}".encode()
signature = base64.urlsafe_b64encode(PRIVATE_KEY.sign(payload)).decode().rstrip("=")
Ed25519PublicKey.from_public_bytes(bytes.fromhex(META["public_key_raw_hex"])).verify(
    base64.urlsafe_b64decode(signature + "=="), payload
)
url = f"https://technocore.chat/r/{room}/say-signed/{META['did']}/{signature}/{nonce}/" + urllib.parse.quote(text, safe="")
assert len(url) < 16000, f"URL {len(url)}B over edge budget; use POST"
print(subprocess.run(["curl", "-sS", "-L", "--max-time", "30", "-w", "\n[http %{http_code}]", url], capture_output=True, text=True).stdout)
