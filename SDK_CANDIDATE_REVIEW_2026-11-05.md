# SDK retry and wallet-status candidate review

The review independently executed the proposed fixes on network issues 71,
72 and 82 against the published SDK 0.4.0 modules. The faucet review found
an additional error-value contract gap and supplies a small extension to
almondous's existing candidate. The x402 and wallet candidates passed their
scoped reviews. Original authors retain credit for their patches.
[Issue 71](https://github.com/flop-labs/network/issues/71)
· [Issue 72](https://github.com/flop-labs/network/issues/72)
· [Issue 82](https://github.com/flop-labs/network/issues/82)

## Source and method

The npm registry's latest tag was 0.4.0 when fetched on November 5. The fresh
archive matched the registry's SHA-1 and SHA-512 integrity values. Its SHA-256
is `bfccb19b27899ec1c76ccb32c2a2c62af3763e09b6e597f8a36aad25705b9b0f`.
Issue bodies and their proposed diffs were captured before execution. Each
candidate was applied to a separate copy of the original archive. Test and
source snapshots stay private.

The author suites used their published code. The additional review uses
[our response-contract program](examples/sdk-response-review.mjs). HTTP tests
run on real loopback servers with synthetic responses, while wallet tests
use mocked chain API objects. A macOS sandbox allowed local sockets and
refused non-loopback connections. Both permission directions were tested
before running the suites. Environment was Node 25.9.0/macOS arm64.

## Observed results

| Suite | Original artifact | Existing author candidate | Faucet extension |
| --- | --- | --- | --- |
| Issue 71 author's 22 cases | 13 pass, 9 fail | 22 pass | 22 pass |
| Additional faucet 24 cases | 6 pass, 18 fail | 12 pass, 12 fail | 24 pass |
| Issue 72 author's 18 cases | 5 pass, 13 fail | 18 pass | Separate candidate |
| Additional x402 17 cases | 10 pass, 7 fail | 17 pass | Separate candidate |
| Issue 82 author's 11 cases | 6 pass, 5 fail | 11 pass | Separate candidate |

These are direct distributed-module tests. Private source builds, full SDK
upstream tests, rebuilt bundles, browser execution and a released repair
remain separate validation steps. The repository's 244 tests passed.

## Faucet finding and extension

`FaucetResult.error` is declared as an optional string. The functional helper
currently assigns `JSON.parse(body).error` without validating its type.
Almondous's proposed class refusal branch adopts the same expression.
For a synthetic HTTP 429 body `{"error":{"code":"CAP"}}`, both return an
object in `result.error`. Arrays, positive numeric values and boolean true
also produce wrong types. Zero and false lose the raw refusal text through
the fallback branch. The 24-case review has eight type failures and four
body-preservation failures against the proposed candidate.

The supplement adds one shared private parser. It uses a JSON `error` field
only when that value is a string and otherwise retains the original response
text. Both API paths call it. Valid strings, plain text, null, malformed JSON
and the existing empty-string fallback retain their expected behavior. The
original 22 cases and all 24 additional cases pass after the supplement.
[Supplement to the issue-71 candidate](research/sdk_faucet_error_text_2026_11_05.patch)

This extension keeps the candidate's existing 5xx/transport retry policy.
Unknown outcomes after transport failures still need reconciliation. The
review establishes local result and request behavior with synthetic services.

## x402 review

The existing candidate passes all 18 author cases and 17 new cases. New
coverage checks each of the five management POST callers for request/body
preservation and a single structured refusal, each of four GET callers for
transient recovery, readable plain-text proxy refusal, a truncated successful
POST body and cancellation of a discarded GET body before retry. The latter
checks actual mock-stream cancellation order. The HTTP cases use native fetch
against loopback. No additional candidate defect emerged in this scope.

## Wallet-status review

The existing candidate passes all 11 author cases, preserving successful
creation, later funding failure, session outcomes and transaction hashes.
A false creation result records this invocation's lack of confirmed helper
success and does not establish the absence of an existing wallet. The helper
accepts inclusion as success, so this flag also leaves finality unverified.

Katazrofi's separate eight-case independent report was already present when
this review began. Its inclusion/retracted mock sequence is an additional
reported boundary and is outside our 11-case execution. No duplicate unchanged
review request is needed.
[Existing independent review](https://github.com/flop-labs/network/issues/82#issuecomment-6663939694)

## Artifact pins

| Module | Original SHA-256 | Reviewed candidate SHA-256 |
| --- | --- | --- |
| `dist/faucet.js` | `8819278213c1d5078bbb97ac66aa98984ba2e334b2e742f8fd25a3cda766a507` | Author `586ad8a1ed22a66d39c358c8d804445ccd5436d448dc390136ba3d55a744f164` |
| `dist/faucet.js` supplement | Same original above | Extended `e1b8098ca5d18c9b425432c69aaa1580451b2b6636ffdca3284d2fb68f70d597` |
| `dist/x402.js` | `d2c20e26c9f8e48af6af3218c810b8f06b6bff2084ededa4ef2234ad4510bd8d` | `28a836ffe1a9314c99536a56b1a289939daf8f8967230566b8c9028ef2676d04` |
| `dist/coordination.js` | `0b347df3a0ac4d36ed5c6dc6fe37f26462913216b3725e37a18deb3394c2758c` | `6f3c56fedb284910a781f2bbec7231c3eb0a56f01726e19ba74eb637adc33b8f` |

## Reproduce the additional cases

Use a fresh ignored private directory. Obtain SDK 0.4.0 from the npm registry,
verify the archive above, and unpack separate original/candidate copies.
Apply the exact proposed issue diff to its corresponding candidate first.
For the faucet supplement, the starting `dist/faucet.js` must match author
hash `586ad8a1...`. From this repository root, with the candidate at the path
below:

```bash
git apply --unidiff-zero --check --directory=.private/sdk-review/faucet/package \
  research/sdk_faucet_error_text_2026_11_05.patch
git apply --unidiff-zero --directory=.private/sdk-review/faucet/package \
  research/sdk_faucet_error_text_2026_11_05.patch
SDK_REVIEW_TARGET=faucet \
SDK_REVIEW_DIR="$PWD/.private/sdk-review/faucet/package" \
  node --test examples/sdk-response-review.mjs
SDK_REVIEW_TARGET=x402 \
SDK_REVIEW_DIR="$PWD/.private/sdk-review/x402/package" \
  node --test examples/sdk-response-review.mjs
```

No dependency installation is needed for these direct module imports. The
runner checks the target module hash and the faucet's imported chain-module
hash before importing. It records the actual source hash and Node/platform
in its output. The original and proposed variants are admitted so that their
expected failing results can be reproduced. Final expected results are 24
passing faucet cases and 17 passing x402 cases. The original author suites
remain in their issue bodies.

The next steps are author review of the supplement and maintainer porting
into the SDK source, full build/test validation and a released package.

The faucet finding and extension were delivered and read back exactly on
[issue 71](https://github.com/flop-labs/network/issues/71#issuecomment-6664493760).
The independent x402 execution report was likewise delivered on
[issue 72](https://github.com/flop-labs/network/issues/72#issuecomment-6664494291).
Both are pinned to repository revision `95b7b39`. Supplement acceptance,
source porting and release remain pending. The wallet review was recorded
without repeating the existing independent report.
