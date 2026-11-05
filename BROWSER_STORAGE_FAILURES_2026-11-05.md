# Browser storage failures

zkasuran reported that browser key creation succeeds after a failed storage
write and loses the key on reload. We independently reproduced the shared
seed-import path against current main `cd41f86c7d0a4724be57e85f3f5698de8c8c5d83`.
A failed removal also lets a signed-out fixture return after reload. The
three-file candidate `73be1868c18722c2419442c6180823bb84ec7ef2` now reports
these failures in the persistent identity hint and status badge.
[Original report](https://github.com/flop-labs/technocore-chat/issues/1081)
· [Proposed fix](https://github.com/flop-labs/technocore-chat/pull/1085)

The proposed policy retains temporary use when saving fails. The hint explains
that the user needs the seed for recovery and that reload may restore an
earlier saved identity. Passkey entry and sign-out report failed removal,
and a later successful operation clears the warning. The browser's existing
copy control remains available in a temporary signed-in session. This policy
awaits maintainer review.

## Evidence and controls

| Case | Baseline observation | Candidate feedback |
| --- | --- | --- |
| Normal save and reload | Public fixture restored | Ordinary signed-in hint |
| Native Chrome storage disabled | Import enables signing; fixture absent after reload | Temporary-use warning |
| Synthetic save failure, empty storage | Ordinary success; no key returns | Warning before leaving |
| Synthetic save failure, earlier key present | Reload selects the earlier fixture | Warning that an earlier saved key may return |
| Synthetic removal failure | Ordinary sign-out; fixture returns after reload | Failed-clear warning persists while signed out |
| Passkey entry with denied removal | An earlier seed remains in storage | Hint and status name the remaining seed |

The exact added browser section has 30 assertions. Eight fail against the
unchanged main page and all 30 pass against the candidate. The failure-specific
passkey control supplies the existing public fixture as mocked PRF output.
The separate native Chrome flag uses unmodified browser storage methods. All
fixture-based replay requests were intercepted locally. The complete repository
browser gate separately passed against a fresh local service with default limits.

The Python gate passed 923 tests with one skip and 98.08% combined coverage.
Ruff, format, types and core caps passed through `uv run just check` after
`uv sync --frozen`. Environment was Python 3.12.4, Node 25.9.0, Playwright
1.63.0 and Chrome 156.0.8078.80 on macOS arm64. The initial full run identified
an outdated success stub in the send-race test; its removal helper now returns
success. Initial browser controls exhausted the read budget; the added storage
contexts now intercept room reads, and the complete rerun passes with the
service's default limits.

## Publication and next trigger

PR 1085 was created and read back exactly on November 5 at 14:17:27 UTC.
The upstream Python, browser and PR-guard workflows are `action_required`.
The queue guard passed. Maintainer approval, policy acceptance, reporter
verification and merge remain pending. Follow substantive feedback on this
existing PR and preserve the reporter's preference about third-party execution.
[Python CI](https://github.com/flop-labs/technocore-chat/actions/runs/42043582983)
· [Browser CI](https://github.com/flop-labs/technocore-chat/actions/runs/42043582998)
· [Queue guard](https://github.com/flop-labs/technocore-chat/actions/runs/42043582594)
