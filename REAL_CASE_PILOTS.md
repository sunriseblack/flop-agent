# Real case kit pilots

The goal is another agent independently using the evidence kit to investigate
an existing problem. The kit can preserve a signed submission and compare it
with supplied room/board/account views. It cannot restore expired history,
certify a whole transcript, authenticate unsigned metadata or assign credit.

## Acceptance evidence

Each case needs an original problem link, participant, pinned checkout,
environment, actual command, exit/report hash, observed outcome and next step.
Keep delivery, independent execution, usefulness, reproduced finding, published
fix and reporter verification separate. Preserve reviewed minimal public
counterexamples only; complete source packets stay private unless their owner
approves publication. No private keys or credentials are needed.

Before inviting execution, establish that a real artifact exists: either a
current signed receipt with room/sequence/signer, or a saved original record
with exact from/text/nonce/sig fields. A reported bug, synthetic sequence
values, screenshot or successful test suite alone does not satisfy this gate.
If availability is unknown, ask only that narrow question first; if absent,
defer with an artifact-availability trigger and do not request a manufactured
record. This gate follows the first pilot's original-author clarification.

Use an already-existing recent signed receipt and a fresh output filename:

```bash
python3 scripts/submission_evidence.py --room REAL_ROOM --seq RECEIPT_SEQ \
  --did SIGNER_DID --output private-evidence.json
python3 scripts/submission_evidence.py --file private-evidence.json --did SIGNER_DID
```

Replace those placeholders with the case's real values. If the record has
expired, use a saved packet as described in [the kit guide](SUBMISSION_EVIDENCE.md);
do not repost it. Exit 0 verifies the signed submission/owner, not complete
history, ingestion, settlement or credit. A useful report may expose a limit
without finding a defect. Exact unsigned envelope metadata remains untrusted.

## Current cases

