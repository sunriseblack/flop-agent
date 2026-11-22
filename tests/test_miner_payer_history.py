import unittest

from research.miner_payer_history import GATEWAY, replay


def row(key, time, miner, opener, paid="100", model="model-A"):
    return {"channelId": key, "settlement": {"timestamp": time}, "miner": miner,
            "agent": opener, "minerPaid": paid, "modelHash": model}


class MinerPayerHistoryTests(unittest.TestCase):
    def test_only_prior_evidence_can_change_label(self):
        rows = [row("past", 9, "m", "p"), row("first", 10, "m", "q"),
                row("again", 19, "m", "q", model="model-B"), row("future", 20, "m", "r")]
        result = replay(rows, 10, 20)
        self.assertEqual(result["transitions"], [
            {"study_only": "one_other_opener", "including_prior_history": "multiple_openers",
             "miners": 1, "settlements": 2, "miner_paid_raw": "200"}])
        control = replay([row("past", 9, "m", "q"), *rows[1:]], 10, 20)
        self.assertEqual(control["cohort_sha256"], result["cohort_sha256"])
        self.assertEqual(control["transitions"][0]["including_prior_history"], "one_other_opener")
        self.assertEqual(replay(list(reversed(rows)), 10, 20), result)

    def test_gateway_and_other_openers_with_zero_and_equal_address_controls(self):
        rows = [row("old", 9, "old_m", "old_p"), row("gw", 10, "m", GATEWAY),
                row("zero", 15, "m", "other", paid="0"), row("same", 16, "m", "m"),
                row("a", 12, "n", GATEWAY), row("b", 18, "n", "p", paid=str(10**25)),
                row("later", 20, "m", "p")]
        result = replay(rows, 10, 20)
        expected = [("multiple_openers", 2, str(10**25 + 100)), ("named_gateway_only", 1, "100")]
        self.assertEqual([(t["study_only"], t["settlements"], t["miner_paid_raw"])
                          for t in result["transitions"]], expected)
        self.assertTrue(all(t["study_only"] == t["including_prior_history"] for t in result["transitions"]))
        self.assertEqual((result["miners"], result["settlements"], result["miner_paid_raw"]),
                         (2, 3, str(10**25 + 200)))

    def test_uncovered_window_or_unusable_cohort(self):
        past, active, future = row("p", 9, "m", "a"), row("a", 15, "m", "b"), row("f", 20, "m", "c")
        for rows in ([active, future], [past, active], [past, future],
                     [past, dict(active, miner=""), future]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                replay(rows, 10, 20)
