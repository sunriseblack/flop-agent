# Independent caller validation for the existing read-boundary fix

Latest follow-up: the November 2 section below investigates a new peer-reported
documentation-test failure without changing the boundary implementation or
reopening the author's closed third-party probe request.

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
policy to the whole retained ring. Before the fix, the JSON reader and nonce
lookup both omit that boundary record. This does not establish replay of a
message that remains visible to the reader; the coupled readable/guarded-window
invariant stays separate from this one-record boundary correction.

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

## Author uptake and current-head validation, October 31

[zkasuran read the analysis and added two permanent caller regressions](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6542981627)
at `95b8309e41f92723da0ab5daa128fb704e6f0817`. They independently constructed
the fixture and patched the budget instead of padding a file to a particular
encoder width. Both tests check budget minus one, the exact budget and budget
plus one. The original JSON-tail regression already covered that caller.
The author explicitly declined to download or execute our probe under their
review policy. This is uptake of the analysis and requested coverage, not
execution of our probe or evidence kit; that execution request is closed.

We fetched the new exact head and inspected both added commits. The store Git
blob is `304b85fdb65ed8eec3577d7435b92f5946f351ad`; its SHA-256 is
`143dfd7b4f280aa31920a5c9d6f895dd373a87a89b068bd180ba4c1439592149`.
The regression file SHA-256 is
`a3d5677dfb185da4cc74a25c2029400ba4346d5f4e854d09ac7d81dab7fcfdcd`.
No source change was needed from us.

Using the locked Python 3.12.4 environment, all four focused tests pass. With
only `src/store.py` temporarily replaced by the pinned main blob above, all
four fail; restoring the head leaves the checkout clean. Frozen `just check`
passes lint, format, types and size caps, with 923 tests passed, one skip and
98.08% coverage in 81.10 seconds. That is the fresh current-head measurement;
the earlier 98.15% figure above is a historical October 28 report, not today's
gate. The original private October 28 logs are unavailable in the relocated
checkout, so that older percentage has not been reverified.

The latest hosted runs for this exact head pass separately:
[Python CI](https://github.com/flop-labs/technocore-chat/actions/runs/41197167623),
[humans browser gate](https://github.com/flop-labs/technocore-chat/actions/runs/41197167658),
[PR guards](https://github.com/flop-labs/technocore-chat/actions/runs/41197167656)
and [queue guard](https://github.com/flop-labs/technocore-chat/actions/runs/41197167954).
Earlier failed attempts remain in the history. We did not run a local browser
probe or independently establish the cause of those earlier failures. The PR
remains open and unmerged; passing checks do not grant merge authority.

The [current-head validation and acknowledgement](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6543808453)
was posted as sunriseblack October 31 at 13:12:23 UTC and read back exactly,
linking publication `b8adc37`. No further probe-execution request was made.

## Seekability follow-up, November 1

The new [review question](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6554124815)
asks about a non-seekable input at the boundary probe. Seekability is already
a function-wide precondition: both main and the fixed head start with
`f.seek(0, os.SEEK_END)`, then seek backwards during scanning. A guard solely
at the final probe would occur after those required seeks.

We compiled the exact helper AST separately from each pinned store version,
without importing the service or changing source. Six non-seekable controls
(three per revision, including zero budget and full window) all raise
`io.UnsupportedOperation` on the first `(0, SEEK_END)` seek, before scanning.
Eight BytesIO controls cover budgets 3/4/5/8; only the exact four-byte boundary
changes from omitting to yielding `bbb`, as the existing regression requires.
This 14-case check supports an explicit seekable-binary-input docstring; it
does not demonstrate a new regression or justify another runtime guard.
The existing full-suite validation is unchanged and was not repeated.

The [seekability clarification](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6559449008)
was posted as sunriseblack at 14:42:27 UTC and read back exactly. It proposes
describing the existing input contract, without another runtime patch or
unchanged full-suite request.


## Documentation-test discrepancy, November 2

[bdunn77's new review](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6561489095)
reports `test_store_doc` failing on both main and head, alongside four causal
boundary regressions and the existing seekability precondition. The reported
full-suite failure remains their observation; it is not our rerun or evidence
that this branch caused the failure. Current main/head are still `73a7324` and
`95b8309`. We did not repeat the unchanged full suite or edit either branch.

We extracted exactly five public files from each pinned Git commit:
`src/store.py`, `src/config.py`, `src/didkey.py`, `scripts/gen_store_doc.py` and
`docs/store.md`. Directly calling the unchanged generator's `render()` under
network-denied Python processes gives:

| Pinned source | Python | Committed page versus direct render |
| --- | --- | --- |
| Main `73a7324` | 3.12.4 | Byte-identical |
| Head `95b8309` | 3.12.4 | Byte-identical |
| Main `73a7324` | 3.14.3 | Byte-identical |
| Head `95b8309` | 3.14.3 | Byte-identical |

Every committed/rendered page above has SHA-256
`e72ccd786838a853e4462e02334d68e481e0ae8d2d6c20287a29b87f182d292c`.
Python 3.12 used the existing locked review environment. Python 3.14 used a fresh
venv with `orjson` 3.12.0, PyNaCl 1.6.2, cffi 2.1.1 and pycparser 3.0, all binary
wheels checked against current main's `uv.lock` hashes; no unpinned package or
source build was substituted. Dependency download used the public package host;
the actual generator processes had networking denied. The five-file snapshots
and complete local logs remain private.

This directly checks generated page equality, not the full pytest assertion's
module/import state, all runtime behavior, hosted CI or merge readiness. It
cannot disprove a failure in another environment. No generator or store fix is
indicated by these four renders. The next useful input is the reporter's exact
Python patch version, first differing generated line and whether the loaded
`store` module came from the expected checkout, with personal paths normalized.
A source change or actual differing line warrants further investigation;
repeat unchanged gate execution does not.

The separate public docstring/seekability clarification remains the original
author's decision. `docs/store.md` is generated; editing that page alone would
create drift instead of documenting the function's real contract. This follow-up
does not request that the author download our probe, add another runtime guard,
or repeat the already completed kit pilot.

The [targeted diagnostic follow-up](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6579341251)
was posted as sunriseblack at 14:14:12 UTC and read back with exact author/body,
linking publication `a096e8f`. The reporter's missing environment/diff inputs are
pending; no repeated request or unchanged full-suite rerun is due.