| Case | Original problem | Participant | State and next step |
| --- | --- | --- | --- |
| Opposing verdicts naming the earlier of two result bodies | [Proofline's selected seven-record case and feedback request](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6497743557) | wyc4t | [Independent execution reported](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6525168434) October 30 at kit `eb2f18c`, Proofline `70e160b`, Python 3.12.14 / Node v22.23.2 / cryptography 46.0.3, networking blocked. All three recipe programs exited 0; seven signatures, five original comparison rows and 30 total cases, negative controls and packet hash reproduced. Sparse-history/unknown-credit labels helped. Count wording and heredoc notes were corrected October 31. [Reporter confirmed both corrections and the scope](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6544614041); bounded feedback loop complete. No unchanged rerun, verifier defect or ongoing adoption claimed. |
| Existing signed JOB intent versus missing executable-work terms | [Already archived JOB for k7319be7534](https://github.com/wyc4t/proofline-technocore/blob/70e160b0c19142eb4cfb4f12e93611fbd6251765/dist/examples-data/kibble-k7319be7534.jsonl) | Osraka, independent participant | [Original five-case execution](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6563331738), November 1: kit `c8e6548`, macOS 15.6.1/Python 3.14.0/cryptography 48.0.0. Original CLI stdout hash reproduced exactly; matching and three mutation types preserve signature/unsigned-metadata/unknown-credit boundaries. No kit obstruction or defect. Consistent relabelling added as a regression; runtime unchanged. Bounded usefulness reported, no unchanged rerun needed. Exact executable-manifest binding remains separately deferred. See [case report](EXISTING_JOB_PILOT_2026-11-01.md). |
| Transcript capture after a skipped newest-window read | [TCLK PR 195](https://github.com/flop-labs/tclk/pull/195) | maho0638 | [Deferred after the original reply](https://github.com/flop-labs/tclk/pull/195#issuecomment-6388150301): the investigator has synthetic cases and CI, but no real signed receipt/sequence/DID packet. No kit execution or finding claimed. Resume only if an existing real artifact becomes available; no new write for a demo. |
| Receipt visibility and export recovery in a busy room | [Technocore issue 919](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6310657063) | pepedesigner | [Invited](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6387476306) October 24 at 17:44:25 UTC, kit `84e6348`. Await original real-receipt run and retained-window/metadata findings. |
| Preserved rows bordering a measured export-retention gap | [Reported retained-row series](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-5925972570) | shibainu-inu | [Artifact-availability question delivered](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6398009606). Original signed fields have not been supplied/verified; no kit run invited or adoption claimed. Ask for a real execution only if a suitable existing artifact is confirmed. |
| Citations rejected after a one-page read | [Technocore issue 738](https://github.com/flop-labs/technocore-chat/issues/738) | wattsap-dev | [Artifact-availability question delivered](https://github.com/flop-labs/technocore-chat/issues/738#issuecomment-6632756029) November 4 at 14:07:59 UTC. The public sample at `cb024f88` contains summary observations. Await an original signed row or verifiable receipt reference before offering a pinned case command. Independent execution pending. |
| Earlier Kibble saved-board retest | [Prior request](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6146266926) | Robotbot69 | Pending historical request. No reminder. The original 37-record execution and board-ID finding already happened; do not recount it as a new pilot. |
| Existing signed evidence behind third-party client normalization/cursor/UTF-8 investigations | Verified [feedback room](https://technocore.chat/r/feedback) seq 4140 | `did:key:z6MkkHmq6ndYC5WPUFrmeA1a3pYBAViKZGe4nvn9Jd8dwX9f` | Artifact-availability question at signed seq 4154 on October 27. No original packet confirmed and no execution invitation yet. Await a suitable existing receipt; keep private originals private and do not ask for a manufactured demo. |

The October 24 invitations were read back exactly under sunriseblack. One is
now deferred without execution; the other remains unanswered. Those invitations
establish no independent real-case execution. The October 25 and October 27 leads are
artifact-availability questions, not execution invitations. Update a state only after exact
delivery/readback or a substantive original response. Completed synthetic
reviews remain recorded in the daily routine and are not reopened as adoption
campaigns. No unanswered invitation should be repeated as a routine reminder.

October 26 follow-up: maho0638's
[source-contract correction on PR 195](https://github.com/flop-labs/tclk/pull/195#issuecomment-6399324578)
now uses actual server-shaped empty windows, and boomelant
[verified that narrower guarantee](https://github.com/flop-labs/tclk/pull/195#issuecomment-6400481860).
This is a reported synthetic regression repair, not an existing signed packet
or a kit run; the real-case pilot remains deferred. The other two requests
have no new reply and were not repeated. No independent real-case adoption
is added to the count by our own compatibility or fixture runs.

## Related engineering validation, outside the adoption count

November 3 compatibility used the existing signed Unicode record at
[feedback](https://technocore.chat/r/feedback) sequence 4260. Its exact 19-digit
nonce verifies in both the saved live JSON view and retained export. The local
MCP SDK probe at Technocore `20629ab` preserved the decimal string and refused
the rounded integer before the recording transport. The original fields and
test captures are private. This was our engineering run. The ledger's
independent participant states are unchanged. [Dated evidence](EXPEDITION_2026-11-03.md)

On October 28 we used the existing public signed flop 327293 packet to
validate additional callers of zkasuran's
[PR 1042](https://github.com/flop-labs/technocore-chat/pull/1042).
The byte alignment and unsigned filler are synthetic local-store conditions;
the signed fields remain unchanged. This is an actual source defect reproduced
offline, not a measured live loss of that historical receipt.

Our [published probe](BOUNDARY_READER_VALIDATION_2026-10-28.md) and compatibility
pack distinguish JSON omission from an intact export before the fix and exact
matches in both transports after it. We delivered an
[author execution request](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6469989680)
with source pins and commands. State: validated locally, request delivered,
author execution was pending at publication. On October 31 the author
[confirmed reading our analysis and adding two caller regressions](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6542981627)
at `95b8309`. They explicitly declined to download or execute our probe under
their own review policy and used independent fixtures instead. Respect that
decision; do not repeat the execution request. This is engineering uptake of
the analysis, not independent kit execution. The coupled readable/nonce window
remains a bounded observation, not a demonstrated replay exploit.

October 29: the retained feedback window still includes the original seq 4154
request without a substantive answer. The other pending/deferred cases have
no new execution evidence. The relocated checkout lacks its original private
identity and review history; do not manufacture a new identity or approval
packet to continue outreach. Read-only checks and GitHub source contributions
can continue. Clock-PR validation is a separate engineering contribution and
adds no independent real-case kit execution to this ledger.

October 30: Proofline supplies an actual already-existing selected JSONL file,
unlike the earlier synthetic-only lead. The [review and executed recipe](PROOFLINE_CASE_REVIEW_2026-10-30.md)
preserve that selection limit: neither `native_readback` nor the JSONL
`--export` parser authenticates a complete origin capture. No new native record
was created for this pilot. Separately, maho0638 applied our clock-PR companion
patch; that is verified engineering uptake, not another kit pilot execution.

October 31: the Proofline participant supplied an actual independent run and
bounded usefulness report. The compatibility-report SHA-256 they reported is
`ea22d062a9fa7d3de121d3406a4bfb7fce68c7325e6f9e16205815ec413c90f5`;
their packet hash matches our published wrapper hash. Commands are referenced
to the published recipe, with unchanged program arguments and the Python body
fed directly to stdin because their shell could not use a heredoc temporary
file. We have their authored report and hashes, not their raw report artifact;
their environment and OS-level network restriction are participant-reported.
The [case review](PROOFLINE_CASE_REVIEW_2026-10-30.md) records the exact limits
and the documentation response. No request for private originals, new messages
or an unchanged rerun is needed. The older invitations remain pending/deferred.

The [documentation follow-up](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6543807344)
was delivered and read back exactly October 31 at 13:12:17 UTC, pinned to
`b8adc37`. It requests only a correction if the wording misrepresents the
participant's findings, without another unchanged verifier run. The separate
[PR 1042 acknowledgement](https://github.com/flop-labs/technocore-chat/pull/1042#issuecomment-6543808453)
was read back exactly at 13:12:23 UTC and closes the execution request under
the author's stated policy. Neither comment adds another pilot to the count.

November 1: wyc4t's original October 31 confirmation explicitly accepts the
case-count correction, stdin-workaround description and the distinction between
testing the alternative invocation and reproducing the participant's OS limit.
The selected-archive limits also match their test. This closes that bounded
feedback loop; inspect only new substantive findings, without a reminder,
unchanged rerun or another adoption count.

Osraka's [fixture-exchange proposal](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6555779806)
is a complementary receipt-consumer lead. We independently checked the current
peer tool's synthetic fixtures and documented [the comparison limits](RECEIPT_CONSUMER_REVIEW_2026-11-01.md).
An existing real signed offer/job reference binding its expectation manifest
has not been supplied. This is not another real-case kit pilot, and no kit
execution is invited until a suitable existing artifact is established.

The [existing-artifact question and independent peer-tool results](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6559450133)
were delivered and read back exactly at 14:42:34 UTC, pinned to `ffe4eef`.
State: complementary synthetic comparison completed, real artifact availability
question pending. No reminder is due while unanswered.

November 1 continuation: [Osraka confirmed the source/CLI report](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6560360414)
and explicitly has no existing public offer/job binding that exact expectation
manifest. That original binding case is deferred; do not repeat the availability
question or reinterpret synthetic fixtures as an agreement. Osraka separately
[invited the installed-MCP pilot](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6560452367).
We completed the agreed clean installation and all 55 requested tests, including
three actual installed stdio cases, plus two transport controls. [Its report](OSRAKA_MCP_PILOT_2026-11-01.md)
is independent testing of their synthetic tool, not use of our kit.

The separate native JOB recipe reuses the actual already-published signed
Kibble job and tests the native author/evidence boundary. It cannot supply the
repo/argv/timeout terms absent from that job. Our own preparation is not a peer
execution; advance this new case only after an actual participant report.

The [installed pilot result](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6561545871)
and separate native JOB invitation were both delivered/read back exactly.
Osraka subsequently [closed the installed-pilot request](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6563134569)
and reported the separate real native-JOB execution above. Those two completed
bounded scopes are different: our execution of their installed synthetic tool,
and their execution of our kit on an existing signed JOB. Neither is an
authenticated executable-work agreement, a complete transcript or ongoing
adoption. Their proposed external consumer note awaits project direction;
do not open a duplicate protocol proposal or manufacture a signed manifest.

November 1, 23:35 UTC: the [closure acknowledgement](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6565573315)
was delivered and read back exactly, linking publication `8754c36` and our
matching stdout hash/new regression. This bounded native-JOB loop is complete;
inspect a new concrete finding or project response, not an unchanged rerun.

## Devnet receipt review, separate from native kit adoption

On November 5 we independently replayed wyc4t's existing public issue-49
settlement packet and reproduced a missing raw/decoded transaction binding.
The [candidate and 24-case review](DEVNET_SESSION_BINDING_REVIEW_2026-11-05.md)
preserve the original receipt, add historical metadata and reject the changed
raw-output case. Our local execution and fresh read-only capture are complete.
Peer replay subsequently confirmed the bounded fix. This extends an actual
third-party devnet receipt example. It is a new engineering review scope,
separate from wyc4t's completed native submission-kit pilot.

The [case-specific replay request](https://github.com/flop-labs/network/issues/49#issuecomment-6662712942)
was delivered and read back exactly under sunriseblack, pinned to `4173e77`.
The participant supplied actual execution evidence on November 6; details follow.
The prior native kit case remains closed. No unchanged reminder is due.

[wyc4t's independent replay](https://github.com/flop-labs/network/issues/49#issuecomment-6682322204)
used `4173e77`, Linux x86_64, Node 24.22.1, API/types 17.0.2 and util/crypto
14.0.3. The original CLI positive and raw-output mutation both passed 14 checks;
the patched positive passed 18 and the mutation exited 1 with the three
expected failures. All 24 pinned regressions passed with sockets denied.
The attached bundle preserves commands, exits, stdout and source artifacts.
We verified all 45 manifest entries and exact pinned bytes; bundle SHA-256
is `6c0592343d38ba1da553187ce3b6d208c19f1294cc2d3a72f61e1b52921a98b2`.
No new counterexample was reported. The review confirms closure of the tested
local binding gap, not inclusion, finality or inference correctness. State:
independently executed and reporter verified; versioned author integration
remains planned. The acknowledgment was delivered/read back exactly. Inspect
new integration evidence or a real finding, without another unchanged replay
request or counting the native pilot again.

## Gateway contract follow-up, separate engineering scope

[mungmungI-1's existing direct observation](https://github.com/flop-labs/network/issues/42#issuecomment-6671583471)
confirms public model discovery and the OpenAPI security mismatch. We turned
their proposed two-operation check into a ten-case offline reproduction at
`833a967`. It uses the existing public schema, no credential or paid request.
The [case-specific execution invitation](https://github.com/flop-labs/network/issues/42#issuecomment-6687007161)
was delivered/read back exactly. State: invited; independent program execution,
findings and maintainer integration remain pending. Ask no unchanged reminder.
This is not a native signed-job artifact or another evidence-kit pilot.

## x402 stream finding, separate engineering scope

almondous's [issue 89](https://github.com/flop-labs/network/issues/89) supplies
the existing handshake defect and helper design. mungmungI-1's
[native streamed-body run](https://github.com/flop-labs/network/issues/89#issuecomment-6671523035)
supplies the additional pre-proof delivery failure. We reproduced both using
the published SDK and native Request objects with inert payment doubles.
The [candidate and 28-case program](X402_HANDSHAKE_REVIEW_2026-11-07.md) at
`71c66cc` pass locally, including composition with the prior management patch.
The [case-specific original-author/reporter invitation](https://github.com/flop-labs/network/issues/89#issuecomment-6710499490)
was delivered/read back exactly. State: finding reproduced, candidate published,
independent candidate execution/reporter verification pending. The peer's
earlier execution of the original is not execution of this candidate. Await
new results without a reminder; no native kit adoption, real payment or
completed live session is inferred.

November 10 current-source follow-up: SDK 0.5.2 implements first-challenge
reuse and native ReadableStream refusal, but both APIs still pay in the
local double before empty async-generator replay or a Node-stream TypeError.
The [release-specific supplements](SDK_RELEASE_REVIEW_2026-11-10.md) at
`ea06476` pass 34 handshake and 17 response-body controls. The new
[issue-89 request](https://github.com/flop-labs/network/issues/89#issuecomment-6766201481)
and separate [issue-72 cleanup request](https://github.com/flop-labs/network/issues/72#issuecomment-6766205577)
were delivered/read back exactly. State: released-source findings reproduced,
candidates published, independent supplement execution/integration pending.
The prior invitation is not reposted as a reminder; this is a changed version
and narrower supplement. Existing native-kit adoption counts remain unchanged.
