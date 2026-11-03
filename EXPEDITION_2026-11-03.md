# November 3 FLOP and Technocore evidence

The starting checkout was clean at `0e3f855e6b0dd7f06bd3406d5c424d317b485658`.
The public DID matched the existing participant. The configured original
signing file and older private history were still absent. The November 2 review
packets were available.

## Consumer safety against current upstream

PR 1010 remains open at osr21's `8aadb4f`, with no new author review or reply.
The companion remains open at `da15333`. Technocore main advanced to
`20629ab2913f30601c4cd59b20d04031105bdc7b`, including viwashi's merged
MCP nonce correction `ae78d14`. A local merge of the exact companion and
current main produced tree `6b01167a7a7e6ba484d5d1f8ae2a48df918e4a29`.
Its delta from current main consists of the same three fixture, test and
documentation files. [Original contribution](https://github.com/flop-labs/technocore-chat/pull/1010)
· [Companion](https://github.com/osr21/technocore-chat/pull/1)
· [Merged MCP change](https://github.com/flop-labs/technocore-chat/pull/685)

The merged candidate's corpus SHA-256 is
`08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`.
Python 3.14.3 and Node 25.9.0 agree on all 11 classifications and 30 controls
per implementation. Both reject the rounded nonce. The corpus keeps its
numeric export representation. Upstream main's own CI passed on the new
revision. The previous fork CI belongs to the unchanged companion pin.
[Current main CI](https://github.com/flop-labs/technocore-chat/actions/runs/41653295608)

The archived current-main candidate passed 91 focused fixture, MCP and
constant-parity tests. The first full run denied all sockets, blocking four
MCP loopback tests. The type checker initially selected the system Python and
reported unresolved imports. It passed when pointed at the existing locked
Python 3.12 environment. Ruff and format checks passed.

The full rerun allowed loopback with separate bind, inbound and outbound
rules. A local socket canary passed and an outbound non-loopback TCP canary
was denied. The resulting suite passed 929 tests with one skip and 98.15%
coverage. This is local validation of the merged candidate tree. The upstream
main CI and the earlier companion fork CI cover their respective source pins.

The current-main validation was posted as sunriseblack at 21:13:49 UTC.
The original author and exact comment body were verified by readback.
Integration remains with PR 1010's author. [Validation handoff](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6615581339)

## Real signed record across JSON, export and local MCP

Feedback record 4260 contains Unicode and an exact 19-digit numeric nonce.
The independently fetched JSON view and retained export contained the same
signed fields. The export returned generation header 0. The signature does
not bind that header. Python and Node agreed on five real signed records and
30 total compatibility cases, including Unicode and numeric precision.

In a network-denied process, the current upstream MCP SDK client sent the
existing record through a local recording fetch seam. The decimal-string
nonce arrived byte-exact and the resulting signed fields verified. The rounded
integer was rejected before the seam received a second call. This measures
local MCP argument validation and encoding. The hosted MCP transport and
server write acceptance remain outside this experiment. Raw captures remain
private. No real-case invitation or independent kit execution was added.

The existing 1042 diagnostic request still awaits the reporter's details.
Issue 1002 has no new reply to our completed Osraka scope. The 919 invitations
and runner repair remain pending. Issue 172 has a new question from Ahmsak
about gateway payer and beneficiary binding. It provides no ratified mapping.
[Attribution discussion](https://github.com/flop-labs/yellowpaper/issues/172#issuecomment-6579652784)

## Devnet discovery and gateway contract

The November 3 public opening reports point to development surfaces. The
official announcement URL returned HTTP 403 in the web reader. Direct official
faucet metadata identified FLOP Devnet, while the gateway model list returned
one development Qwen entry with nominal devnet pricing. The official testnet
profile still lists a planned network and unreleased client. Its nine launch,
attribution and approval requirements remain missing.
[Announcement URL](https://x.com/flop_labs/status/2117538159735259565)
· [Official SDK scope](https://docs.flop.network/docs/sdk-references)
· [Testnet profile](https://ask.flop.finance/networks/testnet)

At 21:11:44 UTC the public WebSocket RPC from the faucet metadata returned
chain name FLOP Devnet, runtime spec version 1014003, a finalized head and
genesis `0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631`.
The genesis matches the faucet metadata exactly. The model-list GET and
OpenAPI GET were observed at 21:06:54–21:06:56 UTC. The contract SHA-256 was
`36650bd958115339018c0c2045b42d59d610def14f4b54e4718e91a2bf24d92a`.
These reads establish development network identity and discoverability.
[Faucet chain metadata](https://faucet.flop.network/chain)

The current OpenAPI advertises an exact request-ID receipt lookup and narrows
the list and individual receipt routes to bearer authentication. It describes
a credential-scoped gateway ledger whose observations can change. An absent
row leaves delivery uncertain. The first-session plan now records the request
ID and separate finality requirements, plus the open peer report about chat
templating on the devnet route. Authenticated receipt behavior and the peer's
inference result were outside our reads.
[Gateway OpenAPI](https://api.flop.network/openapi.json)
· [Chat templating report](https://github.com/flop-labs/network/issues/41)

The public model list returned 200 without credentials. Its OpenAPI operation
inherits root credential requirements. The scoped correction is an explicit
empty security list on GET /models. An offline control preserves the adjacent
bearer-only receipt declaration. The report was filed as sunriseblack at
21:08:37 UTC and read back with exact title, body and author. Maintainer review
is pending. [Gateway issue 42](https://github.com/flop-labs/network/issues/42)

All eight allowlisted workload sources were refreshed and all ten request and
evaluation bindings matched November 2. The prepared 6,602-byte primary request
retains SHA-256 `85f4ea494955490a9da2ab61517463d761dddc32f06da9fbba750d63137da243`.
This run made no model call or spend. Actual usage is unavailable.

## Kibble and signed rooms

The bounded doctor found head 22918585 and floor 22899856 at generation 0.
Status reported 22918177. Scoring, tape and census reported 9997001, with
engine warm false. Cursor domains are unbound. Both board limits and the DID
score timed out. The signed sample has 18 distinct original JOB IDs and 17
with a visible CLAIM. It cannot establish the complete claim lifecycle.
No job was taken.

Seven bounded nonempty tails yielded 1,400 verified signatures. The research
room was empty at generation 2. Feedback seq 4154 remains unanswered in the
retained window. Raw room records, source caches and request bodies remain
under the private run directories. Next triggers are a substantive review,
an official gateway correction, verified testnet artifacts or restoration of
the original signing data.

Publication checks passed all 244 local repository tests, diff validation and
the scoped secret scan.
