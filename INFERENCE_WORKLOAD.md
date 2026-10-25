# Public document inference workload

The workload turns public FLOP and Technocore documents into source-backed
answers, protocol requirements and draft documentation corrections. Ten
tasks cover message attribution, retained-window collection, testnet demand,
allocation versus unlocking, conflicting editions, implementation evidence
and money-path conformance scope, plus two questions that require abstention.
The October 20 task compares the agent overview's delegation invitation with
the newer operator self-stake, sponsored-bond and community-pool rules.
Outputs remain drafts until their claims are reviewed for meaning and correctness.

This first version is transport-neutral. It prepares model requests and
imports responses from a separately approved model client. It has no model
API, execution tool, signing key, wallet, payment or publication path. FLOP's
live client and settlement adapter must wait for the verified official
network and protocol. Local preparation is never counted as FLOP usage.

## Run the preparation pipeline

Use a fresh run directory; the commands never overwrite an earlier result.
The `.private/workload` cache is ignored by Git and is separate from the
existing signing identity. Only the collector performs network reads:

```bash
python3 scripts/docs_workload.py collect \
  --output .private/workload/run-001/corpus.json
python3 scripts/docs_workload.py prepare \
  --corpus .private/workload/run-001/corpus.json \
  --output .private/workload/run-001/jobs.json
```

Sources are a fixed allowlist: Technocore's `auth.md` and `llms.txt`, plus
FLOP's testnet, airdrop, agent overview and website Yellow Paper, and the
official repository's current `src/store.py`, and the public money-path notes
pinned to Yellow Paper commit `70e691c758e53eed17a016a02b0a2ae1200d3744`.
The latter separates five landed accounting fixtures from ten pending
alternatives and the public structural checker from the private pallet runner.
The October 16 website draft adds an 85/15 session-fee split that those dated
zero-audit mock fixtures do not establish conformance with. The money-path task
now asks for that edition/scope distinction explicitly.
It is a dated revision, not a live network or deployment attestation. Source code
describes that revision; it is not proof that a deployment runs the same code. The
collector blocks cross-host, HTTP-downgrade, alternate-port and credential-bearing
redirects before following them, and bounds each response to 2 MiB.
It hashes both downloaded bytes and extracted text. The text extractor
removes HTML navigation, scripts and other non-document sections without
executing them. Snapshots older than 24 hours, future timestamps, wrong
source URLs and changed text hashes block preparation.

Each job has a stable system instruction, a question, bounded excerpts with
source hashes and offsets, and a request hash. Model context is limited to
24,000 source characters per task; a suite has at most 16 tasks. Identical
questions and unchanged source text produce the same request hash, allowing
the daily routine to reuse reviewed work instead of spending on duplicates.
The task's human rubric is separate from the model request. Prepare only a
changed or new task with `--task-id`; repeat it for a subset. Selected tasks
retain the same request hashes as in the full suite:

```bash
python3 scripts/docs_workload.py prepare \
  --corpus .private/workload/run-001/corpus.json \
  --task-id money-path-scope --output .private/workload/run-001/money-jobs.json
```

Compare the freshly prepared bundle with a previous one before generating
drafts. This command is offline and never overwrites an earlier report:

```bash
python3 scripts/docs_workload.py compare \
  --previous-bundle .private/workload/previous/jobs.json \
  --bundle .private/workload/run-001/jobs.json \
  --output .private/workload/run-001/comparison.json
```

The report separates new, changed, unchanged and removed requests. Changed
abstention rules or human rubrics require regrading and review even when the
model request hash is unchanged. A matching request does not prove a saved
response exists or was accepted; `saved_response_available` stays `not_checked`
and semantic review remains required. No model client or network is called.
Refresh the corpus before preparation; comparison is not a freshness check.

Normative rule selectors use complete headings such as `R8.4 — Conversion
eligibility.`, not bare rule IDs. An October 20 document insertion put an
earlier `R8.4` cross-reference ahead of the actual rule and exposed the bare-ID
selector's wrong-section retrieval. A synthetic regression exercises the actual
three affected task configurations, with and without distant earlier references.
The fix changes task selectors, not the retrieval engine. The engine still
uses bounded first-match text windows, not a structural document parser;
humans must inspect completeness and missing context before approving a draft.
Changing source editions or selectors changes request hashes and requires
fresh preparation and review; never relabel an old approval as current.

