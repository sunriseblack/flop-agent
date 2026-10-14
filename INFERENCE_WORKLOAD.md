# Public document inference workload

The workload turns public FLOP and Technocore documents into source-backed
answers, protocol requirements and draft documentation corrections. Nine
tasks cover message attribution, retained-window collection, testnet demand,
allocation versus unlocking, conflicting editions, implementation evidence
and money-path conformance scope, plus two questions that require abstention.
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

The harness is a bounded single-step context/model/import/review loop, not
an autonomous action agent. It needs no compaction because each task has a
small fixed context and independent durable files. The operational trace
is the source snapshot, prepared request/hash, imported response and review
result. No hidden reasoning is collected.

## Testnet launch gate

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
