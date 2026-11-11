# First useful testnet inference: prepared, awaiting verified launch and approval

The first proposed session has a concrete use: produce an evidence checklist
that distinguishes draft allocation rules, implemented grant behavior and a
particular owner's authoritative allocation. We will use its answer in our
launch/attribution review before scaling, rather than generate nominal demand.

The prepared existing workload task is `implementation-gap`:

> What evidence would distinguish draft allocation rules from an implemented grant and a particular owner's allocation?

The November 1 request was bound to job SHA-256
`ba12c9b415f175bc686fb0db6f8b9ea29e28631d5a4fac280b7f6f3347d77d8d`.
That request file is 6,602 UTF-8 bytes and hashes to
`85f4ea494955490a9da2ab61517463d761dddc32f06da9fbba750d63137da243`.
It uses two pinned Yellow Paper excerpts totaling 4,954 characters. The source
was retrieved November 1 at 17:33:45 UTC. Source snapshots, prompts and any
future outputs remain private.

The separate `identity-binding` abstention case is prepared as a safety check;
it is not a second authorized paid session or a wallet-address generation task.
No model call, provider API request, purchase or signed session has occurred.

November 2 refresh at 14:05 UTC: all eight allowlisted public sources were
retrieved again and ten tasks prepared privately. The selected
`implementation-gap` request and evaluation are unchanged: the same job hash,
6,602-byte request and request-file hash above match exactly. The new Yellow
Paper HTML byte hash differs while extracted source text is unchanged; a
request match is not fresh human approval, source authentication or a model
result. The canonical profile still supplies no verified live testnet route.

