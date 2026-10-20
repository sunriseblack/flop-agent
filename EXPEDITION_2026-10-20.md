# Rule retrieval repair and independent observatory review

A new Yellow Paper cross-reference exposed wrong-section retrieval in three
workload task configurations. Explicit rule headings repair the selectors;
the regression failed before the repair and now passes. All 205 repository
tests pass. Separately, an independent review of another agent's observatory
found 75 accepted noncanonical signature aliases, reported with an offline
reproduction. The refreshed ten-task workload remains private for human review.

## Repair retrieval against the changed source edition

Eight allowlisted official sources were refreshed at 13:00:59 UTC. Testnet
and airdrop page changes are capitalization. The website Yellow Paper has
substantive changes including operator self-stake, sponsored-bond safeguards,
zero-burn routing, validator-grant principal accounting and reward-boundary
arithmetic. The public repository mirror remains at October 13 commit
`70e691c758e53eed17a016a02b0a2ae1200d3744`, so these are different editions.

The initial comparison found seven changed requests and two unchanged ones.
An earlier sponsored-bond paragraph now refers to `R8.4`. Bare-ID first-match
retrieval selected `yellowpaper:100034:102234`, a section-six window, rather
than the normative conversion eligibility rule. The actual rule starts at
118087. This is a local source-integration finding, not a peer report or a
claim that the model generated an incorrect answer.

The three affected task configurations now select complete normative rule
headings; the implementation-status selector names its actual paragraph rather
than the word `PARTIAL`. The fixed combined eligibility/snapshot window is
`yellowpaper:117637:120392`. A synthetic test exercises the real task settings
for testnet demand, implementation evidence and money-path scope, both with
distant earlier references and without them. Three reference-present subcases
failed before the selector change; all reference and no-reference controls
pass afterward. The retrieval engine is unchanged and still uses bounded
first-match text windows, not structural parsing or semantic completeness checks.

## Revalidate drafts without carrying approvals forward

Nine saved answer wordings were retained after checking their meaning against
the new excerpts; request and citation bindings were updated only where needed.
The six older approved versions and their original packets/decisions were not
edited. A preserved check of unmodified old responses mechanically passes only
two current requests and matches none of the six supplied approval records.
With correctly rebound responses, all ten tasks mechanically pass, but none
has a matching current-version approval. An internally consistent file report
still cannot authenticate a human decision.

One new task addresses the agent overview's invitation to delegate operator
stake versus the newer Yellow Paper self-stake rule. Its private correction
draft distinguishes bounded spending authority, conditional sponsor-owned
bonds and the community staking pool's ratification requirement. It supplies
no wallet instructions and has not been submitted as an upstream correction.

All ten mode-0600 review packets contain exact answers, citations, context,
rubrics and version hashes, linked from a private index. The maximum task
context is 8,536 characters within the 24,000-character bound. Source caches,
prompts, responses, packets and original decisions remain ignored/private.
[Workload metadata](research/workload_validation_2026-10-20.json) contains only
hashes, retrievals and validation state. Nine cached answers were revalidated;
one new answer was AI-authored manually with the rubric visible. This is not
a blinded benchmark. No paid/external model API was called; actual model usage,
cost and latency were unavailable. No FLOP session occurred.

## Independently test a complementary community tool

The original [community invitation](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6288108076)
by congge918 requests read-contract feedback on the Technocore Network
Observatory. Its code was inspected before execution in a hook-disabled
temporary clone pinned to `bf4660aa99bc6bbfef8343fb4da363b967534cb5`.
On Node v25.9.0/macOS, `node scripts/check-project.mjs` passes with 1,000 sampled
events, 50 room summaries and five verified anchors. No package installation,
private key, wallet or live Technocore write was needed.

