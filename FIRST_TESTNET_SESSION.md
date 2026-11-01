# First useful testnet inference: prepared, awaiting verified launch and approval

The first proposed session has a concrete use: produce an evidence checklist
that distinguishes draft allocation rules, implemented grant behavior and a
particular owner's authoritative allocation. We will use its answer in our
launch/attribution review before scaling, rather than generate nominal demand.

The prepared existing workload task is `implementation-gap`:

> What evidence would distinguish draft allocation rules from an implemented grant and a particular owner's allocation?

The selected request is bound to job SHA-256
`ba12c9b415f175bc686fb0db6f8b9ea29e28631d5a4fac280b7f6f3347d77d8d`.
The fresh request file is 6,602 UTF-8 bytes and hashes to
`85f4ea494955490a9da2ab61517463d761dddc32f06da9fbba750d63137da243`.
It uses two pinned Yellow Paper excerpts totaling 4,954 characters. The source
was retrieved November 1 at 17:33:45 UTC. Source snapshots, prompts and any
future outputs remain private.

The separate `identity-binding` abstention case is prepared as a safety check;
it is not a second authorized paid session or a wallet-address generation task.
No model call, provider API request, purchase or signed session has occurred.

## Proposed bounded session

| Limit | Proposal |
| --- | --- |
| Sessions | One |
| Automatic retries/replacement requests | Zero |
| Input | At most 16,384 UTF-8 bytes and 4,096 tokens under the selected model's actual tokenizer |
| Output | At most 768 tokens and 8,192 UTF-8 bytes |
| Observation time | 120 seconds; a timeout becomes an uncertain state requiring read-only reconciliation |
| Spend | Not set: exact test-token asset, units, quote and maximum amount need approval before submission |
| Provider/model/miner/client/network/genesis | Unselected and unverified |

These are operator-side proposed bounds, not assumed FLOP API fields. The saved
harness request is not a FLOP wire request. If a model's tokenizer exceeds the
input cap, stop and review the input; do not silently create multiple sessions.
A timeout or uncertain write must not trigger another purchase.

## Acceptance and actual consumption

The returned JSON must name the exact task and job hash and use the existing
workload schema. Check byte/token limits before parsing, reject extra/action
fields, fabricated citations, changed bindings and malformed output. Exact
quotes must occur in the pinned excerpts. The owner then reviews whether each
quote supports its claim and whether the answer correctly separates:

1. Draft or proposed allocation rules.
2. Pinned implemented runtime/grant behavior and finalized evidence.
3. The official owner allocation record and parameters, without inventing an award.

Consume an accepted answer by incorporating its reviewed evidence requirements
into the launch checklist. A mechanically valid answer is not authority to
submit, transfer funds, publish a correction or assign credit. Publication of
the answer requires its own exact-version review/approval.

Local synthetic controls accept the structural/citation positive and reject a
wrong job hash and fabricated quote. A false entitlement claim with a real
quote still passes mechanical matching, so human semantic rejection remains
necessary. An 8,193-byte sample exceeds the proposed byte cap; this arithmetic
check does not implement or verify live transport budget enforcement. Token,
time and spend enforcement must be checked in the eventual client before
submission. These are preparation checks, not model results or useful inference
already delivered.

### Bounded review of a saved answer

`scripts/first_session_output.py` now applies the 8,192-byte bound before
UTF-8 decoding or JSON parsing. It requires exactly one checked workload job
and a separately selected expected job hash, rejects duplicate/nonfinite JSON,
and reuses the workload's schema, citation and abstention checks. It accepts
the answer JSON itself, not an arbitrary provider envelope. A future verified
client must save the exact answer bytes while separately retaining its original
response/usage evidence; no envelope extraction is implemented here.

```bash
python3 scripts/first_session_output.py \
  --jobs .private/workload/2026-11-01-followup-01/primary-job.json \
  --answer .private/readiness/first-session/answer.json \
  --expected-job-sha256 ba12c9b415f175bc686fb0db6f8b9ea29e28631d5a4fac280b7f6f3347d77d8d \
  --output .private/readiness/first-session/output-review.json
```

The future `answer.json` does not exist yet. Do not manufacture a model result.
Inputs must be regular files inside this checkout's `.private`; file symlinks
and directory escapes are blocked. Reports are exclusive, mode `0600`, inside
`.private/readiness`. Exit 0 means mechanical checks passed, exit 1 means a
written report has response errors, and exit 2 means invalid/unavailable input.
Eleven offline tests cover boundary-sized and oversized UTF-8, hash mismatch,
fabricated quotes, action/envelope fields, abstention and exclusive private
output. A real quote attached to a false entitlement still passes mechanically:
semantic review, source freshness/authenticity, model execution, token limits,
transport enforcement, spend, proof and settlement remain unverified.

