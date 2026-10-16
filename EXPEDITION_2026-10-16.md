# FLOP peer review closure and draft review export 16 October 2026

The changed request-contract validator now has an independent execution report.
Its extra cases are preserved as regressions. The workload also has a private
human-review export, used for one updated money-path draft after the official
website changed. All 176 local tests pass; no inference purchase or allocation
is claimed. The owner subsequently approved the exact exported answer; the
decision is recorded separately from the immutable draft packet.

## Close the completed review round

[HE-Lingfeng's original report](https://github.com/sunriseblack/flop-agent/issues/2#issuecomment-6194863955)
was published October 15 at 14:45:45 UTC against `71dc3aa`, on Python 3.13.12
with cryptography 46.0.5. It reports all 40 workload tests passing, six malformed
input cases rejected in 18 actual grade/compare CLI invocations with no output
files, and two positive input controls passing four CLI invocations. The stated
implementation hash matches the reviewed Git revision. No new defect was found
within that scope, and the reviewer explicitly completed a one-off review.

Two new regression tests reproduce the 18 negative and four positive cases
through the CLI main entrypoint with actual temporary files. [Commit ca4f7d8](https://github.com/sunriseblack/flop-agent/commit/ca4f7d8ee64763ba601b4be47559166e79ceafa7)
passed 167 tests and [CI](https://github.com/sunriseblack/flop-agent/actions/runs/38905001958).
Our [acknowledgement](https://github.com/sunriseblack/flop-agent/issues/2#issuecomment-6216162955)
at 13:07:00 UTC was read back exactly. No unchanged rerun was requested.
[Review metadata](research/peer_reviews_2026-10-16.json) pins the report and scope.
This is peer-reported execution, not observation of the reviewer's machine,
continuing adoption or approval of model answers. The new export described below
was not part of that review. Issue 1/965 had no new reply; Robotbot69's saved-board
retest on 955 remains pending.

## Advance the human review handoff

`docs_workload.py review-packet` exports one mechanically passing draft as inert
private `.txt` data. It includes the question, answer, exact quotes, source hashes
and offsets, human rubric, and all supplied excerpts, including uncited context.
Each excerpt appears once. Request, draft and bundle hashes distinguish changed
answers to the same question. Export never records human acceptance.

The output guard permits only `.txt` files under the real `.private/workload`
directory, rejects public/HTML/symlink-escaping destinations, bounds output to
8 MiB, and refuses overwrites. Model and source strings remain escaped JSON
literals rather than active markup. Tests cover these boundaries, invalid and
ambiguous responses, abstention, uncited conflicting context, and distinct draft
hashes for different answers to the same request. Nine new export tests bring
the repository to 176 tests, including 51 workload tests; the ten-case kit runner
also passes.

[The final export revision](https://github.com/sunriseblack/flop-agent/commit/0abbdb6fa28cd3a9baaea48df3cd5dae3a73ff9d)
is published after diff review and secret-pattern checks. [CI run 38906442612](https://github.com/sunriseblack/flop-agent/actions/runs/38906442612)
is green. The guide and daily routine now require review of the exact request
and draft, not just a successful export. No claim of independent review is made
for this new feature.

## Refresh changed official sources

Eight allowlisted sources were refreshed at 12:58:32–33 UTC. Extracted text changed
in the Airdrop page and website Yellow Paper; six other texts were unchanged.
The website now describes an 85/15 settled-payable fee split with the audit pool
funded within the validator leg, and R8.7 now includes finalized minted miner-leg
block rewards in miner unlock credit. The public repository mirror still points
to October 13 commit `70e691c7`, so the dated zero-audit fixture notes must not be
silently treated as conformance evidence for newer website rules.

Six of nine request hashes changed. The existing money-path question and rubric
were refined to compare those editions explicitly; the suite remains nine tasks.
One AI-authored manual draft passed exact-citation/schema checks, then received a
private review packet. Its request hash is
`1e952713560fe850b90a1434773941698c0ce0923c89271f339f12399447602d`, and draft hash is
`32637c6de1f690df22d75bda6933a8f86d7776be9a936af914af905a6d49825e`.
The five other changed requests have no new accepted outputs. Three unchanged
requests were not regenerated. [Validation metadata](research/workload_validation_2026-10-16.json)
records hashes, retrieval times and the later user approval; source
snapshots, prompts, drafts and the packet remain ignored/private. The author had
the rubric visible, so this is not a blinded model benchmark.

Relevant policy/binding issues 31, 32, 123, 127 and 133 remain open with no newer
substantive update than the previous check. Existing issue 79 already qualifies
the older gross/net distinction; no duplicate protocol issue or runtime-fork
claim was opened. Testnet/airdrop terms remain drafts and the official public
catalog still has seven repositories, with no newly identified purchase client.
The visible official X profile's new post reiterates capped own-wallet spending;
the KOL item is still a preview. Neither supplied operational onboarding. No
application, wallet, funding or promotional action was taken.

## Reconcile a material Kibble follow up

[pepedesigner's new issue 955 comment](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6194200602)
reported absent engine fields on the current host. Our initial doctor timed out
on status but observed stats-origin cursor 9997001 and `stats_engine_warm=true`.
A bounded follow-up read at 12:59:35 UTC again found those qualified stats paths;
status returned at 12:59:40 UTC with `flybrain_hello.last_seq=18783737`.

The [public observation record](research/kibble_field_observation_2026-10-16.json)
pins URLs, collection times, response-body hashes, headers and exact paths. Both
responses said no-store/DYNAMIC; those headers do not establish that the
underlying projection advanced. Our [technical reply at 13:07:01 UTC](https://github.com/flop-labs/technocore-chat/issues/955#issuecomment-6216163219)
was read back exactly and preserves the unresolved cursor-domain/liveness
contract. No later substantive reply was visible at the final check. Neither
the differing responses nor a warm flag establish scorer recovery or account
credit, and no submission was replayed.

The initial doctor observed native head 18871084, retained floor 18854361,
generation 0, matching queried DID, and `found=false`, score 0. The board's
maximum job sequence was 9998999; stats/board/score reported 9997001. Board tape
bounds were 18848990–18849189. Diagnostic health stayed false. One full retained
Kibble audit verified 16,957 contiguous signatures, seq 18854361–18871317,
covering sampled head 18871315. It counted 2,043 JOB-shaped records, 7,050
claim-shaped records, 1,435 noncanonical jobs, 2,519 noncanonical claims and
23 duplicated IDs, with no tape-unclaimed candidates. No CLAIM/RESULT/ATTEST
was posted.

## Signed community follow ups and next gates

The `flop` export was contiguous from 335911 to sampled head 364129, generation 0:
28,217 signatures verified, two records lacked stored signatures, none were
invalid. Two signed messages, seq 358001 and 359157, referred to the earlier
polling question 356001 and discussed 429 waits; neither came from the original
questioner or referred to our reply 356030. They do not prove use of our advice
or resolution of the earlier 408. No response was manufactured or request
reposted. The research room was empty at generation 2. `technocore` supplied
197 verified and three unsigned records in its latest 200; `lobby` supplied 200
verified records. No invalid signatures appeared in these tails.

Next: use the approved draft within its pinned-source scope, inspect substantive
replies rather than repeating outreach, and refresh
website-versus-mirror evidence before interpreting future fixtures. Only enable
a bounded test-token session after the official network/client/faucet,
owner/delegate attribution, independent miner and final terms are verified.
No real funds, paid model API, additional participant identity, live FLOP
session, airdrop credit or finished-contest activity occurred. Actual token
usage and draft latency were unavailable; no target volume is claimed as spent.

## Owner approval of the exact draft

At the subsequent handoff, the repository owner directly approved the linked
money-path draft. The decision was recorded at 16:02:30 UTC against request
`1e952713560fe850b90a1434773941698c0ce0923c89271f339f12399447602d`, draft
`32637c6de1f690df22d75bda6933a8f86d7776be9a936af914af905a6d49825e`, and packet
`8dd3f8bda549a5cfac6a4870f6e3f67edba71a24a17aedc124ef3cb825a6995f`.
The original packet remains unchanged; a separate ignored receipt preserves
the direct decision. Its SHA-256 is
`f0a17dfd813c572a1bd9b4b078bf985bf612e696a9a2ec86f6641c01682a20bc`.

This is owner content approval, not independent review. No reasons or itemized
rubric assessment were supplied, so neither is invented. It does not approve
the other changed outputs or authorize funds, wallet actions, paid API use or
a FLOP session. The source snapshots and model traces remain private.
