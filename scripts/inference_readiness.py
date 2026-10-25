#!/usr/bin/env python3
"""Read public launch documentation and reconcile supplied session observations.

No signer, wallet, RPC, faucet request, model call or purchase is implemented.
Supplied evidence and finality claims remain unverified, even when consistent.
"""

import argparse
import concurrent.futures
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys

import docs_workload as docs
from submission_evidence import strict_json
from verify_tape import public_key_from_did


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"verification": "https://flop.finance/official/",
           "testnet_profile": "https://ask.flop.finance/networks/testnet"}
REQUIREMENTS = ("network_identity", "genesis", "supported_client", "official_faucet",
                "owner_delegate_mapping", "final_allocation_rules", "model_catalog",
                "independent_miner", "bounded_session_approval")
HASH = re.compile(r"[0-9a-f]{64}\Z")
AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,29})(?:\.[0-9]{1,18})?\Z")
MAX_BYTES = 2 * 1024 * 1024
MAX_OBSERVATIONS = 1000
PHASES = {"requested", "submitted", "delivered", "finalized", "disputed", "refunded"}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be text")
    result = datetime.datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return result


def text(value, maximum=200):
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or any(ord(c) < 32 for c in value):
        raise ValueError("invalid bounded text")
    return value


def checked_hash(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise ValueError("expected lowercase SHA-256")
    return value


def chain_hash(value):
    # Chain hashes are not assumed to use SHA-256. Normalize only hex notation.
    if not isinstance(value, str) or not re.fullmatch(r"(?:0x)?[0-9a-fA-F]{64}", value):
        raise ValueError("expected a 32-byte hexadecimal chain hash")
    return value.removeprefix("0x").lower()


def private_path(path):
    base = ROOT.resolve() / ".private" / "readiness"
    original = Path(path)
    if original.is_symlink():
        raise ValueError("symlink files are not supported")
    target = original.resolve()
    if base.resolve() != base or not target.is_relative_to(base) or target.suffix != ".json":
        raise ValueError("use a JSON path inside .private/readiness; symlink escapes are blocked")
    return target


def load(path):
    target = private_path(path)
    if not stat.S_ISREG(target.stat().st_mode):
        raise ValueError("input must be a regular file")
    with target.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds byte bound")
    return strict_json(raw)


def save(path, value):
    raw = (json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()
    if len(raw) > MAX_BYTES:
        raise ValueError("output exceeds byte bound")
    target = private_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(raw)


def collect(timeout=12):
    def get(item):
        try:
            return docs.fetch_source(item, timeout)
        except (OSError, ValueError) as exc:
            return {"id": item[0], "url": item[1], "retrieved_at": docs.utc_now().isoformat(),
                    "error": str(exc)[:300]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        sources = list(pool.map(get, SOURCES.items()))
    return {"schema": "flop-launch-sources-v1", "sources": sources}


def assess(corpus, evidence=None, now=None):
    """Report missing evidence. Text matching never ratifies a launch or permission."""
    now = docs.utc_now() if now is None else now
    if (not isinstance(corpus, dict) or set(corpus) != {"schema", "sources"}
            or corpus["schema"] != "flop-launch-sources-v1"
            or not isinstance(corpus["sources"], list) or len(corpus["sources"]) != len(SOURCES)):
        raise ValueError("invalid launch source corpus")
    seen, rows, blockers = set(), [], []
    for source in corpus["sources"]:
        if not isinstance(source, dict):
            raise ValueError("invalid launch source")
        key = source.get("id")
        if key not in SOURCES or key in seen or source.get("url") != SOURCES[key]:
            raise ValueError("unexpected or duplicate launch source")
        seen.add(key)
        age = (now - timestamp(source.get("retrieved_at"))).total_seconds()
        row = {"id": key, "url": SOURCES[key], "retrieved_at": source["retrieved_at"]}
        if age < -60 or age > 24 * 3600:
            row["state"] = "stale_or_future"
            blockers.append(key + ":fresh_source_required")
        elif "error" in source:
            text(source["error"], 300)
            row["state"] = "unavailable"
            blockers.append(key + ":source_unavailable")
        else:
            body = source.get("text")
            if (not isinstance(body, str) or not body.strip() or len(body.encode()) > MAX_BYTES
                    or hashlib.sha256(body.encode()).hexdigest() != source.get("text_sha256")):
                raise ValueError("source text hash mismatch or invalid text")
            checked_hash(source.get("raw_sha256"))
            row.update(state="supplied_snapshot", text_sha256=source["text_sha256"],
                       raw_sha256=source["raw_sha256"])
            lower = body.casefold()
            signals = []
            for phrase, label in (("testnet (planned)", "testnet_planned"),
                                  ("next (unreleased)", "release_unreleased"),
                                  ("no verified public value", "network_values_unverified"),
                                  ("none verified", "no_verified_release"),
                                  ("a target, not a fixed date", "date_is_only_target"),
                                  ("no rewards and no airdrop weight", "devnet_no_weight")):
                if phrase in lower:
                    signals.append(label)
            row["observed_text_signals"] = signals
            blockers.extend(key + ":" + s for s in signals if s not in {"date_is_only_target", "devnet_no_weight"})
        rows.append(row)
    supplied = {}
    if evidence is not None:
        if (not isinstance(evidence, dict) or set(evidence) != {"schema", "requirements"}
                or evidence["schema"] != "flop-launch-evidence-v1"
                or not isinstance(evidence["requirements"], dict)
                or set(evidence["requirements"]) - set(REQUIREMENTS)):
            raise ValueError("invalid launch evidence inventory")
        for key, value in evidence["requirements"].items():
            if not isinstance(value, dict) or set(value) != {"reference", "artifact_sha256"}:
                raise ValueError("invalid evidence reference")
            supplied[key] = {"reference": text(value["reference"], 500),
                             "artifact_sha256": checked_hash(value["artifact_sha256"])}
    requirements = [{"requirement": key, "state": "supplied_not_verified" if key in supplied else "missing",
                     **supplied.get(key, {})} for key in REQUIREMENTS]
    blockers.extend(row["requirement"] + ":missing" for row in requirements if row["state"] == "missing")
    return {"schema": "flop-readiness-report-v1", "observed_at": now.isoformat(), "sources": rows,
            "requirements": requirements, "blockers": blockers,
            "readiness": "blocked" if blockers else "requires_independent_verification",
            "launch_gate_verified": False, "live_session_authorized": False,
            "source_authenticity": "not_verified_by_hash", "airdrop_eligibility": "not_determined",
            "caution": "Snapshots and supplied references are evidence inventory only. A text match, calendar date, hash or complete inventory does not verify a live network, owner mapping, final rules, approval or settlement. No embedded URL or command is followed."}


def checked_observation(row):
    required = {"network", "genesis_hash", "session_id", "owner_account", "delegate_account",
                "miner", "phase", "observed_at", "evidence"}
    if not isinstance(row, dict) or set(row) != required:
        raise ValueError("invalid session observation fields")
    if row["network"] not in {"devnet", "testnet"} or row["phase"] not in PHASES:
        raise ValueError("invalid network or phase")
    genesis = chain_hash(row["genesis_hash"])
    timestamp(row["observed_at"])
    for key in ("session_id", "owner_account", "miner"):
        text(row[key])
    if row["delegate_account"] is not None:
        text(row["delegate_account"])
    evidence = row["evidence"]
    optional = {"output_sha256", "proof_sha256", "review_sha256", "settlement"}
    if not isinstance(evidence, dict) or set(evidence) - optional:
        raise ValueError("invalid session evidence fields")
    for key in set(evidence) - {"settlement"}:
        checked_hash(evidence[key])
    if "settlement" in evidence:
        item = evidence["settlement"]
        if (not isinstance(item, dict) or set(item) != {"block_number", "block_hash", "asset", "paid_amount"}
                or type(item["block_number"]) is not int or not 0 <= item["block_number"] <= 2**64 - 1
                or not isinstance(item["paid_amount"], str) or not AMOUNT.fullmatch(item["paid_amount"])):
            raise ValueError("invalid settlement fields; use exact nonnegative decimal amounts")
        chain_hash(item["block_hash"])
        text(item["asset"], 80)
    if row["phase"] == "finalized" and set(evidence) != optional:
        raise ValueError("a reported finalized row needs output, proof, review and settlement references")
    normalized = {**row, "genesis_hash": genesis, "evidence": dict(evidence)}
    if "settlement" in evidence:
        normalized["evidence"]["settlement"] = {**evidence["settlement"],
                                                "block_hash": chain_hash(evidence["settlement"]["block_hash"])}
    return normalized


def reconcile(ledger):
    if (not isinstance(ledger, dict) or set(ledger) != {"schema", "owner_did", "observations"}
            or ledger["schema"] != "flop-session-observations-v1"
            or not isinstance(ledger["observations"], list)
            or len(ledger["observations"]) > MAX_OBSERVATIONS):
        raise ValueError("invalid or oversized session ledger")
    public_key_from_did(ledger["owner_did"])
    groups, seen, duplicates = {}, set(), 0
    for item in ledger["observations"]:
        row = checked_observation(item)
        # Re-reading the same statement at a later time must not add spend.
        fingerprint = docs.digest({k: v for k, v in row.items() if k != "observed_at"})
        if fingerprint in seen:
            duplicates += 1
            continue
        seen.add(fingerprint)
        key = (row["network"], row["genesis_hash"], row["session_id"])
        groups.setdefault(key, []).append(row)
    rows, totals = [], {}
    for (network, genesis, session_id), items in sorted(groups.items()):
        identities = {(r["owner_account"], r["delegate_account"], r["miner"]) for r in items}
        finals = {docs.digest(r["evidence"]) for r in items if r["phase"] == "finalized"}
        phases = sorted({r["phase"] for r in items})
        conflicts = []
        if len(identities) > 1:
            conflicts.append("owner_delegate_or_miner_conflict")
        if len(finals) > 1:
            conflicts.append("conflicting_reported_final_settlements")
        state = ("conflict_requires_review" if conflicts else "reported_disputed" if "disputed" in phases else
                 "reported_refunded" if "refunded" in phases else "reported_finalized_unverified" if finals else
                 "reported_delivered" if "delivered" in phases else "reported_submitted" if "submitted" in phases else
                 "reported_requested")
        row = {"network": network, "genesis_hash": genesis, "session_id": session_id,
               "observations": len(items), "reported_phases": phases, "state": state, "conflicts": conflicts,
               "owner_accounts": sorted({r["owner_account"] for r in items}),
               "owner_binding": "not_verified", "settlement_finality": "not_verified",
               "allocation_credit": "not_determined", "devnet_has_airdrop_weight": False if network == "devnet" else None}
        if state == "reported_finalized_unverified":
            final = next(r for r in items if r["phase"] == "finalized")
            settlement = final["evidence"]["settlement"]
            row["supplied_final_evidence"] = final["evidence"]
            key = (network, genesis, settlement["asset"])
            with localcontext() as context:
                context.prec = 80  # 30 integer + 18 fractional digits, <=1000 rows.
                totals[key] = totals.get(key, Decimal(0)) + Decimal(settlement["paid_amount"])
        rows.append(row)
    return {"schema": "flop-session-ledger-report-v1", "owner_did": ledger["owner_did"],
            "input_observations": len(ledger["observations"]), "duplicate_reads": duplicates,
            "unique_sessions": len(rows), "sessions": rows,
            "reported_paid_totals_unverified": [{"network": n, "genesis_hash": g, "asset": a,
                                                  "paid_amount": format(value, "f")}
                                                 for (n, g, a), value in sorted(totals.items())],
            "live_session_authorized": False, "allocation_reconciled": False,
            "caution": "All phases, identities, amounts and evidence references are caller-supplied. Totals exclude conflicting, disputed or refunded sessions, never mix chains/assets, and are not verified spend or allocation. Hashes do not establish output quality, independent demand, ownership, proof validity or finality."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cmd = commands.add_parser("collect")
    cmd.add_argument("--timeout", type=float, default=12)
    cmd.add_argument("--output", required=True)
    cmd = commands.add_parser("check")
    cmd.add_argument("--sources", required=True)
    cmd.add_argument("--evidence")
    cmd.add_argument("--output", required=True)
    cmd = commands.add_parser("ledger")
    cmd.add_argument("--input", required=True)
    cmd.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        # Validate output location/existence before any network request.
        target = private_path(args.output)
        if target.exists() or target.is_symlink():
            raise ValueError("output already exists")
        if args.command == "collect":
            if not math.isfinite(args.timeout) or not 0 < args.timeout <= 30:
                raise ValueError("timeout must be finite and within 30 seconds")
            report = collect(args.timeout)
        elif args.command == "check":
            report = assess(load(args.sources), load(args.evidence) if args.evidence else None)
        else:
            report = reconcile(load(args.input))
        save(args.output, report)
        print(json.dumps({"output": args.output, "schema": report["schema"],
                          "live_session_authorized": False}))
        return 1 if report.get("readiness") == "blocked" else 0
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        print(f"readiness unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