[HE-Lingfeng's independent selector review](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6291973184)
passed the requested checks at `f598938` but found a Unicode coordinate bug
in `excerpt()`: case-folding `ß` into `ss` shifted an anchor's index before
the original text was sliced. The helper now maps folded match starts back
to original character positions in one pass. Three regressions cover ASCII
and expanding Unicode controls, matches inside an expansion, first-match and
fallback behavior, and the real prepare CLI with all three affected task
configurations intact. [HE-Lingfeng independently verified the repair](https://github.com/sunriseblack/flop-agent/issues/5#issuecomment-6320888724)
at `6138fec`: 208 repository tests passed, the original full-configuration
counterexample passed, and two distinct folded match starts inside one `ﬃ`
character merged into one exact original-text slice. That additional case is
now a permanent local regression, with 60 workload and 209 repository tests
passing; the helper implementation is unchanged. This bounded review is
complete, not ongoing adoption or semantic approval. Bounded first-match
retrieval still does not establish complete semantic context.

## Generate and import draft answers

Pass only each job's `request` to an approved model client, not the human
rubric. Use the `system` field as the instruction and the other request
fields as data. Keep excerpts visibly separate from instructions. The model
has no tools and must return one JSON object with exactly these fields:

```json
{
  "task_id": "signature-scope",
  "job_sha256": "copy the prepared request hash",
  "answer": "A concise source-backed answer.",
  "abstain": false,
  "claims": [
    {
      "text": "One factual claim.",
      "evidence": [{"snippet_id": "copy an excerpt ID", "quote": "a short exact excerpt"}]
    }
  ],
  "limitations": ["A material uncertainty, when present."]
}
```

Store the objects as a JSON array and inspect them:

```bash
python3 scripts/docs_workload.py grade \
  --bundle .private/workload/run-001/jobs.json \
  --responses .private/workload/run-001/responses.json \
  --provider manual --model current-chat-unspecified \
  --output .private/workload/run-001/review.json
```

Those labels describe a manual import, not a verified provider or a live
FLOP session. Record an actual provider/model and measured usage separately
when the chosen client supplies them. The initial harness leaves cost and
usage unavailable and settlement unverified rather than inventing them.

The checker rejects wrong task/request hashes, fabricated or wrong-excerpt
quotes, duplicate or missing answers, oversized output and unexpected
fields such as model-proposed tool actions. The wallet-binding and
guaranteed-award questions require abstention with no factual claims. All
input JSON rejects duplicate keys and nonfinite numbers; saved artifacts
are bounded to 8 MiB.

Saved bundles are validated before grading or comparison: task IDs and excerpt
IDs must be unique, abstention flags must be Boolean, request hashes must match
and the context budget still applies. Recomputing a file hash does not make an
ambiguous bundle valid. In particular, duplicating one task cannot count its
single response as two mechanically passed tasks. Hashes check local integrity,
not authentic retrieval from an official source.

Saved requests must also contain exactly the fields emitted by this harness,
with its exact system policy. Excerpts are data objects, not chat-role or
instruction envelopes. Re-hashed tool, action, model-selection or role fields,
replaced system instructions and huge alternate system prompts are rejected
before grading or comparison. Excerpt URLs must match the fixed source allowlist;
hash shapes, character offsets and excerpt IDs must agree locally. This is not
an independent match against the original complete source. A deliberate system-policy change requires
preparing a new bundle with the new harness revision, not editing saved jobs.
This guards the model-client handoff contract; it does not authenticate sources
or make arbitrary text inside the question or excerpts trustworthy.

## Review what the checks cannot establish

An exact quote can be irrelevant to the sentence citing it. A model can
also contradict its cited source while passing literal matching. The tests
include that failure: the result must remain `semantic_review: required`.
Mechanical passes are not an accuracy score, acceptance or allocation.

For every draft, use the task's human rubric to review factual correctness,
entailment, missing material limitations, draft-versus-runtime status and
whether a correction is genuinely new. Mark reviewer identity and whether
review is independent. Keep a rejected output and its failure case, then
fix the prompt, retrieval or harness and rerun the affected task with a new
version. Publish only reviewed, useful answers or correction proposals.

Export one mechanically passing draft as a private text packet for the human:

```bash
python3 scripts/docs_workload.py review-packet \
  --bundle .private/workload/run-001/jobs.json \
  --responses .private/workload/run-001/responses.json \
  --task-id money-path-scope \
  --output .private/workload/run-001/money-human-review.txt
```

The packet groups the question, answer, exact citations, request/draft/bundle hashes,
rubric and all supplied excerpts, including uncited context. Each excerpt appears
once so the human can inspect omitted conditions and conflicts without duplicate
context. Model/source strings are inert JSON literals in a `.txt` file, not active
Markdown, HTML or tool instructions. Failed selected drafts, ambiguous response
IDs and changed request hashes block export.

Output must stay inside this repository's `.private/workload` directory; public,
HTML and symlink-escaping destinations are rejected. The 8 MiB byte bound and
exclusive creation preserve earlier packets. Nothing is fetched or executed.
New packet files use owner-only `0600` permissions even with a permissive umask;
existing files are never overwritten or chmodded by the exporter.
It does not check source freshness: prepare from fresh sources first and compare
request hashes. A successful export only means `pending_human_review`; it cannot
record acceptance, an independent reviewer identity or a FLOP session. The human
must separately provide a decision and reasons tied to both the request and draft
hashes; a changed answer to the same question needs its own review.

The harness is a bounded single-step context/model/import/review loop, not
an autonomous action agent. It needs no compaction because each task has a
small fixed context and independent durable files. The operational trace
is the source snapshot, prepared request/hash, imported response and review
result. No hidden reasoning is collected.

## Independently test the review exporter

Run the synthetic peer packet through the real local CLI:

```bash
git rev-parse HEAD
python3 scripts/review_exporter_review.py
python3 -m unittest discover -s tests -p test_docs_workload.py -q
```

The runner reports Python/platform, implementation and fixture hashes, and 13
observed cases. It checks request/draft binding, uncited context, inert hostile
strings, abstention and POSIX owner-only output, then checks that malformed
inputs, public/HTML paths,
symlink escapes and overwrites fail without a new output. An unsupported
symlink check is a failure to complete this packet, not a silent pass.

All input text is synthetic, even where the schema requires an official URL
label. Nothing is downloaded or presented as official source evidence. The
runner invokes only this checkout's `review-packet` command with the current
Python interpreter; it needs no signing key, wallet or model. Temporary files
are removed after the run. It does not inspect a participant's private inputs.

For an independent report, include the exact checkout, runner JSON, environment
and an additional counterexample or platform observation. A posted request or
our own passing run is not independent execution. Keep any real private source
or model text out of the report.

[HE-Lingfeng's independent run](https://github.com/sunriseblack/flop-agent/issues/3#issuecomment-6229045181)
tested `ebd59a1` on Python 3.13.12/macOS: 13 CLI cases and 54 workload tests
passed. Additional CLI controls rejected a dangling file symlink, created a
regular file at `0600` under child umask `000`, and preserved an existing
`0644` sentinel. Those three controls are now a permanent local regression;
the exporter and runner implementation hashes are unchanged. This is a bounded
one-off execution report, not independent semantic approval or ongoing adoption.

## Inspect saved review records before reuse

`review_status.py` compares a current bundle and saved responses with explicitly
supplied decision, packet and original-review-bundle triples. It checks request,
canonical draft, packet bytes and evaluation rules. Using the original bundle
preserves a packet exported for a smaller task subset; it is not relabelled as
an export of today's full suite.

```bash
python3 scripts/review_status.py \
  --bundle .private/workload/current/jobs.json \
  --responses .private/workload/current/responses.json \
  --review .private/workload/prior/decision.json \
           .private/workload/prior/review.txt \
           .private/workload/prior/jobs.json \
  --output .private/workload/current/review-status.json
```

Repeat `--review` for at most 16 tasks, supplying one decision per task. Paths
come only from the command line, never from model/source/decision text. Inputs
and output must stay inside this checkout's `.private/workload`; JSON and packet
reads are bounded, decision records to 64 KiB. The report contains hashes and
statuses, not draft answers, excerpts or the direct approval message. New reports
are exclusive and mode `0600`; earlier reports and inputs are not overwritten.

`supplied_record_matches` means the supplied files agree. It does not authenticate
the reviewer or prove semantic correctness. A fabricated but internally consistent
record still reports `decision_authenticity: not_verified` and
`publication_authorized: false`. Verify the original human message yourself;
this tool never accepts a draft, publishes, authorizes a session or changes a
decision. A matching rejected record is not an approval. Changed request/draft,
changed evaluation rules or packet mismatch requires a new review or correction
of the supplied artifact selection, not editing an old receipt to make it pass.

Exit 0 means inspection produced a report, not that all records matched. Read
each status and binding error. Exit 2 means invalid/ambiguous input or a blocked
output, with no intentional overwrite. Source freshness and authenticity are
outside this offline check: refresh and prepare first, then compare editions.

For a synthetic, key-free execution review:

```bash
python3 -m unittest discover -s tests -p test_review_status.py -v
```

The 19 tests include real-CLI runs, a legacy-packet selection mistake,
changed drafts/requests/rubrics, tampering, fake approval text and forged records,
duplicates, missing records and private-file controls. These are local tests,
not an independent peer report or human review.

[HE-Lingfeng completed the independent checker execution](https://github.com/sunriseblack/flop-agent/issues/4#issuecomment-6266428967)
at `6bcb4690c7de7a86b4ecb709ea74138dee5f1e3a` on Python 3.13.12/macOS:
18 checker and 202 repository tests passed, with no skips. Three additional
CLI controls changed only `response.limitations`: the old saved record failed
with exactly `current_draft_mismatch`, while original and freshly rebound
synthetic records matched. All exits were 0 (inspection success, not approval),
all reports were `0600` under child umask `000`, and report text did not leak
the answer or added limitations. These controls are now one permanent
regression, reproduced locally with 19 checker and 203 repository tests.
The checker implementation is unchanged. No counterexample emerged within
this scope; one-off synthetic execution is not semantic approval, ongoing
adoption, authenticated human permission or FLOP credit.

## Testnet launch gate

The separate [readiness checker and observation ledger](INFERENCE_READINESS.md)
now implement the read-only preparation side: bounded official-document reads,
explicit missing evidence and immutable deduplicated observation reports. They
do not expand this workload's model-input allowlist or implement live transport,
owner binding, finality verification or allocation reconciliation.

The October 22 [native TCLK HTLC adapter](https://github.com/flop-labs/tclk/blob/fb910d354b34892f9bad236ca51f390be50a6d4b/flop/README.md)
is a separate devnet settlement transport, explicitly not the inference-task
HTLC API. It documents same-key Ed25519 account binding within that adapter;
this does not establish R8.4 attribution or an owner's allocation. A read-only
devnet chain-info response and another author's published escrow receipts are
not a finalized inference session by this workload. The eight-source model-input
allowlist is unchanged. Do not run its fresh-key/funding example or copy signing
material into it to manufacture readiness.

Before enabling a FLOP transport, identify the official client, chain and
genesis identity, faucet, supported model, DID/account/delegate mapping,
independent miner and finalized allocation rules. Use a bounded approved
test-token session whose output is actually consumed by this workload.
Capture session ID, owner/delegate, miner, settlement block/hash, paid amount,
proof, usage, quality review and any refund or dispute. Keep requested,
submitted, delivered and finalized states distinct, with no automatic retry
of an uncertain purchase.

The transport adapter must enforce session/cost/time budgets outside the
model and verify settlement and owner attribution before scaling. No real
funds, hardware rental, extra identity, circular demand or wallet connection
is authorized by this preparation tool. A later per-owner allocation must
be reconciled against its official snapshot and hash.

## Validation

```bash
python3 -m unittest discover -s tests -p test_docs_workload.py -v
python3 -m unittest discover -s tests -q
```

Tests cover stale and changed sources, wrong versions, missing data,
fabricated citations, abstention, output budgets, duplicate responses,
prompt-injection text remaining data, attempts to add action fields and the
gap between literal citation checks and semantic truth, including contradictory
drafts with a mechanically matching quote. Redirect tests verify denial before
the redirect-following handler is called; task-selection tests preserve request
hashes and reject unknown or duplicate selections. These are harness
checks, not measurements of a particular inference model's accuracy.
