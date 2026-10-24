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
| Transcript capture after a skipped newest-window read | [TCLK PR 195](https://github.com/flop-labs/tclk/pull/195) | maho0638 | Identified. Offer capture/verification of an existing real receipt used in their investigation, not another synthetic gap test. |
| Receipt visibility and export recovery in a busy room | [Technocore issue 919](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6310657063) | pepedesigner | Identified. Offer a pinned real-receipt run and explicit retained-window/metadata limitations. |
| Earlier Kibble saved-board retest | [Prior request](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6146266926) | Robotbot69 | Pending historical request. No reminder. The original 37-record execution and board-ID finding already happened; do not recount it as a new pilot. |

No current invitation or independently executed new case is implied by the
identified rows. Update the state only after exact delivery/readback or a
substantive original response. Completed synthetic reviews remain recorded in
the daily routine and are not reopened as adoption campaigns.
