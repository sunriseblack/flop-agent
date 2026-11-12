# SDK 0.6.0 faucet network metadata and uncertain outcomes

The November 12 registry publishes SDK 0.6.0 and CLI 0.5.0, at 03:39:23 and
03:41:39 UTC. The SDK archive is 4,717,469 bytes, SHA-256
`2a4a8888db2a814e401f58c9c89df327494188b80f31f8625862d312258ff610`;
its registry SHA-1 and SHA-512 integrity match. The CLI metadata was read;
the CLI was not installed or executed.
[Published SDK](https://registry.npmjs.org/@flop-labs/sdk/-/sdk-0.6.0.tgz)
· [CLI registry](https://registry.npmjs.org/@flop-labs/cli)

## Configured network is lost by the class

`FaucetClient` resolves the constructor's selected endpoint but does not retain
`config.network`. Its `fund()` call passes the endpoint to `requestFunding()`
without the network. The shared helper therefore labels its result `testnet`.
The functional API preserves the same configured network.

With an in-process response and a synthetic endpoint:

| Configured network | Class result | Functional result |
| --- | --- | --- |
| `devnet` | `testnet` | `devnet` |
| `local` | `testnet` | `local` |
| `testnet` | `testnet` | `testnet` |

The mismatch also affects refusal metadata. This is a result-label defect;
it does not establish that a transfer happened on another chain, authenticate
any endpoint, or make an observation eligible for testnet credit. It is present
in the reviewed release, without a claim that 0.6.0 introduced it. Duplicate
searches found the earlier closed [retry/status issue 71](https://github.com/flop-labs/network/issues/71),
whose fix concerns a different response boundary.

The [small distributed-artifact patch](research/sdk_faucet_network_2026_11_12.patch)
retains the constructor-selected network and passes it to the shared helper.
It also adds the private field to the declaration. Endpoint selection, the
existing default, HTTP outcomes, amounts, retry behavior and grant confirmation
are unchanged. The source repository was not available for a TypeScript port;
the source equivalent is `sdk/typescript/src/faucet.ts`. Full source builds,
type checks, regenerated bundles/source maps and browser behavior are untested.

## Current contract controls

The [40-case program](examples/faucet-outcome-review.mjs) pins both the faucet
module and its only runtime import before loading them. It uses native
Response objects with an in-process fetch double; no dependency install,
identity, credential, faucet request or chain operation is needed.

Released source passes 37 and fails three network-label controls. The candidate
passes all 40, including configured/default networks, refusal metadata, one-shot
HTTP/transport failure handling, malformed responses, pre-funding identity
mismatch, and the accepted-response/grant distinction. Patch application to
a fresh unpacked release yields exactly the tested JavaScript/declaration bytes.
Node 25.9.0/macOS arm64 ran with native network access denied.

The release now makes one funding attempt even with `maxRetries: 99`.
HTTP 408/5xx or response loss remain unknown; 400/403/429 are refusals. An
accepted response carries amount/hash metadata, while `fundFromFaucetDetailed`
still reports the grant as unknown because no authenticated request-to-
transaction binding is supplied. The older boolean helper returns false even
after the mock funding POST; false must not be read as proof that nothing was
sent. These are verified released behaviors, without claiming adoption or
credit for any earlier contribution.

One initial test incorrectly assumed that a planned testnet profile had no
SDK faucet URL. The unchanged chain module contains planned endpoint names;
that assumption was corrected before the final run. The no-faucet control
uses mainnet, whose SDK faucet field is null. Static names and the helper's
availability boolean do not verify testnet launch. The official network profile
still supplies no verified public testnet identity or release.

| Artifact | SHA-256 |
| --- | --- |
| Released `dist/faucet.js` | `546c798ab5772a34bd0f7dc40f8d75745c70d5f91485bb0bcfe881bbdca5ac42` |
| Candidate `dist/faucet.js` | `2cb714f9cd3fb8ae1a8a46603d560dcda8078bab62fc78177a57eb22317b2215` |
| Candidate `dist/faucet.d.ts` | `175822e0a249e7d286ab567638c74dd2a21c8d689050c08c445daa657edc7325` |
| Patch | `38ad91176a668ab558dd3b4e096fb6614ecdc155097a7d9f8d6134c36e0c0c57` |

From this repository root, after independently downloading, integrity-checking
and inspecting the release into the example private path:

```bash
git apply --check --directory=.private/sdk-060/candidate/package research/sdk_faucet_network_2026_11_12.patch
git apply --directory=.private/sdk-060/candidate/package research/sdk_faucet_network_2026_11_12.patch
SDK_REVIEW_DIR="$PWD/.private/sdk-060/candidate/package" node --test examples/faucet-outcome-review.mjs
```

State: reproduced and locally tested candidate. Independent execution,
maintainer source integration and release require separate evidence. Existing
x402 modules and their runtime imports are byte-identical to 0.5.2; its pending
stream/response cleanup supplements are not claimed to have shipped in 0.6.0.

## Runtime and useful-session gate

The read-only devnet RPC reports runtime 1014020 at block 3,548,227, hash
`0xcf6297cb5ca9ea75b54b5ae68f50dd472a751e3c4e1d04004384dfae090aaf41`,
with the expected devnet genesis. The exact released 0.6.0 guard admits that
spec and all 21 listed versions, rejecting six negative controls, without
modification. This is guard admission for an RPC-trusted snapshot, separate
from full client qualification, independently verified finality, attribution,
testnet launch and approval of a concrete first session.
