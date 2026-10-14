## Scope

Independent execution review of the offline workload bundle validator and
request comparator at commit `55e295fc1e67f1f44da2f3edc39ba50e6c71f0a6`.
This is separate from the ten-case submission-evidence kit review in #1;
that implementation and its previously reviewed hash are unchanged.

I found a local counting defect: a bundle with the same task twice and a
recomputed `jobs_sha256` allowed one response to be counted as two mechanical
passes. The fix validates unique task and excerpt IDs, Boolean evaluation
flags, request hashes and context budgets before grading or comparison.
The comparator distinguishes changed requests from changed review rules and
never treats a matching request as proof of an existing or accepted response.

## Reproduce without keys or model calls

```bash
git clone https://github.com/sunriseblack/flop-agent.git
cd flop-agent
git checkout 55e295fc1e67f1f44da2f3edc39ba50e6c71f0a6
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -p test_docs_workload.py -q
```

The 32 workload tests run offline after dependency installation, using
synthetic public text and temporary files. No source download, model API,
signing key, wallet, FLOP session or private cache is required.

@HE-Lingfeng Your packet-boundary review was useful. If you take this new
scope, please report the pinned revision, Python version, command and actual
test summary, plus one extra adversarial case. Useful negatives include two
different request hashes under the same task ID, duplicate excerpt IDs, or
a changed abstention rule with an unchanged request. A changed request plus
a changed rubric must still request a new draft rather than imply cache reuse.

Passing these checks is not human semantic review, source authenticity,
FLOP settlement or a contribution-credit attestation. Please include only
public or synthetic fixtures, not keys, credentials or private outputs.
