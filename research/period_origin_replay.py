"""Compare scoring-period origins over a fixed capture of devnet settlements."""

import argparse
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

if __package__:
    from .settlement_cutoff_replay import read_settled_items
else:
    from settlement_cutoff_replay import read_settled_items


PERIOD = 86_400
END = 49 * PERIOD
THROUGH_MS = 1_795_225_680_000
PHASES = (0, PERIOD // 4, PERIOD // 2, 3 * PERIOD // 4)


def allocate(rows, start, end, period, phase, proportional=False):
    """Give each bucket its clipped block or spend weight. None holds the empty budget."""
    if not (0 <= start < end and period > 0 and 0 <= phase < period):
        raise ValueError("invalid block window or grid")
    buckets = defaultdict(Counter)
    total = 0
    for block, opener, amount in rows:
        if not start <= block < end:
            continue
        if amount < 0 or not opener:
            raise ValueError("invalid observation")
        buckets[(block - phase) // period][opener] += amount
        total += amount
    if not total:
        raise ValueError("window has no positive spend")
    result = Counter()
    empty = 0
    first, last = (start - phase) // period, (end - 1 - phase) // period
    for index in range(first, last + 1):
        lower = phase + index * period
        width = min(end, lower + period) - max(start, lower)
        spend = buckets[index]
        volume = sum(spend.values())
        budget = Fraction(volume, total) if proportional else Fraction(width, end - start)
        if volume == 0:
            empty += 1
            if budget:
                result[None] += budget
        else:
            for opener, amount in spend.items():
                result[opener] += budget * Fraction(amount, volume)
    if sum(result.values()) != 1:
        raise ValueError("pool did not balance")
    return result, empty, last - first + 1


def compare(reference, alternative):
    changes = {k: abs(reference[k] - alternative[k]) for k in reference.keys() | alternative.keys()}
    return sum(changes.values()) / 2, max(value for key, value in changes.items() if key is not None)


def pct(value):
    return round(float(100 * value), 6)


def replay(items, start, end):
    within = [r for r in items if start <= r["statusBlockNumber"] < end]
    weights = {"escrow": [], "minerPaid": []}
    self_rows = 0
    for r in within:
        if (r.get("cooperative") is not True or not isinstance(r["miner"], str) or not r["miner"]
                or not isinstance(r["escrow"], str) or not re.fullmatch(r"[0-9]+", r["escrow"])):
            raise ValueError("incompatible settlement in window")
        if r["miner"] == r["agent"]:
            self_rows += 1
            continue
        for field, rows in weights.items():
            rows.append((r["statusBlockNumber"], r["agent"], int(r[field])))
    opener_count = len({opener for _, opener, _ in weights["escrow"]})
    results = {}
    for field, rows in weights.items():
        reference, _, _ = allocate(rows, start, end, PERIOD, 0)
        totals = Counter()
        for _, opener, amount in rows:
            totals[opener] += amount
        total = sum(totals.values())
        season = {opener: Fraction(amount, total) for opener, amount in totals.items()}
        results[field] = []
        for phase in PHASES:
            vector, empty, count = allocate(rows, start, end, PERIOD, phase)
            control, _, _ = allocate(rows, start, end, PERIOD, phase, proportional=True)
            if control != Counter(season):
                raise ValueError("spend-weighted grid disagrees with season totals")
            moved, largest = compare(reference, vector)
            results[field].append({"offset": phase, "buckets": count, "empty_buckets": empty,
                                   "reserve_pct": pct(vector[None]), "pool_moved_pct": pct(moved),
                                   "largest_opener_change_pp": pct(largest)})
    return {"start_inclusive": start, "end_exclusive": end, "included_rows": len(weights["escrow"]),
            "excluded_equal_addresses": self_rows, "openers": opener_count, "weights": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="directory containing complete 100-row settled pages")
    args = parser.parse_args()
    try:
        items, missing = read_settled_items(args.pages)
        through = [r for r in items if r["settlement"]["timestamp"] <= THROUGH_MS]
        if not through or max(r["statusBlockNumber"] for r in through) < END:
            raise ValueError("capture does not cover the end of the specified window")
        windows = [replay(through, start, END) for start in (0, END - 14 * PERIOD)]
    except (OSError, KeyError, ValueError, TypeError) as exc:
        parser.error(f"unusable capture: {exc}")
    print(json.dumps({"captured_rows": len(items) + len(missing), "missing_terminal_events": len(missing),
                      "after_time_cut": len(items) - len(through), "through_ms": THROUGH_MS,
                      "period_blocks": PERIOD, "windows": windows}, indent=2))


if __name__ == "__main__":
    main()
