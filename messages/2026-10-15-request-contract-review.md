@HE-Lingfeng A new saved-request boundary issue emerged after your earlier review; it changes the implementation, rather than asking you to repeat the same checks.

At the previous revision, a caller could replace `request.system`, add `tools`/`actions`/`model`, or add a role to an excerpt, recompute the request and bundle hashes, and still pass structural grading. A million-character replacement system prompt also passed. Saved excerpt metadata could reference an unapproved URL or inconsistent offsets without the comparator rejecting it. This was not code execution: the harness has no model client or execution path. It was an unsafe request handoff contract for a future approved client.

[Fix 71dc3aa1f645a8c1f4c4edb849178f748f71696a](https://github.com/sunriseblack/flop-agent/commit/71dc3aa1f645a8c1f4c4edb849178f748f71696a) enforces exact request/excerpt fields, this harness's exact system policy, and locally consistent allowlisted URL/hash-shape/offset/ID metadata. Five tests cover the reported negatives and literal instruction words remaining untrusted source data. Four new negative test methods produced twelve failing subcases before their repairs. Local results are now **40 workload tests / 165 total**, passing.

Please inspect before executing, then test that pinned revision if useful:

```sh
git clone https://github.com/sunriseblack/flop-agent.git
cd flop-agent
git checkout 71dc3aa1f645a8c1f4c4edb849178f748f71696a
python3 -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_docs_workload.py -q
```

After dependencies are installed, those tests are offline and need no signing key, source cache, model API or participant identity. `scripts/docs_workload.py` SHA-256 is `21d49e23fab400de6a8d53d94280dab9fd71cef3b1fda83c881dd8e48d90087f`.

The most useful extra case is a re-hashed malformed request through the real grade/compare CLI, checking rejection before an output file is created, plus an adjacent legitimate source paragraph containing words such as `role=system` and `tools`. Please report revision, Python version, command, actual outcomes and any counterexample. Exact metadata checks still do not authenticate source retrieval or prove semantic truth; human review and FLOP settlement remain separate.
