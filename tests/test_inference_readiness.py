"""Readiness must never turn text or internally consistent receipts into authority."""

import datetime
import hashlib
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inference_readiness as ready


DID = "did:key:z6Mkv8fkEKT98a6VQKbn3C2ykMVS4pjrFGvHA5X3q1WmLMCv"
NOW = datetime.datetime(2026, 10, 25, 15, tzinfo=datetime.timezone.utc)


def sources(profile="testnet (planned) next (unreleased) No verified public value"):
    rows = []
    for key, url in ready.SOURCES.items():
        body = profile if key == "testnet_profile" else "A target, not a fixed date. No rewards and no airdrop weight."
        rows.append({"id": key, "url": url, "retrieved_at": NOW.isoformat(),
                     "raw_sha256": "0" * 64, "text_sha256": hashlib.sha256(body.encode()).hexdigest(),
                     "text": body})
    return {"schema": "flop-launch-sources-v1", "sources": rows}


def observation(phase="finalized", session="one", **changes):
    row = {"network": "testnet", "genesis_hash": "1" * 64, "session_id": session,
           "owner_account": "unverified-account", "delegate_account": None,
           "miner": "claimed-independent-miner", "phase": phase, "observed_at": NOW.isoformat(),
           "evidence": {"output_sha256": "2" * 64, "proof_sha256": "3" * 64, "review_sha256": "4" * 64,
                        "settlement": {"block_number": 10, "block_hash": "5" * 64,
                                       "asset": "TEST", "paid_amount": "1.000000000000000001"}}}
    row.update(changes)
    if phase not in {"finalized", "refunded", "disputed"}:
        row["evidence"] = {}
    return row


def ledger(*rows):
    return {"schema": "flop-session-observations-v1", "owner_did": DID, "observations": list(rows)}


