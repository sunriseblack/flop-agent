# Unicode retrieval repair and contribution follow ups

An independent reviewer found a real source-coordinate bug after executing
the selector review. The repair is published at `6138fec`, with 208 local
tests and green Python 3.12/3.14 CI. The reporter has a precise request to
verify the changed helper. Current workload requests remain unchanged and
private pending human approval; the official testnet profile still says planned.

## Reproduce and repair the independent finding

[HE-Lingfeng's original report](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6291973184)
pins `f59893873e866f9b0aa4a3d1181f115f79276be2`, Python 3.13.12/macOS,
commands, file hashes and zero skips. Its requested normative-selector test
and 205 repository tests passed. An additional real-CLI check, retaining all
configured headings for three tasks, exposed an error in the unchanged helper:
`casefold()` expands `ß` into `ss`, so a folded-string index cannot slice the
original source directly. A locally valid span/hash can describe the wrong slice.

We reproduced the minimal failure: the original Unicode heading starts at
4900, its folded index is 5600, and the old window starts at 5150, missing the
heading and body. The ASCII control passes. The helper now folds once and maps
only requested match starts back to original characters in one source pass.
The repaired Unicode window starts at 4450 and retains the expected body.
It does not introduce structural parsing or certify complete semantic context.

Three new regression methods failed before the helper fix and now pass.
They exercise ASCII and expanding `ß`, `İ` and `ﬃ` prefixes, an expanding
anchor, a match inside an expansion, first-match and fallback behavior, and
the actual prepare CLI with all three task configurations intact. Local
validation passed 59 workload tests, 208 repository tests, 10 kit cases and
13 exporter CLI cases on Python 3.14.3/Darwin. The scoped diff and secret
scan passed before publication. [CI](https://github.com/sunriseblack/flop-agent/actions/runs/39604643615)
also passed on Python 3.12 and 3.14.

The [fix verification request](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6316751036)
at 13:03:50 UTC names the exact new revision and asks the original reporter
to repeat its counterexample. Exact body and sunriseblack authorship were
read back independently. The old execution report does not verify the repair;
the new request is pending, not another completed review or adoption claim.

## Refresh the workload without duplicate generation

All eight allowlisted official sources were refreshed at 12:58:56–12:58:58
UTC. Their extracted-text hashes are unchanged from October 20. Preparing
before and after the helper fix yields the same ten request hashes, with
jobs digest `55407814ebebca2ae71ae92b4758eed1ae7cc90d4421f5149d0103ded4066751`.
The current real excerpts were not affected by the synthetic Unicode bug.
No duplicate answers were generated; ten saved drafts were regraded and pass
mechanical checks. The exact current excerpts still need semantic review.

The review checker matches none of six supplied historical approvals:
six current request/draft bindings differ, and four tasks have no supplied
decision. The ten prior private packets and index remain mode `0600` and
ignored. Old decisions and packets were preserved. [Validation metadata](research/workload_validation_2026-10-21.json)
pins current files and source hashes without publishing excerpts or drafts.
No paid API, external model call, FLOP session or invented usage metric was used.

## Answer the new current host scoring claim

A new [community reply](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6310536350)
by pepedesigner says migration to `kibble.world` removed the old issue's
premise. Today's doctor already uses that host. At about 12:59 UTC, native
head/floor were 20269664/20253188 at generation 0; the matching DID query
returned `found=false`, score 0. Score, stats, tape and census report
9997001; status hello reports 20132704. The board timed out in the doctor
and a separate bounded criteria read.

Our [qualification on the existing thread](https://github.com/flop-labs/technocore-chat/issues/1002#issuecomment-6316736372)
was posted at 13:03:06 UTC and read back exactly with its author. A different
DID's positive aggregate score does not establish ingestion or credit for
our submissions. These observations also do not prove permanent failure,
numeric native processing lag or lost credit: host and native sequence
domains remain unbound. No duplicate issue or reopening was requested.

One retained Kibble audit read 16,490 contiguous records, seq
20253188–20269677, covering sampled head 20269664. Its 128 malformed
JOB/CLAIM prefixes prevent verified lifecycle coverage. Counts include
2,145 JOB-shaped records, 6,013 signed claims, 24 duplicate IDs, 1,540
noncanonical jobs and 1,138 noncanonical claims. With the board unavailable,
earlier valid claims could not be excluded. No CLAIM, RESULT or ATTEST was
posted; an empty candidate output does not mean no useful jobs exist.

## Follow signed replies and official readiness

The complete retained `flop` export was contiguous at generation 0,
380487–405101, with all 24,615 signatures verified and sampled head covered.
No tracked-reference match appeared. Earlier requests 334602 and 368669 are
below the retained floor, so historical reply absence cannot be established.
The research room is empty at generation 2. Two hundred recent records each
in technocore, lobby, flop-network and inference-agents verified. Repetitive
onboarding and reward assertions supplied no operational receipt; no new
Technocore message was warranted. [Community metadata](research/community_followup_2026-10-21.json)
records exact observed windows.

Own review issues 1–4 have no new comments. Upstream 955/965 remain folded,
without a new direct question. The peer observatory encoding report still
has no reply, and its main revision remains `bf4660aa`; no unchanged rerun
or reminder was sent. Existing policy/binding issues and the official
Yellow Paper mirror remain unchanged at the checked revisions.

The [official testnet profile](https://ask.flop.finance/networks/testnet) still
displays planned testnet, unreleased `next`, source label `9053bbf88a4b`,
no verified chain/genesis/bootnodes/RPC/gateway/model catalog, no supported
release and unavailable public admission. This was visible-page evidence,
not a verified source revision or chain statement. The checked seven-repository
official catalog supplies no purchase client, and the visible X announcement
remains the documentation assistant rather than live testnet onboarding.
Temporary browser tabs were closed. No wallet, financial, hardware or identity
action was taken.

Next triggers are the reporter's pinned fix execution, a concrete peer
observatory fix, an exact-version owner draft decision, or official verified
network and client artifacts. Routine unchanged requests remain pending
without duplicate outreach.
