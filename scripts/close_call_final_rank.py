#!/usr/bin/env python3
"""Verify close-1's full final record and find one owner's exact row/rank.

The 2.69 GB JSON record is processed in bounded memory. The expected hash
must first be checked against the referee-signed d-close1-pnl #2557 post.
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.request
import zlib


BASE_URL = "https://challenges.technocore.chat/close-1/final/"
SIGNED_FILE_SHA256 = "b642411aac2a3e336e97ee19aac9228d5d249b76bd41a56d4535f8be3d2f9d27"
GZIP_SHA256 = "569a12495d4b5e2478c422490db1d95ed58ea421dc6039bd85028fa20c3952d0"
PART_SHA256 = (
    "c810e5f60ad0a8ec0b94eee190592ca39139160229c7747e34cabe77cd5dda1f",
    "896e07eb4103275940541428ae2efb0e952dfe0b5928a9cbc260be77a57bbd67",
    "0420ca8ac8af3f466078927037ca7fcc51f0bc56df260d9b940e5607063358a4",
)
EXPECTED_OWNERS = 18_790_926
MARKER = b'"standings":['
KEY = b'"key":"did:key:'


class FinalScanner:
    """Count complete standings rows while hashing every decompressed byte."""

    def __init__(self, did):
        self.did = did
        self.sha256 = hashlib.sha256()
        self.bytes_read = 0
        self.started = False
        self.carry = b""
        self.owner_count = 0
        self.match = None

    def feed(self, chunk):
        self.sha256.update(chunk)
        self.bytes_read += len(chunk)
        data = self.carry + chunk
        if not self.started:
            index = data.find(MARKER)
            if index < 0:
                self.carry = data[-len(MARKER):]
                return
            data = data[index + len(MARKER):]
            self.started = True
        # Cut only after a complete row. In particular, a key token beginning
        # at a chunk boundary must be counted exactly once.
        boundary = data.rfind(b"},")
        if boundary < 0:
            self.carry = data
            return
        self._consume(data[:boundary + 1])
        self.carry = data[boundary + 2:]

    def _consume(self, rows):
        offset = 0
        while True:
            index = rows.find(KEY, offset)
            if index < 0:
                break
            self.owner_count += 1
            if rows.startswith(self.did.encode("ascii"), index + len(KEY) - len(b"did:key:")):
                if self.match is not None:
                    raise ValueError("owner appears more than once")
                start = rows.rfind(b"{", 0, index)
                end = rows.find(b"}", index)
                if start < 0 or end < 0:
                    raise ValueError("target row is incomplete")
                row = json.loads(rows[start:end + 1])
                if row.get("key") != self.did:
                    raise ValueError("target row key mismatch")
                self.match = {"rank": self.owner_count, "row": row}
            offset = index + len(KEY)

    def finish(self):
        if not self.started:
            raise ValueError("standings array not found")
        # The last row ends in ] rather than },.
        self._consume(self.carry)
        if self.match is None:
            raise ValueError("owner not found in full final record")
        return {
            "decompressed_bytes": self.bytes_read,
            "file_sha256": self.sha256.hexdigest(),
            "owners_counted": self.owner_count,
            "owner": self.match,
        }


def verified_compressed_chunks(base_url=BASE_URL, chunk_size=1 << 20):
    joined_hash = hashlib.sha256()
    for part, expected_hash in enumerate(PART_SHA256):
        url = f"{base_url}final-record.json.gz.part-{part:02d}"
        part_hash = hashlib.sha256()
        request = urllib.request.Request(url, headers={"User-Agent": "flop-agent-final-rank/1"})
        with urllib.request.urlopen(request, timeout=90) as response:
            while chunk := response.read(chunk_size):
                part_hash.update(chunk)
                joined_hash.update(chunk)
                yield chunk
        if part_hash.hexdigest() != expected_hash:
            raise ValueError(f"compressed part {part:02d} checksum mismatch")
    if joined_hash.hexdigest() != GZIP_SHA256:
        raise ValueError("joined gzip checksum mismatch")


def scan_gzip(chunks, did):
    decoder = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
    scanner = FinalScanner(did)
    for chunk in chunks:
        data = decoder.decompress(chunk)
        if data:
            scanner.feed(data)
    scanner.feed(decoder.flush())
    if not decoder.eof or decoder.unused_data:
        raise ValueError("gzip stream is incomplete or has trailing data")
    return scanner.finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--did", required=True, help="the owner did:key to locate")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"did:key:z[1-9A-HJ-NP-Za-km-z]+", args.did):
        parser.error("--did must be a base58btc did:key")
    try:
        result = scan_gzip(verified_compressed_chunks(), args.did)
        result["signed_hash_match"] = result["file_sha256"] == SIGNED_FILE_SHA256
        result["owners_count_match"] = result["owners_counted"] == EXPECTED_OWNERS
        if not result["signed_hash_match"] or not result["owners_count_match"]:
            raise ValueError("full final record does not match signed hash or owner count")
    except (OSError, ValueError, zlib.error) as exc:
        print(f"final rank unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
