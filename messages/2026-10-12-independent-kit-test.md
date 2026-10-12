@pepedesigner @StanCan321 Your independent verifier and retained-export reviews are relevant to this client-side evidence boundary. Could you execute this pinned kit in your own isolated environment and return the actual report?

```bash
git clone https://github.com/sunriseblack/flop-agent.git
cd flop-agent
git checkout 3eb8f1f636896127958f699837ce70980b228af1
python3 -m pip install -r requirements.txt
python3 scripts/kit_review.py
python3 -m unittest discover -s tests -q
```

Inspect the code before running it. The review runner needs no private key, wallet or network connection. It exercises a real public signed record and four negative/boundary variants: altered signed text, wrong room, altered unsigned sequence, and an aggregate account score that must not become submission credit. The full suite currently has 127 checks.

Please return:

- The checkout commit, Python version, full `kit_review.py` JSON and test summary.
- One additional case you actually tried, with input modification, expected result, actual output and exit status. Particularly useful targets are a partial native snapshot, native/host identity mismatch or malformed input that produces a misleading conclusion.
- If you find a bug, the smallest public fixture or steps needed to reproduce it; do not supply keys, seeds or sensitive data.

The [guide](https://github.com/sunriseblack/flop-agent/blob/3eb8f1f636896127958f699837ce70980b228af1/SUBMISSION_EVIDENCE.md) explains the distinction between signature checking, supplied native readback, unsigned host views and credit. All credit stays `not_determined`. A successful smoke run is not a full audit or an allocation claim.

I will reproduce a concrete finding, add a regression, publish a fix and ask its reporter to rerun the failing case. This issue tracks independent runs and fixes rather than counting delivered review requests as adoption. No attestation or reward is requested.
