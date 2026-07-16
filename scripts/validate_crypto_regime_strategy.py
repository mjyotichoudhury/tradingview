#!/usr/bin/env python3
"""Validate the regime strategy's execution, sizing, and anti-repainting contract."""

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
    "standard OHLC fills are required": "fill_orders_on_standard_ohlc = true",
    "signals require confirmed bars": "barstate.isconfirmed",
    "confirmed weekly close is offset": "     close[1],\n     lookahead = barmerge.lookahead_on",
    "weekly fast EMA is offset": "ta.ema(close, cycleFastLength)[1]",
    "weekly slow EMA is offset": "ta.ema(close, cycleSlowLength)[1]",
    "weekly slope comparison is offset": "ta.ema(close, cycleSlowLength)[1 + cycleSlopeWeeks]",
    "long trading exists": "strategy.long",
    "short trading exists": "strategy.short",
    "shorts can be disabled for spot": "allowShort",
    "stop-distance risk sizing exists": "riskSizedQuantity",
    "exposure-capped sizing exists": "exposureSizedQuantity",
    "contract point value can be overridden": "contractPointValueOverride",
    "new listings have a history gate": "minimumHistoryBars",
    "hard drawdown protection exists": "strategy.risk.max_drawdown",
    "loss-streak protection exists": "maximumConsecutiveLosses",
    "break-even protection exists": "breakEvenActivationPercent",
    "Smart Hold state exists": "smartHoldActive",
    "partial exits are optional": "usePartialExit",
    "partial exits cannot repeat": "partialTaken",
    "long entry has immediate protection": 'strategy.exit("Long entry protection"',
    "short entry has immediate protection": 'strategy.exit("Short entry protection"',
    "orders include webhook messages": "alert_message = orderMessage",
}

FORBIDDEN_SNIPPETS = {
    "strategy alertcondition calls have no effect": "alertcondition(",
    "same-bar order processing is unrealistic": "process_orders_on_close = true",
    "tick recalculation can diverge from history": "calc_on_every_tick = true",
    "fill recalculation can make same-bar decisions": "calc_on_order_fills = true",
    "unconfirmed higher-timeframe lookahead can repaint": "lookahead = barmerge.lookahead_off",
}

TYPED_FUNCTION_RETURN = re.compile(
    r"(?m)^\s*(?:bool|int|float|string|color)\s+[A-Za-z_]\w*\s*\([^\n]*\)\s*=>"
)


def validate(source: str) -> list[str]:
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
        failures.append("every higher-timeframe request must use offset/lookahead pairing")
    if source.count("strategy(") != 1:
        failures.append("expected exactly one strategy() declaration")
    if source.count("strategy.entry(") != 2:
        failures.append("expected one long and one short strategy.entry() call")
    if TYPED_FUNCTION_RETURN.search(source):
        failures.append("Pine function headers cannot declare a return type")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("strategy", type=Path)
    args = parser.parse_args()
    failures = validate(args.strategy.read_text(encoding="utf-8"))
    if failures:
        print("Crypto regime strategy validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Crypto regime strategy validation passed: {args.strategy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
