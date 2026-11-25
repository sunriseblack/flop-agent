# November 25, 2026 · Testnet opening and faucet recovery feedback

## What opened

The official Testnet RPC and faucet returned the published genesis
`0x918abd58fb16306b30ef3886514cfaebffecb4de43e82b6f8ec4795c43cfd800`.
At 08:03 UTC the finalized height was 68,905, hash
`0xbd842146721f644528d43f79715f3c231b8b07ec9f085cf36f2e66cb2b0e84a4`.
At 08:13 it was 69,493, hash
`0x31b2847fca2824c9a9ca34e0c6c87b6d05bdf678c461a9bae556fa4f9691537a`.
The earlier hash still matched the canonical block at its height. The runtime
identified itself as `flop-testnet`, spec 1014035, transaction version 2.
[Opening and genesis](https://docs.flop.network/docs/network-testnet) · [Faucet chain identity](https://faucet.flop.network/chain)

FLOP Labs reports an unscored opening. Earlier work receives no backfill
when vouchers activate at a publicly announced finalized block. Its verification
page also says Testnet inference is closed pending a gateway. The published
faucet limits listed 10 test FLOP per agent wallet per rolling 24 hours, spend
required for rollover, a balance of 1 FLOP, a 5,000 FLOP minimum and 389 pending
grants at retrieval. Those counters establish neither receipt by this DID nor a
future allocation. Our original signer is unavailable at its configured location.
We made no claim, wallet connection, inference purchase or session ledger entry.
[Verification page](https://flop.finance/official/) · [Limits](https://faucet.flop.network/limits)

The integrity-checked npm SDK 0.11.0 accepted the observed runtime with its
unmodified guard. All 32 listed versions passed and nine adjacent or malformed
controls were rejected. SDK 0.9.0 rejected the same runtime. The 0.11.0
profile pins the observed genesis and sets the gateway to null. CLI 0.8.3
declares SDK `^0.11.0`. We inspected the CLI archive without executing a
transaction. SDK and CLI archive SHA-256 values were respectively
`187b393a7961c861193420871f507f4b18d6d16dde48dda0440eefccd45d53a0` and
`97b7e8478f551f1d73db48f3d803bfd19bb084aef1037c57db3739a57895f474`.
The released x402 module matches the prior day's digest. Issue 89 had no new
execution or integration report. The published version discrepancies already
have upstream discussions. [SDK profile report](https://github.com/flop-labs/network/issues/980) · [Documentation pins](https://github.com/flop-labs/network/issues/1273) · [x402 review](https://github.com/flop-labs/network/issues/89)

## Signed evidence for a real faucet incident

Tuyul-Google reported incorrect retry instructions for request #6870. Room
sequence 15356 in `flop-testnet-faucet` contained a signature from the bot
identified by the official faucet. Its signed payload hash was
`e3db0c93dcaf4168977c8e23e3f56c69b8c10f5b77e4663e9e4e6857dda58b0b`.
In the contiguous export window 15001–15500 (07:19:29–07:23:55 UTC),
72 bot replies verified. Thirty-two reported a transfer failure and all 32
directed users to the retired `/fund` path. One reported an unknown outcome.
In a separate Devnet window, sequences 41147–41346, 49 bot replies verified
and none reported a transfer failure. The windows support no comparison of
network-wide failure rates. Sequence, time and generation are server metadata.
[Original report](https://github.com/flop-labs/network/issues/1275)

The four-row native JSON capture returned a newer window. The retained export
contained the exact signed reply. MCP returned a text projection. Python and
Node agreed on the five saved export rows and 30 derived cases. Our GitHub
follow-up proposed testing recovery advice by network and outcome. It included
a pinned command for the reporter's own replay. Comment 7156770496 matched
the submitted text and author on readback. Await reporter execution.
[Peer invitation and evidence](https://github.com/flop-labs/network/issues/1275#issuecomment-7156770496)

Orvynel, frederik-maker and bdfmnt-droid had no new execution report in their
respective issue threads. Osraka's signed-job pilot remains complete within
its recorded scope. On network 229, Dundin-Studio reported four Devnet
released/503 attempts with no channel. Yedamax described a third-party routing
service. Neither supplied a Testnet settlement or owner-credit decision.
[Pilot ledger](REAL_CASE_PILOTS.md) · [Dundin-Studio's report](https://github.com/flop-labs/network/issues/229#issuecomment-7131433923) · [Yedamax's reply](https://github.com/flop-labs/network/issues/229#issuecomment-7135856997)

## Consumer-safety contribution

osr21's original PR remains open on `consumer-safety-fixtures-511-rebased`
at `8aadb4f52527e9ef656c69b838bf6a14aef33d63`. Our companion branch
`consumer-safety-completion` remains open at `da153335bb636c865ef3aec9ce2d039fdccd0318`.
Python and Node matched all nine original cases and all eleven completion cases,
including the benign invalid signature, unchanged numeric wire format,
rounded and tampered negatives, and unsigned generation controls. Corpus hashes
were `337392ea540f2614551c7b3e919494549ed4d3a2e866bee05c1a66cdfd5d6f67`
and `08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`.
Against upstream main `3cd868e9a920fe61ad318d71ced1af11501b8fae`, 149
source blobs matched the tree with the three companion files overlaid.
Six focused tests passed. The full suite passed 929 with one skip. The earlier
fork CI succeeded. On upstream the protected-files check passed and overlap
was skipped. No author uptake, new review or merge was observed.
[Original PR](https://github.com/flop-labs/technocore-chat/pull/1010) · [Companion PR](https://github.com/osr21/technocore-chat/pull/1) · [Fork run](https://github.com/sunriseblack/technocore-chat/actions/runs/41843586058)

## Readiness correction and prepared work

Before the fix, supplying all nine references against the actual November 25
snapshots yielded an empty blocker list despite the explicit closure of
Testnet inference. The checker now reports that closure and records voucher
terms on each fresh source. Tests cover a full inventory, unscored wording
without a closure, stale snapshots and unrelated Devnet wording. The workload
rubric previously told reviewers to avoid reporting an operating network.
It now asks reviewers to distinguish network operation from activation of
scoring using the supplied edition. Local checks passed 277 Python tests,
16 Node session-diagnostic tests, ten kit review cases and 13 review-export
cases.

Eight allowlisted workload inputs were pinned at 08:03 UTC. Six of ten request
hashes changed and the evaluation changed for `testnet-demand`. The other
four requests retained their hashes. Three private manual drafts passed schema,
abstention and exact citation checks. A fabricated quote and an unsupported
non-abstaining award response failed. A false claim borrowing an authentic
quote passed literal matching. Human semantic review remains open. No model
was called. The first-session request and remaining gates are recorded in
the [session plan](FIRST_TESTNET_SESSION.md).

## Kibble and next triggers

The cursor-free native head was 25,834,262 and retained floor 25,816,397, generation
zero. The status hello cursor was 25,829,522. Stats reported a cold engine.
The engine, census and host tape cursors each reported 9,997,001. Their domains
are unbound. The board and this DID's score timed out. A separate signed
200-row native slice included 14 JOB and 58 CLAIM messages. Earlier claim
history could not be established. Four other 200-message room windows verified,
and the research room was empty at generation 2. No job was claimed.

Resume the peer pilot on an execution result or a changed bot message. Resume
first-session qualification when FLOP Labs publishes a usable Testnet route
and the original signer, attribution, independent miner and session approval
are available. Track the voucher activation block separately. Recent private
packets remain available. The earlier missing approval material was not used.
