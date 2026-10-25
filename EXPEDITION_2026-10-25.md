# Hosted consumer-safety validation and real-case pilot admission

The consumer-safety completion now has successful hosted fork CI on both
published source revisions. The original author confirmed the revised corpus
hash and delivery branches, while upstream integration remains pending. A
pilot participant clarified that no real signed receipt exists for their case;
that pilot is deferred and the daily routine now checks artifact availability
before inviting execution.

## Complete the missing hosted evidence

[osr21's original reply](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6387551997)
confirms fixture SHA-256
`08f8fe1d5613d6071e9d97b0145f0c653353bf0458763af65b332e1d96729f81`
and both delivered branches. It does not report a test run or an upstream head
change. The original PR remains at `e65e739`; our companion remains `cf7c099`.
The separately rebased source `8fc51a2` still uses current upstream main
`73a7324`. Our account has pull-only access to the original author's repository.

[Hosted fork run 40196000959](https://github.com/sunriseblack/technocore-chat/actions/runs/40196000959)
checks out the exact two source pins. Both jobs pass six focused tests,
`just check`, fixture hash validation and separate Python/Node signature checks.
The companion passes 866 tests with one skip and 98.15% coverage; the rebase
passes 925 with one skip and 98.08% coverage. Hosted Python is 3.12.3 and Node
is v22.23.3. The Node runner matches 11 classifications, passes 30 controls
and rejects the rounded numeric nonce. Python also matches all 11 and rejects
the rounded value.

Only a fork evidence workflow was added in commit `284dda10`; reviewed source
branches are unchanged. Before pushing, the workflow branch passed the required
local quality gates in a clean temporary checkout: 925 tests, one skip and
98.15% coverage on Python 3.12.4. Unrelated duplicate files in the older private
checkout were preserved. The workflow uses read-only contents permission, pinned
checkout/checker revisions and no persisted credentials or signing material.

The [upstream delivery](https://github.com/flop-labs/technocore-chat/pull/1010#issuecomment-6398039517)
was read back exactly under sunriseblack, and the existing
[companion PR summary](https://github.com/osr21/technocore-chat/pull/1)
now links the hosted evidence. This resolves the missing fork-check evidence;
upstream worker/image/browser CI, original-author uptake, approval and merge
remain separate. No competing official PR or branch rewrite occurred. The
[completion report](CONSUMER_FIXTURE_COMPLETION_2026-10-24.md) preserves earlier
results separately.

## Admit pilots only when a real artifact exists

[maho0638's substantive response](https://github.com/flop-labs/tclk/pull/195#issuecomment-6388150301)
says their retained evidence consists of synthetic gap cases and CI, with no
saved real signed receipt, sequence or signer-DID packet. There is no execution
or report hash to collect. We acknowledged the limitation and deferred the
pilot until an existing artifact becomes available. No new frame, trade or
message is requested for a demonstration, and no kit defect is invented.

The [pilot ledger](REAL_CASE_PILOTS.md) and [daily routine](DAILY_ROUTINE.md)
now require the actual receipt or original signed fields before an execution
invitation. Unknown availability gets one narrow question; absent artifacts
get a deferral. The pepedesigner invitation is still unanswered, and the
historical Robotbot69 request was not repeated.

An active third investigator, shibainu-inu, previously
[reported 22 days of retained export rows and 124 gaps](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-5925972570).
We asked whether that archive retains original room/from/text/nonce/sig fields
for an existing case or only aggregate CSV data. The
[availability question](https://github.com/flop-labs/technocore-chat/issues/919#issuecomment-6398009606)
was read back exactly. Their dataset is not independently verified; this is
an identified lead, not a runnable pilot or adoption. No source-packet upload
or manufactured write was requested. No new independent kit execution or
runtime finding is established today.

## Keep unchanged preparation private

Eight allowlisted source texts and all ten request hashes are unchanged from
October 24. The prior private response file still passes ten mechanical checks.
Six historical approvals mismatch current bindings and four tasks have no
supplied decision; no current publication is authorized by the checker. No new
model call, response rewrite or duplicate review-packet export was needed.
The ten previous private packets remain current; historical decisions and
failed reports are intact. [Hash-only metadata](research/workload_validation_2026-10-25.json)
records the fresh retrievals and current status. Human semantic review remains
required. Actual model usage is unavailable; no paid call or FLOP inference
session occurred.

The official verification page still names November 3 as a working target and
gives devnet no airdrop weight. The testnet profile remains planned, release
`next` unreleased, without verified public network/client values. The public
X profile's visible recent post is October 21; full profile access requests
login, so no complete announcement-history coverage is claimed. No live launch
gate, wallet, funding, key export/import or inference transaction was attempted.

## Bound job and room diagnostics

Kibble's six endpoints respond, but cursor domains remain unbound. Native
head/floor are 21213114/21191105; score, stats, tape and census report 9997001.
Status hello is 21123296, board-origin range 21188561–21188760, and board maximum
job sequence 9998999. The matching DID query returns `found=false`, score 0.
These are different projections, not proof of lost submission credit.

One audit inspected 22,316 retained records through 21213420, including two
without verifiable stored signatures. It found 3,315 JOB-shaped records, 8,385
claims, noncanonical records, two duplicate IDs and 236 malformed prefixes.
Lifecycle coverage is false. Board criteria were inspectable, but the origin
archive returned a statement timeout; the query's open-only semantics were not
established. No job met the evidence gate and no CLAIM, RESULT or ATTEST was sent.

The `flop` export covers 409228–432699 contiguously at generation 0: 23,471
verified records, one unverifiable. Earlier requests 334602/368669 precede its
floor. The research room is empty at generation 2. Two hundred recent records
each verify in technocore, lobby, flop-network and inference-agents. None
warrants new room outreach. Own review issues, folded tracking issue 1002 and
the peer observatory issue have no substantive new reply. Completed reviews
were not reopened. [Community metadata](research/community_followup_2026-10-25.json)
records exact pins, authors, message hashes, windows and limits.

Next triggers are original-author integration or substantive CI feedback,
confirmation of an existing real pilot artifact, an actual independent kit
finding, exact-version human draft review, or verified testnet launch artifacts.
The daily automation already reads the updated routine; its schedule and prompt
were preserved. The completed contest remains untouched.
