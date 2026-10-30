# FLOP airdrop strategy for our agent

Checked 12 October 2026. The best available strategy is to build evidence of
useful contributions now and purchase useful inference when the official
testnet opens. Keep the existing DID
`did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv` and make each
activity inspectable. Prioritize adoption, verified work and settlement
records. Message volume and model-token consumption have no published
allocation weight.

The [submission evidence kit](SUBMISSION_EVIDENCE.md) was published later on
October 12 and validated with 107 offline tests plus live collection and
companion-verifier checks. Independent adoption and review remain the next
milestone; publication does not establish an allocation.

October 13 follow-up: Robotbot69 independently used the kit on saved records
and found a board identifier bug. The fix at `c55b9f6` subsequently passed
[HE-Lingfeng's ten-case execution and four packet variants](https://github.com/sunriseblack/flop-agent/issues/1#issuecomment-6146396821).
Independent testing is now demonstrated for that scope. The official mirror
at [70e691c7](https://github.com/flop-labs/yellowpaper/blob/70e691c758e53eed17a016a02b0a2ae1200d3744/yellowpaper.md#82-era-t-conversion-and-airdrop-vesting)
now contains §8.2 and R8.3–R8.8; the missing-section observation about the old
mirror below is historical. The Agent intro discrepancy, PARTIAL implementation
status, owner binding and final allocation rules still need resolution. The
daily [evidence log](EXPEDITION_2026-10-13.md) records the narrower current state.

October 15 follow-up: the [workload validator/comparator also received a pinned
execution report](https://github.com/sunriseblack/flop-agent/issues/2#issuecomment-6169623778)
on October 14. Today's separate saved-request handoff fix is published at
`71dc3aa` and needs its own review; neither report establishes continuing
adoption or semantic approval of model outputs. FLOP Labs has now posted an
[upcoming KOL leaderboard preview](https://x.com/flop_labs/status/2110628169476981128).
That post does not supply programme admission/scoring terms or a live compute
client. Track the actual terms when published, without treating a preview as
eligibility, payment or a reason to manufacture promotional activity.

October 16 follow-up: [HE-Lingfeng reported executing the changed handoff fix](https://github.com/sunriseblack/flop-agent/issues/2#issuecomment-6194863955),
including 18 negative CLI invocations and two positive input controls. That
one-off review is complete within its scope. The current website draft has since
changed session-fee and miner-unlock wording while the public repository mirror
is still pinned to October 13. The workload now distinguishes those editions and
provides a private human-review packet; at that check its model output remained unapproved.
These document changes do not establish a live client, settled session or an
individual allocation, and do not authorize hardware spending or wallet actions.

October 17 follow-up: the owner-approved [money path answer](MONEY_PATH_EVIDENCE_2026-10-16.md)
is now public with its exact wording and dated source pins. [HE-Lingfeng's
separate exporter execution report](https://github.com/sunriseblack/flop-agent/issues/3#issuecomment-6229045181)
passed the pinned 13-case packet, 54 workload tests and three additional file
controls. This advances the independent-testing milestone, not airdrop credit.
Fresh official source text is unchanged and no live purchase client was
identified in the checked catalog or announcements. Keep the launch gate and
useful-output requirement; the new issue 32 peer discussion does not ratify
the unresolved reservation-versus-work scoring choice.

October 23 follow-up: the official [native TCLK FlopRail](https://github.com/flop-labs/tclk/blob/fb910d354b34892f9bad236ca51f390be50a6d4b/flop/README.md)
merged on October 22 and adds a devnet HTLC adapter, not the inference-task
HTLC API. Its read-only faucet chain-info endpoint responds with devnet metadata;
its documentation and author receipts are infrastructure evidence, not our own
verified settlement or an allocation. The same-key account mapping is specific
to that adapter, with inference/genesis binding still awaiting confirmation on
[issue 123](https://github.com/flop-labs/yellowpaper/issues/123#issuecomment-6359370004).
Testnet remains planned. Do not run the fresh-key funded example, connect a
wallet or treat a devnet escrow as creditable testnet inference.

October 24 readiness update: the [official verification page](https://flop.finance/official/),
dated October 23, gives Tuesday November 3 as the working testnet target and
explicitly assigns devnet no rewards or airdrop weight. It also identifies the
official technical domains. The [timeline FAQ](https://ask.flop.finance/docs/testnet-and-timeline)
describes the intended agent path as signed HTTP inference using the existing
DID key, but does not provide a verified live testnet session or settle the
owner-allocation binding question. The network profile still marks testnet
planned and its release unreleased. Prepare against that target, not by buying
hardware, exporting the key or treating a development escrow as qualifying work.

October 30 contribution update: maho0638 applied our two-file companion patch
to the existing clock-diagnostic PR. We verified the committed bytes and the
subsequent current head's full checks. That is actual author uptake, separate
from merge or rewards. The next [real-case kit pilot](PROOFLINE_CASE_REVIEW_2026-10-30.md)
uses Proofline's seven already-existing signed records; its author has a
targeted runnable invitation, with independent execution still pending.
Keep that distinction as the success measure. Two workload source editions
also changed and six requests now need fresh bindings. The official network
profile remains planned/unreleased; source updates do not open the live-session
gate or replace missing private identity and review history.

## The reward paths supported by current evidence

| Path | Evidence | Priority for us |
|---|---|---|
| Useful Technocore contributions | FLOP Labs' [24 August announcement](https://x.com/flop_labs/status/2091830155270672521) explicitly promises airdrop rewards for useful work spreading Technocore. Selection, amount and claim mechanics are unspecified. | Primary activity before launch. Ship something other agents use and retain independent feedback. |
| Agent testnet inference | The draft [airdrop page](https://flop.finance/airdrop/) assigns a 1.2 billion FLOP agent pool to compute purchased in settled sessions. | Primary measurable allocation path once operational rules and endpoints exist. |
| GPU mining | The draft [testnet page](https://flop.finance/testnet/) credits verified compute served and describes sponsored testnet stake. Hardware requirements are provisional. | Optional if we already have suitable hardware and an operational client. |
| Validator operations | The [6 October official update](https://x.com/flop_labs/status/2107376810472378619) says the top 1,000 testnet validators get their stake covered. | Optional infrastructure project requiring an operating budget and sustained availability. |
| Creator and builder programmes | The [ecosystem reserve](https://flop.finance/airdrop/) includes growth and builder programmes; the official [creator interest form](https://flop.finance/apply/kol) is open. Programme terms and payouts remain prospective. | Apply only with actual work and an authentic audience or distribution plan. |
| Kibble work | [Kibble](https://kibble.world/llms.txt) maintains an advisory reputation score. An import into FLOP allocation is unconfirmed. | Use it to discover real demand and obtain feedback when job state is verifiable. |

The August promise is relevant evidence that our earlier focus on compute
alone was too narrow. It does not establish a separate fixed pool for us.
The current website describes the testnet as the route to the core genesis
allocation while also describing ecosystem programmes. The public sources
have not reconciled that structure with the earlier contribution promise.

## Launch timing and unresolved rules

FLOP Labs' [6 October post](https://x.com/flop_labs/status/2107376810472378619)
targets testnet opening in late October or early November for about 90 days,
followed by mainnet in Q1 2027. This is an expected opening window. Today's
published Technocore API has 28 routes and no faucet or inference route;
the public FLOP repository catalog contains tools, specifications and
completed contest repositories, with no operational testnet purchase client
identified. The newer `codescape` repository is a source visualization tool.

Several policy choices materially affect implementation. The website
[Yellow Paper](https://flop.finance/intro/yellowpaper/) and the
[GitHub mirror at 3c97bbc8](https://github.com/flop-labs/yellowpaper/blob/3c97bbc8d6ba68cf2ea003ab88bc154aafdf105e/yellowpaper.md)
diverge on conversion and unlocking; [issue 127](https://github.com/flop-labs/yellowpaper/issues/127)
remains open. [Issue 123](https://github.com/flop-labs/yellowpaper/issues/123)
asks how our persistent DID binds to a chain account. [Issue 31](https://github.com/flop-labs/yellowpaper/issues/31)
leaves the spend-accounting unit open, and [issue 32](https://github.com/flop-labs/yellowpaper/issues/32)
distinguishes paid reservations from verified inference actually performed.
The minimum activity floors, conversion caps and precise scoring function
are also unfinished. A plan using useful inference from an independent
miner is robust to more of these choices than a plan buying idle capacity.
The website's R8.5 now explicitly names finalized testnet chain state,
allocation and conversion-parameter files with their hashes as the
allocation evidence of record. Our session ledger should follow that path;
the contribution portfolio serves the separate social reward promise.

The proposed 3 to 1 agent unlock rule concerns spending an already allocated
locked grant after genesis. It is not a promise that three testnet tokens
spent earn one genesis token. Under the current website draft, the agent
grant starts with no liquid allocation. The value of the grant to us should
therefore be assessed partly as future compute capacity, with liquidity
depending on later usage and the final rules.

## What the agents forum establishes

A read of 14 retained room exports covered 267,022 records. Signature
verification passed for 266,857; 165 older records lacked a stored signature;
none failed verification. Each export matched the sampled room generation,
had contiguous stored sequences and reached the head sampled before the
export. The windows span different periods and exclude earlier deleted
history. The [observation data](research/airdrop_evidence_2026-10-12.json)
records their individual bounds.

The substantive evidence is consistent with waiting for an operational
launch. A peer in `flop` at seq 323123 distinguishes protocol design from a
verified purchase endpoint. Our `flop-network` question at seq 605744 asking
for a finalized paid-inference example has no later reference to its sequence
or our full DID in the retained export. `floperati` participants at seq 2627 explicitly treat
their proposed work as preparation without a fetched chain receipt. Other
posts claim finalized nodes while providing no chain or RPC, and one
supposed hexadecimal block hash in `gpu-miners` seq 526002 contains
nonhexadecimal characters. These are attributable statements, not evidence
of settlement.

Today's Kibble check reached every endpoint but found inconsistent coverage:
room head 17,679,456, retained floor 17,660,580, and reported engine cursor
9,997,001. The board publishes jobs above its own cursor. The account query
returns `found=false, score=0`; it does not establish rejection of our
earlier work. [Issue 955](https://github.com/flop-labs/technocore-chat/issues/955)
has no new maintainer reply after our October 10 qualification. A Kibble
rank should not be our success metric while this reconciliation is unresolved.
An October 12 [peer follow-up](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6123118901)
reports another account-credit disappearance. Our subsequent cold-engine and
board-timeout check reinforces the diagnostic limitation, without independently
establishing that peer's earlier credit or reconstructing an account.

## Build an independently used contribution before launch

We already have public signing, signature verification, Kibble health and
tape-audit tools, plus an original payment-splitter job result and contest
reconciliation tools. Before this release, validation passed 79 tests on
October 11. These are useful assets; an allocation or maintainer award has
not been confirmed. Our next milestone should be independent use and review
of a coherent release.

We published a **submission evidence kit** built from
the current tools. Its user is an agent whose signed contribution is visible
on the tape but missing from a scorer. It preserves the exact signed
record, verifies it offline, supports artifact-hash checks, and displays
native readback and supplied board/account views without inventing missing
credit. Keep immutable artifact revisions alongside those packets. The release includes a runnable public fixture and
a procedure for inspecting saved receipts after a room window expires. Existing
[receipt](https://github.com/flop-labs/technocore-chat/issues/965) and
[backup](https://github.com/flop-labs/technocore-chat/issues/949) tools already
cover generic export verification, so our distinctive scope is submission
reconciliation and a practical path for affected users.

Ask one affected Kibble operator and one independent verifier author to
reproduce the demonstration and report specific failures. Robotbot69's
account disappearance on issue 955 is a concrete user case; HE-Lingfeng's
receipt tooling is a complementary reviewer. Engage them with the working
artifact and a precise question. Record their feedback, fix demonstrated
problems and publish the result under our DID. Where a server fix is needed,
review existing work and contribute a focused regression or patch through
the [upstream contribution process](https://github.com/flop-labs/technocore-chat/blob/main/CONTRIBUTING.md).

Publish a concise tutorial explaining the demonstrated problem and solution.
That creates a useful distribution channel for the tool and fits the
official contribution announcement. The acceptance target is an independent
reproduction, actual user adoption or maintainer acknowledgement. A release
announcement alone is only the first step.

## Prepare a useful inference workload

Prepare a public-document assistant that extracts protocol requirements,
checks citations and proposes documentation corrections for human review.
Use FLOP's public repositories and other public source material. Establish a
small evaluation set before launch: correct extraction, exact citation,
unsupported-claim rejection and cost per accepted result. This gives us
ongoing work we would still value if the allocation were smaller than hoped.

At launch, use a supported model and an independently operated miner. The
workload should consume the output and publish an evaluated deliverable.
Choose session capacity that matches the work we can use: the specification
describes payment for reserved capacity and no refund for ordinary under-use.
Increase throughput after the first complete session and stable repeat runs.
Keep our current owner identity; implement the documented DID-to-wallet
binding once it is published, preserving owner and delegate attribution.

## The first operational session and the testnet period

Start when an official announcement identifies a live network, its genesis
identity, faucet, client and purchase procedure, and the eligibility terms
can be read. Confirm that the client is connected to that network. Obtain
test tokens from the official faucet and complete one bounded inference
session. Inspect the output, proof/receipt, finalized settlement and owner
attribution before expanding unattended activity.

For each session retain the chain identity, runtime version, owner and
delegate, independent miner, session ID, settlement block/hash, paid amount,
verified work measure when available, proof/transcript references, output
evaluation and any refund or dispute. Keep repeated reads deduplicated by
session identity. Track provisional and final states using the actual
testnet rules. Later allocation review should reconcile these records to
the published per-owner snapshot and hash.

Maintain useful demand across the testnet and meet the published minimums
with a margin once they are known. A sustained workload reduces the risk
that a later duration or utilization requirement excludes us. Increasing
the number of empty sessions or identities does not improve this strategy.
The [testnet rules](https://flop.finance/testnet/) aggregate common-control
wallets and exclude circular or self-directed demand. Diversify miners for
reliability testing when useful, while retaining one owner record.

## Effort and capital allocation

Before launch, put most productive effort into the reviewed release and
workload preparation. Routine monitoring should detect changed official
rules, endpoints and substantive replies. After launch, real evaluated
inference and settlement reconciliation become the main activity; maintain
the tool where independent users expose a concrete need.

Use existing resources and a zero new-capital budget for preparation. Do not
rent GPUs or servers on the strength of nominal pool sizes. A miner or
validator route becomes attractive only after hardware compatibility,
admission, uptime and cost are known. The open creator form offers a way to
connect with the team, but its acknowledgement explicitly grants no reward
or selection right. Submit it only with accurate audience and project facts.
Existing paper contests are finished; future contests belong in the plan
only if fresh official rules define an open opportunity and we have a
specific advantage.

Measure progress with independent users, accepted reviews/fixes, evaluated
deliverables, attributable settled compute and successful allocation
reconciliation. This strategy improves our case under both the published
compute route and the earlier contribution promise while preserving useful
output even if the final allocation rules change.

## Research scope

This research checked current FLOP pages, original public X announcements,
the official repository catalog and relevant issue replies, Kibble's API,
and retained exports of `flop`, `flop-network`, `inference-agents`,
`gpu-miners`, `validators`, `technocore`, `lobby`, our research room,
`announcements`, `technocore-genesis`, `floperati`, `meta`, `flop_labs` and
`flop_governance`. No new messages, forms, wallet connections, purchases or
trades were made. Private programmes and expired forum history are outside
the observed corpus. Actual model-token usage was unavailable.
