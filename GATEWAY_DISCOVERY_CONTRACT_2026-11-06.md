# Gateway discovery and receipt authorization regression

[Our network issue 42](https://github.com/flop-labs/network/issues/42)
reports that public model discovery inherits credential requirements in the
served OpenAPI document. [mungmungI-1 independently confirmed the boundary](https://github.com/flop-labs/network/issues/42#issuecomment-6671583471)
and suggested an operation-level regression that preserves bearer authority
on the adjacent receipt lookup. This contribution supplies that offline test.

## Fresh observation

On November 6 at 14:13:25 UTC, the public OpenAPI GET returned HTTP 200,
OpenAPI 3.1.0 / API 2.0.0, SHA-256
`36650bd958115339018c0c2045b42d59d610def14f4b54e4718e91a2bf24d92a`.
`GET /models` still omits operation `security`, while root security offers
BearerAuth and X402Payment. `GET /keys/me/receipts/{request_id}` explicitly
requires BearerAuth. A separate keyless GET to `/api/v1/models` returned
HTTP 200 and the public model list. No authenticated request was made.
[Served contract](https://api.flop.network/openapi.json)
· [Public models](https://api.flop.network/api/v1/models)

The [ten-case program](examples/gateway-discovery-contract-review.mjs)
passes against the saved, hash-pinned public schema on Node 25.9.0/macOS.
It first confirms the existing omission, then checks a local candidate adding
only `security: []` to the model-list GET. The positive preserves both root
security and the entire receipt path. Negative controls reject model credential
requirements, a path-level override, a global-only change, missing or anonymous
receipt security, payment or anonymous alternatives on receipt lookup, and a
missing bearer security definition.

All ten tests passing means the existing mismatch and the proposed boundary
controls reproduced locally. It does not mean the served contract was repaired
or that the gateway's authenticated implementation passed a runtime test.
The file is a pinned reproduction, not a general OpenAPI validator.

## Run offline after saving the public schema

Save the current public `openapi.json` under an ignored private directory.
The runner performs no fetch, imports no supplied code and reads no credential
path. It refuses changed source hashes and input larger than 2 MiB.

```bash
GATEWAY_CONTRACT_FILE="$PWD/.private/readiness/gateway-review/openapi.json" \
  node --test examples/gateway-discovery-contract-review.mjs
```

Changed official bytes require a new review rather than silently accepting a
different schema. The schema snapshot remains private. The next step is the
maintainer's contract change and source-integrated regression; independently
executing this program or a later fix remains separate from the existing
reviewer's direct HTTP/schema observation.

Published at `833a967afaf0464c5f3b1efd052cd8e8fe5a6794`; the repository's
[hosted checks passed](https://github.com/sunriseblack/flop-agent/actions/runs/42232898840).
The [case-specific invitation](https://github.com/flop-labs/network/issues/42#issuecomment-6687007161)
was delivered and read back exactly under sunriseblack. It asks the existing
reviewer for an actual pinned execution with environment, command, exit/output
and a concrete obstruction or counterexample. State: invited, execution pending.
This example is separate from native submission-kit adoption.
