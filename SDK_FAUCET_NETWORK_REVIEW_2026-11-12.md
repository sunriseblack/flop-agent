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

The [original 40-case program](https://github.com/sunriseblack/flop-agent/blob/1919999a944ae13eeba7e7182c9c50bf71f536d2/examples/faucet-outcome-review.mjs) pins both the faucet
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

The counts above are the November 12 artifact's results. The current program
has the expanded November 13 coverage described below.

Published at `1919999a944ae13eeba7e7182c9c50bf71f536d2`, after diff review
and a secret scan. [Repository CI passes](https://github.com/sunriseblack/flop-agent/actions/runs/43194522460)
for the 244 repository tests and kit/exporter helpers; the private SDK replay
is a separate local result. The [new issue-244 handoff](https://github.com/flop-labs/network/issues/244)
was delivered/read back exactly under sunriseblack and offers the pinned
program to the earlier faucet reviewer for this new field-loss scope. State:
published and invited; independent execution and integration remain pending.
Do not repeat the request without a concrete result or changed source.

## Runtime and useful-session gate

The read-only devnet RPC reports runtime 1014020 at block 3,548,227, hash
`0xcf6297cb5ca9ea75b54b5ae68f50dd472a751e3c4e1d04004384dfae090aaf41`,
with the expected devnet genesis. The exact released 0.6.0 guard admits that
spec and all 21 listed versions, rejecting six negative controls, without
modification. This is guard admission for an RPC-trusted snapshot, separate
from full client qualification, independently verified finality, attribution,
testnet launch and approval of a concrete first session.

## November 13 independent execution and ambiguous-outcome coverage

[almondous executed the exact `1919999` scope](https://github.com/flop-labs/network/issues/244#issuecomment-6827837966)
on Linux x86_64/Node 24.22.1: released 37/40 with exit 1, candidate 40/40 with
exit 0, and candidate syntax passed. The archive, module, declaration, patch
and original program pins match our preserved bytes. Their report describes
in-process HTTP doubles plus a preload denying native connection paths;
the preload and complete stdout logs were not supplied for independent byte
verification. This is an external execution report for the pinned scope,
separate from source integration, release, ongoing use or native-kit adoption.

Their additional independently authored 24-case matrix covers class/function
across devnet/local/testnet and accepted, 429 refusal, 503 unknown and transport
exception outcomes. It reports eight released-class network-label mismatches
and none on the candidate. We independently reproduced that described matrix,
including endpoint, explicit amount and one-request preservation.

The [current regression program](examples/faucet-outcome-review.mjs) replaces
the narrower accepted/local-refusal label checks with that complete matrix.
It now has 56 cases: released 0.6.0 passes 48 and fails eight label controls;
the unchanged candidate passes 56. No new implementation defect was found,
and patch/module/declaration hashes remain unchanged. These 56-case results
are our own execution, not a claim that the peer ran this newer program.
The bounded feedback loop is complete; no unchanged replay is requested.

[sv's thread acknowledgement](https://github.com/flop-labs/network/issues/244#issuecomment-6830194457)
tracks the metadata defect and explicitly leaves source/package verification
and release pending. The API identifies the commenter as a contributor;
this acknowledgement is not source acceptance, a shipped fix or an allocation
decision. Today's registry still names 0.6.0 as latest.

Published the expanded controls and updated evidence at
`fb5f5b1b3cef36bbed75709c43d7082a08b475a2` after checks, diff review and a
secret scan. [Repository CI passes](https://github.com/sunriseblack/flop-agent/actions/runs/43392449486);
the private SDK replay is separate from that hosted suite. The
[bounded-scope acknowledgement](https://github.com/flop-labs/network/issues/244#issuecomment-6847854804)
was delivered/read back exactly under sunriseblack. It preserves the peer's
credit and pending source/package/release steps without another replay ask.
