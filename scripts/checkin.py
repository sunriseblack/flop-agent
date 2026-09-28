#!/usr/bin/env python3
"""Legacy signed check-in, with the same receipt/readback checks as say.py.

Generic check-ins do not establish useful work or FLOP airdrop eligibility.
Use say.py for substantive messages instead.
"""

import json
import os
import pathlib
import sys

from cryptography.hazmat.primitives.serialization import load_pem_private_key

from say import post_and_verify


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    identity_dir = pathlib.Path(os.environ.get("FLOP_IDENTITY_DIR", PROJECT_ROOT / ".private" / "identity"))
    try:
        meta = json.loads((PROJECT_ROOT / "agent-did.json").read_text())
        private_key = load_pem_private_key((identity_dir / "agent-ed25519.pem").read_bytes(), password=None)
        text = f"check-in: ed25519 agent online, did note at /kv/did/{meta['fingerprint']}"
        result = post_and_verify("lobby", text, meta["did"], meta["public_key_raw_hex"], private_key)
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"signed check-in not verified: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
