# Draft public document readiness checks 12 October 2026

The source-pinned workload produced eight draft answers from seven official
public documents. All eight passed request-version, citation and structural
checks, including two required abstentions. The AI author checked the claims
against the supplied excerpts; human semantic review is still required.
These are local Codex-session outputs, not paid FLOP inference or allocation
evidence. Source hashes and retrieval times are retained with the run.

## Attribution and collection requirements

A Technocore signature authenticates the room, nonce and stored text for its
public key, not a person's identity, honesty, or server-assigned sequence and
timestamp. Preserve those signed fields and inspect server provenance
separately. [Authentication reference](https://technocore.chat/auth.md).

The repository's `read_messages` implementation scans from the newest
records and stops at the requested limit. A client must not assume `since`
provides the complete interval after its previous cursor. Require the first
new sequence, adjacent continuity, generation and intended head coverage;
use the retained export for backfill and record irrecoverable gaps. The
snapshot of repository code is not a deployed-revision attestation.
[Source implementation](https://github.com/flop-labs/technocore-chat/blob/main/src/store.py),
[service manual](https://technocore.chat/llms.txt).

## Testnet demand and allocation boundaries

The testnet draft credits agents for settled compute purchases, aggregates
common-control wallets and excludes circular or self-directed demand. It
does not make faucet holdings or chat activity sufficient. Final operating
rules and activity floors must be verified at launch.
[Testnet draft](https://flop.finance/testnet/).

The airdrop page's proposed three-to-one mechanism releases part of an
already granted locked allocation through later inference spending. It is
not a conversion rate from testnet tokens to a genesis award. The agent
grant is described as initially non-liquid.
[Airdrop draft](https://flop.finance/airdrop/).

The agent overview still leaves release timing open, while the airdrop
page provides unlock mechanics. A useful correction would synchronize both
pages to a named specification edition and distinguish proposed policy
from deployed behavior. This discrepancy already overlaps the open
[edition-sync issue 127](https://github.com/flop-labs/yellowpaper/issues/127);
no duplicate correction issue was posted.
[Agent overview](https://flop.finance/intro/agent/).

## Evidence required before claiming readiness or an award

Protocol requirements are not implementation proof. Check Appendix H and
the linked code, verify the deployed revision and grant state, and reconcile
a particular allocation against finalized chain state, the owner allocation
file, conversion parameters and their hashes.
[Website Yellow Paper](https://flop.finance/intro/yellowpaper/).

The supplied documents do not establish an exact wallet address bound to our
DID or an exact guaranteed individual award. Both workload questions
therefore abstained. Official binding evidence, final rules, attributable
settlement history and the published owner snapshot are still required.

## Reproduction and review

Use [the workload guide](../INFERENCE_WORKLOAD.md) to collect fresh sources,
prepare the eight tasks and import draft responses. Raw snapshots and
unreviewed outputs remain in the ignored local cache. Exact quote matching
does not establish semantic entailment: a dedicated negative test deliberately
allows a false claim with a real quote through mechanical checks while
preserving the mandatory semantic-review gate. The transport and settlement
adapter remains gated on verified official launch details.
