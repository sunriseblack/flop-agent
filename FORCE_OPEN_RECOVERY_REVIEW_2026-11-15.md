# Expired force-open recovery: an existing operation, an unclosed observation

infinity-nashi's [network issue 291](https://github.com/flop-labs/network/issues/291)
asks how to terminate an expired `pendingAck` channel. The existing public
surfaces identify `expire_force_open`; SDK 0.6.0 calls it `expireForceOpen`.
The reported channel was still pending in our read-only snapshot. Operation
availability is separate from successful execution, automatic cleanup and an
observed refund. No transaction was constructed, signed or submitted.

## Actual case and current runtime

At 08:01:35 UTC on November 15, the public devnet RPC reported finalized
block **3,794,660**, hash
`0xec1c3384f8d0b2a9493545032419515e44dc1229075a641aa77b10356fcd2e3e`,
spec **1014020**, genesis
`0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631`.
Only the two already-reported channel IDs were queried; no whole-map scan or
new funded session was needed.

| Channel | Finalized storage observation |
| --- | --- |
| `0xda15edcf0232816d32b4684c221896de08d60ce9238152e9a44c682c30b3d7a3` | Present, `pendingAck`, deadline **3,782,716**, openedAt **3,782,116**. The sampled head is **11,944 blocks** after its deadline. |
| `0xb1c8245598e202acebce0626730442a90d31d265ef8baa7074afacfd5fd09d9d` | Present, `closed`. Terminal transaction/refund was not captured, so closed storage alone is not classified as a verified refund. |

Both name agent `5ECvjJf7RKEfzbX72uAU25ptHZKsgrusHxHzanvqR2gNc6HG`
and miner `5Hb5PRJPLSxLgjj776pECCADGvARcWJiPTk2sRMKwK2yLJxc`.
Both retain an escrow field of **10000000000000000 raw units**, zero
`lockedComputeConsumed` and null `transcriptRef`. Stored escrow is not an
independent measurement of currently reserved wallet funds. No account-hold
attribution or terminal event was checked here.

At 08:02:52 UTC, both exact explorer detail lookups returned HTTP 404. Native
storage supplies the bounded observations above. A 404 does not establish a
nonexistent channel or authorize a replacement purchase. This extends the
[earlier public-view comparison](GATEWAY_CHANNEL_REVIEW_2026-11-14.md).

## Recovery operation and source boundaries

The [official named-miner guide](https://docs.flop.network/docs/send-to-specific-miner),
dated November 3, distinguishes expired pending acknowledgements, expired open
sessions and forced settlements. Its recovery section points them to
`expire_force_open`, `timeout` and `finalize`, respectively. It also treats fees
and miner-side counters separately from refund/rollback. The sampled HTML hash
is `404193725243478b18c8f9ee5d06e0b4a7ae6980f7fe0e4a7976273d601e19fb`.

Decoded metadata at the anchor exposes pallet **ComputeChannel (103)**,
call **expire_force_open (11)**, with one **channel_id: H256** argument.
Its documentation describes expiry after the acknowledgement window, closing
the channel, releasing its weights pin and refunding escrow. It also describes
a possible non-dust `FailedAcks` increment and a `ForceOpenExpired` event.
Metadata declares that event's channel, miner, refunded and failed-ack fields.
Metadata is not execution proof or a guarantee of the current amount returned.

The exact historical metadata bytes hash to
`91294eb61225c4de7459e6a8fed3c37169a2c8a1b1906b46a5890d5e0d328238`.
The call was located by decoding that metadata, not by treating an absent
method on a historical API decoration as an absent runtime operation.
The original diagnostic's null decoration lookup is superseded by this
decoded call evidence. RPC metadata/state/canonical-finalized claims remain
trusted inputs; independent consensus was not verified.

The unchanged [published SDK 0.6.0](https://registry.npmjs.org/@flop-labs/sdk/-/sdk-0.6.0.tgz)
also contains the path:

- `dist/compute-channel/chain.d.ts:187`: `expireForceOpen(channelId)`.
- `dist/compute-channel/chain.js:299`: submits that method for the existing
  channel and parses `ForceOpenExpired` into refunded/failedAcks/transaction.
- `dist/compute-channel/direct-session.js:85`: the recovery loop invokes it
  when finalized state is `PendingAck` and the sampled block exceeds the
  original acknowledgement deadline. It uses `timeout` for an expired `Open`.

| Verified SDK bytes | SHA-256 |
| --- | --- |
| npm archive, SHA-1 and SHA-512 integrity matched against fresh registry metadata | `2a4a8888db2a814e401f58c9c89df327494188b80f31f8625862d312258ff610` |
| `compute-channel/chain.js` | `6de467441d45e6a908d6938129b11f2b7b920a943a5757dde6cfc9d2eafda95e` |
| `compute-channel/chain.d.ts` | `608936243b95319bfa9577f62fd52a2dbc0db12e30ca989cc4b440f127601c08` |
| `compute-channel/direct-session.js` | `1a6af4ec4be8ed7e46a52eed24bc9abc7d7a9685d37a4d1d1570e4c83fa52f74` |

Each local module was compared byte-for-byte with its archive member. The
released compatibility guard admits spec 1014020 and rejects six adjacent
invalid/unsupported controls, without modification. That is guard admission,
not full client qualification. The CLI was not executed. We do not infer why
the reporter's client left this channel pending, or claim that it ran this
particular SDK recovery loop.

The operation's existence answers the missing-path question. Its successful
execution on this case, final transaction/event, exact refund, fee and counter
effects remain unverified. No competing issue, recovery transaction, automatic
retry, new wallet or funded reproduction is proposed. Worker-wide scan timing
in [issue 282](https://github.com/flop-labs/network/issues/282) is a separate
investigation and was not reproduced by querying these two records.

## First-session planning consequence

The proposed first useful session has a 120-second observation limit. The
reviewed direct-session implementation may keep observing acknowledgement or
recovery state after that window and can submit a later cleanup transaction.
Its public options do not expose an overall observation deadline/cancellation
control. A caller-side timeout alone does not cancel the ongoing operation.

Before selecting this route, establish how the actual client stops further
writes, persists the original channel intent and obtains read-only recovery
evidence. Any authorized later expiry/finalization must have its own explicit
fee/side-effect allowance within the approved session plan. Neither abandoning
a process nor refunding escrow reverses fees or miner availability counters.
This is a client/approval gate, not a reason to test it through a paid session.
Testnet launch, owner mapping and the original-identity/history gates remain
unmet. Devnet observations do not establish airdrop credit.
