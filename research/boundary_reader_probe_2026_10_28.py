#!/usr/bin/env python3
"""Offline caller coverage for zkasuran's Technocore PR 1042, not a new fix.

Use its locked Python environment. Both source revisions and the existing public
signed packet are pinned. Unsigned local filler places that unchanged record at
a synthetic byte boundary. No key, signer, public write, or external HTTP call.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
STORES = {"67cd17b9d0563e2224f8d3c5129d12194c37c99c": "main-73a7324",
          "a8960449955743bb374589dfb4066fc6f604898d": "pr1042-3393e71"}
PACKET_SHA256 = "de2ca99a3404874ba056239db72866046e5d1bd446a6526d7a91b5b05c21402c"


def pad_record(store, seq, size, stamp):
    """Construct only unsigned offline filler, within the service's text limits."""
    record = {"seq": seq, "ts": stamp, "from": "boundary-control", "text": ""}
    framing = len(store.orjson.dumps(record)) + 1
    target = size - framing
    four = max(0, -(-(target - store.MAX_TEXT_CHARS) // 3))
    ascii_count = target - 4 * four
    assert ascii_count >= 0 and four + ascii_count <= store.MAX_TEXT_CHARS
    record["text"] = "\U0001d11e" * four + "x" * ascii_count
    assert store.clean_text(record["text"]) == record["text"]
    encoded = store.orjson.dumps(record) + b"\n"
    assert len(encoded) == size
    return encoded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    upstream = Path(args.upstream).resolve()
    source = (upstream / "src/store.py").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    if blob not in STORES:
        raise ValueError("supply one of the two exact reviewed store revisions")
    packet_path = ROOT / "examples/submission-evidence-flop-327293.json"
    packet_bytes = packet_path.read_bytes()
    if hashlib.sha256(packet_bytes).hexdigest() != PACKET_SHA256:
        raise ValueError("public packet differs from the reviewed original")
    packet = json.loads(packet_bytes)
    record, room = packet["submission"], packet["room"]
    sys.path.insert(0, str(ROOT / "scripts"))
    from verify_tape import verify_record
    import inference_readiness as private

    assert verify_record(room, record)[0] == "verified"
    output = private.private_path(Path(args.output_dir) / "report.json").parent
    if output.exists():
        raise ValueError("output directory already exists")
    output.mkdir(parents=True, mode=0o700)
    sys.path.insert(0, str(upstream / "src"))
    import config
    import store
    import app
    from starlette.testclient import TestClient

    def save_transport(name, raw):
        # Preserve actual UTF-8 response bytes; JSON-escaping filler triples its size.
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("derived transport exceeds the two-MiB probe bound")
        fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
        return hashlib.sha256(raw).hexdigest()

    assert store.WINDOW_MESSAGES >= 9
    rows = []
    for kind, budget, fillers in (("tail-and-nonce", store.READ_BUDGET, 128),
                                   ("engagement", store.WINDOW_BYTES, 8)):
        target = store.orjson.dumps(record) + b"\n"
        width, extra = divmod(budget - len(target), fillers)
        for shift in (-1, 0, 1):
            with tempfile.TemporaryDirectory(prefix="flop-boundary-offline-") as directory:
                root = Path(directory)
                sizes = [width + (i < extra) for i in range(fillers)]
                sizes[-1] += shift
                prefix = pad_record(store, record["seq"] - 1, 256, record["ts"])
                body = prefix + target + b"".join(
                    pad_record(store, record["seq"] + i + 1, size, record["ts"])
                    for i, size in enumerate(sizes))
                path = store.room_path(root, room)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
                assert len(body) - len(prefix) == budget + shift
                local = {"kind": kind, "shift_bytes": shift, "file_bytes": len(body),
                         "budget": budget, "target_signature": "verified",
                         "source_condition": "synthetic local alignment; existing signed record unchanged"}
                if kind == "tail-and-nonce":
                    direct = store.read_messages(root, room, limit=200)
                    local["last_nonce"] = store._last_nonce(root, room, record["from"])
                    with config.override(ROOT=root):
                        # ASGI calls only; no lifespan/background worker is started.
                        client = TestClient(app.app)
                        response = client.get(f"/r/{room}?format=json&limit=200")
                        export = client.get(f"/r/{room}/export")
                        client.close()
                    assert response.status_code == export.status_code == 200
                    view = response.json()
                    assert view["messages"] == direct["messages"]
                    assert export.content == body
                    found = [r for r in view["messages"] if r.get("from") == record["from"]]
                    assert not found or found == [record]
                    local.update(count=view["count"], first_seq=view["first_seq"],
                                 target_in_json=bool(found), export_byte_exact=True,
                                 target_in_export=record in [store.orjson.loads(r) for r in body.splitlines()])
                    if shift == 0:
                        local["view_sha256"] = save_transport("aligned-view.json", response.content)
                        local["export_sha256"] = save_transport("aligned-export.jsonl", export.content)
                else:
                    _, nicks = store.room_window(root, room)
                    local.update(nicks=len(nicks), target_in_engagement=record["from"] in nicks)
                expected = shift < 0 or (shift == 0 and STORES[blob].startswith("pr1042"))
                if kind == "tail-and-nonce":
                    assert local["target_in_json"] is expected
                    assert local["last_nonce"] == (record["nonce"] if expected else None)
                    assert local["target_in_export"] is True
                else:
                    assert local["target_in_engagement"] is expected
                rows.append(local)
    report = {"schema": "flop-boundary-caller-check-v1", "store_blob": blob,
              "source": STORES[blob], "public_packet_sha256": PACKET_SHA256,
              "existing_record_seq": record["seq"], "cases": rows,
              "external_http_requests": 0, "signatures_created": 0,
              "scope": "independent offline caller regression; not a live retention incident or peer kit adoption"}
    private.save(output / "report.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
