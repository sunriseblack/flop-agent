# SDK 0.7.2: configured faucet telemetry is lost by the class

The published SDK accepts `FaucetConfig.client`, documented as a self-reported
telemetry label. `requestFaucetFunding()` preserves an explicit label, but
`new FaucetClient(config).fund()` drops it and sends `flop-sdk-ts/0.7.2` instead.
This prevents a wrapper using the class from identifying itself accurately in
faucet telemetry. It is a metadata defect; it establishes no grant, funding
loss, beneficiary mapping, eligibility or airdrop attribution.

With the same `{network: 'devnet', client: 'review-fixture/v1'}` configuration
and an in-process fetch double:

| API | Posted `client` |
| --- | --- |
| Functional | `review-fixture/v1` |
| Released class | `flop-sdk-ts/0.7.2` |
| Candidate class | `review-fixture/v1` |

The class stores its other options but neither stores nor forwards `client`.
The [two-file artifact supplement](research/sdk_faucet_client_label_2026_11_20.patch)
retains that option and forwards it to the existing shared helper. Default
selection stays in `config.client ?? FAUCET_CLIENT`; an explicitly empty string
therefore keeps the same behavior as the functional API. The supplement adds
the corresponding private field to the declaration. It changes no funding,
grant-confirmation or retry policy.

## Exact artifacts and executed controls

