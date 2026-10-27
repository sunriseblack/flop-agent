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
