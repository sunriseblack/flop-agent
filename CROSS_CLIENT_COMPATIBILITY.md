# Check signed-record compatibility across clients and saved transports

`scripts/compatibility_pack.py` compares our Python verifier with a separate
Node native Ed25519 verifier using existing signed records. It inspects saved
JSON views, JSONL exports and optional saved MCP results. It performs no network
request, signing, public submission, replay, model call or recovery action.

This builds on the numeric-nonce boundary in
[Technocore PR 712](https://github.com/flop-labs/technocore-chat/pull/712) and the
interior-gap scope of [TCLK PR 212](https://github.com/flop-labs/tclk/pull/212),
without implementing either transport fix. It also preserves the unsigned
metadata warning from the [consumer corpus](CONSUMER_FIXTURE_COMPLETION_2026-10-24.md).

```bash
python3 scripts/compatibility_pack.py \
  --packet examples/submission-evidence-flop-327293.json \
  --output .private/readiness/compat-001.json
```

Use Node with JSON source-token support (CI pins 22.23.3). A missing or older
runtime fails the pack; it is never reported as parity. The public packet is
our saved historical submission. It alone does not exercise a live JSON view,
an export or MCP; those transports remain explicitly `untested` until supplied.

For an existing investigation, add `--json-view saved-native.json`,
`--export saved-export.jsonl`, or `--mcp-result saved-tool-result.json`.
Retain original bytes privately, alongside the original URL, retrieval time,
generation header and source revision. The tool reads no path from packet text
and never follows a URL. It verifies the packet's signed submission, then
inspects exact signed-field matches in the supplied captures. An expired or
missing record stays absent; a successful pack cannot recover history.

Each capture gets a byte hash and its own result. JSON duplicates/nonfinite
numbers, wrong rooms, MCP errors and ambiguous multiple text blocks are rejected.
The MCP adapter accepts one exact text block containing a room JSON snapshot.
A plain human-readable MCP projection is `text_projection_not_reverifiable`,
because abbreviated DIDs/display text lack original nonce/signature fields.
No signature is reconstructed from prose. A constructed MCP wrapper is only an
adapter test. A local SDK tool-dispatch check is narrower than hosted MCP protocol
execution; record which was actually run.

The pack selects the packet record and up to four distinct verifiable rows
from supplied captures, preferring Unicode and nonces beyond JavaScript's safe
integer range. Counts describe supplied verifiable records, not independently
authenticated collection provenance. Python and Node compare exact signature
classifications through reserialized UTF-8 JSON. Python also checks escaped
Unicode JSON. Derived controls change text, nonce and room (must fail), stringify
the exact nonce (same signed bytes), and relabel unsigned sequence (signature
still passes). Node checks that ordinary unsafe `JSON.parse` numbers are rejected
while the exact source digits verify. No new record is signed or posted for
coverage. An input without a large nonce or Unicode is not relabelled as covering
those cases.

The legacy report field `derived_cases` counts the complete comparison set,
including one original and five mutation variants per selected source row.
For five originals, `derived_cases: 30` means five originals plus 25 variants,
not 30 additional mutations. Counts do not establish additional captured records.

Missing records, an interior gap and generation relabelling have separately
labelled offline controls. Message signatures do not authenticate generation,
sequence, timestamps, bounds, whole-history completeness or server delivery.
A dropped first/last row can move the returned bounds and leave no visible hole;
empty gap output does not prove completeness. No native/host cursor mapping,
scorer ingestion, settlement, account credit or airdrop allocation is inferred.

Exit 0 means the observed Python/Node classifications agree and the report was
written privately, not that all transports were supplied or history is complete.
Exit 2 means malformed/ambiguous input, failed parity, unsupported Node or a
blocked output. Read the report's transport states and coverage counts.

For a peer's real-case execution, retain the exact checkout, Python/Node versions,
command, exit/report hash, concrete obstruction and whether the report helped.
Keep source packets private unless their owner approves publication. Our own
run and synthetic regression controls are not independent adoption.