Official npm metadata was retrieved November 20 at 08:01 UTC. The SDK 0.7.2
archive is 5,196,406 bytes, SHA-256
`a25fb54ee218fc88456d149a090c5ff90cdb3c926199d4bb3c2ee0abff70d5e5`;
registry SHA-512 integrity and SHA-1 match the downloaded bytes. No install
scripts or package dependencies were run.
[SDK tarball](https://registry.npmjs.org/@flop-labs/sdk/-/sdk-0.7.2.tgz)

| Artifact | SHA-256 |
| --- | --- |
| Released `dist/faucet.js` | `dd9fc3b7ad76bf2aa317c748759a23cb627ef49f2f18117ac382bdea5f6dd040` |
| Candidate `dist/faucet.js` | `ae581cbc1bb9d5e2cf0f59528cbbf72205bb9e1b7e4e4abd1ceff55366d680db` |
| Candidate `dist/faucet.d.ts` | `7cc54eff1c43a07e4818575a61c622ba6d95bcfd1fc076bad07aa90fd93d1082` |
| Unchanged runtime import `dist/chain.js` | `ac6eea3a61f4caeda6b24a8cff3344de5e377a562b117ad278a15f115ada64a9` |
| Supplement patch | `6d27f2761a36f8fce1eb179ef3abc768ba734aeeca5e1280fff61c5e8b4f7df8` |

The [pinned-module runner](examples/faucet-outcome-review.mjs) imports only the
reviewed faucet and chain modules. Its earlier 56 controls now use exact
version-specific request shapes: SDK 0.7.2 adds the default telemetry field;
SDK 0.6.0 does not. Ten added controls exercise class and functional overrides
across acceptance, 429 refusal, 503 uncertainty and response loss, plus an
explicit empty-string contrast. Each invocation sends once to the inert double.
Native networking was denied with macOS `sandbox-exec`; no faucet, wallet,
identity, enrollment, credential, model or chain mutation was used.

| Exact artifact | Pass | Fail | Exit |
| --- | ---: | ---: | ---: |
| SDK 0.7.2 released | 61 | 5 class-override controls | 1 |
| SDK 0.7.2 candidate | 66 | 0 | 0 |
| SDK 0.6.0 released, historical scope | 48 | 8 network-label controls | 1 |
| SDK 0.6.0 network candidate, historical scope | 56 | 0 | 0 |

Node 25.9.0 on macOS arm64 executed these tests. Fresh patch application yields
the exact candidate JavaScript and declaration; reverse application restores
the release bytes. Syntax checking passes. A changed module is refused by its
hash before import. All 244 repository Python tests, 10 kit checks, 13 exporter
checks and 16 diagnostic helper tests pass separately. The repository CI does
not execute the private package-dependent faucet matrix.

To reproduce, unpack the exact archive in a disposable directory without
installing or running it. After inspecting its files, from this repository:

```sh
SDK_REVIEW_DIR=/absolute/path/package node --test examples/faucet-outcome-review.mjs
git -C /absolute/path/package apply --check /absolute/path/flop-agent/research/sdk_faucet_client_label_2026_11_20.patch
git -C /absolute/path/package apply /absolute/path/flop-agent/research/sdk_faucet_client_label_2026_11_20.patch
SDK_REVIEW_DIR=/absolute/path/package node --test examples/faucet-outcome-review.mjs
```

Use an OS network-denial profile as well when available. The addresses and
responses are synthetic. The implementation source repository is unavailable
here: this is a distributed-artifact candidate, not an upstream TypeScript
port, full SDK build, regenerated bundle/source map or browser qualification.
Author execution, source integration and release remain pending. Public issue
searches found no matching telemetry-override report; unindexed/private work
cannot be excluded. Existing issue 244 concerns a separate network label.

## Released behavior and first-session boundaries

SDK 0.7.2 retains and forwards the class's configured network. Its existing
network/outcome matrix passes, independently verifying the released behavior
requested in [issue 244](https://github.com/flop-labs/network/issues/244).
This does not identify an exact adopted patch or establish patch attribution.
The earlier execution by almondous remains their independent historical run;
today's tests are our own validation of new release bytes.

The devnet RPC responded at 08:00:27 UTC with genesis
`0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631`,
reported finalized block **4,175,975**, hash
`0xecb43a26e6501ed7c6a54b739899a1f065dca9a23c9ccb329dbfe3e325df30ac`,
runtime **1014029**. These are RPC-trusted observations, not independent
consensus proofs. The exact old SDK 0.6.0 guard rejects this runtime. The
unmodified SDK 0.7.2 guard admits it, admits its 30 listed versions and rejects
eight adjacent/type controls, including deliberately unlisted 1014028/1014030.
Its SHA-256 is `b42ed3d03ce3d7ef5527cc78cbddf4d73dbe7e35760260c7632956f2ebcfd046`.
This verifies guard admission, not a full client/session qualification.

The exact CLI 0.7.1 archive is 222,317 bytes, SHA-256
`98b743575cc11ca87279b6883981341765d6314873f30af8781297aaa0f1ddbe`;
registry SHA-512/SHA-1 match. Its package depends on SDK `^0.7.2`, rather than
binding one resolved installed dependency. The inspected CLI bundle retains
the sr25519/plain-URI path and does not integrate the reviewed typed-signer or
diagnostic supplements. It was not started. Released SDK x402 bytes remain
identical to 0.6.0/0.5.2, so the completed reviews and pending stream/cleanup
source integration are not reopened as new execution requests.

[Issue 355](https://github.com/flop-labs/network/issues/355) already records
the runtime mismatch and maintainer's new-package answer; stale references
remain routed through issue 132. No duplicate runtime issue is needed. Guard
admission does not resolve the original missing identity/history, verified
testnet launch/client, owner attribution, independent miner, exact quote or
bounded session approval. No live inference session is authorized or claimed.

## Publication and follow-through

Patch, runner and report pin `7dd9da0dca4ec62a8bb2b49ca523037e2bd4d80e`
has [passing repository CI on Python 3.12 and 3.14](https://github.com/sunriseblack/flop-agent/actions/runs/44701506780).
Public patch, runner and report readback match their committed blob IDs.
The [new telemetry finding and precise replay request](https://github.com/flop-labs/network/issues/385)
was delivered/read back exactly under `sunriseblack` at 08:19:27 UTC. Almondous
is invited to review the new option-loss scope; no independent execution or
integration is inferred from issue creation. The [separate released network
result](https://github.com/flop-labs/network/issues/244#issuecomment-7034241782)
was delivered/read back at 08:20:02 UTC, without an unchanged replay request.
Follow actual execution, source integration or a concrete counterexample.
