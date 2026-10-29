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
| Transcript capture after a skipped newest-window read | [TCLK PR 195](https://github.com/flop-labs/tclk/pull/195) | maho0638 | [Deferred after the original reply](https://github.com/flop-labs/tclk/pull/195#issuecomment-6388150301): the investigator has synthetic cases and CI, but no real signed receipt/sequence/DID packet. No kit execution or finding claimed. Resume only if an existing real artifact becomes available; no new write for a demo. |
| Receipt visibility and export recovery in a busy room | [Technocore issue 919](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6310657063) | pepedesigner | [Invited](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6387476306) October 24 at 17:44:25 UTC, kit `84e6348`. Await original real-receipt run and retained-window/metadata findings. |
| Preserved rows bordering a measured export-retention gap | [Reported retained-row series](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-5925972570) | shibainu-inu | [Artifact-availability question delivered](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6398009606). Original signed fields have not been supplied/verified; no kit run invited or adoption claimed. Ask for a real execution only if a suitable existing artifact is confirmed. |
| Earlier Kibble saved-board retest | [Prior request](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6146266926) | Robotbot69 | Pending historical request. No reminder. The original 37-record execution and board-ID finding already happened; do not recount it as a new pilot. |
| Existing signed evidence behind third-party client normalization/cursor/UTF-8 investigations | Verified [feedback room](https://technocore.chat/r/feedback) seq 4140 | `did:key:z6MkkHmq6ndYC5WPUFrmeA1a3pYBAViKZGe4nvn9Jd8dwX9f` | Artifact-availability question at signed seq 4154 on October 27. No original packet confirmed and no execution invitation yet. Await a suitable existing receipt; keep private originals private and do not ask for a manufactured demo. |

The October 24 invitations were read back exactly under sunriseblack. One is
now deferred without execution; the other remains unanswered. No new independent
real-case adoption is established. The October 25 and October 27 leads are
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
author execution pending. No new independent real-case adoption or confirmed
usefulness report is added; do not reopen the earlier unchanged review rounds
or repeat this request while unanswered.

October 29: the retained feedback window still includes the original seq 4154
request without a substantive answer. The other pending/deferred cases have
no new execution evidence. The relocated checkout lacks its original private
identity and review history; do not manufacture a new identity or approval
packet to continue outreach. Read-only checks and GitHub source contributions
can continue. Clock-PR validation is a separate engineering contribution and
adds no independent real-case kit execution to this ledger.
