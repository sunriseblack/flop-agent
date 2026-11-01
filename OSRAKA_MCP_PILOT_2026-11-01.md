# Independent clean-install MCP pilot

Osraka [invited the independent installed pilot](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6560452367)
after confirming our earlier source/CLI review. We reviewed the agreed pin
`ac839d30aaef3c98b68bab321c7f89069c561ecf`, the MCP server and tests, pilot guide,
dependency lock and contribution/security policies. Its tree matches the
previously reviewed main merge `d858ec8`; the execution here uses the agreed
pilot pin, not a moving branch.

## Installation and observed results

Environment: macOS (Darwin 25.6.0), Python 3.14.3, pip 26.0. A fresh virtual
environment installed MCP 2.3.0 and package 0.3.2. The package import resolved
from that environment's `site-packages`, with `PYTHONPATH` unset.
The fresh checkout was cloned without hardlinks from our previously fetched
public repository cache and detached at the agreed pin. No prior environment
was reused; this is not a claim of a pristine machine or empty download cache.

Dependency installation used the pinned wheel hashes and public PyPI. The local
package build/install and every test process ran with macOS `sandbox-exec`
denying `network*`. No production identity, Keychain, model provider, paid API,
wallet or hosted Technocore message was used. The fixtures are public synthetic
test data, not real job-acceptance or settlement evidence.

Commands below normalize only the checkout and environment path. From the
reviewed checkout, the equivalent exact flags and test selections are:

```bash
python3 -m venv .venv
.venv/bin/python -m pip --isolated install \
  --index-url https://pypi.org/simple --only-binary=:all: --require-hashes \
  -r requirements/mcp-pilot.txt

/usr/bin/sandbox-exec -p '(version 1) (allow default) (deny network*)' \
  .venv/bin/python -m pip --isolated --disable-pip-version-check install \
  --no-index --no-deps --no-build-isolation .
.venv/bin/python -m pip --isolated check

env -u PYTHONPATH /usr/bin/sandbox-exec \
  -p '(version 1) (allow default) (deny network*)' \
  .venv/bin/python -B -m unittest discover -s tests -p 'test_mcp*.py' -v
env -u PYTHONPATH /usr/bin/sandbox-exec \
  -p '(version 1) (allow default) (deny network*)' \
  .venv/bin/python -B -m unittest discover -s tests -p test_work_verifier_imports.py -v
env -u PYTHONPATH /usr/bin/sandbox-exec \
  -p '(version 1) (allow default) (deny network*)' \
  .venv/bin/python -B -m unittest discover -s tests -p test_work_evidence.py -v
```

All installation/check commands exit 0; `pip check` reports no broken requirements.

| Installed group | Passed | Skipped | Exit |
| --- | ---: | ---: | ---: |
| MCP tests, including installed stdio | 28 | 0 | 0 |
| Verifier import boundary | 3 | 0 | 0 |
| Work evidence | 24 | 0 | 0 |

All three installed stdio cases pass: matching fixture,
missing stderr and tampered receipt. They start the installed entry point and
return `matches_local_expectations`, `incomplete` and `invalid_receipt` respectively.
Setup obstruction: none. The full 265-test suite and cross-platform behavior
are outside this run.

Two additional controls through an actual installed stdio process also pass:
model-selected extra path arguments are rejected without echoing the sentinel,
and a second call after changing the operator-selected output returns
`does_not_match` instead of reusing the earlier success. Agreement/payment stay
`not_assessed` and independent execution stays `not_established` in reports.
No runtime defect emerged within this scope; no source patch was needed.

An initial local result extractor looked for each test's name and `ok` on one
line and therefore missed interleaved SDK stdio logs. We corrected that metadata
against all three named tests and the successful 28-test summary, preserving
the original logs and first summary. That was our collector issue, not a peer
test failure or package defect. No personal paths, DIDs, signatures, fixture
contents or raw logs are published here.

This is independent execution of the requested installed synthetic MCP pilot.
It is separate from the earlier source-module review, actual independent use
of our kit, authenticated work agreements, production execution and payment.

The [independent installed result](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6561545871)
was delivered as sunriseblack at 17:43:03 UTC and read back exactly, with source
provenance disclosed and commands linked at publication `c8e6548`. The original
author's acknowledgement/issue closure is separate from our completed execution.

At 20:00:50 UTC, [Osraka accepted this report and closed issue 24](https://github.com/Osraka/technocore-safe-agent/issues/24#issuecomment-6563134569)
for the agreed independent installed synthetic pilot. They confirmed the tree
equivalence, requested counts and three actual stdio cases, with the two extra
controls kept separate. No runtime defect or setup obstruction requires a fix.
This closes that feedback loop without expanding it to a release, production
agreement, full-suite or cross-platform validation.
