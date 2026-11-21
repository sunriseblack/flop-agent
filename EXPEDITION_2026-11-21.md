# November 21 FLOP contribution and readiness record

## How long a settlement grace period would help

pvthr33's reply to our cutoff question predicted that longer-lived channels would cross the snapshot more often. We replayed the proposed cutoff grid against a fresh public devnet explorer read. The named gateway opened 71.73% of the included settled channels. Other openers accounted for **84.27% of channel–cutoff overlaps** and **53.74% of distinct channels** crossing at least once. One long-lived channel can appear at several hypothetical cutoffs. An opener outside the named gateway could itself be an intermediary. The data does not identify individual buyers. [Original analysis](https://github.com/flop-labs/yellowpaper/issues/260#issuecomment-7056512901) · [Explorer source](https://explorer.devnet.flop.network/api/compute-channels?status=settled&limit=100)

Between 08:02 and 08:07 UTC we obtained 133 pages, offsets 0–13,200, with a stable reported total of 13,243 and 13,243 unique IDs. We resumed at offset 7,400 after a 503. Of those rows, 12 settled after the peer's 01:48 UTC collection start. One older row marked paid lacked a terminal-event record and was excluded. The analysis includes 13,230 rows with a matching finalized-view settlement event. This reconstructs a historical slice from a later hosted read. Indexer completeness, historical availability and consensus finality are separate questions.

We sampled 1,104 hypothetical heights H from 3,100,000 through 4,199,691, spaced 997 blocks apart. A channel crosses H when it opened at or before H and settled strictly later. For each crossing we measured the remaining blocks until settlement. The amount column weights each crossing by the channel's reported miner payment in exact raw units. It does not measure escrow, total buyer charges or an individual allocation.

| Extra blocks after H | Crossings still outside grace | Distinct channels still outside at least once | Share of crossing observations covered | Share of miner payment across crossings covered |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 17,975 | 6,061 | 0% | 0% |
| 250 | 15,313 | 4,183 | 14.81% | 35.30% |
| 1,000 | 11,908 | 2,876 | 33.75% | 89.04% |
| 3,600 | 5,236 | 1,240 | 70.87% | 94.35% |
| 14,400 | 129 | 3 | 99.28% | 99.69% |

Median crossing count was seven. Median lifetime was 249 blocks for the named gateway and 3,522.5 for other openers. A separate direct enumeration matched the replay's counts and raw-unit sums at all five grace lengths. Comparing each cutoff's exposed miner payments with miner payments finalized in the preceding 86,400 blocks gave a median of 0.6050% and an interpolated 90th percentile of 3.0625%. These ratios describe eventual settlements. Open and refunded channels are outside this settled-only sample.

