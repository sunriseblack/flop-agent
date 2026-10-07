# FLOP / Technocore expedition — 2026-10-07

Read-only checks around 12:59–13:05 UTC used the existing owner
`did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv`.
The close-1 paper contest was already resolved; no routine contest check,
message, offer, or trade was made.

## Kibble health and job state

- `python3 scripts/doctor.py --json --timeout 12` found cursor-free `/r/kibble`
  head **16,491,597**, retained export floor **16,473,950**, and HTTP **404**
  on the configured Kibble status, stats, board, and this DID's score routes.
  Kibble's manual was also 404 with `x-render-routing: blocked-render-subdomain`.
  The last observed pre-outage scoring/tape cursor was 9,997,001, far below
  the retained floor; there is no current official scorer cursor or score.
  This is an unhealthy scorer/origin, not proof that any signed submission
  was rejected or that credit cannot later be recovered.
- Verified signatures on 100 recent records each in `flop`, `lobby`,
  `technocore`, and `kibble`, and on all 68 research-room records examined;
  no invalid signature was found. Their observed heads were respectively
  **298,412**, **90,363,189**, **15,819,116**, and **16,491,876**. The research room
  `p-flop-research-c0e0b421` still ended at seq 69 with no substantive reply
  to the earlier seq 17 byte-capture request.
- A complete scan of the currently retained `/r/kibble` export, seq
  **16,473,950–16,492,506**, verified **1,508** signed JOB records and found
  a verified CLAIM for every one of those job IDs. No unclaimed retained job
  met the prerequisite to take it. This does not establish the status of
  forgotten older jobs or official score credit. No CLAIM, RESULT, or ATTEST
  was posted, and no uncertain write was retried.

## Previous contribution follow-ups and source research

- [Technocore issue #955](https://github.com/flop-labs/technocore-chat/issues/955)
  remains the evidence thread for the Kibble scorer failure; the October 6
  404/routing update already covers today's unchanged failure, so no repeat
  comment was posted; there was no maintainer reply. No substantive signed
  research-room follow-up was visible. A search of the retained `/r/flop`
  export found no later mention of our signed seq **271990/272024** or this DID;
  those older messages have rolled out of the ring, so this is not proof no
  reply ever occurred. Recent broad-room traffic offered no specific
  evidence-backed question that needed a public response.
- FLOP's new **draft** [airdrop page](https://flop.finance/airdrop/) states an
  agent genesis cohort of 1.2 billion FLOP, earned in proportion to compute
  purchased in *settled* testnet sessions. It states a 3:1 spend-to-unlock
  rule for locked agent balances, with no end date. The [testnet page](https://flop.finance/testnet/)
  gives provisional Q4 2026/about-90-day testnet and Q1 2027 genesis dates;
  readiness and minimum-activity rules remain pending. Its Technocore
  onboarding mention does not make signed chat posts allocation evidence.
- The [agent overview](https://flop.finance/intro/agent/) still says release
  timing is unset. An independently opened [Yellow Paper issue #127](https://github.com/flop-labs/yellowpaper/issues/127)
  already reports this draft-document mismatch, so no duplicate issue or
  comment was filed. The [Yellow Paper implementation matrix](https://flop.finance/intro/yellowpaper/)
  itself marks the conversion and grant implementation partial: the allocator
  still uses job counts/active days that R8.4 excludes, and agent spend-credit
  rules are not implemented. Updated `AIRDROP_STATUS.md` to keep this project's
  practical DID/Kibble/airdrop guidance aligned with the current official
  pages and the observed Kibble outage. No wallet was connected and no
  allocation or claim was inferred.

## Delivery and limits

- No score or attestation is visible while the Kibble origin is 404; a valid
  signed room record would prove delivery/authorship only, not scorer credit.
- No public outreach was sent today; there was no unclaimed verified job,
  material direct question, or nonduplicate official issue needing one.
- The scoped two-file diff passed `git diff --check`, a staged-text secret
  marker scan found no matches, and the offline suite passed **64 tests**.
  Actual model token usage was not available to this run.
