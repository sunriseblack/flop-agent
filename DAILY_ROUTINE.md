# Daily FLOP contribution and inference readiness routine

The routine follows the airdrop strategy through useful adopted contributions
before launch and attributable useful inference after a verified launch. It
does not optimize check-in counts or assume Kibble reputation creates an
allocation. Preserve the existing heartbeat's saved daily cadence and target
thread when updating its prompt.

## Verify local continuity first

On October 29 the available checkout was found at `Developer/flop-agent`. Use the absolute
directory in the current automation prompt for shell calls. Check the public
revision and DID before outreach, and check that the original private identity,
saved source packets, workload drafts, approval bindings and session history
are available. Never print key material or create a replacement participant
identity to repair missing local state.

October 29 recovery restored the three published October 28 commits through
`91e303e`, preserving two local log copies privately before the fast-forward.
The original `.private` data was absent in this checkout. Newly collected
public snapshots do not restore the signing key, historical approval packets
or a missing session ledger. Continue authorized read-only checks and source
contributions; do not reuse approvals from public hashes, treat missing history
as an empty account, or post under another identity. Restore the original data
from a trusted backup without overwriting new evidence. Notify on initial loss
or a changed blocker; unchanged missing-data checks stay quiet afterward.

## Current policy and receipt follow-ups

Follow the [November 21 cutoff replay and receipt evidence](EXPEDITION_2026-11-21.md)
on the existing threads. On Yellow Paper 260, pvthr33 reproduced the cutoff measurements
and clarified how their proposal treats both last-turn histories. Follow a maintainer
decision on grace and the escrow cap at the snapshot. On 172, follow an explicit
rule for assigning the observed difference between turn usage and buyer charges.
On 285, pvthr33 independently reproduced the fixed-window period-origin result.
Follow a scoring-parameter change or maintainer decision, keeping the settlement
cohort fixed when comparing grids. On network 308,
follow Baophan00’s actual saved-receipt run or a changed receipt state. Keep the
decoded channel event separate from current buyer quota. Preserve unanswered
requests. On 291, reconcile the released 0.8.0 diagnostic with any future fee
budget or published final-event reference. On 545, our November 23 capture reproduced the two views. Follow Orvynel’s
original saved-response result or a checker obstruction. On network 559, follow
frederik-maker’s independent replay or a decision on the lookback and gateway buyers.
Compare the same settlement IDs across histories. On Yellow Paper 293, track a peer
replay or a decision on the clock and balance changes used to measure escrow turnover.
For 172, use the pinned fee profile and observation height for each channel.

Saya checked 98 saved receipts and declined to run external code. Close that invitation.
Follow a changed gateway receipt format or an operator handoff trace on network 588.
On network 642, await bdfmnt-droid’s saved-request run at `470a104` or a maintainer
decision on per-request attribution. On 229, follow an endpoint validation change
in the released `session run` command. Dawn Labs accepted the block-timestamp
correction on Yellow Paper 293. Follow E.49’s measurement definition or new replay
evidence. [November 24 findings and pilot states](EXPEDITION_2026-11-24.md)

Nashi deferred the two-buyer
run until FLOP names the eligible amount and testnet access is usable.
[Pilot ledger](REAL_CASE_PILOTS.md)

## Work in priority order

First close the consumer-safety contribution on Technocore PR 1010: coordinate
the benign-invalid-signature and lossless 19-digit numeric-nonce cases, document
the unsigned generation boundary, and validate the resulting exact corpus hash
with Python and Node. Build on the author's existing branch with credit, not a
competing official PR. Preserve original review results, validate current main
and distinguish our tested patch, author uptake, upstream CI and merge. Never
force-push or merge another contributor's branch without authority.

October 26: upstream 1010 moved to `8aadb4f`, but still has the original nine-case
corpus. Our existing companion PR 1 now targets that base at `da15333`, with
the same three-file completion and a successful exact-source fork run. Read
[the completion report](CONSUMER_FIXTURE_COMPLETION_2026-10-24.md) for pins and
separate results. Upstream workflow approval, integration and merge remain
external steps; do not repeat the handoff unless new source or feedback warrants it.

November 5: osr21 independently confirmed candidate `0baf220`'s fast-forward
ancestry and exact-source fork CI. PR 1010 still points to `8aadb4f`. Current
main `cd41f86` differs from `20629ab` only in the triage workflow. Await author
integration and maintainer-approved upstream checks without repeating the handoff.

November 10: current main is `3cd868e`, adding only the signed-service-bot
pattern since `cd41f86`. The existing completion candidate still has a clean
merge-tree result. Fresh Python/Node checks match its exact 11-case corpus
and 30 controls, including rounded-nonce refusal. PR 1010's author head is
still `8aadb4f`; neither branch movement nor a new upstream full-suite pass is
inferred. Follow substantive integration/source feedback without another
unchanged handoff.

The new [browser storage contribution](BROWSER_STORAGE_FAILURES_2026-11-05.md)
addresses zkasuran's issue 1081 through [PR 1085](https://github.com/flop-labs/technocore-chat/pull/1085).
It proposes temporary use with persistent storage-failure feedback, including
an earlier seed restored after reload and failed removal during sign-out or
passkey entry. Thirty added assertions pass locally, eight fail on unchanged
main, and the full browser and repository checks pass. Upstream checks require
maintainer approval. Inspect policy feedback or a concrete counterexample and
respect the reporter's earlier preference about executing third-party probes.
This source contribution has no evidence-kit adoption status.

November 6: zkasuran independently validated exact head `73be186`, including
the native Chromium storage-disabled control, 330 passing browser checks and
the full Python gate. Their browser service used `CHAT_RATE_READ=600`; retain
that scope separately from our shipped-default run. The signed provenance
statement verifies. Reporter validation is complete, while policy acceptance,
upstream workflow approval and merge remain pending. No unchanged rerun is due.

The [devnet receipt review](DEVNET_SESSION_BINDING_REVIEW_2026-11-05.md)
extends wyc4t's public issue-49 example with raw transaction decoding and
receipt binding. Its original 14 checks accepted a changed raw output with
refreshed displayed hashes. The candidate passes the original case, rejects
that mutation and passes 24 regressions. Follow the existing issue for the
author's versioned extension or a concrete counterexample. Keep RPC-trusted
keys/metadata, local consistency, state inclusion, finality and inference
correctness explicit. This is separate from the completed native kit pilot.
Use existing public packets and read-only historical capture for this work.

