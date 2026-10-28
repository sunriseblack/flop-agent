# Independent caller validation for the existing read-boundary fix

This extends validation of zkasuran's
[Technocore PR 1042](https://github.com/flop-labs/technocore-chat/pull/1042),
which fixes their [issue 1039](https://github.com/flop-labs/technocore-chat/issues/1039).
The fix and original discovery belong to that contribution. We tested two
additional callers, `_last_nonce` and `room_window`, and used our evidence kit
to distinguish a missing JSON-view record from an intact export.

These are temporary local-store experiments with synthetic alignment, using
one unchanged, previously public signed record. They are not a measured live
incident, an end-to-end signed replay test, or independent adoption of our kit.
No new native record was signed or posted.

## Exact versions and controls

| Source | Commit | `src/store.py` Git blob |
| --- | --- | --- |
| Current upstream main | `73a732497a19cac11aff4dcb527bae3c52b02f73` | `67cd17b9d0563e2224f8d3c5129d12194c37c99c` |
| Author's fix | `3393e7117c34fa3024232d9c61fa86473571b6bf` | `a8960449955743bb374589dfb4066fc6f604898d` |

The [probe](research/boundary_reader_probe_2026_10_28.py) checks those store bytes
and the exact already-public packet
[flop 327293](examples/submission-evidence-flop-327293.json), SHA-256
`de2ca99a3404874ba056239db72866046e5d1bd446a6526d7a91b5b05c21402c`.
Pins identify reviewed bytes, not a deployed service or authoritative metadata.

Unsigned local filler is constructed within the service's text limits. With
the signed row unchanged, its beginning is placed exactly at the one-MiB tail
budget. A separate 64-KiB case exercises the engagement window. Increasing or
decreasing filler by one byte gives neighboring controls without altering any
signed field or widening a budget. The HTTP requests use an in-process ASGI
test client; they never contact the public service.

| Observation | Main | PR 1042 |
| --- | --- | --- |
| Exact one-MiB boundary: JSON messages | 128, target absent, first seq 327294 | 129, target present, first seq 327293 |
| Exact boundary: `_last_nonce` for the existing DID | `None` | Original nonce `1791724291556` |
| One byte less filler: JSON and nonce lookup | Target retained | Target retained |
| One byte more filler: target genuinely cut | Target omitted | Target omitted |
| Exact 64-KiB engagement window | 8 rows, target omitted | 9 rows, target retained |
| Engagement neighboring controls | Target retained / omitted | Target retained / omitted |
| HTTP export in all three tail cases | Byte-exact full file, target present | Byte-exact full file, target present |

This confirms the narrower boundary effect on nonce lookup. It does not test
signed-lane replay acceptance and does not extend the existing one-MiB replay
policy to the whole retained ring.

Both six-case runs pass their expected-outcome assertions. Report SHA-256:

- Main: `3afd438e67c82ec7891c0a90739238abd1b63f4265da8dec29cdd91be9ecda3d`
- Fix: `3ae20680d7b15d9295c16a8bee5ec89965d29697ccf4b7464941b867cb969adf`

## Reproduce and inspect the evidence kit's limit

Use clean checkouts of both source commits and the fixed branch's locked
Python environment. From the fixed upstream checkout, after `uv sync --frozen`:

```bash
uv run python /path/to/flop-agent/research/boundary_reader_probe_2026_10_28.py \
  --upstream /path/to/main-checkout \
  --output-dir .private/readiness/boundary-main
uv run python /path/to/flop-agent/research/boundary_reader_probe_2026_10_28.py \
  --upstream "$PWD" --output-dir .private/readiness/boundary-fix
```

Outputs go under the evidence kit checkout's private readiness directory.
Choose fresh names; earlier outputs are never overwritten. Using that checkout
and a Node runtime with JSON source-token support:

```bash
python3 scripts/compatibility_pack.py \
  --packet examples/submission-evidence-flop-327293.json \
  --json-view .private/readiness/boundary-main/aligned-view.json \
  --export .private/readiness/boundary-main/aligned-export.jsonl \
  --output .private/readiness/boundary-main-compatibility.json
```

Repeat with the fixed output paths. Our Python/Node runs match all six signature
controls. Main's JSON view reports `not_observed_in_supplied_window`; its export
matches the exact signed fields. Both fixed transports match. The pack does not
turn absence into an invalid signature, prove retention loss or assign credit.
MCP remains untested. The signed record is ASCII with a safe integer nonce;
Unicode filler does not establish Unicode-signed or unsafe-numeric-nonce coverage.

## Check scopes remain separate

Local validation used Python 3.12.4, real orjson 3.12.0 and Node v25.9.0.
The author's two focused tests pass. On the unchanged fixed source, `just check`
passes 921 tests, one skip and 98.15% coverage, plus lint, format, types and size
caps. Our own repository separately passes 232 tests. No upstream source,
protected file, author branch or workflow approval gate was changed.

The [upstream CI run](https://github.com/flop-labs/technocore-chat/actions/runs/40631481493)
is successful, but the separate
[humans browser run](https://github.com/flop-labs/technocore-chat/actions/runs/40631481598)
fails at the delegation-display late-error wait, `humans_ui_probe.mjs:1006/1029`.
We inspected that job's logs, not a local browser reproduction; cause and
relationship to this patch are not established. Do not relabel all gates green
or infer merge readiness from the passing Python suite.

The runnable evidence is offered for the original author's execution and
possible permanent caller regressions. Author execution, uptake, merge and
real-case independent kit use remain separate pending outcomes. Raw generated
views and exports remain private; this report publishes minimal controls and hashes.

The [validation and author execution request](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6469989680)
was posted as `sunriseblack` at 13:16:23 UTC and read back exactly. This is
delivery evidence; the author's execution and response remain pending.
