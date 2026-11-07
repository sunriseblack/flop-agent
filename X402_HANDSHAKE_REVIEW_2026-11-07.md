# x402 challenge reuse and streamed request refusal

This extends almondous's [existing network issue 89](https://github.com/flop-labs/network/issues/89)
and mungmungI-1's [streamed-body reproduction](https://github.com/flop-labs/network/issues/89#issuecomment-6671523035).
The original class discards its first valid challenge and starts another
unpaid fetch. The standalone helper can make a payment and observe settlement
before failing to construct a proof-bearing request from a consumed stream.
Our local native Request/Response controls independently reproduce both.
All payment and settlement methods are inert test doubles; no real payment,
signer, gateway inference or chain submission was used.

The [complete candidate patch](research/sdk_x402_handshake_2026_11_07.patch)
implements the original author's shared-helper outline and adds a narrow
stream policy. Both entry points use the challenge already received. After a
valid 402 and the existing cancellation check, streaming/async-iterable bodies
are refused with `PaymentError` code `UNREPLAYABLE_BODY` before creating an
HTLC. Non-402 streaming requests still pass through normally. The wrapper
does not buffer arbitrary streams or introduce a body-factory API. A caller
needing automatic payment must provide prepared replayable data. This also
conservatively refuses re-iterable async sources, rather than assuming they
can reproduce the same bytes.

## Exact sources and controls

The npm registry still named SDK 0.4.0 as latest on November 7. Its SHA-1 and
SHA-512 metadata match the preserved tarball, whose SHA-256 is
`bfccb19b27899ec1c76ccb32c2a2c62af3763e09b6e597f8a36aad25705b9b0f`.
The original `dist/x402.js` SHA-256 is
`d2c20e26c9f8e48af6af3218c810b8f06b6bff2084ededa4ef2234ad4510bd8d`.
The candidate hashes to
`77f98a052ece5882bcad6198ef5356b01d2e0b3ca6950ef5ea5074fc3d59760e`.
The [28-case program](examples/x402-handshake-review.mjs) checks the module
and its three transitive source hashes before import.

| Control | Original | Candidate |
| --- | --- | --- |
| Class: repeated unpaid request refused | HTTP 429, two unpaid fetches, no mock payment | HTTP 200, one unpaid fetch and one proof fetch |
| Class: second challenge changes price | Three fetches; mock payment uses second price | Two fetches; mock payment uses first price |
| Function: consumed ReadableStream | One mock payment and settlement, then TypeError on second fetch attempt | One unpaid attempt, explicit refusal, no mock payment |
| Class: consumed ReadableStream | TypeError on second attempt before payment | One unpaid attempt, explicit refusal, no mock payment |
| Non-402 ReadableStream, both APIs | Unpaid passthrough | Unpaid passthrough |
| 28-case suite | 18 pass, 10 fail | 28 pass |

The suite also checks challenged async iterables, replayable strings/bytes/URL
parameters, ordinary headers/method/body preservation, invalid challenges,
abort-before-payment, creation and settlement failures, missing class client,
and the function's agent, timeout and TEE options. Native Request consumption
causes the baseline stream errors; the fake transport never contacts its
`fixture.invalid` URL. This is our full 28-case suite, not execution of the
original author's unpublished 11-case suite.

The candidate composes with the existing issue-72 management-retry patch.
Applying the patches in either order gives identical module SHA-256
`1879257cc8e91da0b72c518ef06547f81b5209eafbf2a5121a94b3ad7d345042`.
The combined module passes all 28 handshake cases and the earlier author's
18 management cases. Handshake/replay controls ran with native sockets denied;
a socket canary confirmed EPERM. Management controls used loopback-only
networking. Environment: Node 25.9.0, macOS arm64. Patch application, exact
resulting bytes and Node syntax checks pass.

## Reproduce from the preserved public artifact

Unpack the pinned SDK tarball into a fresh ignored private directory, preserving
the original. No package installation is needed for these direct imports.
With a candidate copy at the path below, run from this repository root:

```bash
git apply --check --directory=.private/x402-review/candidate/package research/sdk_x402_handshake_2026_11_07.patch
git apply --directory=.private/x402-review/candidate/package research/sdk_x402_handshake_2026_11_07.patch
SDK_REVIEW_DIR="$PWD/.private/x402-review/candidate/package" node --test examples/x402-handshake-review.mjs
```

Pointing the same program at the unmodified original should exit 1 with the
baseline failures above. It accepts only the three reviewed module hashes
and the pinned transitive definitions. Saved packets, module copies and logs
remain private; only the minimal patch and our runnable controls are published.

## Integration limits and next trigger

This is a distributed-JavaScript proposal retaining the original author's
handshake design and the peer's streamed-body finding. Porting to TypeScript,
source builds, full upstream checks, rebuilt ESM/CJS bundles, browser behavior
and release remain unverified. Existing payment-header parsing, header-container
handling from issue 27, transport/settlement uncertainty and production payment
support remain outside this patch. A consumed stream failure after mock
settlement is not evidence of an observed live loss or double payment.

The current direct SDK also rejects Devnet runtime 1014014. This offline
candidate does not override that guard or establish a working live SDK route.
The next step is original-author/reporter execution of the pinned patch and
then maintainer source integration. No paid third-party demonstration is needed.

Published at `71c66cccd2ef77a51b19b07330a20f6350754c2f`, with successful
[repository CI](https://github.com/sunriseblack/flop-agent/actions/runs/42395144794).
The [pinned original-author/reporter request](https://github.com/flop-labs/network/issues/89#issuecomment-6710499490)
was delivered and read back exactly under sunriseblack. State: candidate and
regressions published, independent candidate execution pending. The repository
CI covers its regular tests and review helpers; it does not independently
execute the packet-dependent SDK replay described above.
