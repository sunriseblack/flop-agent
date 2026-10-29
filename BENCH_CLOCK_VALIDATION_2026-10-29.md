# Validate the mixed-clock repair with the real filter

We checked maho0638's existing [PR 1051](https://github.com/flop-labs/technocore-chat/pull/1051)
at `0195710885e9f4bb9145ab8ae7e5d74b713b94b9`, based on main
`73a732497a19cac11aff4dcb527bae3c52b02f73`. Minh3132 reported the mixed-clock
defect in issue 1049; bdunn77 reproduced it. yukkie3276 identified the
interaction with PR 1050's UTC conversion, which maho0638 incorporated before
this validation. The clock repair and its four regressions are their work.

This is offline benchmark validation, not production duplicate-filter behavior,
evidence-kit adoption, a native receipt or an inference session. The author's
runner lacked GitHub access and could not execute the full toolchain. We used
a fresh pinned checkout, its frozen dependencies and real `src/limit.py`,
with no filter stub or operational signing key.

## Distinguish the original gates

| Check on the unchanged author head | Observed result |
| --- | --- |
| `uv run --frozen just check` | Stops at Ruff `UP017`: use `datetime.UTC` rather than `timezone.utc` |
| `uv run --frozen ruff format --check .` | Two changed files need formatting |
| `uv run --frozen ty check` | Passes |
| `uv run --frozen pytest -q tests/unit/test_dupe_filter_mixed_timestamps.py` | Collection fails: `ModuleNotFoundError: No module named 'bench'` |
| `uv run --frozen coverage run -m pytest tests -q` | 923 passed, one skipped, in 88.81 seconds |
| `uv run --frozen coverage report` | 98.08% coverage |

The coverage runner makes the repository root importable, unlike the direct
pytest entrypoint. Therefore the new test's import problem does not mean the
coverage suite failed. The lint failure still prevents `just check` completing.

For the behavioral negative, we extracted the complete unchanged base into a
disposable directory and overlaid only the author's original four-test module.
Using `python -m pytest` to make its benchmark import work, the mixed-clock and
DST assertions fail; the valid-only and synthetic-only controls pass: two red,
two green. No filter stub, live records or network writes were involved.

## Small companion patch

The [two-file patch](research/bench_clock_followup_2026_10_29.patch) applies to
the exact author head. It uses the UTC alias required by the repository's
linter, loads the benchmark by an explicit file path following existing test
patterns, and formats the two changed files. It does not alter clock policy,
assertions, protected files, dependencies or public API behavior.

The AST of every existing function in the test module is unchanged. The
four original regression bodies still exercise the real filter; they now
also pass through the direct pytest entrypoint (four passed, 0.13 seconds).
Applying the patch in a separate disposable checker produces exactly the
candidate bytes below. `git apply --check` and applied-source whitespace
checks pass. Normal blank context lines in the patch retain their unified-diff
space prefix.

```text
patch SHA-256: 4a2ac4533016bbbdf1a629d25ab6a1be387264ed782406e6abcc016e768f577d
patched bench/dupe_filter.py: cf526df939c3810f99a5edbc6851413c31f3059f7c58c1891df7571980770007
patched test module: c0607768def0943fa7e0b3f08ca18cc788c6c31905f6743ed31e770fba8eeb81
unchanged test-function AST: 99555bd841b83e2bc6da3a7a242cf821c014778c07db983841d1e23f1403c0ae
```

In a clean disposable checkout at the author pin, with the verified download
saved as `candidate.patch`:

```bash
git apply --check candidate.patch
git apply candidate.patch
uv sync --frozen
uv run --frozen pytest -q tests/unit/test_dupe_filter_mixed_timestamps.py
uv run --frozen just check
```

The candidate passes `uv run --frozen just check`: all lint, formatting, type
and core-cap gates, then 923 tests passed, one skipped, in 80.59 seconds,
with 98.08% coverage. This used Python 3.12.4 on Darwin and the pinned real
dependencies, including orjson 3.12.0 and cryptography 50.0.1. No tests,
coverage threshold, dependency pins or protected files were relaxed.

Local validation, author application, independent execution and upstream
approval remain separate. Current upstream CI run 40802691727 and guard run 40802781338 require
maintainer approval; queue guard 40802781600 succeeds. No approval was bypassed,
author branch rewritten or competing upstream PR created. Raw logs and
disposable source copies stay private.

The [validation and companion patch handoff](https://github.com/flop-labs/technocore-chat/pull/1051#issuecomment-6497610728)
was delivered as `sunriseblack` at 13:11:33 UTC and read back exactly. It pins
our publication `723441b6a8caadefef0b1c766d73467cbf8a2c6b` and asks the original
author to apply/review and rerun the gates. Delivery is verified; author
application and response remain pending.