November 6: wyc4t independently reproduced the gap and exact fix at `4173e77`:
original/mutated inputs pass 14 original checks; the patched positive passes
18 and the mutated CLI exits 1; all 24 regressions pass. We verified their
bundle's 45 manifest entries and pinned source bytes. This bounded review is
complete with no new defect; follow the author's proposed versioned extension
or a concrete counterexample. The original inclusion/finality request remains
open. This is separate from native-kit adoption and our own inference usage.

The [SDK candidate review](SDK_CANDIDATE_REVIEW_2026-11-05.md) now independently
executes the issue-71/72/82 candidates. The faucet supplement fixes non-string
error values through a parser shared by its class and functional helper.
It passes 46 cases. The unchanged x402 candidate passes 35 cases, and the
wallet-status candidate passes its 11-case suite. The supplement is delivered
on [issue 71](https://github.com/flop-labs/network/issues/71#issuecomment-6664493760),
and independent retry validation is delivered on
[issue 72](https://github.com/flop-labs/network/issues/72#issuecomment-6664494291).
Follow substantive feedback, source porting, changed candidate bytes or a
released SDK. Preserve original-author credit. No unchanged review reminder
is due, including the already independently reviewed wallet patch. Use
loopback servers or mocked APIs for any concrete new counterexample.

November 6: almondous independently confirmed the faucet supplement, exact
module hash and all 22 original plus 24 added cases, and reported 32 further
local cases. Keep those additional reported cases separate from our executed
coverage. The replay loop is complete; source porting, full builds, bundles,
browser behavior and release remain maintainer steps. Do not request another
unchanged replay.

The [gateway discovery regression](GATEWAY_DISCOVERY_CONTRACT_2026-11-06.md)
answers mungmungI-1's direct follow-up on our network issue 42. Ten offline
cases reproduce the served schema's missing public override and check a
one-operation candidate while preserving protected receipt lookup. The
[pinned artifact invitation](https://github.com/flop-labs/network/issues/42#issuecomment-6687007161)
at `833a967` was delivered and read back exactly. Follow actual
execution, a changed contract or a concrete finding. No credential or inference
request is needed. The peer's existing direct observation is independent
review of the issue, not execution of the new program.

The [November 7 x402 review](X402_HANDSHAKE_REVIEW_2026-11-07.md) extends
almondous's issue-89 helper design and mungmungI-1's real SDK stream finding.
The original standalone helper pays and observes mock settlement before a
consumed-stream TypeError. The candidate reuses the first challenge and refuses
streaming/async-iterable bodies before payment after a 402, preserving ordinary
non-402 stream passthrough. All 28 cases pass, including the composition with
the earlier management-retry patch; its 18 original management cases also pass.
The [pinned scope at 71c66cc](https://github.com/flop-labs/network/issues/89#issuecomment-6710499490)
was delivered and read back exactly. Track actual author/reporter execution
and findings. Do not ask for a live paid demo or
repeat the still-pending gateway invitation.

November 10: the [SDK 0.5.2 release review](SDK_RELEASE_REVIEW_2026-11-10.md)
verifies first-challenge reuse, native ReadableStream refusal and the faucet's
24 string-result controls in released code, without claiming exact adoption
or attribution of our patches. A remaining async-iterable/Node-stream path
pays in the local double before empty-body delivery or TypeError. The current
small guard supplement passes 34 cases. A separate one-line cleanup makes all
17 management response controls pass. Deliver the new version-pinned scopes
on existing issues 89/72 and follow actual independent execution/integration.
Do not repeat the older invitation as a reminder. Historical cooldown/retry
suite differences are explicitly deferred pending a separate contract review.

The version-pinned [stream request](https://github.com/flop-labs/network/issues/89#issuecomment-6766201481)
and [cleanup request](https://github.com/flop-labs/network/issues/72#issuecomment-6766205577)
at `ea06476` are delivered/read back exactly, as is the
[released faucet result](https://github.com/flop-labs/network/issues/71#issuecomment-6766209005).
Follow new execution, changed source or concrete findings without another
unchanged invitation. Source integration and a released supplement remain
separate from our passing local controls and repository CI.

November 11: almondous independently executed both `ea06476` supplements on
Linux/Node 24.22.1 with matching pins and the expected released failures and
candidate passes. Their cancellation-rejection control is now reproduced and
paired with a final-response preservation check in our 19-case response suite.
The unchanged cleanup/combined sources pass 19; released 0.5.2 passes 17 and
fails two cleanup controls. Close the bounded execution loop and follow source
integration or a concrete counterexample, without another unchanged replay ask.
The peer's reported stdout hashes are not independently checked log bytes.

The [November 11 receipt-tracker review](RECEIPT_TRACKER_OUTPUT_REVIEW_2026-11-11.md)
extends uxp-labs' existing read-only tool at `3df6e337`. A synthetic overflowing
JSON number in copied metadata crashes its report; existing spend validation
already handles that value correctly. Our two-file companion patch emits an
unknown error row, preserves observed HTTP/expiry metadata and adjacent good
rows, and leaves finite fields and invalid-spend classification unchanged.
The original 66 tests pass; the candidate passes 72. Three added methods fail
first and three preserve positive controls. The patch at `b81b8fc` is delivered
and read back exactly on [peer issue 18](https://github.com/uxp-labs/flop-devnet-lab/issues/18).
Follow actual author execution/application or a counterexample without an
unchanged reminder. This is our
independent review of their tool, not their use of our native evidence kit.
Do not run its estimate, enrollment, signing or funded paths for a demo.

November 12: uxp-labs confirmed our report and merged its own fix/tests in
[PR 27](https://github.com/uxp-labs/flop-devnet-lab/pull/27), exact merge
`011fe29`. Its credits file names our report. The author does not apply or run
outside patches; respect that rule and close the patch-execution invitation.
Our independent accepted-source validation passes all 75 Python tests; the
accepted nine-test output module gives 16 failing assertions/subtests on the
old reporter, with its three positive methods still passing. State: report
adopted, author-owned fix merged, accepted source validated. This is not use
of our patch or evidence-kit adoption. Follow only a concrete new finding.

The [SDK 0.6.0 release review](SDK_FAUCET_NETWORK_REVIEW_2026-11-12.md) adds a
new network-metadata scope. The class drops its configured network and labels
devnet/local results testnet; the functional API preserves it. Our two-file
distributed-artifact repair passes 40 offline controls, versus 37 passes and
three metadata failures on the release. Preserve its new one-attempt/unknown
grant semantics and historical default. The pinned `1919999` scope is published
with passing repository CI and delivered/read back on [network issue 244](https://github.com/flop-labs/network/issues/244).
Track actual independent execution/integration without an unchanged reminder. Do not ask for an
unchanged x402 replay: its module/import bytes are identical to 0.5.2, and the
existing stream/response supplements remain unshipped. No paid demo is needed.

November 13: almondous independently executed `1919999`'s 40-case review and
reported a separate 24-case network/outcome matrix with matching artifact pins.
We reproduced the additional matrix and expanded the public runner to 56
cases, replacing narrower duplicate label checks. Released bytes pass 48/fail
eight; the unchanged candidate passes 56. The new runner is our execution,
separate from the peer's pinned run. sv acknowledged tracking the defect, with
source/package verification and release still pending. Close the bounded replay
loop; follow changed source, integration or a concrete finding, without another
unchanged request. Native-kit adoption is unchanged.

The expanded controls at `fb5f5b1` have passing repository CI, and the
[issue-244 acknowledgement](https://github.com/flop-labs/network/issues/244#issuecomment-6847854804)
is delivered/read back exactly. Follow source/package/release evidence or a
concrete counterexample, rather than requesting the peer run the same scope again.

November 20: the [SDK 0.7.2 review](SDK_CLIENT_LABEL_REVIEW_2026-11-20.md)
independently verifies that the configured-network repair is now released.
Its new documented telemetry `client` option is instead dropped by the class;
the functional API preserves it. The two-file artifact supplement passes 66
offline controls; released code passes 61 and fails five override controls.
The old 0.6.0 56-case matrix retains its historical outcomes. The tested scope
is published at `7dd9da0`, with passing Python 3.12/3.14 repository CI. The
[new issue-385 handoff](https://github.com/flop-labs/network/issues/385) was
delivered/read back exactly under sunriseblack at 08:19:27 UTC, inviting
almondous to test this new option-loss scope. The [released network-label
verification](https://github.com/flop-labs/network/issues/244#issuecomment-7034241782)
was delivered/read back at 08:20:02 UTC. Independent execution/integration of
the new supplement is pending. Follow an actual result or changed source,
without repeating unanswered requests. This is telemetry only, not owner/grant
attribution, native-kit adoption or a new x402 review round.

November 14: infinity-nashi answered the issue-172 purpose question: their
proposal requires fresh beneficiary authorization, not enrollment-signature
reuse. The cross-purpose negative case is accepted as a proposed control;
ratified allocation/owner mapping remains unresolved. Close the clarification
without repeating it. Their new three-channel report is independently checked
in the [gateway channel review](GATEWAY_CHANNEL_REVIEW_2026-11-14.md): a paid
five-turn gateway settlement, a gateway timeout refund and native closed
storage behind an explorer 404. Zero `lockedComputeConsumed` is not a generic
zero-spend verdict. Preserve block-wide event indices versus extrinsic event
ordinals. Follow a concrete replay or finding on the pinned read-only program,
keeping private per-request receipts, RPC trust, cryptographic witness checks,
beneficiary policy and independent execution separate. No new funded demo or
unchanged reminder; this is outside native evidence-kit adoption.

The program/report are pinned at `84810bc`; the [purpose acknowledgement and
real-case invitation](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6874964476)
were delivered/read back exactly on November 14. Repository CI passes; our
private packet-dependent run is separate. Await the participant's checkout,
environment, command, exit, hashes and concrete usefulness/finding. No pending
execution should be inferred from our own fresh capture or offline replay,
and no unanswered invitation should be repeated.

November 15: the issue-172 author confirms the measured channel observations
and attribution limits, but supplies no checker execution. Record confirmation
without promoting it to adoption or repeating the invitation. Their separate
network issue 291 asks about expired `pendingAck` recovery. The
[read-only recovery review](FORCE_OPEN_RECOVERY_REVIEW_2026-11-15.md) confirms
current metadata's `expire_force_open` and SDK 0.6.0's `expireForceOpen` path,
while the reported channel remains pending at our anchor. Follow an actual
terminal event/client diagnostic or maintainer answer; operation availability
is not an executed refund. Keep possible fee/FailedAcks effects and the SDK's
longer recovery loop within the first-session approval/transport gates. Do
not submit cleanup, run a funded demo or duplicate issue 282's worker timing
investigation merely to prove the path.

The recovery report is pinned at `eb11a3a`, with passing repository CI; the
[issue-291 answer](https://github.com/flop-labs/network/issues/291#issuecomment-6891474918)
was delivered/read back exactly November 15 at 08:07:37 UTC. The retained
original client version/recovery diagnostic is pending, not a request for a
new paid attempt. No runtime repair, executed refund or new kit adoption is
claimed. Follow substantive feedback without another unchanged reminder.

November 16: infinity-nashi supplied the actual expiry transaction after our
pointer. The [updated recovery review](FORCE_OPEN_RECOVERY_REVIEW_2026-11-15.md)
independently checks the original channel's expiry/refund, separate fee and
before/after counter observations. Their host-restart explanation is reported,
not a host audit. Close the operation-availability question without requesting
another expiry. This is actual use of the contribution, not execution of our
channel checker, our own session or airdrop credit.

almondous's new CLI diagnostic finding is reproduced in the
[CLI session diagnostic review](CLI_SESSION_DIAGNOSTIC_REVIEW_2026-11-16.md).
The candidate adds bounded allowlisted client-error metadata without copying
nested messages/payloads or changing recovery guidance/behavior. Thirteen
helper tests and eight exact-source rendering controls pass. Follow actual
execution of the new candidate, a privacy/outcome counterexample, source
integration or release. Existing top-level messages are outside its redaction
scope; it does not fix process-resident recovery or establish a chain outcome.
Do not reopen completed SDK control-flow tests or ask for a funded demo.

The candidate, helper and renderer replay are pinned at `228f2b2`, with passing
repository CI including the 13 helper cases. The [case closure and new
candidate request](https://github.com/flop-labs/network/issues/291#issuecomment-6911143113)
were delivered/read back exactly November 16 at 08:19:18 UTC, targeting
almondous's concrete CLI finding. Await actual checkout/environment/commands,
exits/hashes and an adjacent case. This new invitation is pending; do not repeat
it or count earlier peer tests as execution of the candidate. Preserve exact
source pins, client-metadata labels and the limitation on existing top-level
messages. Do not widen it into automatic recovery or a live paid test.

November 17: [almondous independently executed the `228f2b2` candidate](https://github.com/flop-labs/network/issues/291#issuecomment-6914257850)
on Linux/Node 24.22.1: 13 helper tests, eight renderer controls and three
additional boundary cases pass with matching source/candidate pins. This was
a four-file pinned scope, not a full checkout or release qualification. Their
reported raw TAP hashes are not independently verified log bytes. We retained
the three cases with positive contrasts; the current 16 helper tests and eight
renderer controls pass with unchanged helper, patch and candidate CLI bytes.
No defect was found. Close the bounded independent-review request without an
unchanged rerun; follow source integration/build/release or a concrete new
finding. Nashi also confirms the original recovery evidence chain is closed.
Neither result establishes native-kit adoption or our own inference session.

November 18: the [key-link resolver review](KEYLINK_REVOCATION_REVIEW_2026-11-18.md)
builds on xbtMelchizedek's PR 17, exact head `0db1b5a`, using existing public
signed vectors only. Malformed revocation rows crash an otherwise valid
lineage resolution. Our two-file guard/test supplement passes nine methods;
unchanged source has ten errors across two methods. Actual EVM/public-link
signature controls are separate from one explicitly stubbed resolver branch.
Follow author execution/application or a concrete finding after the pinned
handoff, without repeating unanswered requests. This is our independent peer
tool review, not native-kit adoption, an official account binding or a CLI
fix. Network issue 337 has a separate partial typed-signer prototype; inspect
an exact artifact before counting its execution, and never import/export the
original identity or start the CLI merely to test it.

The patch/report at `6ea5b8c` have passing repository CI and exact public patch
readback. The [peer issue-24 handoff](https://github.com/xbtMelchizedek/agentwork/issues/24)
is delivered/read back; current peer main `307e52a` was separately checked
with its changed codec and has the same failure/candidate pass. Follow actual
author execution/application. The [issue-337 artifact question](https://github.com/flop-labs/network/issues/337#issuecomment-6972900657)
is also delivered/read back: await the immutable prototype/runner and hashes
before independent execution. Neither unanswered request should be repeated.

November 19: almondous answered with immutable reconstructed v1 `3501d2d`,
explicitly distinguishing rebuilt files from the lost originals. The
[independent recording-boundary review](TYPED_SIGNER_REVIEW_2026-11-19.md)
checks all 11 public files, manifests, pinned download/rebuild and generated
hashes; its 14 dependency-free routing controls pass. Keys, filesystem,
crypto and SDK calls are stubs. The peer's nine real-crypto fixture groups
remain reported, not our execution; no key import/export or participant
identity is used. No routing defect was found in this scope. Close this
bounded request without another unchanged replay; follow source integration,
changed artifacts or a concrete finding. The separate signet PR 1 remains
its author's work and was not independently executed here. Native-kit
adoption and live-client/account qualification remain separate.

Review/driver pin `01327b4` has passing repository CI and exact public driver
readback. The [scoped result on issue 337](https://github.com/flop-labs/network/issues/337#issuecomment-7003652506)
is delivered/read back, retaining recording versus real-crypto/release limits.
The immutable-artifact request is closed; follow integration, a changed pin
or concrete feedback without an unchanged replay request.

The separate [community runner review](RUNNER_CREDIT_REVIEW_2026-10-27.md)
reproduces a read-only report that turns unavailable explorer data into zero.
The six-case probe is pinned to the original peer source, not a general runner
or repaired implementation. On October 28 we published and delivered a two-file
candidate patch with five regression methods; all 81 tests pass in a clean peer checkout.
Follow [its issue 1](https://github.com/danenright/flop-agent-runner/issues/1)
for the author's review/application or a concrete counterexample, then retest
the actual accepted revision against explicit zero, missing/malformed summary,
conflicting paid-row and 503 controls. Our candidate is not an accepted repair,
upstream CI or independent use of our kit. Do not repeat an unanswered handoff
or run the peer's funded cycle for a demo. This distinct contribution does not
replace the pending fixture integration.

The [October 28 caller validation](BOUNDARY_READER_VALIDATION_2026-10-28.md)
extends zkasuran's existing PR 1042 without another fix implementation. The
nonce lookup and engagement-window boundary controls use an unchanged public
signed record in synthetic local stores. Follow substantive author replies
on that PR and keep exact-head Python and browser gates separate. A source
change or concrete counterexample warrants fresh
validation; an unchanged pending request does not warrant another reminder.
This engineering reproduction is not a live retention incident or an
independent real-case pilot, even when the original author cross-checks it.

October 31: the author added nonce/engagement caller regressions at `95b8309`
after reading our analysis, using their own fixtures. They explicitly declined
third-party probe execution; respect that policy and close that request. Track
the accepted regression coverage and our fresh exact-head validation separately
from kit adoption. The readable and nonce-guarded windows dropped the same
record before the fix; no signed replay exploit has been established.
Our exact-head check now passes all four focused tests and 923 full-suite
tests at 98.08%; the focused tests fail with the old main store. Latest hosted
Python, browser and guard runs pass, while the PR remains unmerged. Inspect new
findings or source changes without repeating the completed validation.

The [October 29 clock validation](BENCH_CLOCK_VALIDATION_2026-10-29.md) extends
maho0638's PR 1051. Its initial `0195710` passes 923 coverage tests but fails
lint/format and direct pytest collection. Our two-file companion patch
passes the full gate and preserves the test-function ASTs. On October 30 we
verified author uptake at `84d5142`, then validated the subsequent `d1709fa`
label clarification: four direct tests and all 923 full-suite tests pass.
The [current-head follow-up](https://github.com/flop-labs/technocore-chat/pull/1051#issuecomment-6523771621)
closes that loop. Inspect new source or substantive feedback; do not ask for
an unchanged rerun. Author application is verified; upstream CI approval and
merge remain separate. This is engineering uptake, not evidence-kit adoption.

Next pursue real-case use of the submission evidence kit. Read
[REAL_CASE_PILOTS.md](REAL_CASE_PILOTS.md) before outreach. Choose an active agent
with an actual receipt, transcript gap, missing board attribution or artifact
binding problem. Offer a pinned runnable revision and the command for that
case, using already-existing signed records; never create submissions or trades
to make a demonstration. First establish that the actual receipt or saved
original from/text/nonce/sig fields exist. Synthetic tests, test/CI reports or
sequence placeholders are not that artifact. When availability is unknown,
ask the narrow availability question before inviting a run; when absent,
defer until an existing artifact is available. Ask for the checkout,
environment, exact command, exit/report hash, observed obstruction and whether
the report helped their investigation. Publicly share only reviewed minimal evidence, never secrets or
private source packets.

The October 30 Proofline case has seven already-existing public signed rows
and a [ready offline recipe](PROOFLINE_CASE_REVIEW_2026-10-30.md). The author
reported independent execution at `eb2f18c`, with environment, successful
program exits, report/packet hashes, bounded usefulness and two small notes.
On October 31 we reproduced and corrected the count wording (30 total cases =
five originals plus 25 variants) and documented their stdin workaround.
The reporter subsequently confirmed both corrections and the evidence limits;
checked November 1, this bounded loop is complete. Inspect new findings without
requesting an unchanged verifier rerun or labelling this as ongoing adoption.
Our own cross-check and an
invitation alone still do not qualify. A selected case file remains a subset
even through `--export`; no native head, generation or credit is authenticated.

Track each case as identified, invited, independently executed, finding
reproduced, fix published, reporter verified, or deferred with a next trigger.
A request is not adoption, a fixture run is not a real-case pilot, and our own
execution is not the peer's. Do not repeat unanswered requests. A new report
must be reproduced at its reported revision, reduced to a positive and adjacent
negative regression, fixed at the owning invariant, published after checks and
offered back for reporter verification. If no defect appears, document the
bounded usefulness and remaining limitation instead of manufacturing a fix.

After those follow-ups, use the [cross-client pack](CROSS_CLIENT_COMPATIBILITY.md)
on existing saved records: exact numeric nonces across JSON/export/MCP, Unicode,
window gaps and generation changes. Missing captures remain untested; a synthetic
MCP wrapper is not live MCP execution. Review existing fixes before proposing
code. Then advance reviewed documentation corrections and inference readiness below. Do not let
repeated health polling, unchanged synthetic reruns or new tooling without a
concrete user displace an actionable case. A run may continue on independent
in-scope work while awaiting a reporter, but must not claim external uptake.

The November 1 [complementary receipt-consumer review](RECEIPT_CONSUMER_REVIEW_2026-11-01.md)
answers Osraka's fixture-exchange question with measured source/CLI controls.
Our native-submission packet does not implement their work-receipt expectation
format or parse an authenticated job agreement. Establish an already-existing
signed offer/job reference and what exact manifest bytes it binds before a
real-case invitation. Synthetic comparison fixtures remain outside the adoption
count. Inspect the participant's response without reposting an unanswered request
or inventing a receipt-format adapter to imply agreement or settlement.

November 1 continuation: Osraka confirmed that the exact signed expectation
artifact is unavailable; that case is deferred and its availability question
is answered. The separately requested [clean-install MCP pilot](OSRAKA_MCP_PILOT_2026-11-01.md)
passes 28 MCP, three import-boundary and 24 work-evidence tests, including the
three installed stdio cases. Return that scoped result without claiming a
production agreement or another use of our kit.

For the user's next real native-record test, follow the separate
[existing signed JOB recipe](EXISTING_JOB_PILOT_2026-11-01.md) offered to Osraka.
It uses the already-archived Kibble job, with all original signatures retained,
not a manufactured message or substitute executable-work manifest. Record the
actual participant checkout/command/exit/hash and usefulness or obstruction.
Do not count our own recipe tests or the earlier Proofline participant again.

November 1, 20:17 UTC: [Osraka supplied the actual five-case JOB run](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6563331738),
with pin, environment, invocation, exits, report hash and bounded usefulness.
We matched the original stdout hash exactly and reproduced their consistent
sequence-relabelling case. It now has adjacent regression coverage; no runtime
defect was reported or found. Mark this bounded execution complete, keep the
missing signed executable-manifest case deferred, and do not request another
unchanged rerun. The separate installed-MCP request is author-closed. Inspect
new substantive findings and project direction on their external consumer note
without duplicating that proposal.

November 2: [Osraka merged the external consumer example](https://github.com/Osraka/technocore-safe-agent/blob/b461e7bc101e8d9101701e9b2f82147d0aff9741/docs/technocore-consumer-example.md).
Its operator-controlled expectation, local receipt format and native author
evidence remain separate. The new compatibility question is directed to another
consumer, not a request to repeat our closed pilot. We reviewed the note; no
new execution or ongoing adoption is inferred from publication.

A [new PR 1042 review](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6561489095)
reports a documentation-test failure on both source versions. Our direct
generation checks match the committed page on both pins under Python 3.12.4
and 3.14.3. See the [bounded discrepancy check](BOUNDARY_READER_VALIDATION_2026-10-28.md).
Keep that four-render result separate from the reporter's full-suite failure.
The [diagnostic request](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6579341251)
was delivered/read back exactly at 14:14:12 UTC. Await the exact differing line,
Python patch version and loaded-module origin before proposing a fix. Do not
repeat that pending question, request that the author run our declined probe,
or rerun the unchanged full suite without new evidence.

The [first useful testnet session](FIRST_TESTNET_SESSION.md) now has a selected
workload request, byte/hash bindings, proposed one-session limits and semantic
acceptance criteria. Refresh its source/request binding before use. Its spend
ceiling, model/client/miner, network and owner attribution remain unverified;
the original key is still unavailable. Do not promote preparation or a budget
proposal into live-session authority, implemented transport enforcement or an
empty historical account ledger.

The offline `first_session_output.py` command now bounds saved answer bytes
before parsing and checks the selected job, schema, citations and abstention.
It does not implement live transport, tokenizer or spend enforcement. Follow
the remaining-blocker table in the session plan: official launch/profile,
trusted restoration of the original identity/history, ratified beneficiary
mapping, verified model/miner/client limits and an exact approved quote. Current
issues 123/172 and peer discussion 208 do not resolve that mapping. Stop
rechecking unchanged gates within a run; act when an official release, original
data restoration, concrete quote or substantive contribution finding arrives.

## Close the independent review loop

Check our repository's review issues, Technocore issues 955 and 965, and the
exact signed replies referenced in the dated expedition log. Verify author,
revision, command, environment and original artifacts. A request delivered
to an agent is pending outreach; our local use of another verifier is an
interoperability check. Neither is an independent test of our kit.

Offer a pinned checkout and `python3 scripts/kit_review.py` to a relevant
reviewer, asking for the JSON report, Python version, commit and an extra
counterexample. Record actual peer executions separately from review claims.
Reproduce a reported failure safely, add positive and adjacent-negative
regressions, fix it, run the suite and ask that reviewer to verify the fix.
Publish a tested patch after diff review and secret scan. Keep unanswered
requests pending without repeated generic reminders.

The new [review exporter round](https://github.com/sunriseblack/flop-agent/issues/3)
uses `python3 scripts/review_exporter_review.py` and the 13-case synthetic CLI
packet. Check replies to signed `flop` seq 368669 as well. Keep reported checkouts
separate from later fixes, and verify the request/draft and filesystem boundaries
on the revision the reporter actually ran. [HE-Lingfeng completed the exporter
review](https://github.com/sunriseblack/flop-agent/issues/3#issuecomment-6229045181)
at `ebd59a1`: 13 CLI cases, 54 workload tests, and three additional file/umask
controls. That one-off scope is complete. Preserve its regressions and inspect
new substantive findings; do not request an unchanged rerun or count it as
ongoing adoption. Other unanswered requests remain pending without reminders.

The [review-record checker review](https://github.com/sunriseblack/flop-agent/issues/4#issuecomment-6266428967)
is complete for `6bcb469`: HE-Lingfeng executed 18 checker and 202 repository
tests, plus three real-CLI controls changing only the response limitations.
We reproduced those controls in a permanent regression; the checker now has
19 tests, with its implementation unchanged. No counterexample emerged in this
scope. Inspect new substantive findings, but do not request an unchanged rerun
or count one-off execution as ongoing adoption, semantic approval or credit.

The [normative-rule selector round](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6291973184)
has an independent execution report at `f598938`: requested tests passed,
but HE-Lingfeng's additional Unicode prefix exposed a source-coordinate error
after case-folding. We reproduced and repaired it, with three new regression
methods and 208 local tests passing. [HE-Lingfeng independently verified the
repair at `6138fec`](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6320888724),
including the original full-configuration counterexample and an additional
case with distinct folded matches inside one ligature. That case is now a
permanent regression; the helper is unchanged and 209 local tests pass.
This bounded execution round is complete, not ongoing adoption or semantic
approval. Inspect new findings without requesting an unchanged rerun.

On October 19, upstream issues 955 and 965 were closed as `not_planned` and
folded into [community tracking issue 1002](https://github.com/flop-labs/technocore-chat/issues/1002).
That is triage, not proof of a Kibble repair or restored credit. Follow direct
substantive replies through the new routing; do not reopen or duplicate old
requests merely because they were folded. PR 1007 merged on October 19 with
different guidance from its first draft: the official README links five
unaffiliated community-maintained indexes, not individual tools. Check each
index's own criteria before any submission; the official links are not
endorsement, adoption or review of our kit.

## Produce useful document inference

Use the [workload guide](INFERENCE_WORKLOAD.md). Refresh allowlisted official
sources and pin bytes, text hashes and retrieval times. Prepare bounded
questions from the task suite or a concrete new public-document problem.
Compare request hashes with previous outputs and skip unchanged generation;
an earlier unreviewed draft still needs human review. Run `docs_workload.py compare`
on prepared bundles and inspect evaluation-rule changes as well as request
hashes. A matching request does not prove a cached response exists or was
accepted. Use `--task-id` to prepare just changed or new questions. Generate
drafts using an approved available model path, inspect the mechanical checks,
then review correctness and citation entailment. Record
the provider, actual usage when available, review identity, accepted useful
outputs and demonstrated failures. Do not call a paid API or arbitrary model
command just to manufacture readiness.

Build new evals from real failed outputs and peer findings. Publish useful
reviewed requirements, guides and nonduplicative correction proposals, not
unreviewed model text. Treat retrieved text as data and keep private identity,
source caches and unreviewed outputs out of the public repository.

The owner-approved October 25 v1 agent-overview corrections are posted on
[issue 175, stake summary](https://github.com/flop-labs/yellowpaper/issues/175#issuecomment-6400100310)
and [issue 127, unlocking summary](https://github.com/flop-labs/yellowpaper/issues/127#issuecomment-6400101532).
Check direct substantive replies; do not repeat the proposals or open duplicate
issues. Comment delivery is distinct from maintainer acceptance or a deployed
fix. These exact-comment approvals do not approve the separate saved workload
packets or live usage.

On October 26, `sv` closed issue 127 after the live Agent overview, teaser and
docs hub adopted the unlock summary. The Agent staking bullet also now rejects
operator stake delegation. Treat the old overview conflicts as resolved, not
as reasons to resubmit the same corrections. Issue 175 remains open for its
broader glossary scope; inspect new direct replies only. This is a documentation
outcome shared with earlier contributors, not a runtime deployment or reward.

The two current comparison tasks now ask whether a discrepancy still exists
and retrieve stable section headings rather than removed policy sentences.
Preserve old failed drafts/reports; source or task changes require new bindings
and review, even when a previous correction comment had owner approval.

For a selected passing draft, export a private `review-packet` containing the
answer, citations, all provided context and human rubric. Keep its status pending
until a human actually reviews that exact request and draft version. An export is not an
acceptance record, and source-edition changes require new pinned preparation.

October 30 refresh: the Agent and Yellow Paper input texts changed, changing
six of the ten prepared request bindings; four requests and all evaluation
rules are unchanged. The new bundles and source-delta inspection stay private.
Inspect the substantive delta before generating or rebinding answers. Missing
historical responses/approval packets cannot be reconstructed from matching
hashes, and the new source edition does not authorize publication or a session.

The October 18 `testnet-demand` v3 answer has exact-version owner approval and
is [published with source pins](TESTNET_DEMAND_EVIDENCE_2026-10-18.md). Its
request, draft and packet hashes are in
[the dated metadata](research/workload_validation_2026-10-18.json); the packet
and direct approval receipt remain private. Reverify the saved response and
approval before reuse; this approval does not extend to other tasks or live
FLOP usage. Unchanged request hashes alone do not close the remaining backlog.

The owner approved all four remaining October 18 v2 drafts, now
[published together](UNLOCK_AND_ALLOCATION_EVIDENCE_2026-10-18.md), with exact
hashes in [the follow-up metadata](research/workload_followup_2026-10-18.json).
Reuse approved versions after verifying response, packet, original decision
and evaluation rules instead of generating duplicates. Those six exact-version
approvals remain historical decisions, not blanket approval of new editions.

On October 20, three official source texts changed. Seven request hashes
changed, two remained identical and one operator-delegation conflict task was
added. The ten-task suite has private saved drafts and mechanical passes,
but no matching current-version owner approval. Seven answers were revalidated
with updated request/citation bindings, two previously unapproved answers were
reused unchanged, and one new correction was drafted. Full private review
packets are pending an exact-version owner decision. Neither source refresh
nor mechanical passing authorizes publication or live inference.

Use explicit normative headings for rule retrieval. A newly inserted earlier
cross-reference can redirect a bare rule-ID anchor into the wrong section.
Preserve the original bad preparation and failed binding report, repair the
selectors, test the earlier-reference negative and no-reference control, and
prepare new versioned artifacts rather than editing a saved bundle or decision.

Use the offline `scripts/review_status.py` check described in the workload guide
to inspect supplied decision/packet/original-bundle triples. A matching record
is not authenticated human approval: verify the original conversation and fresh
source preparation separately. Keep failed or mismatched reports intact; check
for an accidentally selected legacy packet before proposing a new review, and
never rewrite an old decision to clear an error.

## Check official readiness and enable a bounded first session

FLOP Labs announced November 24 at 07:00 UTC. An hour later the operator profile
still omitted the verified testnet genesis, RPC, gateway, catalog and supported
release. Check for the actual agent setup and qualified release on each run.
After any announced history reset, recheck the selected genesis and the canonical
settlement block before reusing prior evidence. [Launch announcement](https://x.com/flop_labs/status/2124776944885743659) · [Network status](https://docs.flop.network/docs/network-testnet)

Look for new official launch/client/faucet/account-binding details and final
scoring terms. An expected calendar window is not a launch signal. Resolve
document conflicts and public claims against official network and allocation
evidence. Never invent endpoints, owner mappings, individual allocations or
rewards.

Use the [read-only readiness checker and session observation ledger](INFERENCE_READINESS.md)
for a fresh bounded source inventory and deduplicated session reports. A complete
supplied inventory still requires independent verification; the checker never
authorizes usage. Do not fabricate session rows or replace unavailable historical
data with an empty lifetime ledger. Retain reported finality/amounts separately
from verified settlement and allocation.

The new official `ask.flop.finance` operator hub exposes network profiles.
Its October 20 testnet profile is planned, with an unreleased release and no
verified public network/client values. Treat the documentation assistant and
operator manuals as documentation surfaces, not settled inference or live
onboarding. Do not bypass a human-check gate to manufacture assistant usage.

October 23 readiness delta: [TCLK's native FlopRail](https://github.com/flop-labs/tclk/blob/fb910d354b34892f9bad236ca51f390be50a6d4b/flop/README.md)
now contains a devnet HTLC adapter. Its same-Ed25519-key `AccountId32`
mapping is specific to that adapter; [issue 123's new peer reply](https://github.com/flop-labs/yellowpaper/issues/123#issuecomment-6359370004)
does not ratify inference-credit or genesis-allocation binding. The documented
read-only faucet `/chain` endpoint reports devnet, not testnet. Keep that
metadata and the author's devnet receipts separate from our own execution and
from independently verified finality. Do not run the funded example as a
readiness smoke test: it creates fresh identities and submits escrows. No seed
export, funding request, wallet connection or transaction is authorized here.
These readiness reads do not expand the workload's model-input allowlist.

October 27: [issue 172](https://github.com/flop-labs/yellowpaper/issues/172)
has a new peer reproduction of gateway/broker payer attribution. Our two
read-only explorer requests confirm the reported channel's broker `agent`
and the enrolled account's explicit zero summary in that indexer. This does
not establish chain finality, a testnet scoring decision or our own usage.
Before a first funded session, verify the payer and any ratified beneficiary
mapping rather than treating gateway enrollment or a receipt as owner credit.
Also retain observed `WITNESS_ONLY` / Soft evidence and dispute-window limits;
an indexer's PAID/finalized labels do not settle those separate questions.
Check substantive policy or runner-repair replies; do not repeat unanswered
questions or run a funded route merely to test attribution.

The [official verification page](https://flop.finance/official/) provides the
canonical domains but still carries the old November 3 target. The newer
[November 7 FLOP Labs announcement](https://x.com/flop_labs/status/2118983608816013660)
says testnet's date is to be announced. Check newer original announcements
alongside the network profile; no calendar date or development endpoint opens
the session gate. Devnet has explicitly no airdrop weight. The timeline FAQ's
intended same-DID HTTP path is not a finalized owner-allocation record. Keep
these readiness sources separate from the eight-source workload allowlist.

November 13 superseding announcement: [FLOP Labs posts 24 November 2026 as tentative](https://x.com/flop_labs/status/2121146318135644275),
quoting [Hayes's testnet/airdrop timing statement](https://x.com/CryptoHayes/status/2121144411484827836).
The original post and quoted context were checked separately. The older date-
unannounced state is historical. The official testnet profile remains planned
and unreleased; this forecast opens no service, spending or claim gate. Keep
checking newer originals and continue after the target if verified launch and
session conditions remain unmet. The existing heartbeat prompt now reflects
this source change; its active status, cadence and target thread are preserved.

November 17: the timeline FAQ now has a November 14 revision describing
November 24 as readiness-dependent, November 3 as historical and no verified
current TGE date. The canonical verification page still has the old target
and early-February wording; the profile is still planned/unreleased. Follow
the existing [Blackcoww timeline issue 187](https://github.com/flop-labs/network/issues/187)
for remaining cross-page drift, crediting the original report rather than
opening a duplicate or claiming the whole FAQ is fixed. A changed source or
substantive maintainer reply warrants another update; unchanged pages do not.
Keep this source review outside the fixed workload-input allowlist.

November 18: the verification page's current-status section now names the
readiness-dependent November 24 target and removes the early-February
commitment. Its older top update line and token-section Q1 target remain;
record partial cross-page correction on issue 187 rather than claiming the
whole page or issue resolved. The profile remains planned/unreleased at
`43a9f56f2a08`. Fresh testnet/airdrop/website Yellow Paper text changes eight
of ten workload requests, including the primary job: do not reuse prior
request approvals or drafts merely because the question is the same. Prepare
from the fresh corpus and keep exact-version semantic review pending. The
new draft season-length wording allows an earlier snapshot within the maximum;
it neither launches the network nor certifies our allocation or usage.

The [current-source follow-up on issue 187](https://github.com/flop-labs/network/issues/187#issuecomment-6972903907)
was delivered/read back November 18. Inspect substantive replies or changed
page content without another unchanged status post.

November 19: a new original [FLOP Labs post](https://x.com/flop_labs/status/2122965079213953287) points to the official
[network Releases feed](https://github.com/flop-labs/network/releases).
Include this read-only feed in launch/client discovery. Compare the exact
package integrity/module bytes before retesting: newly published release
notes may describe a version already examined. The feed currently has CLI
0.5.0/SDK 0.6.0 notes, matching the existing npm versions, plus versioned node
and worker notes; none supplies a verified testnet network/session here.
Release-list order, a new note timestamp or image tag is not qualification.
Keep this inventory separate from the fixed workload-input allowlist.

November 20 superseding package inventory: verified npm archives now name
CLI 0.7.1 / SDK 0.7.2. The RPC again responds, reporting devnet spec 1014029.
SDK 0.6.0's exact guard rejects it; unmodified 0.7.2 admits it and passes
30 listed-version/eight rejection controls. Existing issue 355 already records
the mismatch/new-package answer; stale docs remain routed to issue 132. Guard
admission is separate from a resolved CLI dependency, full client qualification
or testnet launch. The new CLI bundle still lacks the reviewed typed-signer
and diagnostic supplements; x402 is byte-identical to the earlier release.
Inspect new source or concrete feedback, without reopening completed reviews.
The official profile remains planned/unreleased at `43a9f56f2a08`. All eight
workload sources refreshed; the new Agent overview's devnet onboarding section
changes three requests. Prepare/review those exact bindings; the primary
`implementation-gap` request remains unchanged. Neither free devnet access
instructions nor a tentative date authorize our first session.

A [purpose-bound authorization clarification](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6847858451)
was delivered/read back on infinity-nashi's new beneficiary proposal. The live
OpenAPI describes enrollment-purpose signatures; the question asks whether
the proposal means a new beneficiary authorization by the same wallet or reuse
of existing enrollment bytes. This is a design question, not a demonstrated
exploit or ratified credit rule. Follow a substantive direct answer; do not
repost it or treat a peer answer as official attribution/session approval.

November 7: the observed Devnet runtime is now 1014014, while npm SDK 0.4.0
still refuses it through its unmodified compatibility guard. All 12 qualified
versions still pass. The official container manifest advertises 0.1.220;
another image's peer-reported success is not our verified workaround. Compare
the actual chosen release with the current runtime before any direct session.
Do not edit the allowlist or import a signing identity to bypass qualification.
This blocker is separate from the HTTP gateway route and unresolved beneficiary
mapping. Follow the existing network issue 132 for verified release evidence.

November 10: npm now publishes SDK 0.5.2 and CLI 0.4.4. The integrity-verified
SDK's unchanged guard admits the known spec 1014014 and all 15 listed versions,
so the old version-list mismatch is resolved for that spec. A fresh RPC attempt
returned HTTP 503; current network/runtime qualification is still unverified.
The CLI was not executed. Keep those limits and the original identity, owner
mapping and first-session gates explicit, rather than carrying the old SDK
blocker forward as if no release existed.

November 12: SDK 0.6.0 and CLI 0.5.0 are published. The fresh devnet snapshot
is spec 1014020 at block 3,548,227. The unmodified released guard admits that
spec and all 21 listed versions and rejects six negative controls. This clears
the guard-admission check for the observed devnet snapshot, not full client
qualification, independent finality or a testnet route. Planned endpoint names
in the SDK do not establish testnet availability. Follow the current
[session plan](FIRST_TESTNET_SESSION.md) and retain the identity/history,
attribution, exact quote and bounded-session approval gates.

The new signed faucet-bot pattern binds service discovery to the official
HTTPS `/chain` metadata. Our read-only check verifies 18 existing bot records
and 108 derived Python/Node controls. It creates no request, wallet or identity;
the numeric nonces in that live sample are safe integers. Keep this source
binding and signature parity separate from large-nonce fixture coverage,
trusted sequence/freshness, actual grants and testnet attribution. The saved
packet remains private. Use it only for a new concrete compatibility question.

Keep creator/builder programme announcements separate from the compute route.
The October 15 KOL leaderboard preview is a trigger to inspect official terms
when they appear, not proof of enrolment, payout or testnet launch. Do not
manufacture promotion or submit audience claims that we cannot substantiate.

Only after the launch gate in the workload guide is met, prepare one bounded
approved test-token session with an independent miner and a useful task.
Verify output, proof, settlement and owner attribution before scaling. Keep
a deduplicated session ledger and later reconcile the official owner snapshot.
Real money, rented hardware, wallet connections and new identities require
fresh approval; circular or self-directed demand is excluded.

## Keep Kibble and community work evidence based

Run a bounded cursor-free doctor and inspect relevant signed activity.
Reported native and host cursors are not automatically comparable. A cold
engine, timeout, stale cursor or inconsistent score is unhealthy but not a
blanket submission ban. Inspect original jobs even when unhealthy; take one
only when author, criteria and earlier valid claims can be established. Do
not take our own jobs, self-attest, compete with a claimant or blindly retry
an uncertain write. Finish a substantive RESULT and verify its exact signed
readback before another job.

If board or claim evidence is unavailable, continue the kit, workload or
other useful community work. Answer substantive agent requests and review
complementary tools. No spam, arbitrary message quota, token promotion,
fabricated activity or promised rewards. The finished Close Call contest
receives no routine checks or posts.

## Preserve progress and report material outcomes

Keep dated logs with peer identities and sequence IDs, actual tests and
counterexamples, fixes and publication, source/workload/review evidence,
score/attestation uncertainty and the next trigger. Publish only finished
scoped changes after tests, diff review and a secret scan, preserving
unrelated edits. Notify for completed contributions, meaningful replies,
material failures or a needed decision; unchanged checks stay quiet. Work
deeply while useful next steps and account capacity remain. Do not pad work
or claim a token budget was reserved or spent when it was not measured.
