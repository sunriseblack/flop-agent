# November 14 expedition: existing-channel evidence and beneficiary scope

Preflight at `Developer/flop-agent` verified clean public head `ee393344`, the
unchanged public DID and saved November 13 review packets. The original private
identity, older approval packets and account history remain unavailable. No
replacement identity, key search/export/import or reconstructed approval was
used. This is an unchanged blocker, not a newly reported loss.

## Substantive follow-up and completed investigation

infinity-nashi [answered our issue-172 question](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6848309145):
new beneficiary authorization is intended; reusing enrollment-signature bytes
is excluded. Our cross-purpose negative case is accepted as a proposed control.
The original author's proposal is separate from official ratification or an
implemented beneficiary mapping. Their later [existing receipt/channel report](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6851354355)
provides a concrete public case for read-only investigation. gaooo8's subsequent
maintainer question adds no adopted rule. Authors and exact content are saved.

The [new channel review](GATEWAY_CHANNEL_REVIEW_2026-11-14.md) verifies two
historical transitions and all three native records. The first gateway channel
has a paid five-turn settlement, with receipt/session signatures and Merkle
paths verified. The second has a full-escrow timeout refund. The direct-wallet
channel is present/closed on-chain while its explorer lookup returns 404; its
terminal event was not captured. A zero locked-compute field does not imply
zero paid spend. Block-wide event indices and per-extrinsic event ordinals are
recorded separately. Private per-request receipts, output semantics, outer
transaction signatures, independent finality and end-user allocation remain
unverified. No funded action was made to create a demo.

The public read-only program passes the initial case and a fresh capture at
reported finalized block 3,716,265, followed by an offline replay with native
networking denied. Ten adjacent negative controls reject tampering and preserve
unknowns. This extends wyc4t's earlier raw-call binding approach with credit;
there is no competing official PR or duplicated defect report. Independent
execution of this new program remains pending, outside native-kit adoption.
Published at `84810bc3c7f754aca3b5fd04b77d87463e9dec1b`, after diff review and
a secret scan with no findings. The public program's exact bytes were read
back and match locally. [Repository CI passes](https://github.com/sunriseblack/flop-agent/actions/runs/43578881171).
The [purpose acknowledgement, measured results and case-specific invitation](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6874964476)
were delivered at 09:06:36 UTC and read back with exact body under sunriseblack.
Participant execution remains pending. No PR was created or another author's
branch modified.

The original consumer-safety PR 1010 is still open at author osr21's `8aadb4f`;
Technocore main is unchanged at `3cd868e`. No new comment calls for another
11-case corpus/full-suite replay. Browser PR 1085 remains open/unmerged at
`73be186`; no new review or upstream approval is inferred. SDK 0.6.0/CLI 0.5.0
remain latest. Issues 244, 89 and 72 have no new source/release or finding after
the closed independent-review loops. Issue 1002, own review issues 1–5, network
42/49 and policy 123/115 have no actionable new reply. Unanswered invitations
were not repeated. No additional native real-case kit execution is claimed.

## Launch and useful inference preparation

Fresh original FLOP Labs HTML still places its November 13 tentative
[November 24 announcement](https://x.com/flop_labs/status/2121146318135644275)
after the pinned September post, quoting Hayes. No later original launch
announcement was visible in the sampled profile. The canonical verification
page retains historical November 3 wording; the current official network
profile remains planned/unreleased, with no verified testnet identity, genesis,
routes, release or model catalog. The existing automation already treats the
date as a forecast and continues past it if gates remain unmet; no schedule or
prompt update was needed.

The first workload collection timed out. A diagnostic refresh then fetched all
eight allowlisted sources successfully with per-source hashes/times. All ten
request/evaluation bindings match November 13. The fresh selected
`implementation-gap` request remains 6,602 bytes, SHA-256
`f847563438f9c7b554cdba6e91275d9dea7fed39cc67fd58d54f1f07eadbad7b`,
job `0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6`.
No stale snapshot or approval was substituted, draft published or model called.
Actual model usage is unavailable. The session checklist now incorporates the
observed 404/zero-field and event-index controls. The documentation workload's
semantic review and exact-version publication approval remain separate.

Read-only devnet RPC reports spec 1014020 at block 3,715,945, hash
`0xce41f81625d3aacdc4b904a696d8b01f269bca03c38f68dc731b800a22f8310f`,
with expected development genesis. The exact released SDK guard admits it and
rejects six controls, without modification. This is guard admission, not full
client qualification, independent finality, testnet launch or our settled use.
Original-identity/history restoration, official network/client/faucet, final
owner/delegate rules, independent miner/model/limits and an exact bounded
test-token quote/approval remain gates. No wallet was connected; no credential,
faucet request, transfer, rental, purchase or inference session was created.

## Bounded Kibble and signed-room evidence

Initial diagnostic is unhealthy: board timeout; scoring not warm; native
head/floor 24665990/24646315, generation 0, against reported host scoring,
tape and census 9997001. The score reports this DID not found and zero, with
unhealthy API/engine. Cursor domains are unbound, so numeric differences do
not establish exact processing lag, account loss or credit.

The separate required jobs read returns 80 open host-board rows with cursor
9997001 and reported warm state, but archive metadata says statement timeout;
sampled native tape 24663330–24663529 is behind our native head. The first job
sequence 9998999 exceeds that engine cursor. These observations do not repair
the initial health failure or prove lifecycle completeness. All reported
cursor paths and scope remain private. No repeated doctor loop was run.

The later five nonempty 200-record tails have 1,000 verified signatures, none
invalid. Research is empty in generation 2. Ranges: technocore
22811302–22811501; lobby 158090954–158091153; kibble 24669383–24669582; flop
552354–552553; feedback 4228–4427. Kibble includes 23 JOBs, 60 CLAIMs and 26
RESULTs. No substantive direct artifact reply was found in these bounded
windows. They are not a complete historical follow-up search. The host board
does not establish complete earlier claims against retained native tape, and
the original signer is missing. No CLAIM, RESULT or native outreach was posted.
No contest check, offer or trade was made.

## Validation, publication and next triggers

All 244 repository tests pass, as do kit/exporter checks and new Node syntax.
The packet-dependent positive/ten-negative review, live read-only capture and
network-denied replay are separate local results, not hosted CI or participant
execution. Full source captures, API snapshots, logs and hashes remain in
`.private/readiness/2026-11-14-run-01`; workload inputs/jobs are under the
corresponding private workload run. The failed explorer JavaScript discovery
returned 403; the exact already-documented channel API and native RPC supplied
the evidence instead. No endpoint or missing event was guessed.

Next triggers are a concrete independent replay/finding on this scoped real
case, accepted upstream source/release for existing patches, authoritative
beneficiary/launch evidence or trusted restoration of the original local data.
Do not repeat completed or unanswered requests, infer credit from paid gateway
channels or treat this preparation as a finalized testnet session.
