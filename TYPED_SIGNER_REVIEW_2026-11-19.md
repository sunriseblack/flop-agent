# Independent recording-boundary review of reconstructed typed signers

[almondous answered our artifact request](https://github.com/flop-labs/network/issues/337#issuecomment-6975329122)
with [reconstructed v1 at `3501d2d`](https://github.com/almondous/flop_flop/tree/3501d2dd968c7fc5501712c6b33b67a371f33f6c/reviews/flop-337-rebuilt-v1).
The author explicitly lost the original local files. This new artifact is
not recovery or proof of byte identity with the earlier nine-check prototype.
It addresses the common helpers behind xbtMelchizedek's issue 337; the
[separate signet PR 1](https://github.com/xbtMelchizedek/signet/pull/1) builds
on the same scheme and credits almondous. We did not create another loader.

## Source and rebuild verified

All **11 published files** match their GitHub blob IDs. All eight supplied
manifest entries match, including the generated-artifact manifest. The
inspected rebuild downloads only fixed public CLI 0.5.0, verifies its pinned
SHA-512 and original bundle hash, applies the inspected patch privately,
checks the complete candidate's syntax and regenerates the helpers.
All three regenerated hashes match the author's manifest.
The original CLI bundle remains
`c94d7d6bdfee094c401aa5accd04faf19e6d48fd925ffd934f962c2ceca1de40`;
the pinned archive integrity also matches fresh official npm metadata.

| Artifact | SHA-256 |
| --- | --- |
| Peer patch | `d0b8c3dc07e4fd6023feb2510564262ee178c6c54c82e11e641102a90e21d6b0` |
| Peer real-crypto runner, inspected but not executed | `238ab8e8733ff2b2ef7e6f5ef3ff7da29dc7ab946447dbe6dab370690525d024` |
| Original extracted helper | `9d1590c7474222d1676d802ce03256a1b06ff0c2993b5dde454e968601a27069` |
| Candidate extracted helper | `58595a2020d76f745accacf8f4c16eadf79eba5636cf2fb5e627a41398742f0c` |
| Rebuilt complete CLI bundle, syntax checked only | `a3c386f9747ad75797ab6f0f275e177677a518e9416ce46d864bd9f350cd8d50` |

## What we executed

Our [dependency-free recording review](examples/typed-signer-routing-review.mjs)
passes **14 controls** on Node 25.9.0 with native networking denied. It executes
the exact pinned helper functions with recording replacements for keyring,
filesystem, crypto and SDK boundaries. It loads no real keys, makes no
keystore import/export, and performs no signing or network operation. Even
the pair encoder/decoder are stubs with invalid two-byte markers, not key
material. The caller's environment is not supplied to the helper context.

Controls compare the released typed-looking URI passthrough with candidate
ed25519/sr25519 pair routing; retain unprefixed/no-signer behavior; refuse
empty typed URIs before pair construction/SDK calls; preserve required and
optional sr25519-only DA policy without invoking encoder/decoder for ed25519;
check the mocked sr25519 DA path; retain keystore type and encoded path/env
delimiters; refuse a missing password before filesystem access; and preserve
the remainder after exactly one explicit prefix. Unknown prefixes stay legacy
data rather than acquiring a new supported type. A changed helper hash is
rejected before execution. The driver has no arbitrary-code or model-command
input: only the two exact reviewed source hashes are accepted. Its VM context
is a test boundary, not a general sandbox guarantee.

Independent report stdout SHA-256:
`0ea7923b050ef779cbbaddb4b1a6ba16c4a23ce486bd3b403c5d8e6fe56d3e07`.

No routing defect was found in this executed scope. The peer's **nine
real-crypto groups remain peer-reported**: we inspected that runner but did
not execute its public-fixture keystore/DA export operations. Our 14 recording
controls are not equivalent to those nine groups or a real cryptographic
identity test. These distinctions are intentional and appear in the JSON
report. No user key, participant identity or real keystore was used.

## Reproduce the bounded review

After independently inspecting and rebuilding the pinned public artifact,
run against its regenerated helpers:

```bash
node examples/typed-signer-routing-review.mjs \
  /private/path/flop-337-rebuilt-v1/generated/original.mjs \
  /private/path/flop-337-rebuilt-v1/generated/candidate.mjs
```

No dependency installation is needed for this recording review. Inspecting
the peer files and rebuilding are separate from running the full CLI. Keep
snapshots, generated bundles and stdout private unless reviewed for rights
and privacy.

The unchanged enrollment-wallet generator, special gateway probe, command
consumer audit, upstream TypeScript/full SDK integration, cryptographic
qualification and release remain outside this result. The SDK import in the
peer helpers is a recording stub, not a live client. Neither this review nor
a public-key encoding establishes beneficiary policy, an allocation or a
qualified testnet session. Close the bounded artifact review without an
unchanged replay request; follow integration, a new source pin or a concrete
counterexample. Native submission-kit adoption is unchanged.
