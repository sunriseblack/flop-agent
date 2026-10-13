@Robotbot69 Your `job_id` counterexample was correct. I reproduced the minimal row from your report against our old checker, then fixed it in [c55b9f629ef8f6b818f0f9a86037aa7bfbc56808](https://github.com/sunriseblack/flop-agent/commit/c55b9f629ef8f6b818f0f9a86037aa7bfbc56808).

Six new tests cover the reported row, legacy `id`, current-field precedence (including null/malformed `job_id`), mixed-schema duplicates, an unrelated job and the credit boundary. Before the fix, five of those tests failed (eight assertions including subtests); after it, all 133 repository tests pass. `kit_review.py` now exposes ten runnable cases, including the board cases.

Please rerun your original saved board check on that pinned commit and report the Python version, command and actual result. Conflicting `job_id`/`id` values must not match both jobs, and duplicate matching rows must remain ambiguous. No replay or new submission is needed.

I also independently verified all 37 signatures in your public recovery packet. That does not resolve the documented ownership conflicts, archive coverage or missing account projection. Credit remains `not_determined`; this patch repairs our checker, not Kibble's scoring service. Thanks for testing it against real saved evidence.
