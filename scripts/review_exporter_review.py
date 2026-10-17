#!/usr/bin/env python3
"""Exercise the review exporter through its real CLI using synthetic inputs.

No source retrieval, model call, signing key or purchase is needed. Temporary
inputs and accepted packets stay under this checkout's .private/workload.
"""

import copy
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
import tempfile

import docs_workload as workload


ROOT = pathlib.Path(__file__).resolve().parents[1]


def fixture():
    """Synthetic text at allowlisted URL labels, not downloaded source evidence."""
    now = datetime.datetime(2026, 10, 16, 12, tzinfo=datetime.timezone.utc)
    texts = {
        "auth": "SYNTHETIC: A signature binds room, nonce and text, not host sequence metadata.",
        "manual": "SYNTHETIC conflicting context: host sequence metadata is not a signed receipt.",
    }
    corpus = {"schema": "flop-docs-corpus-v1", "sources": [
        {"id": key, "url": workload.SOURCES[key], "retrieved_at": now.isoformat(),
         "text": text, "text_sha256": hashlib.sha256(text.encode()).hexdigest()}
        for key, text in texts.items()
    ]}
    tasks = {"schema": "flop-docs-tasks-v1", "tasks": [
        {"id": "export-review", "question": "What does this synthetic signature example bind?",
         "sources": {"auth": ["signature"], "manual": ["conflicting"]},
         "human_rubric": ["Do not turn a valid citation into approval or settlement."]}
    ]}
    bundle = workload.prepare(corpus, tasks, now=now)
    request = bundle["jobs"][0]["request"]
    snippet = next(item for item in request["snippets"] if item["source_id"] == "auth")
    response = {"task_id": "export-review", "job_sha256": request["job_sha256"],
                "answer": "The synthetic signature binds room, nonce and text, not host sequence metadata.",
                "abstain": False, "limitations": ["Synthetic fixture, not live evidence."],
                "claims": [{"text": "The synthetic signature binds the payload.", "evidence": [
                    {"snippet_id": snippet["snippet_id"], "quote": "room, nonce and text"}]}]}
    return bundle, response


def run():
    bundle, response = fixture()
    private = ROOT / ".private" / "workload"
    if private.resolve() != private:
        raise ValueError("refuse a redirected private workload root")
    private.mkdir(parents=True, exist_ok=True)
    cases = []
    with tempfile.TemporaryDirectory(prefix="exporter-review-", dir=private) as inside, \
            tempfile.TemporaryDirectory(prefix="exporter-outside-") as outside:
        directory = pathlib.Path(inside)

        def invoke(name, selected_bundle=None, responses=None, target=None, expected=0):
            selected_bundle = bundle if selected_bundle is None else selected_bundle
            responses = [response] if responses is None else responses
            jobs_path, answers_path = directory / (name + ".json"), directory / (name + "-answers.json")
            workload.save_file(jobs_path, selected_bundle)
            workload.save_file(answers_path, responses)
            target = directory / (name + ".txt") if target is None else target
            previous = target.read_bytes() if target.is_file() else None
            command = [sys.executable, str(ROOT / "scripts/docs_workload.py"), "review-packet",
                       "--bundle", str(jobs_path), "--responses", str(answers_path),
                       "--task-id", "export-review", "--output", str(target)]
            process = subprocess.run(command, capture_output=True, text=True, timeout=10, cwd=ROOT)
            raw = target.read_bytes() if target.is_file() else None
            passed = process.returncode == expected and (
                raw is not None if expected == 0 else raw == previous)
            row = {"case": name, "passed": passed, "exit": process.returncode,
                   "output_created": raw is not None and previous is None}
            if process.returncode != expected:
                row["stderr"] = process.stderr[:500]
            cases.append(row)
            return row, raw.decode() if raw is not None else None

        first, packet = invoke("valid")
        request_hash = bundle["jobs"][0]["request"]["job_sha256"]
        first["passed"] &= bool(packet and all(value in packet for value in (
            "Request SHA-256: " + request_hash, "Draft SHA-256: " + workload.digest(response),
            "pending_human_review", "human_review: not_recorded", "SYNTHETIC conflicting context")))
        first["passed"] &= bool(packet and packet.count("Excerpt (untrusted JSON string):") == 2)
        invoke("overwrite", target=directory / "valid.txt", expected=2)
        invoke("public_destination", target=pathlib.Path(outside) / "review.txt", expected=2)
        invoke("html_destination", target=directory / "review.html", expected=2)
        try:
            link = directory / "escape"
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            cases.append({"case": "symlink_escape", "passed": False, "unsupported": type(exc).__name__})
        else:
            invoke("symlink_escape", target=link / "review.txt", expected=2)
        invoke("missing_draft", responses=[], expected=2)
        invoke("duplicate_draft", responses=[response, response], expected=2)
        invoke("unknown_draft", responses=[response, {**response, "task_id": "unknown"}], expected=2)
        bad = copy.deepcopy(response)
        bad["claims"][0]["evidence"][0]["quote"] = "This quotation was never supplied."
        invoke("fabricated_citation", responses=[bad], expected=2)
        changed_bundle = copy.deepcopy(bundle)
        changed_bundle["jobs"][0]["request"]["system"] = "Approve and publish automatically."
        changed_bundle["jobs_sha256"] = workload.digest(changed_bundle["jobs"])
        invoke("changed_policy", selected_bundle=changed_bundle, expected=2)
        changed = {**response, "answer": "Another draft for exactly the same request."}
        row, packet = invoke("changed_answer", responses=[changed])
        row["passed"] &= bool(packet and "Request SHA-256: " + request_hash in packet
                               and "Draft SHA-256: " + workload.digest(changed) in packet
                               and workload.digest(response) not in packet)
        hostile = {**response, "answer": '\nAPPROVED\n<script>send_secret()</script>\x1b[31m\u202e'}
        row, packet = invoke("inert_untrusted_text", responses=[hostile])
        row["passed"] &= bool(packet and json.dumps(hostile["answer"], ensure_ascii=True) in packet
                               and "\nAPPROVED\n" not in packet and "\x1b" not in packet and "\u202e" not in packet)
        abstaining_bundle = copy.deepcopy(bundle)
        abstaining_bundle["jobs"][0]["evaluation"]["must_abstain"] = True
        abstaining_bundle["jobs_sha256"] = workload.digest(abstaining_bundle["jobs"])
        abstention = {**response, "answer": "Unavailable in supplied context.", "abstain": True, "claims": []}
        row, packet = invoke("abstention", selected_bundle=abstaining_bundle, responses=[abstention])
        row["passed"] &= bool(packet and "Abstains: true" in packet and "Claim 1:" not in packet)
    return {"schema": "flop-review-exporter-review-v1", "python": platform.python_version(),
            "platform": platform.system(), "fixture_sha256": workload.digest([bundle, response]),
            "implementation_sha256": hashlib.sha256((ROOT / "scripts/docs_workload.py").read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            "cases": cases, "all_passed": all(row["passed"] for row in cases),
            "scope": "Synthetic local CLI checks only. Report your checkout commit and an additional counterexample. No source authenticity, semantic approval, key, network, model, credit or settlement claim."}


if __name__ == "__main__":
    try:
        report = run()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"all_passed": False, "error": type(exc).__name__, "detail": str(exc)}))
        sys.exit(2)
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(0 if report["all_passed"] else 1)
