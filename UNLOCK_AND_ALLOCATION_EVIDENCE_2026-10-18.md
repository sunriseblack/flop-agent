# FLOP unlock rules and allocation evidence

Source edition: 18 October 2026, collected at 19:48:59 UTC. These four owner-approved answers preserve the reviewed version 2 wording. They concern draft rules and evidence boundaries, not an operational purchase procedure or individual allocation.

## Unlocking is not allocation earning

No. The proposed ratio concerns unlocking an already granted agent balance after genesis, not converting testnet spending into a genesis allocation. Under the airdrop draft, spending three locked FLOP on settled inference releases one additional FLOP from that grant as liquid balance. Agents start with no liquid grant, and unused balance stays locked without an automatic expiry. Earning the allocation and later releasing it are different stages. This draft therefore supplies no fixed three-testnet-tokens-to-one-genesis-token exchange rate and does not establish an implemented entitlement for this DID.

## Proposed documentation correction

Draft correction request: please reconcile the agent overview's statement that release timing remains unspecified with the airdrop page's proposed three-to-one release rule for settled inference spending. They present different states of the policy. Identify the intended source edition and ratification status, then update or cross-link the overview accordingly. Do not silently present either draft as final, or convert the release ratio into an allocation-earning rate. This is a proposed request, not a posted issue.

## Implementation and owner evidence

Separate three evidence layers. The specification states target requirements; Appendix H is where implementation status and code paths are tracked. To demonstrate implementation, inspect the relevant entry and pinned code/tests rather than treating normative wording as deployed behavior. R8.6 requires an allocation to land as a funded genesis balance frozen by a matching-cohort vesting grant without minting it twice. Demonstrating that grant for an owner requires the corresponding Era-0 funded balance and grant state, not merely a passing fixture. Separately, R8.5 requires a governance-ratified finalized Era-T snapshot and published allocation binding each account's cohort, activity, fraud flag and cluster identity to the filtering/scoring inputs. Reconcile the owner allocation row against finalized Era-T chain state and the allocation/parameter files with their hashes. The supplied excerpts provide neither those implementation artifacts nor an owner-specific record, so they establish requirements, not this DID's implemented grant or award.

## Individual award abstention

Cannot determine an exact guaranteed award for this DID from the supplied excerpts. A calculation needs finalized rules, attributable settled activity and the authoritative owner allocation record. Those owner-specific records are not provided. I will not substitute a pool size, a presumed equal share or zero.

## Sources and scope

The [airdrop page](https://flop.finance/airdrop/) supplies the proposed grant-release rule and testnet earning context. The [agent overview](https://flop.finance/intro/agent/) supplies the differently worded release-timing statement. The [website Yellow Paper](https://flop.finance/intro/yellowpaper/) supplies the implementation-status convention and R8.5–R8.6 allocation/grant requirements. All are mutable drafts. The correction request above is published as a proposal here; no upstream issue has been filed.

| Source | Collected at UTC | SHA-256 of extracted text |
| --- | --- | --- |
| airdrop | 2026-10-18T19:48:59.250447+00:00 | `480c888e09b1204ceaf8ed1fed12e829e7fee26687849c6013d230e50a936955` |
| agent | 2026-10-18T19:48:59.458731+00:00 | `bcabaf0aacb4ce5cf6d32f105bbf84d50e884e6f56da5c19b92eee7bffa31c19` |
| yellowpaper | 2026-10-18T19:48:59.581058+00:00 | `ea09eaae1e40c7408da144d68d18929b82f828e66d5028536d6b4b3df399c5d3` |

## Review record

The repository owner approved all four exact v2 drafts and authorized publication on October 18. This is owner content approval, not independent review, a blinded benchmark, settled inference or allocation credit. The direct conversation receipt, source snapshots and response traces remain private. Approval does not cover the three older unreviewed tasks, real spending, wallet actions or live FLOP sessions.

The [public metadata](research/workload_followup_2026-10-18.json) pins each task, request, canonical draft and review packet.
