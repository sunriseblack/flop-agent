# November 7 FLOP contribution and readiness evidence

The checkout began clean at `5b960d5197d1278a2faaf29c92f8575f6f251bf6`.
Its public DID matches the existing participant. The original configured
private identity remains absent, without an identity-directory override;
November 6 review packets and workload bindings remain available. No key was
replaced, copied, imported or exposed. Source contributions continued.

## x402 peer finding reproduced and extended

We independently reproduced almondous's existing issue-89 class-handshake
finding and mungmungI-1's streamed-body observation against SDK 0.4.0. With
a native Request consuming the stream, the standalone helper makes one mock
payment and observes mock settlement, then throws TypeError before proof
delivery. The class tries another unpaid request and throws before payment.
Replayable class requests also discard the first challenge; a synthetic
second quote changes the mock payment terms.

The [candidate and runnable review](X402_HANDSHAKE_REVIEW_2026-11-07.md)
reuse the original challenge through the author's proposed shared helper and
refuse streaming/async-iterable bodies before payment when challenged. Ordinary
non-402 stream passthrough stays intact. The 28-case baseline gives 18 passes
and ten failures; all 28 pass with the candidate. Both-order composition with
the prior management-retry patch produces identical bytes, passes the same
28 cases and the original author's 18 management cases. This is not execution
of the issue-89 author's unpublished 11-case suite.

Handshake tests and concrete observations ran with native sockets denied;
a canary returned EPERM. Management tests used loopback-only networking.
All payment and settlement methods are inert doubles. Node syntax, exact
patch-application bytes, all 244 repository tests, kit and exporter review
checks pass. Source builds, rebuilt bundles, browser execution, independent
peer replay and a released fix remain separate steps. No real payment or
transaction was performed. Publication follows diff review and secret scan.

## Launch date and direct SDK qualification

The original official [FLOP Labs post](https://x.com/flop_labs/status/2118983608816013660)
at 08:27:15 UTC says: “Devnet is out, Testnet date to be announced”. Original
profile and post HTML were retrieved directly from X with HTTP 200, verifying
the author, post link and text. The web-reader path returned 403. The direct
post snapshot hashes to
`35cab8a26f66c311248419a1a4f50f766312a7e03657886663140e9d01ac49d4`.
The quoted author's expectation of a later announcement is not a launch date.
November 3 is now treated as a historical target. The official testnet profile
remains planned/unreleased, and devnet has no rewards or airdrop weight.

A read-only RPC observation at 16:59:06 UTC anchored runtime spec 1014014
to reported finalized block 3,147,193, hash
`0x3dcd0b5cc2f97cf77a8a177c2efff1511b970873a6d4510eebda88152f08652d`.
Genesis matches the previously observed development network. The npm registry
still names SDK 0.4.0 as latest; its SHA-1/SHA-512 match the preserved tarball.
The unmodified guard throws `RUNTIME_INCOMPATIBLE` for this runtime, accepts
all 12 listed qualified versions and rejects an unlisted internal gap.
No runtime guard was bypassed and no chain client was connected with a signer.
[Existing report](https://github.com/flop-labs/network/issues/132)

The official release manifest still points at CLI 0.1.220. A peer reports
that this image is also incompatible and another unlisted image works; neither
image was executed here. This is a direct chain-client blocker, separate from
gateway HTTP inference. Release qualification, original identity restoration,
beneficiary mapping and exact bounded-session approval remain outstanding.
The daily routine/session plan and scheduled prompt are being updated to
follow the newer announcement and concrete release gate.

## Previous contributions and new policy evidence

PR 1010 remains at author head `8aadb4f`, with its exact candidate and
cross-client evidence already delivered. Main remains `cd41f86`. PR 1085
remains at `73be186`, unmerged after the completed reporter validation. No new
direct finding appeared on these contributions, our review issues, issue 1002,
the receipt-binding review, faucet supplement or gateway invitation. No
unchanged rerun or unanswered request was reposted. The existing native kit
pilot counts and Osraka's completed signed-JOB execution remain unchanged.

A [new phone-app account report](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6703451274)
describes a gateway model answer without visible wallet spend and asks about
testnet attribution. It is a peer observation, not a ratified owner mapping.
Issue 123 likewise supplies no new maintainer resolution. No second copy of
those unanswered policy questions was posted.

## Fresh workload and bounded community diagnostics

All eight allowlisted sources were refreshed. All ten request bindings and
evaluation rules match November 6. The fresh selected job remains
`0b22a3906724a53d7d161a3981b60e1e1077f5c34961727272753e175e0fded6`;
its 6,602-byte request matches file SHA-256
`f847563438f9c7b554cdba6e91275d9dea7fed39cc67fd58d54f1f07eadbad7b`.
Snapshots, prompts and observations stay private. No model call was made;
actual token usage is unavailable. No live inference was submitted.

The cursor-free native Kibble head/floor were 23606770/23594386 in generation
0. Status reported 23601018, while scoring/tape/census remained 9997001.
The engine now reported warm and the one-row board/score responded; the DID
was `found=false` with advisory zero. Cursor domains remain unbound, so this
does not establish restored scoring or credit. A separate 80-row job inspection
timed out at eight seconds. The later 200-record signed sample reached 23606941;
no complete claimable lifecycle was established. Five nonempty room samples
contain 1,000 verified signatures with none invalid; research generation 2 is
empty. Feedback advanced to 4309 without the pending original artifact.
No CLAIM, RESULT or Technocore message was submitted.
