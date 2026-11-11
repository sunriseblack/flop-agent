# SDK 0.5.2 release review and remaining body handling

The November 10 npm registry names SDK 0.5.2 and CLI 0.4.4 as latest. We
downloaded the SDK and verified its registry SHA-1 and SHA-512 integrity. The
archive is 4,631,411 bytes, SHA-256
`caa11e4f9955ca3aedadc65fc9401943e256241d3c8424e116af6a7206161d69`.
CLI metadata was checked; that CLI was not installed or executed.
[SDK registry](https://registry.npmjs.org/@flop-labs/sdk)
· [CLI registry](https://registry.npmjs.org/@flop-labs/cli)

The release now reuses the first x402 challenge and refuses native
`ReadableStream` bodies before payment. Its faucet implementation passes our
24 string-result contract cases. These are verified released behaviors, not
proof that our exact earlier patches were adopted or that a particular
contributor received credit. Original reports remain attributed to almondous,
mungmungI-1 and the other authors in the dated reviews.

## Remaining request-body gap

The released stream check uses `instanceof ReadableStream`. With an async
generator yielding `fixture`, both entry points make one mock payment and
observe mock settlement, then send a proof-bearing request whose body is
empty. With `Readable.from(['fixture'])`, both fail with TypeError on the
second attempt after mock settlement. A native Request consumes the initial
body in these controls; all fetch, payment and settlement operations are inert
test doubles. This is not an observed live payment loss.

The [small stream-guard supplement](research/sdk_x402_stream_guard_2026_11_10.patch)
recognizes stream-like and async-iterable bodies. It preserves the release's
existing error text and timing, ordinary non-402 streaming passthrough, and
replayable string/byte/URL-parameter handling. It conservatively refuses all
async iterables when challenged, including repeatable ones, rather than
assuming byte-identical reproduction. It does not buffer streams or add a
factory API. This extends the existing
[issue 89](https://github.com/flop-labs/network/issues/89).

The [handshake program](examples/x402-handshake-review.mjs) now has 34 cases,
including Node streams and non-402 async-iterable controls. It retains the
earlier candidates' typed error assertions while checking the released
module's existing generic Error contract. A generic error alone is not a
finding: refusal before payment is the tested invariant. All transitive
source pins remain checked before import.

## Discarded response cleanup

The release also retries a transient management GET without cancelling its
discarded response body. Our existing order control fails: the next fetch
occurs before cancellation. The separate
[one-line response cleanup patch](research/sdk_x402_response_cleanup_2026_11_10.patch)
awaits cancellation before the unchanged backoff/retry path. Final responses
and POST behavior are unchanged. This supplements the existing
[issue-72 review](SDK_CANDIDATE_REVIEW_2026-11-05.md), rather than adding another
management-client implementation.

## Observed controls

| Suite | Released 0.5.2 | Supplemented source |
| --- | --- | --- |
| Handshake/body, 34 cases | 30 pass, four fail | 34 pass with stream guard |
| Additional management, 17 cases | 16 pass, cleanup-order case fails | 17 pass with response cleanup |
| Both patches, same two suites | Above failures | 34 and 17 pass |
| Earlier November 7 candidate, expanded handshake suite | Separate historical artifact | 34 pass |
| Faucet string-result cases | 24 pass | Unchanged |

Historical proposal tests also expose policy differences: the old faucet
22-case suite gives 20 passes and two differences (unsafe numeric cooldown
and an elapsed HTTP-date); the old management 18-case suite gives 15 passes
and three differences (GET 408 and two Retry-After behaviors). Those complete
suites are not green on this release. We preserve those reports and defer
cooldown/retry-policy changes to a separate source/contract review. Neither
body patch changes that policy or claims to resolve those differences.

Tests ran on Node 25.9.0/macOS arm64. Handshake controls used native-socket
denial; HTTP management/faucet cases used loopback-only networking. No real
key, wallet, funding, inference, payment or chain transaction was involved.

## Pins and reproduction

| `dist/x402.js` variant | SHA-256 |
| --- | --- |
| Released 0.5.2 | `3efba4fb82b77ff207499e8ca3379b25574946ededfb0640d44f76accd4485d6` |
| Stream guard | `c3500d148df8d7bed7f2aa72b2888d425c66d234b8054aa4b8c69d6f228ca899` |
| Response cleanup | `585456ea4765b2650fb2c7d5ba55f0e0b52e3300030f4ecbf8049e7bd268080e` |
| Both patches, either application order | `b746ff062ab1c2673f9768405ae6d9914d99a614c2300773def0e310c3542d18` |

Preserve the original SDK archive privately and unpack a separate candidate.
No dependency installation is needed for these direct module imports. From
this repository root, with that candidate at the path below:

```bash
git apply --check --directory=.private/sdk-release/candidate/package research/sdk_x402_stream_guard_2026_11_10.patch
git apply --directory=.private/sdk-release/candidate/package research/sdk_x402_stream_guard_2026_11_10.patch
git apply --check --directory=.private/sdk-release/candidate/package research/sdk_x402_response_cleanup_2026_11_10.patch
git apply --directory=.private/sdk-release/candidate/package research/sdk_x402_response_cleanup_2026_11_10.patch
SDK_REVIEW_DIR="$PWD/.private/sdk-release/candidate/package" node --test examples/x402-handshake-review.mjs
SDK_REVIEW_DIR="$PWD/.private/sdk-release/candidate/package" SDK_REVIEW_TARGET=x402 node --test examples/sdk-response-review.mjs
```

Patch application in both orders gives the same exact source. Node syntax,
the repository's 244 tests and kit/exporter review checks pass. Full SDK source
builds, regenerated bundles, browser behavior, independent execution and
maintainer integration remain unverified for these supplements. Source packets
and logs remain private; published counterexamples use synthetic data.

## Runtime and first-session boundary

The unchanged 0.5.2 compatibility guard admits all 15 listed versions,
including the previously blocked 1014014, and rejects six negative controls.
This clears the old version-list mismatch for that known spec. Today's RPC
attempt returned HTTP 503 before a fresh runtime/anchor could be read, so it
does not establish compatibility with the currently deployed chain. The
official SDK reference page still lists the older releases. No allowlist was
edited and no signed client was connected. Testnet launch, original identity,
beneficiary mapping and bounded-session approval remain separate gates.

## Publication and peer handoff

Published at `ea06476c13ea18b2172b50713de20db55ff50636`, with successful
[repository CI](https://github.com/sunriseblack/flop-agent/actions/runs/42808121133).
The new [stream-guard request](https://github.com/flop-labs/network/issues/89#issuecomment-6766201481)
and [response-cleanup request](https://github.com/flop-labs/network/issues/72#issuecomment-6766205577)
were delivered and read back exactly under sunriseblack. Both ask for actual
version-pinned execution and counterexamples; independent supplement replay
and integration remain pending. The
[released faucet type-contract result](https://github.com/flop-labs/network/issues/71#issuecomment-6766209005)
was also delivered/read back, with the cooldown differences kept separate.
The hosted CI covers the repository suite and helpers; SDK packet-dependent
replays above are local evidence, not upstream SDK CI.

## November 11 independent execution and adjacent controls

almondous independently executed the pinned `ea06476` programs on Node
24.22.1/Linux x64. Their [issue-89 report](https://github.com/flop-labs/network/issues/89#issuecomment-6767083517)
matches 30 passes/four failures on the release and 34/34 stream/combined passes, including
all module and archive pins. Their [issue-72 report](https://github.com/flop-labs/network/issues/72#issuecomment-6767085001)
matches 16/17 released and 17/17 cleanup/combined results. They describe a
corrected loopback preload and filesystem/child-process restrictions, explicitly
without kernel network isolation. Stdout hashes are reported in the comments;
the underlying log bytes were not attached and have not been hash-checked here.
This is independent reported execution, separate from our own replays, source
integration, regenerated bundles, browser behavior or an upstream release.

The second report adds a synthetic rejected-cancellation callback. We reproduced
it and added it to the response program, together with an adjacent final-GET
control: an exhausted retry budget must preserve the unread error response.
The expanded suite now has 19 cases. Released 0.5.2 passes 17 and fails both
cleanup controls; the unchanged cleanup and combined candidates each pass 19.
The new rejection case confirms one cancellation attempt and two total fetches.
It does not establish bounded cancellation latency or a live gateway outcome.
Existing patch/module hashes above are unchanged; the original 17-case results
remain dated evidence. The replay feedback loop is complete within this scope;
no unchanged rerun is requested. Maintainer integration remains pending.
