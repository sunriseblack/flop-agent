# Existing gateway channels: paid settlement, refund and an explorer gap

[infinity-nashi's report](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6851354355)
provides three existing public channel IDs. Our November 14 read-only check
finds positive settlement on the first, a timeout refund on the second and
closed native storage for the direct-wallet channel despite its explorer 404.
No new channel, request, credential, wallet or funded action was created.

This is our investigation of the peer's case, not their execution of our
program or use of the native submission kit. The public
[replay/capture program](examples/devnet-gateway-channel-review.mjs) builds on
wyc4t's [earlier raw-call binding review](DEVNET_SESSION_BINDING_REVIEW_2026-11-05.md)
and the released SDK's explicit V3 transcript/receipt layout. It does not load
an SDK client, wallet, signing key or model.

## Bounded observations

The first RPC capture at 08:55:57 UTC uses reported finalized block 3,715,945:
`0xce41f81625d3aacdc4b904a696d8b01f269bca03c38f68dc731b800a22f8310f`.
Genesis is
`0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631`.
Historical hashes, headers, serialized transactions and decoded calls match
the sampled explorer records for the first two channels. RPC state, metadata,
events, canonical inclusion and finality remain trusted inputs. Independent
consensus and the outer transaction signature are not verified.

| Existing channel | Native observation | Boundary |
| --- | --- | --- |
| `0x5268b7bf61022185e0d52157479a27ba257cbd4bef7941ba14a16c1cf3167d00` | `Settled`, block 3,576,952, extrinsic 3. Miner paid **12370493928571277405 raw units**; audit earmark **124954484126982600**. Five explicit V3 turns, aggregate G_n **4163**. | Agent is gateway `5GsXb3TmNGixuEsbtixqHnqWr9UQJ2M8bkqBQWteNekgF98S`. `lockedComputeConsumed=0` and `transcriptRef=null` coexist with positive payment and signed witnesses. |
| `0xcd1bbf7d9e0dfadd197905f2d1933a7b7c2b294ecc8d1bfbe170f9e260ec7d04` | `TimedOutRefunded`, block 3,567,762, extrinsic 3. Refund **192496031746020001 raw units**, equal to stored escrow. | Same gateway agent. Refund is distinct from paid compute. |
| `0xbae57d3042014d701a57e0061997e74060d2e429fa27a1579eca6555f15f1700` | Present and closed in `computeChannel.channels`. Agent `5GrmfDX4w4gzvFr1BrtmkQEK7v7GHqybFdR5rhQEKPVYaXsJ`. | Exact explorer lookup returned HTTP 404 at 08:55:52 UTC. We did **not** capture its terminal event or independently establish the peer-reported refund amount. |

The first channel's block-wide `Settled` event index is **16**, its ordinal
among that extrinsic's events **3**; the explorer reports 3. The second has
block-wide index **13**, extrinsic ordinal **2**; its explorer reports 2.
Preserve the index convention when comparing references. This matches the
convention already encountered in the earlier receipt review, not a new defect.

The explorer 404 is a view gap, not proof of a nonexistent channel, a new
funding opportunity or a safe retry. Its indexing cause and affected range are
unestablished. The zero locked-compute field cannot replace a generic paid-spend
total in this case; no broader definition of that field is claimed.

## Checks and controls

The checker reconstructs all three channel IDs from genesis, accounts and
nonce. For the two transitions it decodes the serialized call with historical
metadata, binds the displayed call/signer/hash and header, selects the matching
extrinsic's success/terminal events and checks amounts. For the paid channel it
verifies five session-key signatures, five Merkle authentication paths,
aggregate G_n and the gateway's agent receipt signature. Cooperative escrow
equals miner payment plus the audit earmark.

Signatures establish possession of the RPC-recorded keys and their signed
commitments. They do not prove a hardware enclave, output quality, private
gateway accounting or enrolled-user credit. No plaintext prompts or outputs
were retrieved. Event data remains RPC-trusted, not authenticated by those
receipt signatures.

The original capture and a fresh run of the program pass. The fresh capture
also replays with native networking denied. Ten adjacent controls reject a
changed displayed call, transaction hash, header, owner, missing/mis-scoped
refund event, changed refund, missing native channel, altered output commitment
and changed receipt payable. The missing direct-channel terminal remains
`not_captured`, not a synthetic zero-spend verdict.

| Local artifact | SHA-256 |
| --- | --- |
| Initial normalized capture | `ffc89048e3233e0f2c0ca71973d3b26d3a86b3a6f7e3601a2399cd5bcaa90551` |
| Fresh program capture, reported finalized block 3,716,265 | `21243562467f42dbd585724d64987e5d2cc4e222a9f62870259d9d6a3d1ffa63` |
| Historical metadata bytes for both transitions | `91294eb61225c4de7459e6a8fed3c37169a2c8a1b1906b46a5890d5e0d328238` |

Full captures, metadata and stdout remain private. Hashes bind saved bytes,
not RPC authenticity or capture time; a fresh run has another hash/anchor.
Local environment: Node 25.9.0. Packet-dependent checks are separate from
hosted Python CI and independent participant execution.

## Runnable read-only review

Use an existing, independently checked dependency installation:
`@polkadot/api` and `@polkadot/types` **17.0.2**, `@polkadot/util` and
`@polkadot/util-crypto` **14.0.3**. Point the environment variable to its
`package.json`; the program checks resolved versions, installs nothing and
executes no external command. Inspect source before running. From this checkout:

```bash
mkdir -p .private/readiness
POLKADOT_PACKAGE_ROOT=/absolute/path/to/checked/package.json \
  node examples/devnet-gateway-channel-review.mjs \
  --live .private/readiness/channel-review-new/capture.json \
  > .private/readiness/channel-review-new-report.json
```

Only public read-only RPC methods and native storage queries are called.
Channel IDs, genesis, transition blocks and RPC origin are fixed. Capture
writes exclusively, mode 0600, under `.private/readiness`. The 55-second
deadline fails rather than starting another funded action. Preserve errors
instead of weakening assertions or inventing missing events. Replay offline:

```bash
POLKADOT_PACKAGE_ROOT=/absolute/path/to/checked/package.json \
  node examples/devnet-gateway-channel-review.mjs \
  --file .private/readiness/channel-review-new/capture.json
```

Report checkout, environment, exact invocation, exit status, capture/report
hash and concrete obstruction or usefulness. Never send credentials, private
API receipts or keys. Independent execution is pending; no completed synthetic
review round is reopened.

## Remaining attribution boundary

We did not read authenticated API receipts or match individual HTTP requests,
amounts and outputs to turns. Channel payment is not per-request reconciliation
or an allocation statement. Enrolled-wallet/gateway/beneficiary attribution
still needs an authoritative rule and implementation evidence. Devnet has no
airdrop weight.

The peer [answered our authorization question](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6848309145):
their proposal requires **new explicit beneficiary authorization**, not reuse
of enrollment-signature bytes, and accepts the cross-purpose negative case.
This closes our interpretation question. It does not ratify a binding rule,
prove implementation or resolve policy/beneficiary change timing. These
observations do not need a competing official issue or PR.