## Live execution gates and evidence packet

Before submission, verify the official testnet identity, genesis, supported
client/model/faucet, independent miner, owner/delegate/beneficiary mapping and
final rules. Bind a concrete test-token quote and approved spend ceiling to
the exact request. The existing original signing identity must be available;
it is currently missing from this checkout. Do not replace the participant
identity or copy it into an unverified client.

The official profile remains planned/unreleased. No live session is authorized
by this preparation. Do not infer launch from November 3 or count devnet as
testnet demand.

Capture actual provider/model, usage, latency, request/session identifiers,
source/request/output hashes, proof, independent miner and owner attribution,
finalized settlement block/hash and exact test-token amount. Reconcile any
uncertain delivery, refund or dispute read-only. Verify the first end-to-end
session and attribution before scaling; later reconcile official per-owner
allocation inputs and their hash.

The private preparation manifest does not replace the missing historical
session ledger or assert an empty lifetime account. Future observations need
real protocol identifiers and evidence; no placeholder finalized row is created.
The existing [readiness checker](INFERENCE_READINESS.md) remains an evidence
inventory and cannot authorize or certify a session.

## Separately inspected gateway contract

The canonical verification page lists `api.flop.network` as an official technical
surface. Its root advertises [the OpenAPI document](https://api.flop.network/openapi.json).
We fetched that document read-only at 17:46:32 UTC: OpenAPI 3.1.0, API version
2.0.0, response SHA-256
`2876108b38b998e27a34cd7d625b861bc31f12a6b1c59bc75c4212fde805a2da`.
The gateway describes `/api/v1` and `/v1` facades. Its chat schema requires
`model`/`messages` and requires `max_cost_flop` whenever `max_wait_ms` is set.
Wallet enrollment is explicitly devnet; authentication and gateway-reported
receipts do not establish the missing testnet or beneficiary binding.

A private offline body template now holds the prepared messages, `max_tokens`
768, `max_wait_ms` 120000 and nonstreaming mode. It deliberately omits model and
cost cap. Validation against the inspected schema rejects both omissions;
additional action fields and a null cost cap are also rejected. No endpoint
was called with that template, and it must not be dispatched. Its 6,689-byte
candidate body remains below the proposed byte bound, without establishing a
model token count or live enforcement.

Template-file SHA-256:
`854e92c598d6d9067d2eeb81767c28dc4ae3b3b076d44235a0a73a96c007b9e6`.
The final body will need a new binding and approval after verified model, quote,
spend, identity and network values are supplied. Public contract inspection is
separate from the eight-source model-input allowlist, which remains unchanged.

## Remaining blockers checked November 1 at 23:28 UTC

| Blocker | Evidence and next resolving action |
| --- | --- |
| Public testnet route | [Official network profile](https://ask.flop.finance/networks/testnet) still says planned/unreleased, no verified chain spec, genesis, RPC, gateway, model catalog or release. FLOP Labs must publish these; the date target cannot supply them. |
| Existing signing identity | The original private identity is still absent at its configured path, with no identity-directory override. Restore the original from a trusted backup locally; do not send it in chat, rotate it or copy it into a gateway. No backup source is established here. |
| Historical continuity | The original pre-migration workload/session history remains unavailable. Trusted restoration/reconciliation is still needed; these new preparation files do not assert empty lifetime history or recover old approval bindings. |
| Account/beneficiary attribution and allocation rules | [Issues 123](https://github.com/flop-labs/yellowpaper/issues/123) and [172](https://github.com/flop-labs/yellowpaper/issues/172) remain open. Recent peer proposals, including the discussion linked from issue 208, are not a ratified mapping. Require an official rule and exact client/chain evidence for our existing owner before use. |
| Model, independent miner and client enforcement | Select only after a verified testnet catalog and supported route exist. Measure input with the selected tokenizer, inspect actual timeout/token/cost enforcement and verify the miner is independent. The saved-output checker addresses local review only. |
| Concrete quote and authorization | Obtain exact test-token units, price and maximum spend on that verified route, bind the final wire request, then request approval of that concrete session. No open-ended spend or devnet enrollment is authorized. |

The advertised gateway OpenAPI was re-fetched read-only at 23:28:32 UTC and
has the same SHA-256 as the earlier contract. No new network or owner binding
appeared. After an authorized execution, output quality, proof, final settlement
and actual owner attribution become acceptance checks; they cannot be claimed
in advance. No enrollment, wallet challenge, estimate, credential creation or
inference dispatch was made. Local preparation is advanced; the external gates
and trusted identity restoration are not resolved.
