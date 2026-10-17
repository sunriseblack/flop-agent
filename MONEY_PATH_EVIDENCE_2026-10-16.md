# What the public money path fixtures establish

Source edition: 16 October 2026, collected at 12:58 UTC. This answer concerns
this repository's existing agent identity, not another participant's account.

## Approved answer

No finalized inference or allocation for this agent is established. The notes pinned to 70e691c7 describe five landed accounting fixtures and ten pending alternatives. A public structural-check pass is not execution of the private pallet's amount-transition checks. The landed mock fixtures use a zero audit split and begin and end with zero public work credit; they do not ratify a live audit carve. The current website draft's R12.1a instead specifies an 85/15 split of settled payable between the miner and validator pool, with the audit earmark funded within the validator leg. Treat this as an edition/scope difference, not proof that the older fixtures test the newer policy or that any deployed runtime implements it. Operational verification still needs an attributable finalized session, independently operated miner, useful consumed output and appropriate proof; account allocation requires the finalized Era-T record and the published owner allocation/parameter evidence specified by R8.5. None of that individual session or allocation evidence is supplied here. Do not infer an award from valid corpus JSON or draft protocol text.

## Sources and their scope

The [money path notes at the pinned October 13 revision](https://github.com/flop-labs/yellowpaper/blob/70e691c758e53eed17a016a02b0a2ae1200d3744/evidence/money-path-v1.md)
support the fixture counts, mock accounting scope, and distinction between the
public structural checker and the private pallet runner.

The [website Yellow Paper](https://flop.finance/intro/yellowpaper/) supports the
R12.1a fee-split and R8.5 allocation-evidence statements in the collected
edition. It is a mutable draft, not an immutable deployment record. The source
pins below identify the text used for this answer, not later website versions.

| Source | Collected at UTC | SHA-256 of extracted text |
| --- | --- | --- |
| Pinned money path notes | 2026-10-16 12:58:33.114773 | `3eeab513ab6353c057c5c756be003f00f858b4b4d17c8387585c10db7c1a32c1` |
| Website Yellow Paper | 2026-10-16 12:58:33.221038 | `ea09eaae1e40c7408da144d68d18929b82f828e66d5028536d6b4b3df399c5d3` |

## Review record

The repository owner approved this exact AI-authored answer. This is not an
independent review or a blinded model benchmark. The answer above preserves
the approved wording; private source snapshots, prompts and conversation
receipt are not published.

The request SHA-256 is
`1e952713560fe850b90a1434773941698c0ce0923c89271f339f12399447602d`.
The canonical response SHA-256 is
`32637c6de1f690df22d75bda6933a8f86d7776be9a936af914af905a6d49825e`.
The [validation metadata](research/workload_validation_2026-10-16.json)
records the mechanical checks and scope of approval.
