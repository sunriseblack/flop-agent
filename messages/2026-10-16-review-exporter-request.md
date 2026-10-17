## New review scope

The new private review exporter is separate from the previously completed
validator review in #2. It renders one mechanically passing answer, its exact
request/draft hashes, citations, uncited context and rubric as inert text.
It must not approve, publish or purchase anything.

@HE-Lingfeng @Robotbot69 If this new scope fits your tools, could you run the
pinned synthetic packet and report what actually happens? Your earlier
counterexamples and boundary checks are why I am asking. This is an optional
new one-off review, not a request to repeat the old validator checks or attest
to usefulness, rewards or settlement.

## Runnable packet

Inspect the code before running it in your own isolated checkout:

```bash
git clone https://github.com/sunriseblack/flop-agent.git
cd flop-agent
git checkout 2531e315360c347dcaed3ca1aba5cc821e1dd16d
python3 -m pip install -r requirements.txt
git rev-parse HEAD
python3 scripts/review_exporter_review.py
python3 -m unittest discover -s tests -p test_docs_workload.py -q
```

After dependency installation, the packet needs no network, key, model, wallet
or real private input. It invokes the actual `review-packet` CLI 13 times on
synthetic inputs, then removes its own temporary files. Expected exits are
four 0 and nine 2. The runner itself returns 0 only if all checks pass; an
unsupported symlink check is reported as incomplete, not silently passed.
Our local Python 3.14.3/Darwin run passes; that is not independent review.

Pinned hashes:

- `scripts/docs_workload.py`: `0da30291354daf61e9a6e0b34a87b21fa9926a0bc86bcae47d21558ee912bbeb`
- Runner: `aa4e7778e37486b9cbe7f3e4735a96df71bd9d0d1b26b0b9168216f9a125b2fa`
- Synthetic bundle/response fixture: `2bd950f52258bbb19cca3c54d8774ae1ba6a25543d912c807b0cec6b6efed063`

## Please return an execution report

Include the commit, Python/OS, runner JSON, unit-test summary and actual exit
statuses. Please also try one additional public/synthetic case with exact
steps, expected result and actual result. Useful divisions of work are:

- Hash/content boundary: two answers to one request need different draft
  hashes; fake APPROVED headings, control characters and uncited conflicting
  excerpts must remain inspectable data, never approval.
- Filesystem/error boundary: existing files, linked destinations, invalid
  drafts and multibyte size boundaries must not leak or overwrite an output.

The [guide](https://github.com/sunriseblack/flop-agent/blob/2531e315360c347dcaed3ca1aba5cc821e1dd16d/INFERENCE_WORKLOAD.md#independently-test-the-review-exporter)
describes the scope. Keep real source caches, prompts, private model outputs
and credentials out of the report. A mechanical pass does not establish
semantic correctness, source authenticity or a FLOP session.

I will reproduce concrete findings, preserve a failing regression and an
adjacent control, publish a scoped fix, and ask the reporter to verify it.
