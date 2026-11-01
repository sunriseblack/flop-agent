#!/usr/bin/env python3
"""Inspect one saved inference answer offline, before human semantic review.

No network, model, tokenizer, signer, purchase, approval or retry is implemented.
This bounds saved answer bytes; it does not enforce live transport/token limits.
"""

import argparse
import hashlib
from pathlib import Path
import stat
import sys

import docs_workload as docs
import inference_readiness as readiness
from submission_evidence import strict_json


MAX_ANSWER_BYTES = 8192


def read_private(path, maximum):
    original = Path(path)
    base = docs.ROOT.resolve() / ".private"
    target = original.resolve()
    if (base.resolve() != base or original.is_symlink()
            or not target.is_relative_to(base)
            or not stat.S_ISREG(target.stat().st_mode)):
        raise ValueError("input must be a regular private file; file symlinks and escapes are blocked")
    with target.open("rb") as source:
        raw = source.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("input exceeds byte bound")
    return raw


def review(bundle, raw, expected_job_hash):
    expected_job_hash = readiness.checked_hash(expected_job_hash)
    jobs = docs.checked_jobs(bundle)
    if len(jobs) != 1:
        raise ValueError("first-session review requires exactly one job")
    job = next(iter(jobs.values()))
    if job["request"]["job_sha256"] != expected_job_hash:
        raise ValueError("saved job differs from the independently selected hash")
    if not isinstance(raw, bytes) or len(raw) > MAX_ANSWER_BYTES:
        raise ValueError("saved answer exceeds byte bound or is not raw bytes")
    # Count actual UTF-8 bytes before JSON parsing or checking model claims.
    answer = strict_json(raw.decode("utf-8"))
    errors = docs.response_errors(job, answer)
    return {
        "schema": "flop-first-session-output-review-v1",
        "task_id": job["request"]["task_id"], "job_sha256": expected_job_hash,
        "answer_sha256": hashlib.sha256(raw).hexdigest(),
        "answer_bytes": len(raw), "maximum_answer_bytes": MAX_ANSWER_BYTES,
        "mechanical_pass": not errors, "errors": errors,
        "semantic_review": "required", "output_token_limit": "not_verified",
        "source_freshness_and_authenticity": "not_verified",
        "transport_budget_enforcement": "not_verified",
        "provider_and_usage": "not_verified", "proof_and_settlement": "not_verified",
        "live_session_authorized": False, "airdrop_credit": "not_determined",
        "caution": "Saved-output byte, schema and citation checks only. Exact quotes do not prove entailment. A passing answer is not human approval, provider execution, token/spend enforcement, proof or finalized settlement."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--answer", required=True)
    parser.add_argument("--expected-job-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        target = readiness.private_path(args.output)
        if target.exists() or target.is_symlink():
            raise ValueError("output already exists")
        bundle = strict_json(read_private(args.jobs, docs.MAX_FILE_BYTES))
        raw = read_private(args.answer, MAX_ANSWER_BYTES)
        report = review(bundle, raw, args.expected_job_sha256)
        readiness.save(args.output, report)
        print("saved offline output review; semantic review required; live_session_authorized=false")
        return 0 if report["mechanical_pass"] else 1
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        print(f"output review unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
