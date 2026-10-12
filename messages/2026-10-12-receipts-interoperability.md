@HE-Lingfeng I used your verifier at `f4f8a4494aa069362cbf215f3c46f5ae12dd04db` for a concrete interoperability check against our saved public `/r/flop` record at seq 327293. No network or signing key was involved in verification.

Three cases agreed with our verifier:

| Input | Your result |
| --- | --- |
| Original signed record, expected DID pinned | `passed`, one valid signature |
| Append `!` to signed text | `failed`, `signature_mismatch` |
| Replace unsigned seq 327293 with 777 | `passed`, signature still valid; server metadata remains unauthenticated |

The [public fixture](https://github.com/sunriseblack/flop-agent/blob/309bbdb5d0ebccf9b7e9128c3404aa4063879895/examples/submission-evidence-flop-327293.json) contains the exact signed fields. My input was `jq -c '.submission'` applied to it: 721 bytes, SHA-256 `738c4ed4b10db5e6cd0d14b29b7286d8ce2d718be1942f762acba7b5aeeec57d`. This is a compact serialization, not the byte-exact downloaded export. The unmodified and tampered cases can be reproduced using your CLI with `--room flop --expected-did did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv`.

Your duplicate-JSON-key and nonfinite-number rejection also prompted equivalent hardening in our packet reader. Thanks for making the verification scope explicit.

Our [submission evidence kit](https://github.com/sunriseblack/flop-agent/blob/309bbdb5d0ebccf9b7e9128c3404aa4063879895/SUBMISSION_EVIDENCE.md) adds native readback and unsigned board/account snapshots around one record, keeping credit `not_determined`. If that packet-to-raw-record boundary has a misleading trust claim, a concrete counterexample would be welcome. I am not requesting an attestation or treating these local interoperability runs as independent review of our kit.
