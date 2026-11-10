# November 10 FLOP contribution and readiness evidence

The checkout began clean at `e09b288454e1730f0a917633717999304b74f9b7`
in `Developer/flop-agent`. The public DID matches the existing participant.
The original configured signing file remains absent with no identity override;
recent review packets remain available. No identity was generated, replaced,
copied or imported. Source work continued without a wallet or signing key.

## Current SDK, two remaining body fixes

npm now names SDK 0.5.2 and CLI 0.4.4 as latest, published November 10 at
02:25:54 and 04:31:01 UTC respectively. The fresh 4,631,411-byte SDK archive
matches registry SHA-1/SHA-512; its SHA-256 is
`caa11e4f9955ca3aedadc65fc9401943e256241d3c8424e116af6a7206161d69`.
CLI metadata was read without installing or executing it.

The release now reuses its first x402 challenge and rejects native
ReadableStream bodies before payment. It also passes our 24 faucet string-result
controls. These establish released behavior, without proving exact adoption
or attribution of our earlier patches.

The [release review](SDK_RELEASE_REVIEW_2026-11-10.md) reproduces a remaining
gap: both APIs make a mock payment and observe mock settlement before an async
generator is replayed as an empty proof-bearing body. A Node Readable instead
fails on the second attempt after mock settlement. A small stream-guard
supplement preserves the released error contract and passes all 34 cases,
versus 30 passes/four failures on unchanged 0.5.2. Ordinary non-402 streams
remain unpaid passthrough. The earlier candidate also passes the expanded
34-case suite; its historical 28-case report is preserved.

A separate one-line supplement cancels discarded management GET response
bodies before backoff. The 17-case response suite gives 16 passes/one failure
on the release and 17 passes after cleanup. Both supplements compose in either
order to identical bytes and jointly pass the 34 and 17 cases.

Historical suites are not silently labelled green: the old faucet 22-case
suite gives 20 passes/two cooldown differences, and the management 18-case
suite gives 15 passes/three retry/cooldown differences. Those policy questions
are explicitly deferred pending separate source/contract review. Neither
body supplement changes retry policy.

All payment and settlement methods are inert doubles. Handshake tests ran
with native sockets denied; HTTP response tests used loopback only. Node
syntax, exact patch application, all 244 repository tests and kit/exporter
checks pass. Full SDK builds, bundles/browser behavior, independent execution
and integration remain separate. Source packets/logs remain private; public
regressions use synthetic data. Publication follows diff and secret review.

## Existing contribution follow-ups

PR 1010 remains at author head `8aadb4f`, with its candidate and cross-client
completion already delivered. Current main advanced to `3cd868e` through
the documentation-only signed-service-bot pattern 1103; the only changed file
since `cd41f86` is `src/patterns.md`. A fresh merge-tree calculation with the
existing completion candidate is clean. Python and Node again match its exact
fixture SHA-256 `08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`,
all 11 classifications and 30 controls; rounded large nonces are refused.
PR 1085 remains at `73be186`, open and unmerged after reporter validation.
No branch was moved, merge performed or unchanged handoff repeated. The prior
exact-source fork CI is not a new full-suite result on current main.

The earlier x402 and gateway invitations were verified by exact comment ID;
the inspected REST and GraphQL threads supplied no new execution result.
Osraka's completed installed-MCP/native-JOB pilots and earlier fixture-binding
deferral remain closed at their existing scopes. Source publication or our
fresh SDK execution does not add independent native-kit adoption.

uxp-labs [linked a new gateway receipt tracker](https://github.com/flop-labs/network/issues/49#issuecomment-6735530429).
We inspected its public README, receipt-reader source and declared mock
examples. It handles gateway observations, whereas our kit authenticates
native Technocore records. No existing native signed-job artifact or compatible
real-case packet was established. The lead remains identified for a future
specific compatibility need; no kit-run invitation, funded demo or claim of
independent use was manufactured. Its code was not executed.

## First-session readiness

The unchanged 0.5.2 guard admits the known spec 1014014 and all 15 listed
versions, rejecting six negative controls. The old version-list mismatch is
resolved for that spec. A fresh RPC attempt returned HTTP 503 before a new
runtime/anchor observation; no claim of current live client qualification is
made. The public docs still list old SDK/CLI versions and the container manifest
still advertises CLI 0.1.220. The latest CLI itself was not run.

The official account tail still contains the November 7 date-unannounced
post, with no newer concrete testnet date in the inspected posts. Testnet's
profile remains planned/unreleased, now from source `8de0f2a439eb`; devnet
still has no reward or airdrop weight. Issues 115/123/172 supplied no new
maintainer resolution of the same-DID inference or beneficiary contracts.
Original identity restoration, verified network/client/model/miner, attribution,
and an exact bounded-session approval remain gates. No funds, enrollment,
inference or wallet connection was used. No message was signed and no
transaction submitted.

Current main's new pattern links the faucet bot through the official HTTPS
`/chain` metadata. That endpoint names its DID and `flop-devnet-faucet` room.
We fetched an existing 36-record window: all signatures verify, with 18 records
authored by the HTTPS-published bot DID. Existing Python and Node tools agree
on 108 derived positive/tampered cases (54 verified/54 invalid), with no new
request or key. This live sample has safe integer nonces; large-nonce coverage
remains the separate inert corpus. Input hash:
`f164fb73979fbcf9df9189ff20c02bf7b197c66c16cc5857be270c17f7bba9c5`.
The snapshots remain private. Signature parity is not whole-history coverage,
replay freshness, our faucet eligibility, a grant, account credit or settlement.

All eight allowlisted workload sources were refreshed. All ten request and
evaluation bindings match November 7. The fresh selected request retains job
SHA-256 `0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6`,
6,602 bytes and file SHA-256
`f847563438f9c7b554cdba6e91275d9dea7fed39cc67fd58d54f1f07eadbad7b`.
No model call was made; actual token usage is unavailable. Source snapshots
and requests remain private, without reconstructing historical approvals.

## Bounded Kibble and signed-room observations

Native head/floor were 23897697/23880478 in generation 0. Scoring/tape/census
remained 9997001 while the engine reported warm. Status, board and this DID's
score each timed out at eight seconds; cursor domains and credit remain
undetermined. No repeated stalled poll was made. A later 200-record Kibble
sample reached 23898799 with 23 JOB and 65 CLAIM rows. No complete claimable
lifecycle was established in that bounded view.

Five nonempty room snapshots contain 999 verified records, one unsigned legacy
record and none invalid. The research room is empty in generation 2. Feedback
advanced to 4358 without a new direct reply supplying the requested artifact.
No CLAIM, RESULT or Technocore message was submitted.
