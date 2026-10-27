#!/usr/bin/env python3
"""Bounded offline reproduction of an unavailable-to-zero report in a peer tool.

Target: danenright/flop-agent-runner at 547b4d6fa419311bcfc4c6dc157f72d0fe8974bb.
The source remains in that Apache-2.0 repository. Supply its exact flop_agent.py.
Only four reviewed functions are compiled; module initialization, signing,
state access, CLI execution and actual network requests are excluded.
This probe observes the original behavior. It is not a repaired implementation.
"""

import ast
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import urllib.parse


SOURCE_SHA256 = "5eee57d8ebde22a6454b6e0f5e7be3d792522991c83f452ef5ec79af3161cef7"
FUNCTIONS = {"credit_report", "inference_spend_for", "explorer_fetch", "raw_to_flop"}


def probe(source):
    raw = Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("expected the exact reviewed source revision")
    tree = ast.parse(raw)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in FUNCTIONS]
    if {n.name for n in functions} != FUNCTIONS or len(functions) != len(FUNCTIONS):
        raise ValueError("reviewed function set differs")
    namespace = {"Network": SimpleNamespace, "AgentError": RuntimeError, "urllib": urllib,
                 "resolve_subject": lambda s: (None, s),
                 "error_text": lambda status, body: str(status)}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), namespace)
    network = SimpleNamespace(name="devnet", explorer_url="https://example.invalid/api")
    address = "public-account-control"
    zero = {"totalSpentRaw": "0", "channelCount": 0, "settledChannels": 0}
    one = {"totalSpentRaw": "1000000000000000000", "channelCount": 1, "settledChannels": 1}
    paid = {"agent": address, "channelId": "c", "status": "settled", "paymentStatus": "PAID",
            "minerPaid": "1000000000000000000"}
    inputs = [("explicit-zero", 200, zero, []), ("missing-spend-404", 404, {}, []),
              ("missing-spend-404-but-paid-channel", 404, {}, [paid]),
              ("missing-fields-200", 200, {}, []), ("unavailable-503", 503, {}, []),
              ("positive-one", 200, one, [paid])]
    rows = []
    for name, status, spend, channels in inputs:
        calls = []

        def http(method, url):
            assert method == "GET"
            calls.append(url)
            if url.endswith("/inference-spend"):
                return status, spend
            if "/compute-channels?" in url:
                return 200, {"data": channels}
            return 200, {"balance": "0"}

        namespace["http_json"] = http
        try:
            report = namespace["credit_report"](network, address)
            result = {"case": name, "result": report}
        except RuntimeError as exc:
            result = {"case": name, "error": str(exc)}
        rows.append({**result, "mock_gets": len(calls)})
    assert rows[0]["result"]["credited_inference_spend_flop"] == 0
    assert rows[1]["result"]["verdict"] == rows[0]["result"]["verdict"]
    assert rows[2]["result"]["settled_channels"] == 0
    assert len(rows[2]["result"]["recent_channels"]) == 1
    assert rows[3]["result"]["credited_inference_spend_flop"] is None
    assert "No settled" in rows[3]["result"]["verdict"]
    assert "503" in rows[4]["error"]
    assert rows[5]["result"]["settled_channels"] == 1
    return {"source_sha256": SOURCE_SHA256, "cases": rows, "network_requests": 0,
            "signing_or_state_access": False, "scope": "original diagnostic behavior, not a fix or allocation evidence"}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: runner_credit_probe_2026_10_27.py EXACT_FLOP_AGENT_PY")
    print(json.dumps(probe(sys.argv[1]), indent=2))
