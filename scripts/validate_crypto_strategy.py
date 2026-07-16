#!/usr/bin/env python3
"""Validate the crypto strategy's execution and anti-repainting contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED_SNIPPETS = {
    "Pine Script v6": "//@version=6",
    "backtest begins on 1 January 2018": 'timestamp("2018-01-01 00:00 +0000")',
    "commission is 0.1 percent": "commission_value = 0.1",
    "slippage is one tick": "slippage = 1",
    "pyramiding is disabled": "pyramiding = 0",
    "orders fill after the completed signal bar": "process_orders_on_close = false",
    "intrabar recalculation is disabled": "calc_on_every_tick = false",
    "order-fill recalculation is disabled": "calc_on_order_fills = false",
    "non-standard charts use standard OHLC fills": "fill_orders_on_standard_ohlc = true",
    "signals require confirmed bars": "barstate.isconfirmed",
    "confirmed weekly data uses the previous close": "     close[1],\n     lookahead = barmerge.lookahead_on",
    "weekly fast EMA uses a confirmed offset": "ta.ema(close, cycleFastLength)[1]",
    "weekly slow EMA uses a confirmed offset": "ta.ema(close, cycleSlowLength)[1]",
    "weekly slope comparison uses a confirmed offset": "ta.ema(close, cycleSlowLength)[1 + cycleSlopeWeeks]",
    "higher-timeframe requests use paired lookahead": "lookahead = barmerge.lookahead_on",
    "hard drawdown protection exists": "strategy.risk.max_drawdown",
    "loss-streak protection exists": "maximumConsecutiveLosses",
    "position size is drawdown-compatible by default": 'input.float(30.0, "Position size (% of equity)"',
    "oversold recovery entries exist": "oversoldRecovery",
    "early cycle entries exist": "recentBullishCycleTurn",
    "partial exits are optional": "usePartialExit",
    "partial exits cannot repeat after filling": "partialTaken",
    "completed positions are tracked independently": "completedPositions",
    "break-even protection exists": "breakEvenActivationPercent",
    "entry is protected before the next calculation": 'strategy.cancel("Entry protection")',
    "Smart Hold state exists": "smartHoldActive",
    "orders include webhook messages": "alert_message = orderMessage",
}

FORBIDDEN_SNIPPETS = {
    "strategy alertcondition calls have no effect": "alertcondition(",
    "same-bar order processing is unrealistic": "process_orders_on_close = true",
    "tick recalculation can diverge from historical bars": "calc_on_every_tick = true",
    "order-fill recalculation can create unrealistic same-bar decisions": "calc_on_order_fills = true",
    "short selling is outside this long-only design": "strategy.short",
}

TYPED_FUNCTION_RETURN = re.compile(
    r"(?m)^\s*(?:bool|int|float|string|color)\s+[A-Za-z_]\w*\s*\([^\n]*\)\s*=>"
)


def validate(source: str) -> list[str]:
    """Return human-readable contract violations."""
    failures: list[str] = []
    for description, snippet in REQUIRED_SNIPPETS.items():
        if snippet not in source:
            failures.append(f"missing: {description} ({snippet!r})")
    for description, snippet in FORBIDDEN_SNIPPETS.items():
        if snippet in source:
            failures.append(f"forbidden: {description} ({snippet!r})")

    security_calls = source.count("request.security(")
    paired_lookaheads = source.count("lookahead = barmerge.lookahead_on")
    if security_calls != 4:
        failures.append(f"expected exactly four reviewed weekly requests, found {security_calls}")
    if paired_lookaheads != security_calls:
        failures.append("every higher-timeframe request must use paired lookahead_on")
    if "lookahead = barmerge.lookahead_off" in source:
        failures.append("lookahead_off higher-timeframe values can repaint before confirmation")
    if source.count("strategy(") != 1:
        failures.append("expected exactly one strategy() declaration")
    if TYPED_FUNCTION_RETURN.search(source):
        failures.append("Pine function headers cannot declare a return type")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("strategy", type=Path)
    args = parser.parse_args()

    failures = validate(args.strategy.read_text(encoding="utf-8"))
    if failures:
        print("Crypto strategy contract validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Crypto strategy contract validation passed: {args.strategy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
