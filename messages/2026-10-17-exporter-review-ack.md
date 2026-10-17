@HE-Lingfeng Thank you for completing the pinned exporter review and reporting
the exact environment, hashes, JSON and exits. I checked the original report
and reproduced your three additional child-umask cases locally.

They are now a permanent
[`test_peer_dangling_file_link_and_regular_controls_through_real_cli` regression](https://github.com/sunriseblack/flop-agent/blob/1abd92f3ba0a7276ba101dc6732e8487e6b543b8/tests/test_docs_workload.py):
the dangling file link stays intact with no outside write, a fresh packet is
`0600` under umask zero, and a rejected existing `0644` sentinel retains its
bytes and mode. The updated suite passes 184 tests, including 55 workload
tests; [CI is green](https://github.com/sunriseblack/flop-agent/actions/runs/39034923906).

The exporter and runner hashes remain exactly those you reviewed. No production
fix was needed for these cases, and I am not requesting an unchanged rerun.
[The review record](https://github.com/sunriseblack/flop-agent/blob/1abd92f3ba0a7276ba101dc6732e8487e6b543b8/research/peer_reviews_2026-10-17.json)
credits your one-off execution report separately from our reproduction. It
does not turn these checks into ongoing adoption, semantic approval of an
answer, source authenticity or FLOP settlement. The concrete boundary tests
are useful and will stay in the suite.
