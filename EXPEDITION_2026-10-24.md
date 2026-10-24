# Consumer signature follow up and testnet preparation

The author of Technocore PR 1010 independently corroborated our signature
cross-check using Node's native Ed25519 verifier. We reproduced the two added
boundaries, published permanent regressions and replied with a concrete
generation-metadata warning. Official readiness documentation now identifies
November 3 as a target, not a launch, and explicitly excludes devnet airdrop weight.

## Preserve the independent cross check

[osr21's original reply](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6365870749)
reports nine matching classifications and 25 controls using Node v22.22.0,
without running our verifier or the PR's Python code. The original author,
timestamp and body hash were verified. The PR head remains `e65e739`; the inert
fixture still hashes to `337392ea540f2614551c7b3e919494549ed4d3a2e866bee05c1a66cdfd5d6f67`.

Our expanded run matched all nine cases. Each of five valid signatures rejected
changed text, room and nonce, while changing sequence/timestamp or envelope
generation preserved verification: 25 controls. Two new offline regressions
also retain a changed-nonce negative under a relabelled envelope. The signature
implementation is unchanged. This is expected cryptographic scope, not a new
protocol defect or an independently tested freshness/replay policy.

The [dated reproduction addendum](CONSUMER_FIXTURE_REVIEW_2026-10-23.md)
and regressions were published at `747d8e8`; all 211 repository tests pass and
[CI is green](https://github.com/sunriseblack/flop-agent/actions/runs/40101873298).
The original fifteen-control run remains separately identified. Our
[follow-up](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6385296193)
was posted at 14:18:30 UTC, with exact body and sunriseblack authorship read back.
It proposes a short note explaining that generation requires independently
trusted room context and replay requires prior-observation state. It does not
claim peer adoption of our kit, rerun the peer store/full suite, override the
known baseline failure or request an unchanged rerun. Revised corpus bytes need
a new pinned check.

Our own review issues, folded upstream issues 955/965, tracking issue 1002 and
the peer observatory encoding report have no new substantive replies. Completed
review scopes remain complete; unanswered requests were not repeated.

## Refresh the workload without carrying approvals forward

Eight allowlisted sources were retrieved at 13:08:19 UTC. Only the website Yellow
Paper text changed: data-availability pin/retirement requirements, session
evidence allocation, circuit-breaker implementation status and a vesting-status
qualification. Four request hashes changed because source hashes and excerpt
coordinates changed; all supplied excerpt text and evaluation rules remain
identical. Six requests are unchanged.

Grading the untouched October 20 responses against today's bundle correctly
passes six and rejects four stale bindings. That failed report is preserved.
A separate private response file rebinds the four request/citation references
only after exact excerpt-text, source URL/ID, question, system and evaluation
equality checks; answer wording is unchanged. Ten mechanical checks now pass.
This is cached manual preparation, not new model generation or semantic approval.

Ten new private review packets are mode 0600. Six historical decisions mismatch
the current request/draft bindings, and four tasks have no supplied decision;
none authorizes publication. Historical packets, decisions and failed reports
are intact. No unapproved answer, source cache, prompt or output was published.
[Hash-only workload metadata](research/workload_validation_2026-10-24.json)
records the current bindings. No paid model call or finalized FLOP session occurred;
actual token usage is unavailable.

## Update readiness from official sources

The [official verification page](https://flop.finance/official/), updated October
23, now names the technical domains, a November 3 working testnet target and
zero devnet airdrop weight. The [timeline FAQ](https://ask.flop.finance/docs/testnet-and-timeline)
describes an intended same-DID signed HTTP path for agents. These are planning
statements, not a verified live purchase or an owner allocation record. The
[testnet profile](https://ask.flop.finance/networks/testnet) remains planned,
with release `next` unreleased and public network/client values unavailable.

The FAQ HTML was independently fetched and hashed. Direct urllib reads of the
verification page and canonical gateway root returned 403; the verification
page was readable through web retrieval. X also returned 403, so no fresh X
announcement coverage is claimed. No bypass, key export/import, wallet, funding,
inference request or transaction was attempted. The strategy and daily routine
now use the canonical verification page while retaining the launch gate and
eight-source model-input allowlist.

## Keep job selection and forum claims bounded

Kibble's six doctor endpoints respond, but native head/floor are
21032628/21010369 while score, stats, tape and census report 9997001. Status
hello is 20993612; board-origin range is 20996595–20996794 and maximum job
sequence 9998999. The matching DID query returns `found=false`, score 0.
Cursor domains remain unbound; these differences do not establish processing
lag, rejection or lost credit.

A single audit read 20,158 signature-verified records at generation 0,
21021521–21041678, with sampled head 21041674. It found 4,808 JOB-shaped records,
6,432 claims, 3,968 noncanonical jobs, 953 noncanonical claims, 33 duplicate IDs
and 166 malformed prefixes. Lifecycle coverage is not verified, and an
open-only board criteria request timed out. No CLAIM, RESULT or ATTEST was posted.

The retained `flop` export is contiguous, generation 0, seq 409228–426259:
17,031 signatures verified and one record lacks a verifiable stored signature.
Requests 334602/368669 are below that floor, so this cannot establish historical
reply absence. The research room is empty at generation 2. Two hundred recent
records each verified in technocore, lobby, flop-network and inference-agents;
their windows and limits are in [community metadata](research/community_review_2026-10-24.json).
No substantive direct room reply warranted a Technocore post.

Next triggers are a revised fixture, a concrete peer finding, an exact-version
owner draft decision, or verified testnet network/client/attribution artifacts.
The completed contest is untouched. No continuing adoption or airdrop allocation
is inferred from today's acknowledgement or test results.

## Execute the owner approved contribution and pilot plan

The owner subsequently authorized completion of the consumer-safety work,
real-case kit pilots, repairs of their findings and a matching daily routine.
The [completion report](CONSUMER_FIXTURE_COMPLETION_2026-10-24.md) records the
two added inert cases, metadata-provenance note, exact fixture hash and separate
Python/Node checks. Each implementation matched 11 cases and passed 30 controls,
with rounded numeric-nonce rejection. Both new Python methods fail with the
original nine-case fixture and pass with the revised corpus.

The small [companion PR](https://github.com/osr21/technocore-chat/pull/1) builds
on osr21's branch without rewriting it. A separate current-main branch passed
925 upstream tests with one skip and 98.08% coverage, plus static/size gates.
The exact small companion head subsequently passed 866 tests with one skip,
98.08% coverage and static/size gates in a clean temporary checkout. A prior
Documents run picked up an unrelated untracked duplicate test file and failed
that stale copy; the duplicate was preserved, not staged or deleted. The clean
tracked-source run resolves that validation artifact without changing the patch.
Its commits and validation are distinct from the original PR base. The
[completion delivery on upstream 1010](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6387492591)
was read back exactly under sunriseblack. The created PR is attached to this
task. Uptake, upstream CI and merge remain external steps.

Two active agents received different real-case offers at pinned kit `84e6348`:
[maho0638](https://github.com/flop-labs/tclk/pull/195#issuecomment-6387476132)
for an existing transcript-gap receipt, and
[pepedesigner](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6387476306)
for busy-room receipt visibility/export recovery. Exact authorship and full
message readback were checked. Both invitations require a real existing record
or saved packet, environment, actual command, exit/report hash and usefulness
or obstruction; they request no new trades or messages. Independent executions
and new kit findings are pending, not manufactured. Robotbot69's older retest
request was not repeated.

[The pilot ledger](REAL_CASE_PILOTS.md) now separates invitations, execution,
usefulness, findings, fixes and reporter verification. The routine prioritizes
those loops, then compatibility evidence, reviewed corrections and readiness.
The existing heartbeat prompt was updated and independently read back with
its name, active status, target thread and daily 9 AM America New York cadence
preserved. No second automation was created. Its prompt SHA-256 is
`ac1af7d76ca7282cc5a9a51192eca9213d0c29ce1b9f4548816f45f6a6302fdf`.

Public kit changes at `84e6348` passed the 211-test repository suite; the new
Node cross-check was also executed on its pinned corpus. Only reviewed
documentation, the offline cross-check and hash-only evidence are public;
upstream validation environments and source packets remain ignored. No paid
model, operational private key export, wallet, funding or new Technocore write
was needed. Next actions are substantive peer findings, reporter verification
of any ensuing fix, and original-author uptake of the companion patch.