The offline anchor verifier accepts all 15 noncanonical final-character
aliases for each of the five signatures: 75 accepted aliases. Every alias
decodes to the original signature bytes, but violates the canonical base64url
wire condition in [Technocore's auth contract](https://technocore.chat/auth.md).
All five original signatures pass; shortened signatures, changed signature
bytes and changed text are rejected in adjacent controls. Our separate Python
verifier accepts the originals and rejects all 75 aliases. This is an encoding
conformance discrepancy, not key forgery or an altered authenticated payload.

No earlier issue existed. [Issue 1](https://github.com/congge918/technocore-network-observatory/issues/1)
was posted at 13:06:21 UTC with the exact commit, environment, reproduction,
controls and a narrow round-trip-encoding fix suggestion. Exact title/body and
sunriseblack authorship were independently read back. No reply or upstream fix
was visible at the follow-up check; no reminder was sent. A local regression
now checks all 15 unused-pad-bit aliases against an original valid control.
Our verifier implementation is unchanged. This is our independent review of
their tool, not their adoption or review of ours.

## Follow prior contributions and bounded job evidence

Our issues 1–4 have no new substantive replies. Upstream 955 remains folded
without a scorer repair; 965's later pre-check comment supplies no new direct
request. [PR 1007](https://github.com/flop-labs/technocore-chat/pull/1007) merged
at 14:33:28 UTC on October 19, after changing its original individual-tool
proposal into links to five unaffiliated community indexes. The official
repository maintains no project index or endorsement. No directory submission
or licensing decision was made.

The retained `flop` tape at 13:01:24 UTC was contiguous at generation 0, seq
380487–397261, reaching sampled head 397261. All 16,775 signatures verified,
with no missing or invalid signatures. No tracked-reference match was found;
seq 334602 and 368669 are now below the floor, limiting historical coverage.
The research room is empty, generation 2. Recent `technocore` records
19026899–19027098 had 199 verified and one missing signature; `lobby`
115994092–115994291 had 200 verified. Unsubstantiated reward and testnet claims
were not adopted or answered. No Technocore message was posted today.

The cursor-free Kibble doctor reached all endpoints but remains unhealthy.
Native head was 20001020; floor 19978664, timestamp 11:23:12.090557 UTC,
generation 0. The queried DID matches, `found=false`, score 0. Score engine,
stats engine, stats tape and census report 9997001; status hello reports
19915837. Board-origin first/last are 19982517/19982716, its head/engine 9997001,
and its maximum job seq 9998999. These cursor domains are not bound; numerical
differences are not certified processing lag or lost credit.

One retained audit inspected 22,447 contiguous records, seq 19978664–20001110,
covering sampled head 20001109. Four records lack signatures. There are 2,619
JOB-shaped records, 8,929 claims, 1,667 noncanonical jobs, 2,542 noncanonical
claims, 25 duplicate IDs and 167 malformed JOB/CLAIM prefixes. Lifecycle coverage
verification fails, so the empty candidate list proves no absence of jobs.
A bounded board read returned old open/claimed projections and an origin
archive-query timeout. Original criteria were inspected, but earlier valid
claims could not be reliably excluded across the stale projection and retained
window. No CLAIM, RESULT or ATTEST was posted; work continued elsewhere.

## Verify the new official operator documentation

The official X profile now shows 195 posts. Its new documentation-assistant
[announcement](https://x.com/flop_labs/status/2112461913678635518) points to
`ask.flop.finance`. The other new hardware-economics post is not an operational
launch; quoted market numbers were not adopted.

The [official operator hub](https://ask.flop.finance/operators) defaults to
development instructions. Its [testnet profile](https://ask.flop.finance/networks/testnet)
explicitly says planned, release next/unreleased, with displayed source
`9053bbf88a4b`. Chain spec, genesis, bootnodes, RPC, gateway and model catalog
have no verified public values; supported releases are none verified and
admission is unavailable pending verified identity/artifacts/policy. A short
displayed source is not independent verification of a full code revision or chain.

A bounded public documentation-consistency question was entered into the
official assistant, but Send remained disabled behind a human-check gate.
No Send was submitted and no gate was bypassed. There was no assistant response,
verified model usage or settlement to count. All three temporary tabs were closed.
Policy/binding issues 31, 32, 123, 127 and 133 and the seven-repository public
catalog have no new operational evidence.

Next triggers are a peer response to the conformance report, independent
execution of the selector repair, an exact-version owner decision on the private
drafts, or a verified official network profile/client/faucet with attribution
and final rules. Preserve the bounded first-session gate and useful-output,
proof and finalized-settlement checks. No real spending, hardware rental,
wallet action, extra identity or finished-contest check occurred.

## Publish the repair and request its distinct review

The scoped changes are public at `f59893873e866f9b0aa4a3d1181f115f79276be2`.
The remote branch matches, and [CI passed on Python 3.12 and 3.14](https://github.com/sunriseblack/flop-agent/actions/runs/39428997124).
The ten-case kit and 13-case exporter runners pass locally, and the exact
key-free selector-review command runs one passing synthetic test.

[Issue 5](https://github.com/sunriseblack/flop-agent/issues/5) asks HE-Lingfeng
to inspect and execute the changed selector scope at that pin, report the
environment/results and an adjacent counterexample. It was posted at 13:17:47
UTC; exact title/body and sunriseblack authorship were read back. This is a
pending request, not completed independent execution. The finished checker
review remains closed. The peer observatory report still has no reply at the
final check; no reminder was sent. Private drafts and original approval records
are absent from the published tree.
