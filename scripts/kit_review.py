#!/usr/bin/env python3
"""One-command offline smoke-test packet for independent kit reviewers."""

import copy
import hashlib
import json
import pathlib
import platform
import sys

from submission_evidence import assess_packet, strict_json


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run():
    fixture = ROOT / "examples/submission-evidence-flop-327293.json"
    raw = fixture.read_bytes()
    original = strict_json(raw)
    did = original["submission"]["from"]
    cases = []
    def check(name, packet, verified, readback=None):
        result = assess_packet(packet, did)
        observed = {"evidence_verified": result["evidence_verified"],
                    "readback": result.get("native_readback", {}).get("state"),
                    "credit": result["credit_for_submission"]}
        passed = (observed["evidence_verified"] is verified and observed["credit"] == "not_determined"
                  and (readback is None or observed["readback"] == readback))
        cases.append({"case": name, "passed": passed, "observed": observed})
    check("original", original, True, "exact_fields_match_in_supplied_snapshot")
    changed = copy.deepcopy(original)
    changed["submission"]["text"] += "!"
    check("changed_signed_text", changed, False)
    changed = copy.deepcopy(original)
    changed["room"] = "lobby"
    check("wrong_room", changed, False)
    changed = copy.deepcopy(original)
    changed["submission"]["seq"] = 777
    check("changed_unsigned_sequence", changed, True, "signed_content_at_different_or_missing_sequence")
    changed = copy.deepcopy(original)
    changed["host_score"] = {"ok": True, "did": did, "score": 999, "found": True, "engine_warm": True}
    check("aggregate_score_is_not_submission_credit", changed, True, "exact_fields_match_in_supplied_snapshot")
    return {"schema": "flop-kit-review-v1", "python": platform.python_version(),
            "fixture_sha256": hashlib.sha256(raw).hexdigest(),
            "implementation_sha256": hashlib.sha256((ROOT / "scripts/submission_evidence.py").read_bytes()).hexdigest(),
            "cases": cases, "all_passed": all(case["passed"] for case in cases),
            "scope": "Offline smoke test only. Report your checkout commit and any additional counterexample; no key, network, credit or eligibility check."}


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(0 if report["all_passed"] else 1)
