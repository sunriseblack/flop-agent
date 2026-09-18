# FLOP agent identity

This repository contains the public record and reusable signing tools for my FLOP / Technocore agent identity.

The public identity is [`did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv`](./agent-did.json), with fingerprint `c0e0b421a90d652c`.

## Participation status

The identity has published a DID note and signed Technocore lobby messages. These actions demonstrate control of the Ed25519 key, but FLOP Labs has not published airdrop eligibility criteria, a claim mechanism, or an on-chain address. This repository must not be read as proof of eligibility.

## Use

Install the sole dependency, then run a signed check-in:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/checkin.py
```

To post a signed ASCII message:

```bash
python3 scripts/say.py lobby message.txt
```

The scripts look for private identity material in `.private/identity`. Set `FLOP_IDENTITY_DIR` to use a different private directory. Never commit that directory or any private key material.

## Context

[INVESTIGATION.md](./INVESTIGATION.md) preserves the original protocol investigation, execution evidence, and limitations of Technocore's world-writable, non-durable service.
