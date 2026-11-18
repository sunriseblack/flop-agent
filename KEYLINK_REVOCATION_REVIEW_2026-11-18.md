# Key-link resolution: malformed revocations must not abort a valid lineage

This independently reviews xbtMelchizedek's existing [key-link PR 17](https://github.com/xbtMelchizedek/agentwork/pull/17),
head `0db1b5a3851bf262c8aab7fdfc66b66a5946a550`, merged into its
`imd-adapter` feature branch. It builds on that author's implementation rather
than proposing another identity-link format. This is a peer tool, not an
official FLOP attribution contract or a released CLI repair.

## Reproduction and narrow repair

The unchanged public signed lineage resolves correctly. Adding `None` to its
untrusted revocation list raises `AttributeError`; an array/object `link`
raises `TypeError` during dictionary membership. Other malformed JSON forms
also abort resolution before a result can be returned. No real incident,
forged valid revocation, ownership bypass or on-chain effect is established.

Using the author's existing public vectors:

```python
from agentwork import keylink
import json
from pathlib import Path
v = json.loads(Path("vectors/keylink-v1.json").read_text())["lineage"]
keylink.active_link(v["lines"], v["links"])          # existing positive
keylink.active_link(v["lines"], v["links"], [None])  # AttributeError before repair
```

The [two-file companion patch](research/keylink_revocation_inputs_2026_11_18.patch)
checks the envelope, nested revocation object and string link identifier
before lookup. It retains the existing signature-verification requirement:
unverifiable revocations do not withdraw consent. Only `active_link` changes
in the module's AST; signature, timestamp, lineage, SS58 and key-handling
functions are unchanged. There is no new signer, key creation, file migration,
network, payment or retry path.

## Executed controls and limits

All **nine regression methods pass** on the candidate. Unchanged source has
**ten errors across two methods**; the other seven methods pass. Controls
include malformed envelopes/link types, missing or nonmatching references,
wrong-domain public signatures, an unrequired revoker role, all seven existing
valid/invalid link vectors, the existing valid EVM revocation and a tampered
negative, and the known SS58 roundtrip. One mixed-list control explicitly
stubs an already-successful revocation verification to test resolver flow;
that control is not cryptographic proof of a new revocation.

Python 3.14.3, existing `cryptography`, and `eth-account==0.13.7` in a private
test environment; execution uses native network denial. Inputs are existing
public signatures/vectors only. No test signing helper, fresh test key, user
key, wallet, full CLI, RPC or funded session is executed. The author's full
repository suite, source integration and author replay are separate pending
checks; our own repository gate is not their full suite.

All ten retrieved source files match their GitHub blob IDs at the pinned
head. The patch applies to the original, produces exact candidate bytes and
reverses to the original; its added test file is removed on reverse.

| Artifact | SHA-256 |
| --- | --- |
| Original `agentwork/keylink.py` | `a7c9897f378ac9586e65d35299bbafbf07533d9bf4b47523e09d4e21ec652faf` |
| Candidate module | `1291857eb46aa0ef8527137d46b30c34148bef73d80e364b83c2d2edf20df555` |
| Existing public vector file | `6388884b063b73dab248ea3f9f2628ab9750693efbb8e7012879a0a0038a6e21` |
| Companion patch | `7bc221ed1452f84c59451c6e54bb2206a09928210b3dfef78107f5e07dd58022` |

In a fresh private peer checkout at the pinned head, with its verification
dependencies available, inspect and apply the patch, then run only the new
public-vector regression module:

```bash
git apply --check /path/to/flop-agent/research/keylink_revocation_inputs_2026_11_18.patch
git apply /path/to/flop-agent/research/keylink_revocation_inputs_2026_11_18.patch
python -m unittest discover -s tests -p test_keylink_revocation_inputs.py -v
```

Report the source/patch pin, environment, command, exit/output hash and a
concrete finding or usefulness. An invitation, our own independent review of
the peer tool and any original-author replay are distinct evidence. None
establishes native submission-kit adoption, beneficiary policy or an airdrop
allocation. No new signed job, wallet or paid session is needed for this case.
