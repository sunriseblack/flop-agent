"""Replay the paid-channel estimate in Yellow Paper #293 using two clocks."""

import argparse
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

if __package__:
    from .settlement_cutoff_replay import read_settled_items
else:
    from settlement_cutoff_replay import read_settled_items


# Half-open interval of post-block states, with timestamp.now at each endpoint.
BLOCKS = (3_858_556, 4_234_248)
CLOCK_MS = (1_794_796_928_001, 1_795_224_762_000)
RAW_PER_FLOP = 10**18


def ratio(n, d):
    return format(Decimal(n) / Decimal(d), ".8f") if d else None


def profile(intervals, start, end):
    """Sweep half-open intervals. Quantiles weight the time spent at each level."""
    changes = Counter({start: 0, end: 0})
    for lo, hi, amount in intervals:
        if hi < lo or amount < 0:
            raise ValueError("invalid interval or amount")
        left, right = max(start, lo), min(end, hi)
        if left < right:
            changes[left] += amount
            changes[right] -= amount
    heights = sorted(changes)
    level = 0
    peak = -1
    peak_at = start
    durations = Counter()
    for lo, hi in zip(heights, heights[1:]):
        level += changes[lo]
        durations[level] += hi - lo
        if level > peak:
            peak, peak_at = level, lo

    width = end - start
    if width <= 0 or sum(durations.values()) != width or level + changes[end] != 0:
        raise ValueError("unbalanced or empty window")
    area = sum(value * elapsed for value, elapsed in durations.items())
    cumulative = 0
    for value, elapsed in sorted(durations.items()):
        cumulative += elapsed
        if cumulative * 100 >= 95 * width:
            p95 = value
            break
    return {"duration": width, "area_raw": str(area), "mean_flop": ratio(area, width * RAW_PER_FLOP),
            "p95_raw": str(p95), "peak_raw": str(peak), "first_peak": peak_at}


def replay(items, blocks=BLOCKS, clock=CLOCK_MS):
    start, end = blocks
    t0, t1 = clock
    if start >= end or t0 >= t1:
        raise ValueError("invalid study window")
    if not items or min(r["statusBlockNumber"] for r in items) >= start or max(
            r["statusBlockNumber"] for r in items) < end:
        raise ValueError("capture does not span the specified blocks")

    contained = []
    overlap = []
    for r in items:
        lo, hi = r["openedBlock"], r["statusBlockNumber"]
        if lo >= end or hi < start:
            continue
        if hi == start and lo < start:
            continue
        opened, settled = r.get("openedAt"), r["settlement"]["timestamp"]
        if (type(opened) is not int or type(settled) is not int or opened > settled
                or (lo < start) != (opened < t0) or not (opened < t1 and settled >= t0)
                or (hi < end) != (settled < t1)):
            raise ValueError("block and timestamp windows disagree or a timestamp is unusable")
        row = (lo, hi, opened, settled, int(r["minerPaid"]), r["channelId"])
        overlap.append(row)
        if start <= lo and hi < end:
            contained.append(row)
    if not contained:
        raise ValueError("no contained settlements")

    paid = sum(row[4] for row in contained)
    by_block = profile([(r[0], r[1], r[4]) for r in contained], start, end)
    by_time = profile([(r[2], r[3], r[4]) for r in contained], t0, t1)
    by_block["turnovers_per_86400_blocks"] = ratio(paid * 86_400, int(by_block["area_raw"]))
    by_time["turnovers_per_utc_day"] = ratio(paid * 86_400_000, int(by_time["area_raw"]))
    clipped = profile([(r[0], r[1], r[4]) for r in overlap], start, end)
    peak = clipped["first_peak"]
    peak_ids = sorted(r[5] for r in overlap if r[0] <= peak < r[1])
    return {"start_block": start, "end_block_exclusive": end, "start_ms": t0, "end_ms": t1,
            "contained_channels": len(contained), "contained_miner_paid_raw": str(paid),
            "contained_by_block": by_block, "contained_by_timestamp": by_time,
            "overlapping_channels": len(overlap), "overlapping_by_block": clipped,
            "peak_channel_ids": peak_ids,
            "peak_ids_sha256": hashlib.sha256("".join(i + "\n" for i in peak_ids).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="saved 100-row settled pages named by offset")
    args = parser.parse_args()
    try:
        items, missing = read_settled_items(args.pages)
        result = replay(items)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(f"unusable capture: {exc}")
    print(json.dumps({"captured_rows": len(items) + len(missing), "missing_events": len(missing),
                      **result}, indent=2))


if __name__ == "__main__":
    main()
