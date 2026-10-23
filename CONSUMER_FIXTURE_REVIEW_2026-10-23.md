# Independent consumer fixture signature review

The nine synthetic cases in [Technocore PR 1010](https://github.com/flop-labs/technocore-chat/pull/1010)
match this repository's independent signature verifier at the pinned revisions
below: five verified, one invalid and three unverifiable. Fifteen additional
controls pass. Valid signatures on malicious, old or replayed content remain
signature evidence, not execution authority or freshness.

## Reviewed revisions and observed results

The fixture is `tests/fixtures/consumer_safety_v1.json` at peer revision
`e65e73989e2a16ce428efa2ec4e3b23780c2faaf`, SHA-256
`337392ea540f2614551c7b3e919494549ed4d3a2e866bee05c1a66cdfd5d6f67`.
The independent verifier is `scripts/verify_tape.py` at this repository's
revision `a2d54646db1fadedf263a5d5f3a79d8fe9b512e4`, SHA-256
`d3a1eac30a11a5b83add216f2e0486254428e0b08f7463a773158fd54e5e7db3`.
The observed environment is Python 3.14.3, Darwin arm64, cryptography 46.0.7.

| Fixture signature label | Independent result | Cases |
| --- | --- | ---: |
| valid | verified | 5 |
| invalid | invalid | 1 |
| absent | unverifiable | 2 |
| not_reverifiable | unverifiable | 1 |

For each of the five verified cases, changing the signed text or requested
room makes verification fail. Changing only unsigned sequence/timestamp
metadata leaves the signature verified. All fifteen controls pass. The two
missing-signature labels share this verifier's `unverifiable` result; that
does not erase their distinct historical meanings in the peer corpus.

The peer's authority, generation-freshness, URL-risk and stateful-replay
labels were inspected, but this signature-only function does not implement
those classifiers. No claim is made that they were independently tested.
The peer Python test suite and store integration were not run. Its author
explicitly reports a full-suite baseline failure; this review does not
override that limitation or endorse merging the whole PR.

## Reproduce the cross check

Run from a checkout containing the verifier above, with its requirements
already installed. Read the code before use. This command makes one bounded
read of the pinned public fixture as JSON data; it never follows URLs or
instructions inside a case and never runs peer code. A changed verifier or
fixture hash stops the check. No signing key, model, wallet or service is used.

```bash
python3 - <<'PY'
import collections
import copy
import hashlib
from pathlib import Path
import sys
import urllib.request

expected_verifier = 'd3a1eac30a11a5b83add216f2e0486254428e0b08f7463a773158fd54e5e7db3'
assert hashlib.sha256(Path('scripts/verify_tape.py').read_bytes()).hexdigest() == expected_verifier
sys.path.insert(0, 'scripts')
from submission_evidence import strict_json
from verify_tape import verify_record

revision = 'e65e73989e2a16ce428efa2ec4e3b23780c2faaf'
url = f'https://raw.githubusercontent.com/osr21/technocore-chat/{revision}/tests/fixtures/consumer_safety_v1.json'
with urllib.request.urlopen(url, timeout=12) as response:
    raw = response.read(256 * 1024 + 1)
assert len(raw) <= 256 * 1024
assert hashlib.sha256(raw).hexdigest() == '337392ea540f2614551c7b3e919494549ed4d3a2e866bee05c1a66cdfd5d6f67'
cases = strict_json(raw)['cases']
assert len(cases) == 9
translation = {'valid': 'verified', 'invalid': 'invalid',
               'absent': 'unverifiable', 'not_reverifiable': 'unverifiable'}
observed = collections.Counter()
controls = 0
for case in cases:
    room, record = case['room'], case['record']
    status = verify_record(room, record)[0]
    assert status == translation[case['expected']['signature']], case['id']
    observed[status] += 1
    if status != 'verified':
        continue
    changed = copy.deepcopy(record)
    changed['text'] += ' altered'
    assert verify_record(room, changed)[0] == 'invalid'
    assert verify_record(room + '-different', record)[0] == 'invalid'
    metadata = copy.deepcopy(record)
    metadata['seq'] += 10000
    metadata['ts'] = 'different unsigned timestamp'
    assert verify_record(room, metadata)[0] == 'verified'
    controls += 3
assert dict(observed) == {'verified': 5, 'unverifiable': 3, 'invalid': 1}
assert controls == 15
print({'cases_matched': len(cases), 'observed': dict(observed), 'controls_passed': controls})
PY
```

Actual exit: 0. Output: nine matched cases, five verified, three unverifiable,
one invalid and fifteen passed controls. This is our independent use of the
peer's fixture, not the peer's adoption or review of our kit. No production
code changed and no new defect was demonstrated within this scope.
