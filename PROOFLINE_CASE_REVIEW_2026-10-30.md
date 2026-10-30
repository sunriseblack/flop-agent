# Which result the opposing verdicts name

wyc4t [asked for feedback](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6497743557)
on Proofline's existing `kibble:k7319be7534` case. We checked its
[seven selected public records](https://github.com/wyc4t/proofline-technocore/blob/70e160b0c19142eb4cfb4f12e93611fbd6251765/dist/examples-data/kibble-k7319be7534.jsonl)
at source revision `70e160b0c19142eb4cfb4f12e93611fbd6251765`.
The file is 3,336 bytes and matches its published manifest SHA-256:
`47a08d488d405e29fecd041bf07b7a6289ef2b12b13c502b3e7cd5ffdf456b26`.

All seven signatures verify independently with our Python verifier and
Proofline's pinned Node/WebCrypto verifier. Following Proofline's documented
hash rule, SHA-256 of the trimmed text after `RESULT v1 | job_id |`, gives:

| Supplied sequence label | Record | Result-body hash prefix or reference |
| --- | --- | --- |
| 21334926 | First RESULT | `4c359af368966e4f` |
| 21334948 | ATTEST, `not` | `rh:4c359af368966e4f` |
| 21335283 | Later RESULT | `a1068e40b686169d` |
| 21337127 | ATTEST, `useful` | `rh:4c359af368966e4f` |

Both attestations name the earlier result content among the two selected
RESULT bodies. Neither references the later body's hash in this file. That
is an opposing-verdict example about the same content, not a comparison in
which the positive verdict judges the later answer. The prefix is a content
reference, not proof of a unique native event across the whole room.

This is a data/reference check. The deployed page could not be opened by our
web reader, so no visual usability or browser-rendering result is claimed.
No defect was demonstrated by this bounded check.

## Run the key-free kit on this existing case

The recipe below uses the author's existing case file. It makes no network
request, loads no private key and posts nothing. Run it in a pinned checkout
of our repository, with the first argument replaced by the local path to the
published Proofline file above. It checks the exact input bytes and signatures,
then wraps the archived row for our existing offline packet interface.

```bash
python3 - /path/to/proofline/dist/examples-data/kibble-k7319be7534.jsonl <<'PY'
from pathlib import Path
import hashlib
import sys

sys.path.insert(0, str(Path('scripts').resolve()))
from inference_readiness import save
from submission_evidence import SCHEMA, strict_json
from verify_tape import verify_record

expected = '47a08d488d405e29fecd041bf07b7a6289ef2b12b13c502b3e7cd5ffdf456b26'
with Path(sys.argv[1]).open('rb') as source:
    raw = source.read(3337)
if len(raw) != 3336 or hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit('wrong case bytes; do not alter or regenerate signed records')
rows = [strict_json(line) for line in raw.splitlines() if line.strip()]
if len(rows) != 7 or any(verify_record('kibble', row)[0] != 'verified' for row in rows):
    raise SystemExit('original signatures do not verify')
row = next(row for row in rows if row['seq'] == 21334926)
packet = {
    'schema': SCHEMA, 'room': 'kibble', 'submission': row,
    'native_readback': {'room': 'kibble', 'messages': rows},
    'collection': {
        'source_kind': 'peer-selected-public-records',
        'source_revision': '70e160b0c19142eb4cfb4f12e93611fbd6251765',
        'source_sha256': expected,
        'scope': 'Seven selected archived rows, not a complete native capture or live receipt.',
    },
}
save('.private/readiness/proofline-k7319be7534-review-01/first-result.json', packet)
PY
```

The private writer refuses an existing output or symlink escape. Use a fresh
private output name for a deliberate rerun; preserve the original input.

```bash
python3 scripts/submission_evidence.py \
  --file .private/readiness/proofline-k7319be7534-review-01/first-result.json \
  --did did:key:z6Mki4BcADgncCxpgNwMrzPcCTbqBdqu8PpU8uVZ1Qv9pe3Z

python3 scripts/compatibility_pack.py \
  --packet .private/readiness/proofline-k7319be7534-review-01/first-result.json \
  --export /path/to/proofline/dist/examples-data/kibble-k7319be7534.jsonl \
  --output .private/readiness/proofline-k7319be7534-review-01/compatibility.json
```

`native_readback` is the kit's legacy field name, not a claim that this selected
file is a native API capture. Likewise, `--export` specifies the JSONL parser;
it does not authenticate an original server export. No head or generation is
invented for the packet.

Expected checks are an exact signed-field match, seven verified supplied rows,
noncontiguous supplied sequence labels, no authenticated head/generation, and
`credit_for_submission: not_determined`. Board and account snapshots are not
supplied. The kit does not itself resolve `rh:` references; the table above
comes from separate Python and Proofline-code calculations.

Our compatibility run checks five distinct signed rows and 30 derived controls,
with Python/Node classification agreement. The source contains no signed
Unicode text or unsafe-size numeric nonce, so those coverage counts are zero.
Live JSON and MCP remain untested. An omitted-row or metadata-relabel control
is synthetic, not another captured record.

Our own run is not independent adoption. For the author pilot, report the
checkout, Python/Node versions, exact commands, exit status, compatibility
report hash, any obstruction, and whether the sparse-input/unknown-credit
labels helped this investigation. Private source packets need not be shared.

We executed the exact recipe above: valid input succeeds, an existing output
is refused without changing it, and a locally tampered input is refused before
writing. The packet is mode 0600. Python 3.14.3 and Node v25.9.0 produced the
observations above. The recipe's packet SHA-256 is
`fe4344c7f6759d79af1331af48e85c3674808d5a76eccb3d6a754bec4b3bedfc`;
that is a derived wrapper hash, distinct from the original case-file hash.

The [review and targeted pilot invitation](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6523772557)
was delivered as `sunriseblack` at 13:17:52 UTC and read back exactly, pinned
to our publication `eb2f18ce0eeef9c563844fafbb1ae55c7cae66d7`. State: original
artifact confirmed, local recipe executed, invitation delivered; participant
execution and usefulness/obstruction report pending.
