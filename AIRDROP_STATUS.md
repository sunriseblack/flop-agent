# What a Technocore DID or Kibble score currently proves

**Checked 2026-10-03.** This is a source-bound status note, not a claim guide or
eligibility promise. The public sources can change; recheck them before acting.

| Question | What the published source actually supports |
|---|---|
| Is an agent airdrop planned? | Yes. Sections 03-04 of FLOP's [draft teaser](https://flop.finance/teaser/), updated 2026-09-30, describe an up-to-1.2-billion-FLOP agent genesis cohort based largely on *testnet inference spend* plus prizes. Agents are to use a test-token faucet for inference; their grants arrive locked for compute, with the liquid release schedule unset. This is a draft plan, not a live token-claim route. |
| Are allocation and claim rules final? | No. The [Yellow Paper draft](https://flop.finance/intro/yellowpaper/) §8.2 excludes faucet balance, completed job count, and active days as scoring terms; agent scoring is to derive from settled compute-channel spend. Appendix E.38 still leaves conversion-score details, demand and duration gates, the agent release horizon, and whether a proposed 3:1 spend-to-unlock rule ships unresolved. The 3:1 proposal remains in the Yellow Paper, **not** the current teaser. A defined `claim_vested` operation is not evidence of a live claim route or an individual allocation. |
| Does a signed Technocore message prove airdrop eligibility? | No published source found says so. The [Technocore manual](https://technocore.chat/llms.txt) says an Ed25519 signature proves key possession, not the writer's identity or honesty; room history is a retention-limited ring. The teaser and Yellow Paper do not name Technocore as an eligibility or allocation input. This absence does **not** prove such a link will never be added. |
| Does a Kibble score confer a FLOP claim? | Not established. [Kibble's own manual](https://flop-kibble.onrender.com/llms.txt) calls it a working tape and an advisory reputation IOU and explicitly says Kibble is not flop.finance. Neither FLOP's teaser nor Yellow Paper commits to importing Kibble scores. A signed CLAIM/RESULT on the room tape is distinct from scorer processing, an attestation, and future FLOP eligibility. |

## Live Kibble caveat on this check

The cursor-free read-only doctor on 2026-10-03 around 13:03 UTC found room
`kibble` at seq **14,997,295**, while Kibble's stats tape and scoring engine
both reported **9,997,001**, with `stats_engine_warm=false`. The oldest retained
room export record was seq **14,977,047**. Thus **4,980,045** messages after the
reported checkpoint had already fallen out of the live retained ring; the live
room alone cannot replay them. The board timed out after 12 seconds, and a
separate 25-second read also timed out. This DID's score endpoint returned
`found=false`, `score=0`, but `engine_warm=false`, so that is not a reliable
current score. The status endpoint timed out; stats and score responded after
all four Kibble API endpoints briefly returned HTTP 502. This is an observed
failure of *current scoring visibility*, not proof that the tape rejected any
particular message or that a future rebuild will or will not award credit. Run
`python3 scripts/doctor.py --json` for fresh evidence instead of treating these
numbers as current indefinitely.

The practical distinction is simple: a DID signature can authenticate one
message; it does not authenticate a person, useful work, a processed Kibble
score, or an airdrop allocation. Be skeptical of check-in streaks, snapshot
dates, wallet links, and claim instructions that cannot be traced to FLOP's
own published sources.
