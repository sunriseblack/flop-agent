#!/usr/bin/env python3
"""Inspect exact-version review records offline; never authorize publication.

Each --review explicitly supplies a decision, its packet, and the bundle used
to export that packet. No path or command is taken from the decision text.
Matching files establish local consistency, not that a human made a decision.
"""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import stat
import sys

import docs_workload as workload


ROOT = workload.ROOT
MAX_DECISION_BYTES = 64 * 1024
REQUIRED = {"schema", "recorded_at", "task_id", "request_sha256", "draft_sha256",
            "packet_sha256", "reviewer", "independent_review", "decision", "scope",
            "authorization_boundary"}
OPTIONAL = {"version", "evidence", "reason", "rubric_item_assessments"}


def checked_decision(record):
    if (not isinstance(record, dict) or not REQUIRED <= set(record)
            or set(record) - REQUIRED - OPTIONAL
            or record["schema"] != "flop-docs-human-decision-v1"):
        raise ValueError("unsupported decision schema")
    for field in ("task_id", "reviewer", "scope", "authorization_boundary"):
        if not isinstance(record[field], str) or not 1 <= len(record[field]) <= 2000:
            raise ValueError("invalid decision text field")
    for field in ("request_sha256", "draft_sha256", "packet_sha256"):
        value = record[field]
        if (not isinstance(value, str) or len(value) != 64
                or any(c not in "0123456789abcdef" for c in value)):
            raise ValueError("invalid decision hash")
    if (record["decision"] not in ("approved", "rejected")
            or type(record["independent_review"]) is not bool):
        raise ValueError("invalid decision enum or independence flag")
    if not isinstance(record["recorded_at"], str):
        raise ValueError("invalid decision timestamp")
    timestamp = datetime.datetime.fromisoformat(record["recorded_at"])
    if timestamp.tzinfo is None:
        raise ValueError("decision timestamp must include a timezone")
    if "version" in record and (not isinstance(record["version"], str)
                                or not 1 <= len(record["version"]) <= 100):
        raise ValueError("invalid decision version")
    if "evidence" in record:
        evidence = record["evidence"]
        if (not isinstance(evidence, dict) or set(evidence) != {"channel", "exact_text"}
                or any(not isinstance(v, str) or not 1 <= len(v) <= 16000 for v in evidence.values())):
            raise ValueError("invalid decision evidence")
    if record.get("reason") is not None and (not isinstance(record["reason"], str)
                                             or len(record["reason"]) > 2000):
        raise ValueError("invalid decision reason")
    if record.get("rubric_item_assessments") is not None and not isinstance(
            record["rubric_item_assessments"], (dict, list)):
        raise ValueError("invalid rubric assessments")
    return record