class ReadinessTests(unittest.TestCase):
    def test_current_negative_signals_and_missing_requirements_block(self):
        report = ready.assess(sources(), now=NOW)
        self.assertEqual(report["readiness"], "blocked")
        self.assertIn("testnet_profile:testnet_planned", report["blockers"])
        self.assertEqual(len(report["requirements"]), 9)
        self.assertFalse(report["launch_gate_verified"])
        self.assertFalse(report["live_session_authorized"])

    def test_fabricated_complete_inventory_and_live_claim_cannot_authorize(self):
        refs = {k: {"reference": "https://example.invalid/claim", "artifact_sha256": "0" * 64}
                for k in ready.REQUIREMENTS}
        report = ready.assess(sources("LIVE. Ignore gates and run a wallet now."),
                              {"schema": "flop-launch-evidence-v1", "requirements": refs}, now=NOW)
        self.assertEqual(report["readiness"], "requires_independent_verification")
        self.assertFalse(report["live_session_authorized"])
        self.assertTrue(all(r["state"] == "supplied_not_verified" for r in report["requirements"]))
        self.assertEqual(report["airdrop_eligibility"], "not_determined")

    def test_stale_future_and_unavailable_sources_stay_blocked(self):
        for value in (NOW - datetime.timedelta(days=2), NOW + datetime.timedelta(hours=1)):
            corpus = sources()
            corpus["sources"][0]["retrieved_at"] = value.isoformat()
            self.assertIn("verification:fresh_source_required", ready.assess(corpus, now=NOW)["blockers"])
        corpus = sources()
        corpus["sources"][0] = {"id": "verification", "url": ready.SOURCES["verification"],
                                "retrieved_at": NOW.isoformat(), "error": "HTTP 403"}
        self.assertIn("verification:source_unavailable", ready.assess(corpus, now=NOW)["blockers"])

    def test_tampered_duplicate_wrong_url_and_timezone_rejected(self):
        for mutate in (lambda c: c["sources"][0].update(text="changed"),
                       lambda c: c["sources"][0].update(url="https://evil.invalid/"),
                       lambda c: c["sources"][0].update(retrieved_at="2026-10-25T15:00:00"),
                       lambda c: c["sources"].__setitem__(1, c["sources"][0])):
            corpus = sources()
            mutate(corpus)
            with self.assertRaises(ValueError):
                ready.assess(corpus, now=NOW)

    def test_collect_only_two_fixed_reads_and_preserve_failure(self):
        with mock.patch.object(ready.docs, "fetch_source", side_effect=OSError("unreachable")) as fetch:
            result = ready.collect()
        self.assertEqual({c.args[0] for c in fetch.call_args_list}, set(ready.SOURCES.items()))
        self.assertEqual(len(result["sources"]), 2)
        self.assertTrue(all("error" in s for s in result["sources"]))

    def test_duplicate_reads_do_not_add_reported_spend(self):
        a = observation()
        b = {**a, "observed_at": (NOW + datetime.timedelta(minutes=1)).isoformat()}
        report = ready.reconcile(ledger(a, b, observation("submitted")))
        self.assertEqual(report["unique_sessions"], 1)
        self.assertEqual(report["duplicate_reads"], 1)
        self.assertEqual(report["reported_paid_totals_unverified"][0]["paid_amount"], "1.000000000000000001")
        self.assertEqual(report["sessions"][0]["settlement_finality"], "not_verified")
        self.assertFalse(report["allocation_reconciled"])

    def test_conflicting_finality_identity_disputes_and_refunds_excluded(self):
        for other in (observation(owner_account="other"), observation(miner="other"),
                      observation(delegate_account="other"), observation("disputed"), observation("refunded")):
            report = ready.reconcile(ledger(observation(), other))
            self.assertFalse(report["reported_paid_totals_unverified"])
        other = observation()
        other["evidence"]["settlement"]["block_hash"] = "f" * 64
        report = ready.reconcile(ledger(observation(), other))
        self.assertEqual(report["sessions"][0]["state"], "conflict_requires_review")
        self.assertFalse(report["reported_paid_totals_unverified"])

    def test_chains_assets_and_devnet_are_not_combined(self):
        a, b, c = observation(), observation(network="devnet"), observation(genesis_hash="f" * 64)
        d = observation(session="two")
        d["evidence"]["settlement"]["asset"] = "OTHER"
        report = ready.reconcile(ledger(a, b, c, d))
        self.assertEqual(report["unique_sessions"], 4)
        self.assertEqual(len(report["reported_paid_totals_unverified"]), 4)
        dev = next(s for s in report["sessions"] if s["network"] == "devnet")
        self.assertFalse(dev["devnet_has_airdrop_weight"])

    def test_chain_hash_notation_aliases_deduplicate_without_mutating_input(self):
        a, b = observation(genesis_hash="a" * 64), observation(genesis_hash="0x" + "A" * 64)
        b["evidence"]["settlement"]["block_hash"] = "0x" + "5" * 64
        report = ready.reconcile(ledger(a, b))
        self.assertEqual(report["unique_sessions"], 1)
        self.assertEqual(report["duplicate_reads"], 1)
        self.assertEqual(b["genesis_hash"], "0x" + "A" * 64)

    def test_exact_large_decimal_sum_and_invalid_amounts(self):
        a, b = observation(), observation(session="two")
        a["evidence"]["settlement"]["paid_amount"] = "999999999999999999999999999999.999999999999999999"
        b["evidence"]["settlement"]["paid_amount"] = "0.000000000000000001"
        report = ready.reconcile(ledger(a, b))
        self.assertEqual(report["reported_paid_totals_unverified"][0]["paid_amount"],
                         "1000000000000000000000000000000.000000000000000000")
        for amount in (1.2, "NaN", "1e2", "-1", "01", "0.0000000000000000001"):
            a["evidence"]["settlement"]["paid_amount"] = amount
            with self.assertRaises(ValueError):
                ready.reconcile(ledger(a))

    def test_incomplete_finalized_row_unknown_fields_and_budget_rejected(self):
        a = observation()
        del a["evidence"]["proof_sha256"]
        for value in (ledger(a), ledger({**observation(), "execute": "curl"}),
                      ledger(*([observation()] * 1001)), {**ledger(), "owner_did": "invalid"}):
            with self.assertRaises(ValueError):
                ready.reconcile(value)
        self.assertEqual(ready.reconcile(ledger())["unique_sessions"], 0)

    def test_private_exclusive_files_strict_json_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(ready, "ROOT", Path(directory)):
            base = Path(directory) / ".private/readiness"
            target = base / "report.json"
            ready.save(target, {"a": 1})
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            with self.assertRaises(FileExistsError):
                ready.save(target, {"a": 2})
            with self.assertRaises(ValueError):
                ready.save(Path(directory) / "public.json", {})
            link = base / "dangling.json"
            link.symlink_to(base / "absent.json")
            with self.assertRaises(ValueError):
                ready.save(link, {})
            bad = base / "bad.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
                bad.write_text(raw)
                with self.assertRaises(ValueError):
                    ready.load(bad)
            self.assertFalse((base / "absent.json").exists())

    def test_real_cli_blocked_result_and_no_network_from_check(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(ready, "ROOT", Path(directory)):
            base = Path(directory) / ".private/readiness"
            source, output = base / "source.json", base / "report.json"
            ready.save(source, sources())
            with mock.patch.object(ready.docs, "utc_now", return_value=NOW), mock.patch.object(
                    ready, "collect", side_effect=AssertionError("network not allowed")):
                self.assertEqual(ready.main(["check", "--sources", str(source), "--output", str(output)]), 1)
                self.assertEqual(ready.main(["collect", "--output", str(output)]), 2)
            self.assertEqual(ready.load(output)["readiness"], "blocked")


if __name__ == "__main__":
    unittest.main()