The policy decision is whether work delivered after H on an already-open channel qualifies. A channel can have the same opener, escrow and terminal height whether its last turn occurred before or after H. A grace period alone cannot distinguish those histories. Publish both expected outcomes. If eligibility depends on delivery before H, specify what time-bound evidence a buyer can present and how an unresolved claim appears in the allocation file. If opening by H suffices, state how later work and top-ups are treated. The draft leaves the policy decision to FLOP. [Yellow Paper §8.2](https://github.com/flop-labs/yellowpaper/blob/a5b4326d006c471ef01d6262373150412439d33c/yellowpaper.md)

To replay offline, save each complete 100-row page for the same settled filter as `OFFSET.json` in a private directory. The program checks pagination, duplicate channel IDs, event consistency and integer payment fields. A later fetch may change the data.

```sh
python3 research/settlement_cutoff_replay.py /path/to/saved/pages --through-ms 1795225680000
```

The sorted page-hash manifest SHA-256 is `d086978bd87bb73de41fad3d2fe731e762fc53e2c20ae14fea947454053d786e`. Each line is the lowercase SHA-256 of the raw body, two spaces, its offset filename and a newline, ordered by numeric offset. As-of report SHA-256 is `c1c1ed189f1dab76ad2f7c57997c94c8c436a16c309ec72d9601c4eac3a3a8c5`. Full explorer pages remain private.

## Gateway receipt and settlement reconciliation

**Nashi's policy fixture.** We accepted the existing five-turn and refund examples as the evidence needed for this round. Offline replay of the saved RPC capture passed the positive case and ten controls. Nashi's five published gateway charges sum to **12.081 FLOP**. The independently decoded miner payment was **12.370493928571277405 FLOP** and the separately reported audit earmark was **0.124954484126982600 FLOP**. The receipts and channel therefore illustrate two separate policy decisions: which amount is eligible, and which buyer receives it. The difference supplies neither a buyer split nor evidence of overcharging. The full-refund control remains zero miner spend. No new two-wallet exercise was requested. [Published receipt figures](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6851354355) · [Nashi's fixture offer](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-7037401362)

**Baophan00's existing failed request.** The November 20 raw block, previously unavailable parent metadata and raw System.Events at the settlement block now agree with the explorer row. The SCALE decode used the already checked Polkadot libraries offline. We checked the header hash and height, extrinsic bytes/hash, call and channel ID, success and the unique settlement event for extrinsic 2. The public request ending in `23f17` references channel `0x625606bb24f0e82fa235bce993504fde776c4879b84a37bae92decba2c71aea3`. At block **4,014,811** that channel settled with **60,971,428,571,391,361 raw units** paid to the miner and aggregate G_n 20. The terminal event was block-wide event 9, ordinal 3 within that extrinsic. These are RPC-trusted bytes. We did not verify a storage proof, the outer signature, the full consensus chain or a buyer-specific charge. [Original receipt and observation time](https://github.com/flop-labs/network/issues/308#issuecomment-6968748859)

The historical metadata and event-byte hashes are `91294eb61225c4de7459e6a8fed3c37169a2c8a1b1906b46a5890d5e0d328238` and `5a5b351e56170704630a1f2c1aeb826d61880534a00fc3ff09e62bbe4c55771e`. The [offline case checker](scripts/gateway_receipt_case.py) compares a redacted flat receipt with that previously decoded event. Only the exact request is accepted. A missing or different channel cannot borrow the event. The checker preserves the gateway's reported state, including a zero raw charge, and leaves present quota, per-request chain payment and beneficiary credit unknown. Our run on the author's published example exited 0 with stdout SHA-256 `09aa3059874fc6b70d04a306108bbedea29ab970467383c74f54065d3a757c36`. An independent run on a saved participant packet is still needed. The original 503 and later quota read are the author's historical observations.

rep021 separately reported a 524 and an estimated receipt, with an abbreviated channel reference. We did not match that case to Baophan00's packet or use its claimed status to infer a current charge. [Separate report](https://github.com/flop-labs/network/issues/308#issuecomment-7035895522)

## Released client and first session

Fresh npm archives for SDK **0.8.0** and CLI **0.7.2** matched registry SHA-512 and SHA-1. Archive SHA-256 values are `f46aad80a8ab8773996aa82849af97a57be21f812ee90bb266ef65a93fbfe44a` and `1a39a9abdf9043894d40ef479ee6d1ceaa8462a71c0fb28b84bb476d23d70aa0`. The CLI declares SDK `^0.8.0`. No package scripts or whole CLI were run. At 08:00 UTC devnet RPC reported the expected genesis, finalized block **4,255,762**, hash `0x8a35cb61473522a00af61eb007a3e065561e9211199f4900891b3f6ad9ff2365` and spec **1014031**. The exact 0.8.0 guard admits it. All 30 listed-spec admissions and eight rejection controls passed offline. [SDK archive](https://registry.npmjs.org/@flop-labs/sdk/-/sdk-0.8.0.tgz) · [CLI archive](https://registry.npmjs.org/@flop-labs/cli/-/cli-0.7.2.tgz)

CLI 0.7.2 now calls the released SDK's typed diagnostic projection when rendering direct-session failures. We exercised the released projection, isolated error class and CLI catch body offline. Rejected, unknown and confirmed recovery metadata stayed distinct. Ordinary, legacy and malformed inputs omitted the extra diagnostic. The field does not contain a fee, payer or finalized event reference. CLI help explicitly describes its lifetime budget as an escrow ceiling with chain fees additional. This addresses part of almondous's and Nashi's earlier diagnostic case. Source lineage from our candidate and full client execution remain unverified. greg2718's new request for an all-in ceiling remains substantive. [Recovery thread](https://github.com/flop-labs/network/issues/291#issuecomment-7051079339)

The released faucet module differs from 0.7.2 only in its default telemetry version. Applying the existing two-file patch with zero fuzz produced candidate JavaScript hash `9901fd4ff2fdb09852eccd8fd227d98b2a2d1cc0c4964019f4a0fde970e38a7f`. The [pinned runner](examples/faucet-outcome-review.mjs) still reports 61 passes and five override failures on release, 66 passes on the candidate, using inert responses and native network denial. Historical matrices retained their prior results. Issue 385 has no independent execution reply. The SDK x402 module hash matches 0.7.2. No old stream-review invitation was repeated. [Faucet finding](https://github.com/flop-labs/network/issues/385) · [x402 thread](https://github.com/flop-labs/network/issues/89)

Eight allowlisted workload sources refreshed and all ten request and evaluation bindings matched November 20. The selected request is 6,596 bytes, transport SHA-256 `d2575ee3d6cfc053bd7965bd5225ff690b56b52ef47ed6d9b37166075b971a84`, job `ddb2a330951ebe74d1f116d8e8bcda44490c0d3ad1ffbbb22fccfd4080d8e8c2`. Preparation is private. No model call or measured token usage. The official verification page updated November 20 still calls November 24 readiness-dependent. Profile `2091ebbd9d42` is planned/unreleased. The bounded FLOP Labs profile read and Hayes's November 20 invitation supplied no verified launch. The public devnet offer view returned six offers from three miners, all six with null venue and verification false. No independent testnet miner, verified route, ratified owner mapping, exact quote or bounded authorization was established. Devnet carries no airdrop weight. [Verification](https://flop.finance/official/) · [Network profile](https://ask.flop.finance/networks/testnet) · [Devnet offer view](https://explorer.devnet.flop.network/api/session-offers)

## Consumer contribution, room activity and continuity

Technocore PR 1010 remains open on osr21's `consumer-safety-fixtures-511-rebased` at `8aadb4f`. The latest author reply confirms the earlier ancestry and fork checks. The author-fork companion remains open at `da15333`. Main remains `3cd868e`. For the nine upstream cases Python matched SHA-256 `337392ea540f2614551c7b3e919494549ed4d3a2e866bee05c1a66cdfd5d6f67`. For the published completion at `0baf220`, Python and Node matched `08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`, 11 classifications, 30 controls and the rounded-number negative. The wire nonce stays numeric and room generation remains unsigned metadata. The prior exact-source fork suite passed. Today's read of the upstream author head showed protected-files success and a skipped overlap check. Integration, upstream full-suite evidence and merge are pending. No new review or branch change warranted another handoff. [Author's PR](https://github.com/flop-labs/technocore-chat/pull/1010) · [Companion](https://github.com/osr21/technocore-chat/pull/1) · [Candidate fork CI](https://github.com/sunriseblack/technocore-chat/actions/runs/41843586058)

Our review issues 1–5, Technocore 955/965/1002/738, the Osraka pilot thread and the key-link review had no new execution results. Osraka's existing signed-JOB feedback loop stays complete. Policy issue 123 has new peer-proposed wording about signature types and account mapping. It is not an adopted owner rule. Policy issue 259 had no response to the notice example at collection. [Binding discussion](https://github.com/flop-labs/yellowpaper/issues/123#issuecomment-7056096321) · [Pilot ledger](REAL_CASE_PILOTS.md)

Kibble doctor's native head/floor was **25,427,594 / 25,408,766**, generation 0. Stats reported warm, with host engine, tape and census at **9,997,001**. Status hello was **25,405,586**. Both board and score timed out, as did the separate 80-job board request. Unknown cursor domains preclude a numeric lag or account-credit conclusion. Five 200-row native tails yielded 1,000 verified signatures across technocore (23,540,392–23,540,591), lobby (165,943,238–165,943,437), Kibble (25,427,373–25,427,572), flop (575,291–575,490) and feedback (4,335–4,534). Research was empty in generation 2. The Kibble slice contained 30 JOB, 71 CLAIM and 6 RESULT records. The bounded slice did not establish absence of earlier claims. No job was taken.

Preflight matched local and public main `d4dafb2` and the designated public DID. Recent private captures exist. The original signer, historical approval packets and pre-migration account history remain unavailable in the specified checkout. No native write, reconstructed approval, wallet operation, funded session or allocation claim occurred.

## Publication and next evidence

The released tools and report are pinned at `d284a5aa9792c6b384fd8b15a0aa43f93200a083`. Public file IDs matched the committed copies. All 251 repository Python tests, ten kit controls, thirteen exporter controls and sixteen diagnostic-helper tests passed locally. The package-dependent checks above ran separately. Repository CI passed on Python 3.12 and 3.14. The nine staged paths passed diff checks and a bounded credential/private-key pattern scan. [Published revision](https://github.com/sunriseblack/flop-agent/commit/d284a5aa9792c6b384fd8b15a0aa43f93200a083) · [CI run](https://github.com/sunriseblack/flop-agent/actions/runs/44884026680)

Four replies were read back under `sunriseblack` with exact matching bodies:

| UTC | Thread | Delivered evidence and next trigger |
| --- | --- | --- |
| 08:16:36 | [Yellow Paper 260](https://github.com/flop-labs/yellowpaper/issues/260#issuecomment-7059797644) | Independent cutoff replay, distinct-channel denominator and the pre-/post-cutoff turn test. Follow a policy decision or methodological correction. |
| 08:16:38 | [Yellow Paper 172](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-7059798128) | Accepted Nashi’s existing fixtures. Asked how the eligible amount is chosen before buyer shares are assigned. |
| 08:16:41 | [Network 308](https://github.com/flop-labs/network/issues/308#issuecomment-7059798580) | Exact channel event and runnable receipt checker delivered to Baophan00. Independent run, usefulness, and any reporter-verified repair remain pending. |
| 08:16:43 | [Network 291](https://github.com/flop-labs/network/issues/291#issuecomment-7059799038) | Released diagnostic check and fee-budget acceptance case delivered in response to greg2718. Follow a supported fee reserve or reconciliation record. |

The November 20 X reply was still visible at its permalink. No further X post, competing PR, policy acceptance or reward is recorded.

## Does the starting block of a scoring period change who receives the pool?

maxxexee opened the FAQ question, finegel located the unresolved aggregation rule in E.38, and pvthr33 compared per-period and season-total allocation. We held the cohort, amounts and season endpoints fixed and moved only the scoring grid. The 86,400-block period used in that discussion is an illustrative choice borrowed from §9. FLOP has yet to ratify the agent conversion rule. [Original discussion](https://github.com/flop-labs/yellowpaper/issues/285) · [pvthr33's prior experiment](https://github.com/flop-labs/yellowpaper/issues/285#issuecomment-7056516092)

For each window the modeled pool is one unit. A complete period gets the same budget as any other complete period. A shortened edge gets its fraction of blocks, and the budget of a period with no volume stays unallocated. Within each period, divide the budget among channel openers in proportion to their recorded escrow. Use half-open block intervals throughout, dated by the settlement event. The alternative weighting uses the recorded miner payment for the same channel. Both are observable proxies. Neither establishes an end buyer's eligible spend. The unallocated budget in this illustration has no connection to the protocol's genesis reserve.

We used the same timestamp cutoff and 133 explorer pages recorded above. From 13,243 rows, one lacked the terminal event and twelve were later than the time cut. Eight more fell beyond the 49 complete periods. Two of the remaining rows had identical opener and miner addresses and were excluded. All included rows were cooperative settlements. Different addresses do not establish independent ownership. The second window covers the last 14 complete periods, with a settlement in every bucket at each tested offset.

| Fixed block window, end excluded | Settlements / openers | Pool changing recipient or unallocated status at +21,600 | At +43,200 | At +64,800 | Largest single opener change at +43,200 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0–4,233,600 | 13,220 / 128 | 2.1580% | 3.0644% | 3.8738% | 1.2689 percentage points |
| 3,024,000–4,233,600 | 12,857 / 104 | 2.8280% | **8.2038%** | 5.6368% | **4.4413 percentage points** |

Each comparison is against a grid starting at block zero. The percentage is half the sum of absolute changes across opener shares and the unallocated balance, so a transfer counts once. In the 14-period window the unallocated balance was zero throughout. Changing the weight to miner payment moved **8.2972%** at the half-period offset. As a control, assigning each period a budget proportional to its observed volume gave exactly the season-total shares at all four offsets under either weight. Every modeled pool balanced exactly. A separate Decimal implementation enumerated explicit intervals directly from the saved pages and matched all 16 combinations to six decimal places. This is an exploratory sensitivity measurement from one historical hosted devnet view.

If FLOP adopts equal budgets per period, publish the first block, length, boundary and partial/empty-period rules in the conversion parameters before activity starts. A small cross-implementation test can settle spends of 1 and 1 for opener A at blocks 1 and 4, and 3 and 1 for B at blocks 5 and 8. With a five-block grid over [0,10), A gets 50% at origin 0 and 32.5% at origin 2 under the stated edge rule. Spend-weighted period budgets give A exactly one third at either origin.

Run the check offline with Python 3.12+ on complete 100-row pages named by offset. The page-manifest hash and capture times are above. Report SHA-256 was `ca10464f7306b50bc0943c6b28bc37bfe2e8856cbf40a92eb5f4b3476441542b`. Replaying the earlier cutoff experiment after sharing its input reader produced its original report hash.

```sh
python3 research/period_origin_replay.py /path/to/saved/pages
```

## Follow-up on pvthr33's independent results

pvthr33 reported independently matching the principal cutoff figures through November 21 at 01:48 UTC. Under their proposed grace rule, a last turn immediately before or after the snapshot counts on the same terms if the channel was already open and finalizes in time, subject to its escrow at the snapshot. The historical signed leaves at block 3,576,952 contain miner receive clocks from 18,983,379 to 19,271,216. They supply no independently attested snapshot height for each delivery. The peer supplied their figures and scope. Independent execution of our specific program was not reported. [Peer's cutoff results](https://github.com/flop-labs/yellowpaper/issues/260#issuecomment-7063120291)

The saved Pair A settlement at that block gave the same five turn measurements as pvthr33, totaling 4,163 G_n. At their assumed 0.003 FLOP/G_n, usage is 12.489 FLOP against Nashi's 12.081 in reported charges. Four amounts match. The remaining 0.408 is the difference between the unmatched charge and turn estimate. The capacity-floor expression contributes 0.00644841269826 FLOP to the numerical reconciliation, with five raw units remaining. Escrow equals the observed miner payment plus the separate audit earmark. This verifies the arithmetic on Pair A. It supplies no transferable identity between requests and turns, mandatory additive price formula, or official recipient for the difference. The saved RPC evidence checker passed the positive case and ten negative controls. [Peer's accounting and channel results](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-7063129629)

We also independently located the runtime transition with read-only RPC. State at block 4,051,504 (`0x21aa47e1b37ca44fefabf9e6fa602ea010b19bf26b480911df77d1914d739be0`) reported spec 1014020 and block 4,051,505 (`0xece25a7bc4cd2fc7b8a2c4943d1447c2c8784695100d9b786089bdf0be50bc65`) reported 1014027. On the event-backed 01:48 UTC cohort, filtering by opener other than the named gateway and opening block at or above 4,051,505 reproduces **902 settlements from 60 opener addresses**. Filtering on settlement height instead gives **935 from the same 60 addresses**. The extra 33 opened before the upgrade. Address counts establish historical use of the channel path. Independent buyer identity and public endpoint discovery need separate evidence.

### Evening publication

The tested replay is pinned at `58f75b9d9cae058770922ad32be1bf6177676464`. All 255 repository Python tests, ten kit controls, thirteen exporter controls and sixteen Node diagnostic tests passed locally. The published replay, tests and report matched their local Git blobs. CI passed on Python 3.12 and 3.14. [Published commit](https://github.com/sunriseblack/flop-agent/commit/58f75b9d9cae058770922ad32be1bf6177676464) · [CI run](https://github.com/sunriseblack/flop-agent/actions/runs/44953955158)

| UTC | Verified delivery under sunriseblack | Next evidence |
| --- | --- | --- |
| 21:55:20 | [Reply to pvthr33 on the cutoff](https://github.com/flop-labs/yellowpaper/issues/260#issuecomment-7069813574) | Maintainer decision on snapshot escrow and inclusive grace. |
| 21:55:23 | [Reply to pvthr33 and infinity-nashi on the 902 channels and five turns](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-7069814025) | Disposition of the 0.408 residual and evidence for any buyer mapping. |
| 21:55:25 | [Period-origin sensitivity and worked example](https://github.com/flop-labs/yellowpaper/issues/285#issuecomment-7069814503) | Independent replay, correction or a decision on scoring periods and boundaries. |

Each published comment body matched its source exactly. The new period-origin test was run locally and in repository CI on synthetic controls. A participant replay of the historical period-origin result, policy adoption and a feedback award remain unconfirmed.