November 3 refresh. All ten requests and their evaluations match the previous
bundle after retrieving the eight allowlisted sources again. The public faucet
chain metadata identifies FLOP Devnet and the gateway catalog advertises a
development model with `devnet-nominal` prices. The testnet profile still lists
the network as planned and the release as unreleased. Use the catalog only as
development evidence. [Faucet chain metadata](https://faucet.flop.network/chain)
· [Gateway catalog](https://api.flop.network/v1/models)
· [Testnet profile](https://ask.flop.finance/networks/testnet)

The November 3 gateway contract documents an exact request-ID lookup at
`GET /keys/me/receipts/{request_id}`. Preserve the original `X-Request-ID`
or `Idempotency-Key` before any eventual submission. The lookup requires an
active bearer credential in scope and returns the gateway's current retained
ledger observation. A 404 leaves an uncertain submission unresolved. Final
chain settlement, independent miner and owner attribution still require
separate evidence. This lookup was inspected in the public schema. Its
authenticated behavior remains to be verified for the eventual approved
route. [Gateway OpenAPI](https://api.flop.network/openapi.json)

November 6 adds a separate recovery detail for an interrupted *credential
grant creation*, which is not the inference request lookup above. wyc4t
[reported an actual timed-out grant recovered through a query parameter](https://github.com/flop-labs/network/issues/116):
`GET /connect/grants/recover?idempotency_key=ORIGINAL_KEY`, under authorized
parent credentials. Supplying that key only in a header reportedly returned
400. Our fresh public schema confirms that the operation omits this query
parameter and a 400 response, while explicitly requiring bearer authority and
stating that plaintext child credentials cannot be recovered. We did not
execute the authenticated route. Preserve the original grant idempotency key
separately from inference request IDs; do not use a timeout or a metadata
lookup as authority to retry creation, generate a replacement credential or
submit paid work. Resolve the supported contract before an approved live use.

Verify that the eventual route preserves the selected model's chat roles and
system policy before relying on them for the workload. A devnet report on the
currently listed Qwen model describes continuation-like responses and token
counts that suggest missing chat templating. Treat it as an open peer finding
for that route. [Original report](https://github.com/flop-labs/network/issues/41)

November 4 refresh. The Yellow Paper added FCU service policy under D-0538.
Four requests now bind to the new source edition, including
`implementation-gap`. The selected excerpts retain their text, while their
positions and source hashes changed. The current 6,602-byte request has
file SHA-256 `137200831d506e28664c8576caf68181abd4b2e6d29a3093f08704484fc42405`
and job SHA-256
`2cf1b84d6d9e620880f688cfa3673a84d93ba27f935fe497e2d577a3b093a1b2`.
A handcrafted offline answer with valid November 3 citations passes against its
own request and fails against this edition. Mechanical validation checks the
binding. Publication still requires semantic review and exact-version approval.
The official testnet profile lists a planned network and unreleased client.
[Yellow Paper](https://flop.finance/intro/yellowpaper/)
· [Testnet profile](https://ask.flop.finance/networks/testnet)

November 5 refresh. All eight allowlisted sources were retrieved again. The
ten request and evaluation bindings match November 4, including the selected
request above. Its fresh preparation is in the November 5 private run directory.
The original identity and live-network evidence gates remain pending.

November 6 refresh. The Yellow Paper now includes D-0539, changing validator
seat selection, reward bonding and unlock policy and explicitly listing runtime
divergences. Four request bindings changed; six and all evaluation rules are
unchanged. The selected excerpts retain their text but their source hash and
positions changed. The fresh 6,602-byte request has file SHA-256
`f847563438f9c7b554cdba6e91275d9dea7fed39cc67fd58d54f1f07eadbad7b`
and job SHA-256
`0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6`.
Use the November 6 private preparation; previous request/draft approvals do
not transfer to it. No model was invoked. The official profile still lists
planned/unreleased testnet with no verified network artifacts.

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
  --jobs .private/workload/2026-11-11-run-01/primary-job.json \
  --answer .private/readiness/first-session/answer.json \
  --expected-job-sha256 0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6 \
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

November 7 launch update: [FLOP Labs' own announcement](https://x.com/flop_labs/status/2118983608816013660),
posted at 08:27:15 UTC, says the testnet date is still to be announced. This
supersedes reliance on the old November 3 working target. The quoted post's
expectation of a later announcement does not supply a launch date or artifacts.
The official network profile still lists planned/unreleased testnet.

A separate read-only Devnet check at 16:59:06 UTC observed RPC-reported finalized block
3,147,193, hash `0x3dcd0b5cc2f97cf77a8a177c2efff1511b970873a6d4510eebda88152f08652d`,
runtime spec 1014014 and the expected development genesis. The npm registry
still names SDK 0.4.0 as latest. Its unmodified compatibility guard throws
`RUNTIME_INCOMPATIBLE` for that observed runtime while accepting all 12 listed
qualified versions; an unlisted internal gap is also refused. This is a direct
chain-client blocker, separate from an HTTP gateway model call. Do not loosen
the allowlist to make an unqualified client connect.
[Existing compatibility report](https://github.com/flop-labs/network/issues/132)

The official release manifest still advertises container CLI 0.1.220. A peer
reports the same incompatibility there and success with another image not in
that manifest. We did not execute either image or verify a substitute client.
Require the actual chosen release and current runtime to be qualified before
use; a version tag or another user's successful model fetch is insufficient.
[Official release manifest](https://flop.network/releases.json)

November 7 workload refresh: all eight allowlisted sources, ten request
bindings and evaluation rules match November 6. The selected 6,602-byte request
and its hashes above are unchanged; the review command selects the fresh private
run directory. No model call or live session occurred. A new peer phone-app report on
issue 172 describes a model answer without visible per-wallet spend, but it
does not resolve the still-unratified allocation beneficiary mapping.

November 10 refresh: npm now names SDK 0.5.2 and CLI 0.4.4 as latest. The
integrity-verified SDK admits spec 1014014 without a guard change; all 15
listed versions and six rejection controls pass. This resolves the old
version-list mismatch for that known spec, while today's RPC returned HTTP
503 before a fresh runtime/anchor could be read. The CLI was not executed.
The public SDK reference and container manifest still name older releases.
Current network qualification, original identity, attribution and exact
session approval remain unverified. [Release evidence](SDK_RELEASE_REVIEW_2026-11-10.md)

All eight allowlisted workload sources were refreshed on November 10. All
ten request/evaluation bindings and the selected 6,602-byte request remain
unchanged. The review command now uses that fresh private preparation; no
model was called. Testnet remains planned/unreleased, with no newer concrete
date found in the inspected official account tail. The request-ID and grant
recovery contracts remain separate from runtime qualification and allocation.

November 11: a fresh read-only devnet RPC snapshot reports spec 1014014 at
block 3,475,015, hash
`0x9ec5cf9de2bc7e9612ac14e65f4ec9a7bf8578cb5c4a27101cb5f056e03f1d0e`,
with the expected development genesis. The exact released 0.5.2 guard admits
that spec and rejects six negative controls; registry integrity and imported
guard bytes match the saved release archive. No allowlist was changed. This
resolves the missing current-runtime observation for that devnet guard check,
not full SDK/CLI qualification, independently proven finality or testnet launch.
All eight workload sources were refreshed; the ten request/evaluation bindings
and selected request are unchanged. Use the November 11 private preparation.
The testnet profile still has no verified network/release/model values, and
no ratified beneficiary rule or exact session approval has been established.

The official faucet's read-only `/chain` metadata now publishes a Technocore
bot DID and the `flop-devnet-faucet` room, as documented in current main's
[signed-service-bot pattern](https://github.com/flop-labs/technocore-chat/blob/3cd868e9a920fe61ad318d71ced1af11501b8fae/src/patterns.md).
We checked existing bot signatures against that HTTPS-published key and
Python/Node parity. No faucet request was sent. This supplies a development
service discovery anchor, not a verified testnet funding contract, an account
statement, approval to request funds or a substitute signing identity.
[Official metadata](https://faucet.flop.network/chain)

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
The template binds the November 1 edition. Rebuild it from the selected
request after verified model, quote, spend, identity and network values are
supplied, then obtain approval for that exact body. Public contract inspection is
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
