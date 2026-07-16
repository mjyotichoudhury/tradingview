#!/usr/bin/env python3
"""Validate the Pine strategy's non-repainting and risk-control contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REQUIRED_SNIPPETS = {
    "Pine Script v6": "//@version=6",
    "orders execute after the completed signal bar": "process_orders_on_close = false",
    "intrabar recalculation is disabled": "calc_on_every_tick = false",
    "signals require confirmed bars": "barstate.isconfirmed",
    "daily filter uses a confirmed value": "ta.ema(close, trendLength)[1]",
    "higher-timeframe request uses paired lookahead": "lookahead = barmerge.lookahead_on",
    "breakout high excludes the current bar": "ta.highest(high, breakoutLength)[1]",
    "breakout low excludes the current bar": "ta.lowest(low, breakoutLength)[1]",
    "intraday loss control exists": "strategy.risk.max_intraday_loss",
    "drawdown control exists": "strategy.risk.max_drawdown",
    "position-size cap exists": "strategy.risk.max_position_size",
    "orders have webhook messages": "alert_message = orderMessage",
}

FORBIDDEN_SNIPPETS = {
    "strategy alertcondition calls have no effect": "alertcondition(",
    "same-bar order processing can inflate results": "process_orders_on_close = true",
    "tick recalculation can diverge from historical bars": "calc_on_every_tick = true",
}


def validate(source: str) -> list[str]:
    """Return human-readable contract violations."""
    failures: list[str] = []
    for description, snippet in REQUIRED_SNIPPETS.items():
        if snippet not in source:
            failures.append(f"missing: {description} ({snippet!r})")
    for description, snippet in FORBIDDEN_SNIPPETS.items():
        if snippet in source:
            failures.append(f"forbidden: {description} ({snippet!r})")

    if source.count("strategy(") != 1:
        failures.append("expected exactly one strategy() declaration")
    if source.count("request.security(") != 1:
        failures.append("expected exactly one reviewed higher-timeframe request")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("strategy", type=Path)
    args = parser.parse_args()

    source = args.strategy.read_text(encoding="utf-8")
    failures = validate(source)
    if failures:
        print("Strategy contract validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Strategy contract validation passed: {args.strategy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
