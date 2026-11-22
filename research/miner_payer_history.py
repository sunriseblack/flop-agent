"""Measure how the payer lookback changes labels on a fixed set of devnet settlements."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

if __package__:
    from .settlement_cutoff_replay import GATEWAY, read_settled_items
else:
    from settlement_cutoff_replay import GATEWAY, read_settled_items


# 14 Nov 00:00 through 21 Nov 09:00 (exclusive), UTC+7, across all models.
START_MS = 1_794_589_200_000
END_MS = 1_795_226_400_000


def payer_group(openers):
    if len(openers) > 1:
        return "multiple_openers"
    if openers == {GATEWAY}:
        return "named_gateway_only"
    return "one_other_opener"


def replay(items, start_ms, end_ms):
    """Compare opener counts at period end, allowing or omitting pre-period history."""
    times = [row["settlement"]["timestamp"] for row in items]
    if not times or not min(times) < start_ms < end_ms <= max(times):
        raise ValueError("capture must span the study window and contain earlier history")

    entire_history = defaultdict(set)
    study_openers = defaultdict(set)
    study_counts = Counter()
    study_paid = Counter()
    channel_ids = []
    for row in items:
        timestamp = row["settlement"]["timestamp"]
        if timestamp >= end_ms:
            continue
        miner, opener, paid = row["miner"], row["agent"], int(row["minerPaid"])
        if not isinstance(miner, str) or not miner.strip():
            raise ValueError("missing miner address")
        if miner == opener or paid == 0:
            continue
        entire_history[miner].add(opener)
        if timestamp >= start_ms:
            study_openers[miner].add(opener)
            study_counts[miner] += 1
            study_paid[miner] += paid
            channel_ids.append(row["channelId"])
    if not channel_ids:
        raise ValueError("no qualifying settlements in the study window")

    transitions = defaultdict(Counter)
    for miner, openers in study_openers.items():
        pair = payer_group(openers), payer_group(entire_history[miner])
        group = transitions[pair]
        group["miners"] += 1
        group["settlements"] += study_counts[miner]
        group["miner_paid_raw"] += study_paid[miner]

    # Sort full channel IDs as ASCII, one per line including the final newline.
    manifest = "".join(key + "\n" for key in sorted(channel_ids))
    return {
        "start_inclusive_ms": start_ms, "end_exclusive_ms": end_ms,
        "first_observed_settlement_ms": min(times), "last_observed_settlement_ms": max(times),
        "miners": len(study_openers), "settlements": len(channel_ids),
        "miner_paid_raw": str(sum(study_paid.values())),
        "cohort_sha256": hashlib.sha256(manifest.encode("ascii")).hexdigest(),
        "named_gateway": GATEWAY,
        "transitions": [
            {"study_only": short, "including_prior_history": long,
             "miners": group["miners"], "settlements": group["settlements"],
             "miner_paid_raw": str(group["miner_paid_raw"])}
            for (short, long), group in sorted(transitions.items())
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="directory of complete saved 100-row settled pages named OFFSET.json")
    args = parser.parse_args()
    try:
        items, missing = read_settled_items(args.pages)
        report = replay(items, START_MS, END_MS)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"unusable settlement capture: {exc}")
    print(json.dumps({"source_rows": len(items) + len(missing),
                      "missing_terminal_events": len(missing), **report}, indent=2))


if __name__ == "__main__":
    main()
