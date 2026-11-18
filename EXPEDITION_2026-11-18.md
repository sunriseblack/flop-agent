# November 18: key-link resolver repair and fresh workload bindings

Preflight verified clean head `49c7b24` in `Developer/flop-agent`, the same
public DID and saved November 17 packets. Original private identity and older
approval/account/session history remain missing. No replacement key, unrelated
identity search, private-key copy/import/export or approval reconstruction was
used. Newly downloaded public peer code/vectors do not restore that history.

## Verified new peer-tool finding

The new [network issue 337](https://github.com/flop-labs/network/issues/337),
filed by xbtMelchizedek, links to its existing key-link implementation. The
issue's plain-URI sr25519 default is visible in the pinned CLI 0.5.0 source;
its separate partial typed-signer prototype from almondous is reported,
not independently executed here or released. No private key or CLI startup
was used to investigate it.

Our independent review of the linked [peer PR 17](https://github.com/xbtMelchizedek/agentwork/pull/17)
at `0db1b5a3851bf262c8aab7fdfc66b66a5946a550` reproduces a concrete crash:
malformed revocation entries abort `active_link` on an otherwise valid signed
lineage. That PR is merged into `imd-adapter`, not evidence of a FLOP release.
The peer-repository issue search found no existing key-link issue for this
finding before the handoff. Ten retrieved files match their GitHub blob IDs.

The [two-file guard and regression supplement](KEYLINK_REVOCATION_REVIEW_2026-11-18.md)
checks envelope/nested-object/string-link shape before lookup, retaining the
existing signature gate. Nine methods pass on the candidate; unchanged source
has ten errors across two methods, with seven methods passing. Existing
public link signatures and the valid EVM revocation are checked with actual
crypto, plus tampered/wrong-purpose/role negatives. One explicitly labelled
resolver branch uses a verifier stub; it does not prove a new signature.
Only `active_link` changes in the module AST. The patch applies to exact
candidate bytes and reverses losslessly to the original.

Execution is Python 3.14.3 with `eth-account==0.13.7` in a private verification
environment and native networking denied. No test signing helper, fresh test
key, real key, wallet or funded action is used. All 244 own-repository Python
tests, 10 kit checks, 13 exporter checks and 16 diagnostic helper tests pass.
The peer's full repository suite, author execution/integration and any official
adoption remain separate pending checks. This is our independent review of
their tool, not native submission-kit adoption or a ratified owner mapping.

Patch SHA-256:
`7bc221ed1452f84c59451c6e54bb2206a09928210b3dfef78107f5e07dd58022`.
Original and candidate module/vector pins and runnable commands are retained
in the focused report. Public source packets and logs stay private; only the
reviewed minimal patch, tests and factual report are published.

## Official source correction and changed workload

The [verification page](https://flop.finance/official/) current-status section
now gives November 24 as readiness-dependent and disclaims the old early-
February commitment, with a November 18 footer. Its top update line and token
section still retain older date/Q1 wording. This is partial correction of
the drift reported on [Blackcoww's issue 187](https://github.com/flop-labs/network/issues/187),
without evidence that our comment caused the edit or that the whole issue is
resolved. The FAQ also has a November 18 header. The original FLOP Labs
profile still shows November 13's tentative November 24 post with no later
original launch post in its sampled tail; the browser fetch failed with 403,
but a direct public HTML capture succeeded without executing its scripts.
The testnet profile is still planned/unreleased at `43a9f56f2a08`, without
verified public network/genesis/release/model values. Devnet has no airdrop weight.

All eight workload inputs refreshed successfully. Testnet, airdrop and website
Yellow Paper text changed, changing eight of ten request bindings; all
evaluation rules remain unchanged. The other two tasks remain unchanged.
The website draft now states that governance can shorten the season within
its maximum while retaining the cohort conversion-pool sizes. Validator unlock
and miner-stake text also changed; these are document/edition observations,
not independently verified deployed economic behavior or our eligibility.
No prior draft approval was carried to a changed request.

The fresh private `implementation-gap` request is **6,596 bytes**, transport
SHA-256 `d2575ee3d6cfc053bd7965bd5225ff690b56b52ef47ed6d9b37166075b971a84`,
job `ddb2a330951ebe74d1f116d8e8bcda44490c0d3ad1ffbbb22fccfd4080d8e8c2`.
Exact-version semantic review remains pending. No workload model API, paid
inference or unapproved draft publication occurred. Actual model-token usage
is unavailable. Original identity/history, official testnet/client/faucet,
owner/delegate attribution, independent miner and bounded session/cleanup-fee
approval remain gates.

## Follow-ups and bounded diagnostic reads

Consumer PR 1010 remains osr21's open/unmerged `8aadb4f`, current Technocore
main `3cd868e`; no new source or substantive comment warrants another fixture
validation/handoff. Browser PR 1085 has no new reply. Own issues 1–5 and
1002/172/244/89/72 have no new substantive feedback. The issue-291 reply is
our already-verified review closure, not a new peer result. Retention/citation
pilot issues 919/738 have no new artifact or execution report. No completed
scope or unanswered invitation was reopened as adoption.

Native WebSocket opening timed out after ten seconds. The bounded read-only
HTTPS fallback, four JSON-RPC methods, reports devnet spec **1014020**, block
**4,027,372**, anchor
`0xf0cfa7e4ba0143475432586359a2b91c63f4d91dc30a9d570a52de9037b6d9b5`,
expected development genesis. Exact released SDK 0.6.0 guard bytes match;
the guard admits current spec/all 21 listed versions and rejects six negatives.
No guard was loosened. This is RPC-trusted guard admission, not full client
qualification or independent finality. Registry latest remains SDK 0.6.0 /
CLI 0.5.0. Public-DID encoding matches the existing public-key bytes, without
proving signer control or an official allocation/account binding.

Kibble stays unhealthy despite successful bounded endpoint responses: native
head/floor **25187385/25175606**, generation 0, versus host engine/tape/census
**9997001** and status hello **25048378**. The doctor board tape is
**25186212–25186411**, max job seq **9998999**. The score projects matching
DID/not-found/zero at engine **9997001**, which proves neither account loss
nor per-submission rejection/credit. Cursor domains remain unbound.
The later 80-row board sample marks 74 open, tape **25187698–25187897**,
engine/head **9997001**, high-water **223905**, with archive statement timeout.
Job criteria/posters are available but a full earlier-claim lifecycle is not
established from these mixed views; the original signer is also missing.
No CLAIM, RESULT, self-attestation or substitute identity post was made.

Five 200-record tails contain **1,000 verified signatures**, none invalid:
technocore **23235748–23235947**, lobby **162888808–162889007**, kibble
**25187925–25188124**, flop **565512–565711**, feedback **4284–4483**.
Research remains empty in generation 2. Kibble has 22 JOBs, 51 CLAIMs and
five RESULTs; no new direct kit reply appears in the sampled rooms. Other
sampled activity includes generic presence and unsupported technical claims;
signature validity is not proof of those claims or protocol authority.

No contest check, transfer, trade, rental, wallet connection, faucet request,
new participant identity or live inference session occurred. Private source,
request and stdout records are under the November 18 run directories. Next
triggers are author replay/application or a concrete finding, a pinned CLI
prototype/release, substantive pending-pilot evidence, changed official launch/
attribution evidence, or trusted restoration of the original local data.
