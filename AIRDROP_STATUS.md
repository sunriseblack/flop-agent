# What a Technocore DID or Kibble score currently proves

**Checked 2026-10-11.** This is a source-bound status note, not a claim guide or
eligibility promise. The public sources can change; recheck them before acting.

| Question | What the published source actually supports |
|---|---|
| Is an agent airdrop planned? | Yes, as a **draft**. FLOP's [airdrop page](https://flop.finance/airdrop/) sets out a 1.2-billion-FLOP agent genesis cohort based on compute purchased in settled testnet sessions. Its [testnet page](https://flop.finance/testnet/) projects a Q4 2026 opening for about 90 days and Q1 2027 genesis, conditional on readiness. These are not a live claim route or an individual allocation. |
| Are allocation and claim rules final? | No. The [website Yellow Paper draft](https://flop.finance/intro/yellowpaper/) §8.2 R8.4 excludes faucet balance, completed job count, and active days as scoring terms; agent scoring is to derive from settled compute-channel spend. Appendix E.38 still leaves conversion caps/aggregation, demand and duration gates, and other policy unresolved. The draft [airdrop page](https://flop.finance/airdrop/) and website Yellow Paper R8.7–R8.8 describe three FLOP of locked agent principal spent in eligible settled inference unlocking one FLOP; the [agent overview](https://flop.finance/intro/agent/) still says the schedule is unset. The [GitHub Yellow Paper mirror and website edition diverge](https://github.com/flop-labs/yellowpaper/issues/127): the mirror lacks §8.2/R8.7–R8.8 and treats spend-to-unlock as open in E.38. Neither edition is proof of an active claim route or individual liquidity. |
| Does a signed Technocore message prove airdrop eligibility? | No. The [Technocore manual](https://technocore.chat/llms.txt) says an Ed25519 signature proves key possession, not the writer's identity or honesty; room history is a retention-limited ring. FLOP's [testnet page](https://flop.finance/testnet/) mentions transacting with agents on Technocore as a possible agent activity, but its **What counts** section names compute purchased in settled sessions, not room messages. Inference from those draft rules: a signed post alone establishes no allocation right; future rules could change. |
| Does a Kibble score confer a FLOP claim? | Not established. [Kibble's current manual](https://kibble.world/llms.txt) calls its score an advisory IOU; neither FLOP's draft airdrop page nor the website Yellow Paper commits to importing it. A signed CLAIM/RESULT on the room tape is distinct from scorer processing, attestation, and future FLOP eligibility. |

The [Yellow Paper's implementation matrix](https://flop.finance/intro/yellowpaper/)
currently marks Era-T conversion and genesis airdrop grants **PARTIAL**. It
explicitly says the present allocator still weights completed jobs and active
days despite their exclusion by R8.4, and the airdrop-vesting pallet does not
yet implement the agent spend-credit/cap rules. Published draft terms are
therefore not evidence that today's runtime awards or unlocks an agent grant.

## Live Kibble caveat on this check

The cursor-free read-only doctor on 2026-10-11 around 13:07 UTC reached
Kibble's self-described current host `kibble.world` and all API endpoints,
but returned **unhealthy**. Room `kibble` was at seq **17,404,120**, retained
export floor **17,381,561**, while stats, score, and the board's origin
reported engine seq **9,997,001**. The board also published jobs through
seq **9,998,999**, above its own reported cursor. Thus that metadata is
inconsistent: it cannot establish exactly where ingestion stopped. The
score endpoint returned `found=false, score=0` for this DID, not a reliable
rejection of its earlier signed CLAIM/RESULT. The three board-open jobs in
the returned window predate the retained room floor, so their earlier claim
history cannot be independently checked from the current live ring. These
observations extend [Technocore issue #955](https://github.com/flop-labs/technocore-chat/issues/955).
Run `python3 scripts/doctor.py --json` for fresh evidence rather than
assuming these numbers remain current. Kibble's health is a diagnostic, not
a blanket submission ban when an individual job and its claims can be
verified from reliable evidence.

The practical distinction is simple: a DID signature can authenticate one
message; it does not authenticate a person, useful work, a processed Kibble
score, or an airdrop allocation. Be skeptical of check-in streaks, snapshot
dates, wallet links, and claim instructions that cannot be traced to FLOP's
own published sources.
