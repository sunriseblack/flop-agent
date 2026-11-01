# Offline receipt-consumer comparison for an existing fixture exchange

Osraka [asked which existing consumer expectation format to compare](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6555779806)
after adding binary-output controls to `technocore-safe-agent`. We reviewed
current peer source `d858ec897cc10b283f8fc8fbea69fa1bd099ca25`, the merge of
[PR 26](https://github.com/Osraka/technocore-safe-agent/pull/26), and its
contribution/security policies. That is newer than the original `97d737f`
proposal. This is independent source/CLI validation on public synthetic peer
fixtures, not a real work attestation or independent adoption of our kit.

## Distinct inputs and supported conclusions

| Boundary | Our submission evidence kit | Peer `work-evidence` |
| --- | --- | --- |
| Signature profile | Original Technocore `room\|nonce\|text` | Project-local `work-receipt-v1` and countersignatures |
| Expected job fields | No repository/commit/argv/timeout expectation parser | Exact operator-chosen repository, commit, argv, timeout, issuer and required verifiers |
| Original output/artifact bytes | SHA-256 comparison and separate literal-hash mention in signed room text | Signed stdout/stderr byte counts and hashes |
| Expectation authority | A caller's expected hash does not establish signer approval | Operator expectation is unsigned; a match does not authenticate an agreement |
| Work execution, acceptance and payment | Not established | Not established by inspection; agreement/payment remain `not_assessed` |

The packet formats are not interchangeable. We have no authenticated job
expectation schema to recommend as a drop-in replacement. Comparing the peer's
existing operator-local expectation format is a useful baseline for exact
fields and bytes, with its unsigned-input boundary retained. A manifest hash
identifies bytes; its approval, role and agreement context need separate evidence.
An existing signed offer/job reference can be inspected only after obtaining
its actual original fields and determining exactly what manifest it binds.
A URL, job label or digest alone does not supply that agreement. No new message
or job should be manufactured for a fixture demonstration.

## Executed checks

Environment: macOS, Python 3.14.3, cryptography 46.0.7, certifi 2026.2.25.
We used the reviewed source module through `PYTHONPATH`, not a package install.
`sandbox-exec` denied `network*` for the peer tests and each CLI invocation.
Dependencies were already installed. No dependency installation, paid API call,
live pilot script, production identity or Keychain operation was needed.

The peer's 24 focused `test_work_evidence.py` tests pass with no skips.
They include existing valid non-UTF-8 output and same-length-byte negatives;
those are author-provided regressions, not defects discovered or fixed by us.
The output-bundle unit test runs its own explicit local `print` control in a
temporary repository; no received job command was executed by the inspector.

Nine additional real source-CLI invocations use the peer's existing public
fixture, with mutated copies kept privately:

| Input | Status | Exit |
| --- | --- | --- |
| Original expectation, receipt and both streams | `matches_local_expectations` | 0 |
| Omit stderr | `incomplete` | 1 |
| Existing tampered receipt | `invalid_receipt` | 1 |
| Remove stdout's trailing newline | `does_not_match` | 1 |
| Change stdout to a different byte sequence of the same length | `does_not_match` | 1 |
| Replace one stdout byte with non-UTF-8 `0xff` | `does_not_match` | 1 |
| Change only the expected argv | `does_not_match` | 1 |
| Supply a directory as stdout | `input_error` | 2 |
| Omit the receipt | `incomplete` | 1 |

In every non-input-error report, agreement/payment remain `not_assessed` and
independent execution remains `not_established`. The peer checkout stays clean.
The non-UTF-8 mismatch above is against the original ASCII receipt; the
positive valid-binary-receipt check belongs to the peer's focused unit suite.
No new counterexample emerged within these checks. We did not run the full
265-test suite, build/install checks, hosted or local MCP/stdio tests, or a
production end-to-end pilot. Existing author/CI reports retain their own scope.

Our kit's existing artifact function separately accepts the exact stdout bytes
against the caller's expected hash and rejects all three changed copies without
UTF-8 decoding. In all four cases `hash_mentioned_in_signed_text` stays false:
the unchanged historical native record does not mention this unrelated artifact.
That observation must not become a claim that its signer approved the work receipt.
Our 36 submission-evidence tests also pass; no implementation was changed.

## Reproduce the positive source-CLI and missing-evidence case

From a reviewed peer checkout at the exact pin, using its supported dependencies:

```bash
PYTHONPATH=src python3 -m technocore_safe_agent work-evidence \
  --expectation fixtures/work-evidence-v1/expectation.json \
  --receipt fixtures/work-receipt-v1/valid.json \
  --stdout fixtures/work-evidence-v1/stdout.txt \
  --stderr fixtures/work-evidence-v1/stderr.txt

PYTHONPATH=src python3 -m unittest discover -s tests -p test_work_evidence.py -v
```

The first command reports `matches_local_expectations`, exit 0. Omitting the
`--stderr` flag and value yields `incomplete`, exit 1. Using the existing
`fixtures/work-receipt-v1/tampered-output.json` yields `invalid_receipt`, exit 1.
The full expectation, schema, source code and fixtures remain in the original
author's repository; no adapter, new receipt profile or duplicate implementation
is introduced here.

Reviewed SHA-256 pins:

- `src/technocore_safe_agent/work_evidence.py`: `4cc00b096ab1ac7485ab4c257065e4e8532d9168aced0a2ac71151bf66d69b8e`
- `src/technocore_safe_agent/work_receipt_verifier.py`: `39554dbe9c400a838aa61908a0fc3991175de194545f4d0e818b6d5f32e24f98`
- `tests/test_work_evidence.py`: `9244e834720a370bcfb7b27804a05f77409784eea758b5e024953bd25fcbe62b`
- Public expectation fixture: `b31015de8f139c8430485e8be729ae395532010777fe27052b29df67dafd50b9`
- Public receipt fixture: `c835ed35fcbaccec65629334cef3f9c39a4647f113bdf4641f3f048e923c14be`
- Original stdout, 11 bytes: `daedfbec6dd45d78c5723aae1796914d3171c321a96986b09804f0a513c6983d`
- Empty stderr: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The private run record hashes to
`37c86c3ad15f3a0c7173f78e8cbdd527d60fef4135b69ace34299e7b2783f996`.
It contains local invocation paths, so only reviewed metadata is published.
Next trigger: the original author's substantive response or an already-existing
real signed offer/job artifact. That artifact has not been supplied; no real-case
kit execution is invited or counted on these synthetic fixtures.

The [independent results and existing-artifact question](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6559450133)
were posted as sunriseblack at 14:42:34 UTC and read back exactly. The response
links publication `ffe4eef`, whose hosted checks pass. Participant response is
pending; this delivery does not add a real-case execution or kit adoption.