def assess(bundle, responses, supplied_reviews):
    """Return metadata only; supplied_reviews contains explicit input triples."""
    jobs = workload.checked_jobs(bundle)
    report = workload.grade(bundle, responses)
    if report["global_errors"]:
        raise ValueError("unexpected response IDs")
    if not isinstance(supplied_reviews, list) or len(supplied_reviews) > workload.MAX_JOBS:
        raise ValueError("review count exceeds budget")
    reviews = {}
    for record, packet, original_bundle in supplied_reviews:
        checked_decision(record)
        task_id = record["task_id"]
        if task_id not in jobs or task_id in reviews:
            raise ValueError("unknown or duplicate decision task ID")
        if not isinstance(packet, bytes) or len(packet) > workload.MAX_FILE_BYTES:
            raise ValueError("invalid or oversized packet")
        original_jobs = workload.checked_jobs(original_bundle)
        if task_id not in original_jobs:
            raise ValueError("decision task missing from original review bundle")
        reviews[task_id] = (record, packet, original_bundle, original_jobs)

    rows = []
    for mechanical in report["results"]:
        task_id, draft = mechanical["task_id"], mechanical["draft"]
        row = {"task_id": task_id, "mechanical_pass": mechanical["mechanical_pass"],
               "request_sha256": jobs[task_id]["request"]["job_sha256"],
               "draft_sha256": workload.digest(draft) if draft is not None else None,
               "record_status": "not_supplied", "reported_decision": None,
               "claimed_independent_review": None, "binding_errors": [],
               "decision_authenticity": "not_verified", "semantic_correctness": "not_verified",
               "publication_authorized": False, "next_step": "human_review_required"}
        if task_id in reviews:
            record, packet, original_bundle, original_jobs = reviews[task_id]
            errors = row["binding_errors"]
            row["reported_decision"] = record["decision"]
            row["claimed_independent_review"] = record["independent_review"]
            original_job = original_jobs[task_id]
            if not mechanical["mechanical_pass"]:
                errors.append("current_draft_failed_mechanical_checks")
            if record["request_sha256"] != row["request_sha256"]:
                errors.append("current_request_mismatch")
            if record["draft_sha256"] != row["draft_sha256"]:
                errors.append("current_draft_mismatch")
            if record["request_sha256"] != original_job["request"]["job_sha256"]:
                errors.append("original_review_request_mismatch")
            if workload.digest(original_job["evaluation"]) != workload.digest(jobs[task_id]["evaluation"]):
                errors.append("evaluation_changed")
            if hashlib.sha256(packet).hexdigest() != record["packet_sha256"]:
                errors.append("packet_hash_mismatch")
            if draft is not None and not any(error in errors for error in (
                    "current_request_mismatch", "current_draft_mismatch", "original_review_request_mismatch")):
                selected = [r for r in responses if r["task_id"] in original_jobs]
                expected = workload.review_packet(original_bundle, selected, task_id).encode("utf-8")
                if packet != expected:
                    errors.append("packet_does_not_reproduce_original_review")
            row["record_status"] = "binding_mismatch" if errors else "supplied_record_matches"
            row["next_step"] = ("new_review_required" if errors else
                                "do_not_reuse_rejected_draft" if record["decision"] == "rejected" else
                                "verify_original_human_decision_before_reuse")
        rows.append(row)
    return {"schema": "flop-review-status-v1", "jobs_sha256": bundle["jobs_sha256"],
            "tasks": len(rows), "mechanical_passes": report["mechanical_passes"],
            "matching_supplied_approval_records": sum(r["record_status"] == "supplied_record_matches"
                                                       and r["reported_decision"] == "approved" for r in rows),
            "matching_supplied_rejection_records": sum(r["record_status"] == "supplied_record_matches"
                                                        and r["reported_decision"] == "rejected" for r in rows),
            "results": rows, "network_requests": 0, "model_calls": 0,
            "source_freshness": "not_checked", "source_authenticity": "not_verified",
            "decision_authenticity": "not_verified", "publication_authorized": False,
            "live_usage_authorized": False, "flop_settlement": "not_verified",
            "caution": "Matching supplied files are not proof of a human decision, semantic truth or permissions. Verify the original human message and fresh source preparation separately. No action is executed."}


def private_path(path, suffix):
    root = ROOT.resolve() / ".private" / "workload"
    target = pathlib.Path(path).resolve()
    if root.resolve() != root or not target.is_relative_to(root) or target.suffix != suffix:
        raise ValueError("inputs and report must remain inside .private/workload with the expected suffix")
    return target


def read_private(path, suffix, limit=workload.MAX_FILE_BYTES):
    target = private_path(path, suffix)
    if not stat.S_ISREG(target.stat().st_mode):
        raise ValueError("input is not a regular file")
    with target.open("rb") as source:
        raw = source.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("input exceeds byte bound")
    return raw


def save_report(path, report):
    target = private_path(path, ".json")
    raw = (json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()
    if len(raw) > workload.MAX_FILE_BYTES:
        raise ValueError("report exceeds byte bound")
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--review", nargs=3, action="append", default=[],
                        metavar=("DECISION", "PACKET", "ORIGINAL_BUNDLE"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if len(args.review) > workload.MAX_JOBS:
            raise ValueError("review count exceeds budget")
        def load(path, limit=workload.MAX_FILE_BYTES):
            return workload.strict_json(read_private(path, ".json", limit))
        supplied = [(load(decision, MAX_DECISION_BYTES), read_private(packet, ".txt"), load(original))
                    for decision, packet, original in args.review]
        report = assess(load(args.bundle), load(args.responses), supplied)
        save_report(args.output, report)
        print(json.dumps({"output": args.output, "tasks": report["tasks"],
                          "matching_supplied_approval_records": report["matching_supplied_approval_records"],
                          "decision_authenticity": "not_verified", "publication_authorized": False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(f"Review status unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
