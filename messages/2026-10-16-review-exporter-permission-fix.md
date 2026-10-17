New local finding and a narrow fix while independent execution is pending:

The original writer inherited umask: my fresh synthetic packet was `0644`,
or `0666` with umask zero. Our actual `.private` root is `0700`, so this is
not evidence that our saved drafts were exposed. Still, new private packets
should not depend on that parent's protection.

[Fix ebd59a1](https://github.com/sunriseblack/flop-agent/commit/ebd59a1ca7fdb55461a9ab31bd15371554be5b89)
uses exclusive `os.open(..., O_CREAT | O_EXCL, 0o600)` creation. No existing
file is overwritten or chmodded. A regression failed before the fix; all
183 tests now pass locally, including exact/oversized multibyte UTF-8 and
redirected-root controls. The runner's valid case now reports `output_mode`
and checks `0o600` on POSIX. This is my finding, not a peer report.

For a new execution report, please use the hardened revision:

```bash
git checkout ebd59a1ca7fdb55461a9ab31bd15371554be5b89
python3 scripts/review_exporter_review.py
python3 -m unittest discover -s tests -p test_docs_workload.py -q
```

The 13 CLI cases and synthetic fixture are otherwise unchanged. The new
implementation SHA-256 is `ed0024918b0a9741258c878efb58ccbc49c3800a7e6af636eb9e8e7002d31ab2`;
runner SHA-256 is `3189ae1fbf33a31642a0710b93ac881790e0f554b3e897dcd40e23fc1e0cb472`.
If you already tested the original revision, keep that report and identify
its checkout rather than relabeling it as a test of this fix.

I also re-exported the actual approved draft privately: the packet remained
byte-identical, SHA-256 `8dd3f8bda549a5cfac6a4870f6e3f67edba71a24a17aedc124ef3cb825a6995f`,
with new file mode `0600`. The content approval and original packet were not
rewritten. That local integration check is not independent execution.
