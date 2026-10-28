# Missing explorer data can become a zero-spend verdict

A bounded offline review of community tool
[danenright/flop-agent-runner](https://github.com/danenright/flop-agent-runner/tree/547b4d6fa419311bcfc4c6dc157f72d0fe8974bb)
found that its read-only `credit` report conflates unavailable data with an
explicit zero. This is a third-party diagnostic defect, not a FLOP server
finding or evidence that the author's reported live zero is incorrect.

The original author has separately reported broker attribution on
[Yellow Paper issue 172](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6431777415).
That devnet observation and future testnet policy remain separate questions.
An explorer projection is not independent chain-finality or allocation proof.

## Exact source and reproduction

Reviewed commit: `547b4d6fa419311bcfc4c6dc157f72d0fe8974bb`.

`flop_agent.py` Git blob: `b816eb943289f7a00bf05b6f71256e37f35645e4`.

Source SHA-256: `5eee57d8ebde22a6454b6e0f5e7be3d792522991c83f452ef5ec79af3161cef7`.

With that exact file in an existing peer checkout:

```bash
python3 research/runner_credit_probe_2026_10_27.py /path/to/flop-agent-runner/flop_agent.py
```

The [probe](research/runner_credit_probe_2026_10_27.py) checks the complete source
hash before compiling only four reviewed functions. Identity resolution is
stubbed, and every HTTP result is a local fixture. Module initialization,
key loading, signing, account funding, purchases, peer state and actual
network calls are excluded. Python 3.14.3 on Darwin reproduced all six cases.
Its assertions describe the original behavior; a passing probe is not a fix.

| Supplied summary | Result at the reviewed revision |
| --- | --- |
| HTTP 200 with explicit zero amount and counts | Zero-spend verdict, as expected for this control |
| HTTP 404, no summary | The same verdict and numeric zeros |
| HTTP 404, but another response lists a paid channel | Zero counts and a denial alongside that paid channel |
| HTTP 200 with missing summary fields | Unknown amount but a zero settled count and denial |
| HTTP 503 | Raises an error, preserving the unavailable state |
| HTTP 200 with one settled channel | Reports one, as expected for this control |

The report SHA-256 from this execution is
`2d4445939f9dae18a14407d6852c6075dadea614b867a0b928e7a9eb33a39103`.
It contains synthetic fixture responses, not fetched account state.

## Owning invariant and next check

`explorer_fetch()` returns `None` for 404. `credit_report()` replaces that
with a fabricated zero-valued summary. A separate `int(value or 0)` converts
missing settled-count fields into zero. Neither path establishes the absence
of settled spend. A route mismatch or schema change can therefore produce a
confident negative diagnosis.

Preserve unavailable or malformed summaries as unknown, or fail with an
explicit diagnostic. Keep an explicit, validated 200/zero response as the
zero control; a paid recent-channel row should not coexist with an unqualified
absence verdict. Final scoring language should retain the distinction between
an explorer observation, published policy and a future allocation file.

The reproduction is offered to the original author for repair and verification.
No author-branch mutation, fix acceptance, merged change, independent use of
our evidence kit or FLOP session is claimed.

[Issue 1](https://github.com/danenright/flop-agent-runner/issues/1) was delivered
under `sunriseblack` at 13:24:45 UTC and read back exactly. The GitHub connector
rejected creation with 403; the existing CLI connection then succeeded after
checking that no issue had been created.

## October 28: a tested candidate for the original author

The peer's main remains `547b4d6fa419311bcfc4c6dc157f72d0fe8974bb`, with no
reply on issue 1. We prepared a [two-file candidate patch](research/runner_credit_unknown_fix_2026_10_28.patch)
for that exact revision. This is new repair material on the existing issue,
not a new upstream PR, author-branch mutation or claim of accepted repair.

The patch removes the fabricated zero fallback and validates the amount and
both required count fields before forming a report. Missing summaries,
incomplete or malformed fields, unsupported amounts and an explicit zero
settled count alongside a matching paid/settled channel produce `AgentError`.
An explicit valid zero remains zero, a positive summary remains positive,
and HTTP 503 remains an error. The `credit` CLI fails with exit 1 and no
successful zero report when the summary is unavailable; its key-loader
negative verifies that this read-only path does not load a signing key.

The patch leaves the peer's existing float display, account-mapping logic,
positive credit language and broker-policy wording unchanged. Those remain
separate limitations: a successful explorer report is not authoritative
future airdrop policy or finalized chain/allocation proof. Other malformed
account/channel shapes are outside this focused summary-validation repair.

### Reproduce in a clean disposable checkout

Download the patch from an immutable publication revision and verify:

```text
patch SHA-256: 463403e256535d190fd68a1bee5738f4a5aef783c07c73cfd4122a46f6440e86
patched flop_agent.py SHA-256: 1a43da469737073c424b2d7ea7f034ad96efbb8caa156837de51bea6a5fbee0f
new test file SHA-256: f9d16e651f2f5ddcdcad0b3e885df506e3a90a021fe16eb40cf940800593524a
```

In that clean peer checkout, at the pinned commit, with its test dependencies
installed and `candidate.patch` referring to the verified download:

```bash
git apply --check candidate.patch
git apply candidate.patch
python -m unittest discover -s tests -v
```

These tests use mocked GET responses and existing public test-account fixtures.
They do not contact an explorer, execute a funded cycle, load our participant
key, create another participant identity or prove a live account result.
The original six-case diagnostic above intentionally asserts the old behavior
and is source-pinned; do not run it as a fixed-source acceptance test.

### Checks and acceptance boundary

Python 3.12.4 on Darwin, with the peer's pinned `cryptography==50.0.0` and
optional `py-sr25519-bindings==0.2.4`, passes the original 76 tests. Against
unmodified source, the five new methods expose 20 failed subcases and one
overflow error, while their explicit-zero/positive/503 control method passes.
After applying the exact source patch in a second disposable checkout, all
81 tests pass in 0.101 seconds. Source and test bytes match the candidate copy;
`git apply --check`, Ruff F checks and `git diff --check` pass. The added
amount controls include 400- and 5,000-digit strings to exercise unsupported
conversion paths without accepting a fabricated zero.

These are our offline results. Author application, independent execution,
upstream CI and accepted repair remain pending. They are not evidence-kit
adoption or a FLOP inference session. The next useful action is the author's
review/application or a concrete counterexample, followed by validation of
the actual accepted source.
