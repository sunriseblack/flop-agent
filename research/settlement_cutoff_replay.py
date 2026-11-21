"""Replay pvthr33's proposed settlement grace period on saved devnet explorer pages."""

import argparse
import json
import re
from bisect import bisect_left
from collections import Counter
from pathlib import Path
from statistics import median


# Fixed comparison window. G is measured after each hypothetical cutoff.
HEIGHTS = range(3_100_000, 4_200_000, 997)
GRACE = (0, 250, 1_000, 3_600, 14_400)
GATEWAY = "5GsXb3TmNGixuEsbtixqHnqWr9UQJ2M8bkqBQWteNekgF98S"


def read_settled_items(folder):
    """Require a complete offset traversal and unique terminal rows."""
    rows = []
    seen = set()
    missing_event = []
    offset = 0
    total = None
    while total is None or offset < total:
        page = json.loads((folder / f"{offset}.json").read_bytes())
        meta = page["pagination"]
        if total is None:
            total = meta["total"]
        batch = page["data"]
        if (type(total) is not int or total <= 0 or meta["total"] != total
                or meta["limit"] != 100 or meta["offset"] != offset
                or len(batch) != min(100, total - offset)
                or meta["hasMore"] != (offset + len(batch) < total)):
            raise ValueError(f"inconsistent pagination at offset {offset}")
        for item in batch:
            key = item["channelId"]
            opened, settled = item["openedBlock"], item["statusBlockNumber"]
            if (not isinstance(key, str) or not re.fullmatch(r"0x[0-9a-f]{64}", key) or key in seen
                    or item["status"] != "settled" or item["paymentStatus"] != "PAID"
                    or item["observationHead"] != "finalized"
                    or type(opened) is not int or type(settled) is not int
                    or not 0 <= opened <= settled
                    or not isinstance(item["agent"], str) or not item["agent"]
                    or not isinstance(item["minerPaid"], str) or not re.fullmatch(r"[0-9]+", item["minerPaid"])):
                raise ValueError(f"invalid or duplicate settlement at offset {offset}")
            seen.add(key)
            terminal = item.get("settlement")
            if terminal is None:
                missing_event.append(key)
                continue
            if (terminal["event"] != "computeChannel.Settled"
                    or type(terminal["blockNumber"]) is not int
                    or settled != terminal["blockNumber"] or type(terminal["timestamp"]) is not int):
                raise ValueError(f"inconsistent settlement event at offset {offset}")
            rows.append(item)
        offset += len(batch)
    return rows, missing_event


def read_settlements(folder):
    items, missing = read_settled_items(folder)
    return [(item["openedBlock"], item["statusBlockNumber"], int(item["minerPaid"]),
             item["agent"] == GATEWAY, item["settlement"]["timestamp"])
            for item in items], missing


def summarize(rows, heights=HEIGHTS, grace=GRACE):
    """Count unique channels separately from channel/cutoff observations."""
    exposure = Counter()
    outside_raw = Counter()
    outside_channels = Counter()
    caught_per_height = [0] * len(heights)
    cohorts = {}
    for opened, settled, paid, gateway, _ in rows:
        cohort = "named_gateway" if gateway else "other_opener"
        group = cohorts.setdefault(cohort, {"lifetimes": [], "crossing_channels": 0,
                                            "exposures": 0, "exposed_miner_paid_raw": 0})
        group["lifetimes"].append(settled - opened)
        start = bisect_left(heights, opened)
        end = bisect_left(heights, settled)
        if end > start:
            group["crossing_channels"] += 1
            for g in grace:
                if settled > heights[start] + g:
                    outside_channels[g] += 1
        group["exposures"] += end - start
        group["exposed_miner_paid_raw"] += (end - start) * paid
        for i in range(start, end):
            caught_per_height[i] += 1
            residual = settled - heights[i]
            for g in grace:
                if residual > g:
                    exposure[g] += 1
                    outside_raw[g] += paid
    for group in cohorts.values():
        lifetimes = group.pop("lifetimes")
        group["exposed_miner_paid_raw"] = str(group["exposed_miner_paid_raw"])
        group["settlements"] = len(lifetimes)
        group["median_lifetime_blocks"] = median(lifetimes)
    return {"cutoffs": len(heights), "median_crossing_channels": median(caught_per_height),
            "cohorts": cohorts, "outside_grace": [
                {"blocks": g, "channel_cutoff_pairs": exposure[g], "distinct_channels": outside_channels[g],
                 "miner_paid_raw_across_pairs": str(outside_raw[g])} for g in grace]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="directory of saved 100-row settled pages named OFFSET.json")
    parser.add_argument("--through-ms", type=int, help="inclusive explorer settlement timestamp in Unix milliseconds")
    args = parser.parse_args()
    try:
        rows, missing = read_settlements(args.pages)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"unusable settled-page capture: {exc}")
    eligible = [r for r in rows if args.through_ms is None or r[4] <= args.through_ms]
    if not eligible:
        parser.error("no settlements in the selected time window")
    print(json.dumps({"source_rows": len(rows) + len(missing), "missing_event_ids": missing,
                      "included_settlements": len(eligible),
                      "through_ms": args.through_ms, "first_cutoff": HEIGHTS[0],
                      "last_cutoff": HEIGHTS[-1], **summarize(eligible)}, indent=2))


if __name__ == "__main__":
    main()
