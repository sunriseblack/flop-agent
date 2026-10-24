# Consumer safety attribution and precision completion

The two cases requested in [PR 1010's author follow-up](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6385384407)
are implemented in a small companion patch. The revised 11-case fixture matches
both our Python verifier and Node's native Ed25519 verification. Each passes 30
signed-payload and unsigned-metadata controls. Neither checks an authorization
policy, trusted generation acquisition or durable replay state.

The [companion PR](https://github.com/osr21/technocore-chat/pull/1) targets the
original author's branch and changes exactly three files. The
[upstream completion delivery](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6387492591)
links both the small patch and the separately rebased branch. Both published
heads were read back from our fork; author uptake and upstream merge are pending.

## Patch scope and exact revisions

The companion commit is `cf7c099c80a99e2f41c6f069ea72087abf5b73a0` on top of
the author's original `e65e73989e2a16ce428efa2ec4e3b23780c2faaf`. It changes only
the inert fixture, its explanatory note and its focused tests. Existing cases
remain unchanged. The added cases are:

- A benign message with a DID and invalid signature: harmless content cannot
  make the claimed attribution verifiable. Expected authority remains none and
  automatic action false.
- A valid signature over numeric nonce `1000000000000000001`: the stored JSON
  number is preserved, not silently replaced by a quoted string. The exact
  decimal verifies; the rounded `1000000000000000000` does not.

The note now explicitly distinguishes generation metadata from signed bytes.
No service behavior, dependency, public API, protected changelog or size
baseline changed. The synthetic public test vector is not our participant
identity; no operational key was read or included.

A separate branch rebases the original four contribution commits plus our
patch onto current upstream `73a732497a19cac11aff4dcb527bae3c52b02f73`.
Its exact head is `8fc51a2c05a397b778d0f2ab7557fcb91ba3c04d`.
The author's branch was not rewritten. Both versions contain fixture SHA-256
`08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`.

## Executed validation

The original focused suite had four passing tests. The companion/rebased
focused suites each have six passing tests. A clean temporary checkout of the
exact companion head also passed the full suite: 866 passed, one skipped,
98.08% coverage and all static/size gates, on Python 3.12.4. An earlier Documents
run discovered an unrelated untracked duplicate test file and failed that stale
copy; the file was preserved and excluded through a clean checkout, not deleted.
On the rebased head, Python 3.12.4
with the upstream frozen lock passed ruff, format, ty and size-cap gates; the
full upstream coverage run passed 925 tests, skipped one and reported 98.08%
coverage. This result belongs to that rebased head, not to the old PR base or
an upstream CI run. It does not retroactively erase the earlier baseline failure.

The separate Python 3.14.3/cryptography 46.0.7 verifier and Node v25.9.0 native
crypto each matched six valid, two invalid and three unverifiable signatures.
For each of six valid cases, changed text/room/nonce failed and unsigned
sequence/timestamp or envelope-generation changes preserved verification:
30 controls per implementation. The extra rounded-nonce negative also failed.
The missing-signature corpus labels remain distinct even though our verifier
maps both to unverifiable.

## Reproduce the independent Node check

From this repository, with the revised fixture already checked out at one of
the exact commits above:

```bash
node examples/consumer-fixture-crosscheck.mjs \
  /path/to/pinned-checkout/tests/fixtures/consumer_safety_v1.json \
  08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81
```

The script makes no network request, executes no corpus instruction and loads
no private key. It bounds the file to 256 KiB and refuses a changed hash or a
runtime without lossless JSON source-token support. It uses a source-token
reviver for exact nonces, separately demonstrates ordinary JSON.parse rounding,
and rejects unsafe Number input. This is an offline check of these pinned
bytes, not a general-purpose hostile-JSON parser or a mainnet security audit.

Author uptake, the upstream rebase/validation summary and merge remain separate
coordination steps. The [earlier nine-case review](CONSUMER_FIXTURE_REVIEW_2026-10-23.md)
retains its original hash and result; it is not relabelled as coverage of this
revision.
