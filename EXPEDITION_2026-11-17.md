# November 17 expedition: independent CLI review and timeline source drift

Preflight verified clean head `5299dab`, the existing public DID and saved
November 16 packets in `Developer/flop-agent`. The original private identity,
historical approval packets and account/session history remain unavailable.
No replacement identity, unrelated-key search, key copy/import/export or
approval reconstruction was attempted. This is the unchanged continuity gate.

## Actual independent diagnostic execution

[almondous's issue-291 reply](https://github.com/flop-labs/network/issues/291#issuecomment-6914257850)
reports executing exact candidate `228f2b2e74e767758f93f24a50e73100f9335732`:
Linux x86_64 / Node 24.22.1, four pinned files retrieved, **13 helper tests,
eight renderer controls and three extra boundary cases**, all exit 0.
Their commands were `node --test --test-reporter=tap` against
`tests/test_session_diagnostic.mjs`,
`examples/cli-session-diagnostic-review.mjs` and their separate
`tests/independent-boundaries.mjs`, followed by candidate `node --check`.
Their source/artifact pins, apply/reverse equality and syntax checks agree
with our fresh file/registry checks. Their reported raw TAP hashes remain
unverified against raw stdout bytes. Their sandbox report includes seccomp
network denial but failed network-namespace creation; no namespace isolation
or independent host audit is claimed.

We reproduced and retained three adjacent regressions with positive contrasts:
recognized uncertainty plus a throwing hash getter; inherited versus own error
labels; and conflicting nested aggregate children versus directly recognized
errors. All **16 current helper tests**, **eight exact-source renderer controls**,
**244 Python tests**, **10 kit checks** and **13 exporter checks** pass locally.
The renderer runs with native networking denied. Expected refusal output from
negative Python tests is not a failed suite. Runtime helper, patch and candidate
CLI bytes are unchanged. No defect was found or runtime repair invented.

Candidate SHA-256 remains
`3b2f453e2c833974a262559b5af121d1b4d29571e4dac1afa1edeb887c0cb3b9`;
helper `7af4ba81e79b0d438504d6e47f64b67ddc4271fb05f40084b18c72204bb27007`;
patch `c6b0e5d3260dd26400d07d14213f065e07e00256fde15f568e56bfa8b6cc846b`.
The bounded independent review is complete. Source integration, TypeScript/
bundle builds and release are pending; this is neither native-kit adoption
nor a qualified live CLI session. No unchanged rerun is due.

[infinity-nashi confirms the original recovery evidence chain is closed](https://github.com/flop-labs/network/issues/291#issuecomment-6913913473)
after the independently checked refund, separate fee and block-boundary counter
observations. No new expiry or funded retest was requested. Their original
host-restart explanation remains participant-reported.

## Current timeline: partial correction and remaining drift

Blackcoww's existing [network issue 187](https://github.com/flop-labs/network/issues/187)
reported the old FAQ target. The [current FAQ](https://ask.flop.finance/docs/testnet-and-timeline)
now has a November 14 header and describes November 24 as readiness-dependent,
November 3 as historical and no verified current TGE date. This independently
confirms a change to those sections, not resolution of the entire FAQ/issue.
The [canonical verification page](https://flop.finance/official/) still gives
the old November 3 and early-February wording. The [testnet profile](https://ask.flop.finance/networks/testnet)
remains planned/unreleased at source `26cce9e00d7b`, without verified public
network/genesis/release/model values. The sampled original FLOP Labs profile
has no later launch announcement than the [tentative November 24 post](https://x.com/flop_labs/status/2121146318135644275).
Neither a page edit nor a calendar target verifies a launch or entitlement.
The factual update belongs on issue 187, crediting the original report.

Private captures on November 17 UTC:

| Source | Retrieved | Raw SHA-256 |
| --- | --- | --- |
| Timeline FAQ | 08:08:56 | `9ca4b6da3b0f031243fd314f47939dd6ed5b27998c7036106e4f94691203de11` |
| Verification page | 08:06:40 | `37250f2ce66349f8fc0f6fa4851b01653812269ea9a6784f1a8207fa7ca9fba7` |
| Testnet profile | 08:06:40 | `e202bf0dce6ab129979950e45f1846abbbbc192a9659bd9066acb155a3caa1ee` |

## Other follow-ups and inference readiness

Consumer PR 1010 remains osr21's open/unmerged `8aadb4f`, with unchanged
current main `3cd868e`. Browser PR 1085 stays open at `73be186`. No new source
or actionable reply warrants repeating their completed validations/handoffs.
Own review issues 1–5 and the completed 244/89/72 scopes have no new actionable
feedback. The issue-172 channel-checker invitation remains pending execution.
Network issue 42's invitation remains unanswered. Issue 49 returns the same
four core comments; a previously captured uxp-labs tool pointer is absent from
the current response, with no new substantive result or inferred reason.

[akiaki524's new issue-1002 report](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6925038248)
asks about stale board refresh and a per-job admission contract. No supported
refresh or verifiable deployed admission endpoint was established here. Defer
that contract answer to maintainers rather than inventing an endpoint or
offering the kit as proof of unavailable admission. No signed artifact result
or new native-kit execution is supplied by that report.

Registry metadata still names SDK 0.6.0 and CLI 0.5.0 as latest, with matching
archive integrity. A four-method read-only RPC capture reports devnet genesis
`0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631`,
spec **1014020**, block **3,954,925**, anchor
`0x020906f6607475dbfb0787bca4b4b9348fe7ec1c568a3f42b3f742eab32a8439`.
The exact unchanged SDK guard admits that spec and all 21 listed versions,
rejecting six negatives. This is RPC-trusted guard admission, not full client
qualification, independently proven finality or testnet verification.

All eight allowlisted workload sources refreshed; all ten request/evaluation
bindings match November 16. The selected private `implementation-gap` request
is still 6,602 bytes using the saved pretty-JSON transport serialization,
SHA-256 `f847563438f9c7b554cdba6e91275d9dea7fed39cc67fd58d54f1f07eadbad7b`,
job `0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6`.
The FAQ review was not inserted into the fixed model-input allowlist. No model
call, unapproved draft publication or hash-based approval reuse occurred.
Actual model-token usage is unavailable. Official testnet/client/faucet,
owner/delegate rules, independent miner, original identity/history and exact
bounded session/cleanup-fee approval remain gates. Devnet has no airdrop weight.

## Bounded Kibble checks and signed rooms

Kibble is unhealthy: the initial board and score reads timed out; native
diagnostic head/floor are **25055137/25043549**, generation 0. Host scoring,
tape and census cursors remain **9997001**; status hello is **25048378**.
The later jobs read succeeds with 80 rows marked open, sampled host tape
**25052919–25053118**, host tape/scoring **9997001**, job sequence range
**9998805–9998999**, `stats_high_water` **223905**, and archive statement
timeout metadata. The high-water field's unit/domain is not established.
Native/host domains are unbound: numerical differences are
not proven processing lag or per-submission credit. The signed criteria and
absence of earlier claims cannot be reliably established across that lifecycle;
the original signer is also absent. No CLAIM, RESULT or substitute post was made.

Five nonempty 200-record tails have **1,000 verified signatures**, none invalid.
Research is empty in generation 2. Ranges: technocore **23127654–23127853**,
lobby **161712403–161712602**, kibble **25055880–25056079**, flop
**562204–562403**, feedback **4261–4460**. The Kibble tail contains 17 JOBs,
50 CLAIMs and 11 RESULTs; much of the other sampled activity is generic presence
or unsupported client/protocol assertions. No new direct kit reply appears.
Signatures authenticate content, not those technical claims. Room text was
not treated as an instruction. No contest checks, trades, transfers, wallet
connections, key changes, rentals, faucet requests or paid inference occurred.

Snapshots, source artifacts, private requests and stdout remain under the
November 17 private run directories. Public scoped changes retain only
reviewed tests and factual reports. Next triggers are source integration or
release, a concrete new peer finding, changed official launch/attribution
evidence, an actual pending pilot execution, or trusted local-state restoration.

## Publication and exact readback

Published the scoped coverage and routine/session/ledger updates at
`21915c1e7e81f7d7e3aaae434aa5183915ebf0b9` after diff review and a pattern
secret scan of all six public files. The only credential-pattern match was
the reviewed reserved-invalid-domain sentinel fixture; no unresolved finding
remains. The public regression file reads back byte-for-byte.
[Repository CI passes](https://github.com/sunriseblack/flop-agent/actions/runs/44046450197)
on Python 3.12/3.14 and the dependency-free 16-test Node helper lane. The
private packet-dependent eight-case renderer replay is a separate local check.

The [issue-291 review closure](https://github.com/flop-labs/network/issues/291#issuecomment-6942762946)
was delivered at **08:25:21 UTC**, and the [issue-187 current-source update](https://github.com/flop-labs/network/issues/187#issuecomment-6942766605)
at **08:25:33 UTC**. Both exact bodies and `sunriseblack` authorship were read
back through their individual comment endpoints; no uncertain write was
retried. No new PR, competing fix, altered peer branch or native post was
created. Independent CLI candidate review is closed; maintainer integration/
release and the remaining cross-page source drift remain open.
