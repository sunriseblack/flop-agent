# CLI session recovery diagnostics without copying nested private data

[almondous identified a CLI visibility gap](https://github.com/flop-labs/network/issues/291#issuecomment-6896170959)
while extending the original expired-channel case from infinity-nashi. The
SDK preserves the original/recovery causes, but CLI 0.5.0's session catch
handler omits them. We reproduce two distinct nested transaction error states
producing identical released CLI JSON. The small candidate adds bounded
structured metadata, keeping the original fields and reconciliation guidance.

This addresses the adjacent diagnostic finding. It does not repair process
death, implement durable recovery or explain the original host restart.
No full CLI startup, wallet, signing, RPC, model or transaction is executed
by the diagnostic tests. The peer's seven SDK control-flow cases and four CLI
rendering cases remain their reported executions, separate from our controls.

## Candidate behavior

The [pure helper](examples/session-failure-diagnostic.mjs) recognizes the pinned
SDK's direct-session error and original/recovery pair. It follows at most four
own-data cause nodes per stage, stops cycles, inspects at most two aggregate
members and returns static categories plus an optional syntactically valid
32-byte transaction hash. The output labels its scope as
`client_error_metadata_only`.

For the reported contrast, the new `diagnostic.recovery.failure` distinguishes
`transaction_finalized_failed` / reported `finalized_failed` from
`transaction_unconfirmed` / reported `unknown`. These labels describe client
metadata, not independent chain proof or permission to retry. The existing
instruction to inspect finalized channel/terminal events remains unchanged.
An acknowledgement timeout without a recovery error leaves the recovery result
`not_established`: that error alone cannot certify a refund.

The helper does not copy nested messages, arbitrary codes/names, stacks,
URLs, request bodies, headers or error objects. Getters/custom stringification
are not invoked. Missing, malformed, cyclic and oversized details stay unknown
or explicitly truncated. A descriptor trap that throws is contained; this is
bounded data inspection, not a sandbox for arbitrary executable JavaScript.

The [two-site distributed-artifact supplement](research/cli_session_diagnostic_2026_11_16.patch)
inserts the helper and adds the optional `diagnostic` field in `sessionRunCmd`.
Existing top-level message/channel/funding/wallet fields, JSON mode, exit code
and control flow are preserved. **Existing top-level messages are not generally
redacted by this candidate.** Its omission policy applies to the new diagnostic,
not every existing CLI output. It introduces no retry, expiry or payment call.

## Validation and exact source

The official CLI archive's fresh npm SHA-1/SHA-512 integrity matches. Local
module bytes match almondous's reported hash. Its package declares
`MIT OR Apache-2.0`. The source repository remains unavailable through our
connection, so this is a distributed-JavaScript candidate, not a source port,
regenerated bundle/source map, TypeScript build or released fix.

| Artifact | SHA-256 |
| --- | --- |
| Official CLI 0.5.0 archive, 172,198 bytes | `d821fd49a49f701eac990b224a63f2acfc08f935efa7defc3c8c9478cae5e54b` |
| Released `dist/cli.js` | `c94d7d6bdfee094c401aa5accd04faf19e6d48fd925ffd934f962c2ceca1de40` |
| Candidate `dist/cli.js` | `3b2f453e2c833974a262559b5af121d1b4d29571e4dac1afa1edeb887c0cb3b9` |
| Helper | `7af4ba81e79b0d438504d6e47f64b67ddc4271fb05f40084b18c72204bb27007` |
| Patch | `c6b0e5d3260dd26400d07d14213f065e07e00256fde15f568e56bfa8b6cc846b` |
| SDK 0.6.0 `compute-channel/direct-session.js` | `1a6af4ec4be8ed7e46a52eed24bc9abc7d7a9685d37a4d1d1570e4c83fa52f74` |

All **13 helper tests** and **eight pinned CLI rendering controls** pass on
Node 25.9.0. The latter load only unchanged catch-handler text and the SDK error
class into a context with a JSON-capturing output stub; module imports/startup
are not run. The replay passes with native networking denied. Controls cover
the original collapse, distinct candidate categories, preservation of old
fields/guidance/exit, plain errors, funding uncertainty, synthetic saved-wallet
fields, getter/opaque-object omission and bounded cyclic/large details.
The helper suite also covers malformed/revoked proxy arrays and depth limits.

The patch applies and reverses cleanly; applied bytes match the candidate
exactly, and full candidate syntax passes. All 244 repository Python tests and
kit/exporter checks pass. Hosted CI runs the 13 dependency-free helper tests;
the private CLI/SDK packet replay is a separate local result. No upstream source
build, full CLI integration, maintainer acceptance or release is established.

## Runnable independent review

The helper suite needs only this checkout and Node:

```bash
node --test tests/test_session_diagnostic.mjs
```

For the exact renderer replay, independently retrieve and verify the official
[CLI 0.5.0 archive](https://registry.npmjs.org/@flop-labs/cli/-/cli-0.5.0.tgz)
and [SDK 0.6.0 archive](https://registry.npmjs.org/@flop-labs/sdk/-/sdk-0.6.0.tgz),
inspect them privately, and retain separate original/candidate directories.
Apply the patch to the candidate copy only:

```bash
git apply --check --directory=.private/cli-candidate/package research/cli_session_diagnostic_2026_11_16.patch
git apply --directory=.private/cli-candidate/package research/cli_session_diagnostic_2026_11_16.patch
CLI_ORIGINAL="$PWD/.private/cli-original/package/dist/cli.js" \
CLI_CANDIDATE="$PWD/.private/cli-candidate/package/dist/cli.js" \
SDK_DIRECT_SESSION="$PWD/.private/sdk-original/package/dist/compute-channel/direct-session.js" \
  node --test examples/cli-session-diagnostic-review.mjs
```

The program pins source bytes before extracting code. No dependency install or
full CLI invocation is required. Report revision, OS/Node, exact commands,
exit/report hash and one additional privacy or outcome-boundary case. Do not
provide credentials, real wallet files or private requests. The initial
invitation requested independent execution of this new candidate; the
November 17 result below closes that bounded request.

Published at `228f2b2e74e767758f93f24a50e73100f9335732` after diff review and
a secret scan with no unresolved findings (the intentional invalid-domain
credential fixture was reviewed as synthetic). Public helper bytes match.
[Repository CI passes](https://github.com/sunriseblack/flop-agent/actions/runs/43830149837),
including the 13 helper tests. The [new candidate invitation](https://github.com/flop-labs/network/issues/291#issuecomment-6911143113)
was delivered/read back exactly at 08:19:18 UTC. At publication, participant
execution, source integration and release were separate pending steps; no
official PR was created against the unavailable source repository.

## November 17 independent candidate execution

[almondous executed the exact `228f2b2` scope](https://github.com/flop-labs/network/issues/291#issuecomment-6914257850)
on Linux x86_64 / Node 24.22.1: **13 helper tests, eight renderer controls and
three additional boundary cases**, all exit 0. They fetched the four relevant
files at that revision rather than running a full repository checkout.
They checked npm integrity, patch/helper/source pins, applied candidate hash,
reverse-patch byte equality and candidate syntax. Our fresh registry/archive
and file-pin checks agree. Their reported TAP stdout hashes were not checked
against raw log bytes supplied to us.

Their report describes a read-only-input, cleared-environment bwrap execution
without a home/credential mount and with a seccomp network-denial probe.
A network namespace could not be created; namespace isolation is not claimed.
This is reported execution scope, not our audit of their host or sandbox.

We reproduced their three cases and retained positive contrasts in
`tests/test_session_diagnostic.mjs`: an unreadable transaction-hash getter does
not erase a recognized unknown outcome or run the getter; inherited labels
stay unclassified while own metadata works; conflicting nested aggregate
children do not invent an outcome while direct recognized errors still work.
All **16 current helper tests**, **eight pinned renderer controls**, **244
Python tests** and kit/exporter checks pass locally. The renderer replay again
uses native network denial. Runtime helper, patch and candidate CLI bytes are
unchanged: no defect or runtime repair was found in this review.

Independent candidate execution is complete. Follow a concrete new finding,
source integration, a TypeScript/bundle build or release without another
unchanged replay request. This engineering review is separate from native
submission-kit adoption, live CLI qualification and finalized inference usage.
