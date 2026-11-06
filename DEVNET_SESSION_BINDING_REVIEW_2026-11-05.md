# Devnet receipt example and raw transaction binding

We independently reviewed wyc4t's existing FLOP-EXP-001 public third-party
settlement example on network issue 49. The original CLI passes all 14 checks.
A changed output commitment in the raw transaction also passes all 14 checks
when its two displayed transaction hashes are recomputed and the separately
decoded call is left unchanged. The signature checks use that separate call.
[Original example](https://github.com/flop-labs/network/issues/49#issuecomment-6630270608)

The proposed patch decodes the raw extrinsic with runtime metadata fetched
at the settlement block. Receipt checks consume those decoded arguments. It
also checks the supplied call and signer against the raw decode, exact
extrinsic round-trip bytes, and the header hash and number. The original
source, captures, metadata and modified fixture packets remain private.
[Patch](research/devnet_session_binding_fix_2026_11_05.patch)
· [Regression program](examples/devnet-session-binding-review.mjs)

## Verified case

The existing channel is
`0x833afcbb7ec3f3c658f17e65fd5b1149656b666e83222f7fe524fe06307efe7d`.
Settlement block 1,570,506 has hash
`0x384335a43151a7b64e63c98fe87683b875ad15b15ec08d04b3ce2270ceccf10e`
and extrinsic index 2. This is an example belonging to other participants.

The original ZIP SHA-256 is
`aa0c00cd39a340da27c61c17108696227390d2150ed9bc8d7241a0d18c2f12d1`.
The original checker hashes to
`a5a114c211bb11ea455df15420547a7d21aafde14048e5765e2814e718f9f547`.
The patched checker hashes to
`0836ee9185157b83cae8630ad1ea8aab77161a097d8b3407cba5f04629a4e1dc`.
Historical metadata is 470,131 decoded bytes with SHA-256
`4a144b9e881f9c086b26f3225ace9958593acf393c8194a9f367059f6948d8dd`.
Hashes establish the reviewed artifact versions.

## Results

| Control | Original checker | Patched checker |
| --- | --- | --- |
| Original public receipt | All 14 checks pass | All 18 checks pass after adding historical metadata |
| Raw output commitment changed, displayed transaction hashes recomputed | All 14 pass | CLI exits 1, decoded-call, root and miner-signature checks fail |
| Raw and supplied decoded output changed together | Signature/root checks reject | Signature/root checks reject |
| Extra raw trailing byte with recomputed hashes | All 14 pass | Round-trip check rejects |
| Unrelated raw `0x00` with recomputed hashes | All 14 pass | Decode refuses |
| Header number changed | All 14 pass | Header check rejects |
| Call object property order or capture timestamp changed | Remains valid | Remains valid |
| Missing historical metadata | Earlier format accepted | Explicit migration refusal |

The public regression program passes all 24 cases. It also covers malformed
metadata, truncated bytes, altered receipt/witness signatures, mismatched
signer and call names, wrong block coordinates, changed genesis and escrow.
Malformed signature encodings can throw; the real CLI refuses those inputs
with exit 1. Two early assertions expected a boolean for those malformed
encodings and were corrected to accept the observed refusal.

The final patched normal CLI was also run in fresh read-only capture mode
against the historical RPC and explorer at 15:56:34 UTC on November 5. All
18 checks passed. Environment was Node 25.9.0/macOS arm64, with the author's
locked `@polkadot/api` and types 17.0.2 and util/crypto 14.0.3. Replay and
regressions passed with network access denied. Patch application, exact
resulting source bytes and Node syntax checks passed.

## Reproduce without changing the preserved packet

Download the author's ZIP to an ignored private directory and verify its hash
above before extracting it. From the original `flop-exp-001` directory run
`npm ci --ignore-scripts --no-audit --no-fund`. Preserve its original files.
The patch uses zero context and requires `--unidiff-zero`. The following
commands run from this repository's root after placing that
original directory at `.private/devnet/review/flop-exp-001`.

```bash
set -eu
mkdir .private/devnet/review/patched
cp .private/devnet/review/flop-exp-001/verify-session.mjs \
  .private/devnet/review/patched/verify-session.mjs
git apply --unidiff-zero --check --directory=.private/devnet/review/patched \
  research/devnet_session_binding_fix_2026_11_05.patch
git apply --unidiff-zero --directory=.private/devnet/review/patched \
  research/devnet_session_binding_fix_2026_11_05.patch
```

The original fixture lacks `rpc.metadataHex`. Capture a fresh copy into the
separate patched directory using the script's existing read-only path. Its
reads target the original fixed channel and historical block.

```bash
FLOP_CLI_ENTRY="$PWD/.private/devnet/review/flop-exp-001/package.json" \
  node .private/devnet/review/patched/verify-session.mjs --live
python3 - <<'PY'
import json
from pathlib import Path
base = Path('.private/devnet/review/patched')
metadata = json.loads((base / 'capture.json').read_text())['rpc']['metadataHex']
with (base / 'historical-metadata.hex').open('x') as output:
    output.write(metadata + '\n')
PY
DEVNET_PACKET_DIR="$PWD/.private/devnet/review/flop-exp-001" \
DEVNET_METADATA_FILE="$PWD/.private/devnet/review/patched/historical-metadata.hex" \
DEVNET_PATCHED_CHECKER="$PWD/.private/devnet/review/patched/verify-session.mjs" \
  node --test examples/devnet-session-binding-review.mjs
```

The regression program verifies the original source, capture, lock, patched
source and decoded metadata hashes before loading either checker. It loads
the unchanged verification definitions before their CLI entry points in
a private temporary module and removes the temporary copies. Supplied
object key order remains immaterial. Its inputs are the original public
fixture and caller-specified metadata/checker paths.

## Trust boundary and next step

This improves local consistency between a serialized transaction, its supplied
decoding and signed receipt fields. Historical signing keys and runtime
metadata remain RPC assertions. The outer transaction signature, transaction
and event inclusion, authenticated historical state, AlephBFT finality and
inference correctness remain outside this example's checks. The original
feature request still needs supported proof and trust-bootstrap tooling.

The patch extends the existing example with credit to wyc4t. The remaining
steps are a versioned author integration and a supported inclusion and
finality example from the project. Replaying this public third-party receipt
is an engineering contribution, with no own-session or allocation claim.

The pinned review was delivered and read back exactly under sunriseblack on
November 5. Independent author execution subsequently confirmed the bounded fix.
[Author follow-up](https://github.com/flop-labs/network/issues/49#issuecomment-6662712942)

## Independent author replay, November 6

[wyc4t executed revision 4173e77](https://github.com/flop-labs/network/issues/49#issuecomment-6682322204)
on Linux x86_64, Node 24.22.1, API/types 17.0.2 and util/crypto 14.0.3.
The original and changed-raw CLI inputs both passed the original 14 checks.
The metadata-enriched original passed all 18 patched checks, while the same
raw mutation exited 1 with decoded-call, root and miner-signature failures.
The unchanged 24-case regression passed. Their socket-denied replay reused
previously installed dependencies after an offline install cache miss; it
does not establish a successful clean install or fresh live capture.

The [supplied review bundle](https://github.com/user-attachments/files/34474591/FLOP-EXP-001-independent-binding-review-2026-11-06.zip)
has SHA-256 `6c0592343d38ba1da553187ce3b6d208c19f1294cc2d3a72f61e1b52921a98b2`.
We verified all 45 manifest entries and matched the original ZIP, patch,
regression program and both checker versions to our pins. The four supplied
CLI reports agree with their execution summary. This is our verification of
their preserved execution evidence, not another local execution or pilot.
The full bundle and source packets remain private in this checkout.

No additional defect was reported in this bounded review. The
[acknowledgment](https://github.com/flop-labs/network/issues/49#issuecomment-6686843209)
was delivered and read back exactly. The author plans a separately versioned
extension while preserving the original evidence. Integration/publication of
that extension and the original inclusion/finality request remain open.
RPC-trusted metadata/keys and the trust boundaries above are unchanged.
