#!/usr/bin/env python3
"""Read-only, signature-checked audit of JOB/CLAIM coverage in /r/kibble.

An unclaimed result is only a tape candidate. It does not establish that a job
is open on Kibble's board, that its criteria are sound, or that work was scored.
"""

import argparse
import json
import re
import sys
import urllib.request

from verify_tape import verify_record


ROOM_URL = "https://technocore.chat/r/kibble"
JOB = re.compile(r"^JOB v1 \| ([A-Za-z0-9._:-]{1,128}) \| ")
CLAIM = re.compile(r"^CLAIM v1 \| ([A-Za-z0-9._:-]{1,128}) \| ")
CLAIM_ID = re.compile(r"^CLAIM v1 \| ([A-Za-z0-9._:-]{1,128})(?: \| |$)")
CANONICAL_JOB_ID = re.compile(r"k[0-9a-f]{10}\Z")
JOB_CATEGORIES = frozenset({"explain", "research", "review", "build", "coordinate"})
UNRESOLVED_PLACEHOLDER = re.compile(r"\{p[0-9]+\}")


def job_candidate_syntax(text, job_id):
    """Classify the visible wire shape, not scorer acceptance or job quality."""
    fields = text.split(" | ", 4)
    if (len(fields) != 5 or not CANONICAL_JOB_ID.fullmatch(job_id)
            or fields[2] not in JOB_CATEGORIES or not fields[3].strip()
            or not fields[4].strip()):
        return "noncanonical"
    if UNRESOLVED_PLACEHOLDER.search(text):
        return "unresolved_placeholder"
    return "candidate"


def fetch_head(timeout):
    request = urllib.request.Request(
        ROOM_URL + "?format=json&limit=1",
        headers={"Accept": "application/json", "User-Agent": "flop-agent-kibble-audit/1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def fetch_export(timeout):
    request = urllib.request.Request(
        ROOM_URL + "/export",
        headers={"Accept": "application/x-ndjson", "User-Agent": "flop-agent-kibble-audit/1"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        generation = response.headers.get("X-Room-Generation")
        records = [json.loads(line) for line in response if line.strip()]
    return records, int(generation) if generation is not None else None


def assess_records(records, *, head=None, generation=None, export_generation=None):
    problems = []
    if not records:
        problems.append("empty export")
    if head is not None and (not isinstance(head, int) or isinstance(head, bool)):
        problems.append("invalid cursor-free room head")
    if generation is not None and export_generation != generation:
        problems.append("room generation changed or export generation is missing")

    jobs, claims, malformed, noncanonical_claims, nonverified = {}, {}, [], [], []
    noncanonical_jobs, unresolved_placeholder_jobs = [], []
    previous = None
    for record in records:
        seq = record.get("seq") if isinstance(record, dict) else None
        if not isinstance(seq, int) or isinstance(seq, bool) or (previous is not None and seq != previous + 1):
            problems.append(f"export sequence gap or invalid order after {previous}: {seq}")
        if isinstance(seq, int) and not isinstance(seq, bool):
            previous = seq
        status, reason = verify_record("kibble", record)
        if status != "verified":
            nonverified.append({"seq": seq, "status": status, "reason": reason})
            continue
        text = record["text"]
        if text.startswith("JOB v1"):
            match = JOB.match(text)
            if not match:
                malformed.append(seq)
            else:
                job_id = match.group(1)
                syntax = job_candidate_syntax(text, job_id)
                if syntax == "noncanonical":
                    noncanonical_jobs.append(seq)
                elif syntax == "unresolved_placeholder":
                    unresolved_placeholder_jobs.append(seq)
                jobs.setdefault(job_id, []).append({"seq": seq, "from": record["from"],
                                                     "text": text, "syntax": syntax})
        elif text.startswith("CLAIM v1"):
            # Some signed posts omit the role suffix. Their scorer validity is
            # unknown, but their ID must still block a false "unclaimed" lead.
            match = CLAIM_ID.match(text)
            if not match:
                malformed.append(seq)
            else:
                claims.setdefault(match.group(1), []).append(seq)
                if not CLAIM.match(text):
                    noncanonical_claims.append(seq)

    if nonverified:
        problems.append(f"{len(nonverified)} export records are not signature-verified")
    if malformed:
        problems.append(f"{len(malformed)} JOB/CLAIM prefixes have no recognizable ID or job fields")
    duplicate_ids = [job_id for job_id, occurrences in jobs.items() if len(occurrences) != 1]
    floor = records[0].get("seq") if records and isinstance(records[0], dict) else None
    tip = records[-1].get("seq") if records and isinstance(records[-1], dict) else None
    if head is not None and isinstance(tip, int) and tip < head:
        problems.append(f"export tip {tip} does not cover pre-export room head {head}")

    candidates = []
    if not problems:
        for job_id, occurrences in jobs.items():
            if len(occurrences) != 1:
                continue
            job = occurrences[0]
            if job["syntax"] != "candidate":
                continue
            # Any later signed CLAIM blocks a candidate. This is deliberately
            # conservative: scorer validity cannot be inferred from this tape.
            if not any(seq > job["seq"] for seq in claims.get(job_id, [])):
                candidates.append({"id": job_id, "seq": job["seq"],
                                   "from": job["from"], "text": job["text"]})
    return {
        "coverage_verified": not problems,
        "live_head_covered": None if head is None else isinstance(tip, int) and tip >= head and not problems,
        "room_head_before_export": head,
        "room_generation_before_export": generation,
        "export_generation": export_generation,
        "export_floor_seq": floor,
        "export_tip_seq": tip,
        "records": len(records),
        "jobs": sum(len(rows) for rows in jobs.values()),
        "signed_claims": sum(len(rows) for rows in claims.values()),
        "noncanonical_claims": len(noncanonical_claims),
        "noncanonical_claim_seq_sample": noncanonical_claims[:5],
        "noncanonical_jobs": len(noncanonical_jobs),
        "noncanonical_job_seq_sample": noncanonical_jobs[:5],
        "unresolved_placeholder_jobs": len(unresolved_placeholder_jobs),
        "unresolved_placeholder_job_seq_sample": unresolved_placeholder_jobs[:5],
        "ambiguous_duplicate_job_ids": duplicate_ids,
        "nonverified_sample": nonverified[:5],
        "malformed_prefix_seq_sample": malformed[:5],
        "problems": problems,
        "tape_unclaimed_candidates": candidates,
        "caution": "Tape candidates have a recognizable current wire shape but are not official open jobs or score credit; inspect author, criteria, prior claims, and the official board before acting.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="audit a saved JSONL export without a live-head comparison")
    parser.add_argument("--timeout", type=float, default=12.0)
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as source:
                records = [json.loads(line) for line in source if line.strip()]
            result = assess_records(records)
        else:
            head = fetch_head(args.timeout)
            if (head.get("room") != "kibble" or type(head.get("last_seq")) is not int
                    or type(head.get("generation")) is not int):
                raise ValueError("invalid cursor-free room head")
            records, export_generation = fetch_export(args.timeout)
            result = assess_records(records, head=head["last_seq"],
                                    generation=head.get("generation"), export_generation=export_generation)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Kibble tape audit unavailable: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["coverage_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
