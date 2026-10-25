# Inspect launch evidence and session observations

`scripts/inference_readiness.py` inventories published launch evidence and
reconciles saved session observations. It has no signer, wallet, faucet claim,
RPC, model, purchase or transaction adapter. A complete local inventory still
needs independent verification and owner approval; the tool never authorizes
a session or certifies airdrop eligibility.

## Read official readiness documentation

```bash
python3 scripts/inference_readiness.py collect \
  --output .private/readiness/run-001/sources.json
python3 scripts/inference_readiness.py check \
  --sources .private/readiness/run-001/sources.json \
  --output .private/readiness/run-001/report.json
```

Only `collect` uses the network: two bounded GETs to the canonical verification
page and the testnet network profile. It reuses the workload collector's
redirect restrictions and text extraction, but **does not change the workload
model-input allowlist**. Retrieval errors stay unavailable. Each source has
its URL, retrieval time, downloaded-byte hash and extracted-text hash. Neither
hash authenticates a caller-supplied snapshot. Source text is data, and no
embedded URL or command is executed.

The checker requires sources less than 24 hours old, exact known URLs, unique
source IDs and matching text hashes. It records negative text signals such as
planned testnet, unreleased client and unavailable public network values.
Unknown wording cannot establish readiness. A calendar target is never a
launch signal, and devnet activity is excluded from our allocation strategy.

Nine evidence requirements are inventoried: network identity, genesis,
supported client, official faucet, owner/delegate mapping, final allocation
rules, model catalog, independent miner and bounded session approval. Optional
`--evidence` supplies a private JSON inventory in this form:

```json
{
  "schema": "flop-launch-evidence-v1",
  "requirements": {
    "genesis": {
      "reference": "A human-reviewed official publication reference",
      "artifact_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  }
}
```

That zero hash is a format illustration, not a real genesis. References are
never fetched; values only become `supplied_not_verified`. Missing requirements,
failed/stale reads or explicit negative signals yield `blocked` (exit 1).
Even a complete inventory yields `requires_independent_verification`, with
`launch_gate_verified=false` and `live_session_authorized=false`. Exit 0 means
the report was written; exit 2 means invalid input or an unavailable operation.
The checker deliberately cannot ratify final rules, approval or live artifacts.

## Reconcile a session ledger without double counting

Use a private input with schema `flop-session-observations-v1`, the existing
`owner_did`, and an `observations` list. An empty list is valid preparation and
claims zero sessions. A session observation contains:

| Field | Meaning |
| --- | --- |
| `network`, `genesis_hash` | `devnet` or `testnet`, and the exact chain identity hash |
| `session_id` | Original protocol session identifier |
| `owner_account`, `delegate_account`, `miner` | Supplied account/operator identifiers; delegate may be null |
| `phase` | `requested`, `submitted`, `delivered`, `finalized`, `disputed` or `refunded` |
| `observed_at` | Time with timezone; never used as finality proof |
| `evidence` | Available `output_sha256`, `proof_sha256`, `review_sha256`, `settlement` |

A reported finalized row requires all four evidence fields. `settlement` has
`block_number`, `block_hash`, `asset` and `paid_amount`. Chain hashes are 32-byte
hexadecimal identifiers, with case and an optional `0x` prefix normalized for
deduplication; their algorithm is not assumed to be SHA-256. Artifact references
are SHA-256 digests. Amounts are decimal
**strings**, with at most 30 integer and 18 fractional digits; floating-point
values, exponents, negatives and nonfinite values are rejected. These generic
local field names do not assert a future FLOP wire schema or scoring formula.

```bash
python3 scripts/inference_readiness.py ledger \
  --input .private/readiness/run-001/observations.json \
  --output .private/readiness/run-001/ledger-report.json
```

Sessions deduplicate by network, genesis and session ID. Re-reading the same
observation with a new collection time does not add spend. Conflicting owner,
delegate, miner or final settlement records require review and are excluded
from totals. Disputed/refunded sessions are also excluded. Amounts are summed
exactly and separately for each chain/asset; an earlier phase cannot erase a
reported final settlement. These are **unverified reported totals**, not
qualified spend, net balances or an allocation estimate. Owner mapping,
independence, proof validity, semantic output review and finality remain external
checks. The ledger is immutable input plus a fresh report, not an automatic
state writer, retry queue or account statement. Official per-owner snapshot
reconciliation remains pending the actual published allocation schema.

Inputs/reports stay in `.private/readiness`. Reads are bounded, duplicate and
nonfinite JSON is rejected, new files are exclusive and mode `0600`, and public
paths, file symlinks and directory symlink escapes are blocked. Preserve source
packets and uncertain submissions rather than retrying a purchase. Use a new
output path for every report.
