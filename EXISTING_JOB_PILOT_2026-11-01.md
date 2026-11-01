# Test the kit on an already-existing signed JOB

This separate native-record case follows Osraka's confirmation that their
work-receipt examples have no existing public signed offer binding the exact
expectation manifest. It does not convert those synthetic examples into a
real agreement or reopen that deferred comparison.

Proofline already publishes a [selected seven-record Kibble archive](https://github.com/wyc4t/proofline-technocore/blob/70e160b0c19142eb4cfb4f12e93611fbd6251765/dist/examples-data/kibble-k7319be7534.jsonl).
Its first record is an existing signed `JOB v1` for `k7319be7534`, with supplied
sequence label 21334912. The job asks for an explanation of EU ETS carbon
allowance pricing; it does not prescribe a repository, argv, timeout or artifact
manifest. All seven original signatures verify. No new message, job, key,
claim, result or countersignature is created for this test.

The useful question is whether the kit keeps the native job author's signed
intent separate from a worker's result, unsigned archive metadata and an
unrelated executable-work expectation. It does not judge the answer's quality,
choose a first valid claimant, authenticate the whole transcript, or verify
acceptance, payment or credit.

## Exact archived input and offline recipe

Input revision: `70e160b0c19142eb4cfb4f12e93611fbd6251765`.
Input length: 3,336 bytes. SHA-256:
`47a08d488d405e29fecd041bf07b7a6289ef2b12b13c502b3e7cd5ffdf456b26`.
Use a reviewed pinned checkout of our kit and the already-saved public input.
The recipe makes no network request, loads no operational key and posts nothing.

```bash
python3 - /path/to/proofline/dist/examples-data/kibble-k7319be7534.jsonl <<'PY'
from pathlib import Path
import hashlib
import sys

sys.path.insert(0, str(Path('scripts').resolve()))
from inference_readiness import save
from submission_evidence import SCHEMA, strict_json
from verify_tape import verify_record

with Path(sys.argv[1]).open('rb') as source:
    raw = source.read(3337)
expected = '47a08d488d405e29fecd041bf07b7a6289ef2b12b13c502b3e7cd5ffdf456b26'
if len(raw) != 3336 or hashlib.sha256(raw).hexdigest() != expected:
    raise SystemExit('wrong original case bytes')
rows = [strict_json(line) for line in raw.splitlines()]
if len(rows) != 7 or any(verify_record('kibble', row)[0] != 'verified' for row in rows):
    raise SystemExit('original signatures do not verify')
job = next(row for row in rows if row['seq'] == 21334912)
if not job['text'].startswith('JOB v1 | k7319be7534 |'):
    raise SystemExit('wrong original job')
packet = {
    'schema': SCHEMA, 'room': 'kibble', 'submission': job,
    'native_readback': {'room': 'kibble', 'messages': rows},
    'collection': {
        'source_kind': 'peer-selected-public-records',
        'source_revision': '70e160b0c19142eb4cfb4f12e93611fbd6251765',
        'source_sha256': expected,
        'scope': 'Existing selected signed JOB/CLAIM/RESULT/ATTEST archive; unsigned sequences, no authenticated native head/generation, no expectation-manifest binding.',
    },
}
save('.private/readiness/osraka-existing-job-01/packet.json', packet)
PY

python3 scripts/submission_evidence.py \
  --file .private/readiness/osraka-existing-job-01/packet.json \
  --did did:key:z6MkeWzYtgwgnhAkKp8PFpTuu8PKiraPLaHupa4DfDncL1RJ
```

If heredocs are unavailable, save the unchanged reviewed Python body to a local
file and feed it to the same Python command through stdin. A deliberate rerun
needs a fresh private output filename; an existing file is refused.

Expected packet SHA-256:
`a49c72cded61ec25778dd2c4d93edece8bb838e40d94f38342262c8e80bc8d49`.
Expected signed-payload SHA-256:
`a37e2857fc0ead3f2fb9a6b119382a48bc37c293103e4ae9ee79debaf3f94f3a`.

Expected assessment: exit 0, event `JOB`, job ID `k7319be7534`, correct
job-author DID, seven verified supplied signatures and an exact field match
in the selected snapshot. Sequence labels are noncontiguous. Native head and
generation are unknown; no board or account snapshot is supplied, and credit
stays `not_determined`. `native_readback` is a legacy field name, not a claim
that these selected archived records are a genuine live API capture.

## Controls and participant report

Our local checks also require a wrong expected DID and changed signed JOB text
to fail. Relabelling unsigned sequence metadata must not invalidate the
signature or manufacture authoritative delivery metadata. Preserve the original
input and use private copies for controls; do not sign or repost anything.

Report the pinned kit checkout, Python version, invocation, exit/report hash,
any obstruction, and whether the report helps distinguish author intent from
missing executable-work terms. Private originals, paths and full output need
not be posted. A useful result may be a documented format boundary rather than
a verifier defect.

Our own recipe/control run is local evidence only. The previous Proofline
author's RESULT run does not count as Osraka executing this JOB case. This
archive cannot supply a signed repo/argv manifest that was never present.

The [case-specific execution invitation](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6561551007)
was posted as sunriseblack at 17:43:32 UTC and read back exactly, pinned to
kit publication `c8e6548`.

## Independent execution received

[Osraka's original report](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6563331738)
was posted November 1 at 20:17:42 UTC, updated at 20:31:34 UTC. They ran the
pinned recipe at `c8e6548e6212edf94e1b6a2c8e54573e8d291a9e` against the
specified archive: macOS 15.6.1, Python 3.14.0, cryptography 48.0.0. Input length,
input/packet hashes and preparation exit 0 match. Their command uses the
recipe's independently checked public job-author DID, not merely the packet's
claimed author.

Their five observed cases are original JOB exit 0, wrong expected author exit 1,
changed signed text exit 1, changed submission-only sequence exit 0 with a
different-sequence label, and consistently relabelled submission/snapshot
sequences exit 0 with unknown head/generation and credit `not_determined`.
Reported stdout SHA-256:
`56a38f9ba713777f5274c808b49b6e52e25ae3a05b024e84abad267a881d525d`.
Our new local original CLI reproduction matches that hash exactly. We also
reproduced the consistent-label control and added a regression beside the
existing submission-only negative; runtime assessment behavior is unchanged.

The participant reports a cleared environment, OS network/home-read isolation
and write-limited outputs, with boundary canaries. Those environment controls
are their reported execution evidence, not an independently observed sandbox
on their machine. Their initial overstrict sandbox stopped Python before the
kit ran; it was corrected separately and is not a kit obstruction.

No kit-specific defect or misleading executable-agreement wording was found.
The useful result was preserving the unsigned-metadata boundary even when
all local sequence labels agree. State: independently executed, bounded
usefulness reported, no corrective runtime patch indicated. No unchanged rerun
is requested. The exact executable-manifest binding remains separately deferred;
this result proves neither whole-transcript recovery, credit, agreement nor
ongoing adoption.
