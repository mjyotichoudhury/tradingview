# Robust Gold Trend Breakout

A reviewable TradingView Pine Script v6 strategy for medium-frequency gold and
energy research. The first version implements a symmetric 55-bar breakout,
confirmed daily trend filter, volatility-scaled risk sizing, ATR protection,
channel exits, and hard strategy-level loss controls.

> **Research only.** This repository does not connect to a broker or place live
> trades. Historical results do not guarantee future performance.

## What is included

- `strategies/gold_trend_breakout.pine` — Pine Script v6 strategy.
- `scripts/validate_strategy.py` — deterministic anti-repainting and safety
  contract checks.
- `tests/` — regression tests for the repository validator.
- `.github/workflows/ci.yml` — validation on every push and pull request.
- `docs/validation.md` — the backtest and promotion methodology.

## Strategy defaults

| Control | Default |
| --- | ---: |
| Chart timeframe | 4 hours |
| Breakout / channel exit | 55 / 20 bars |
| Higher-timeframe filter | Previous confirmed daily EMA(200) |
| Emergency stop | 2.5 × ATR(20) |
| Equity risk per entry | 0.35% |
| Target annualized volatility | 10% |
| Gross leverage cap | 2× |
| Intraday loss halt | 1.5% |
| Maximum drawdown halt | 12% |

The values above are starting hypotheses, not optimized claims. Test broad
parameter neighborhoods and retain the locked out-of-sample result.

## Use in TradingView

1. Open TradingView **Pine Editor** and paste
   `strategies/gold_trend_breakout.pine`.
2. Add it to a **4-hour** chart. Start with one exposure family: MCX
   GOLD/GOLDM or XAUUSD, not both as independent positions.
3. Set realistic commission, slippage, point value, minimum contract size, and
   annualization bars for the instrument and data feed.
4. Inspect long and short results separately and follow `docs/validation.md`.
5. Create an order-fill alert only after paper validation. Use
   `{{strategy.order.alert_message}}` as the alert message.

## Local validation

```bash
python scripts/validate_strategy.py strategies/gold_trend_breakout.pine
python -m unittest discover -s tests -v
```

The local checks cannot replace compilation in TradingView. They enforce the
repository's safety contract: Pine v6, confirmed-bar execution, confirmed
higher-timeframe data, prior-bar breakout windows, explicit risk limits, and no
strategy `alertcondition()` calls.

## Roadmap

The next reviewable increments are a locked backtest-report template, broker
webhook schema with signature verification, paper-trading reconciliation, and
deployment monitoring. Live execution stays out of scope until all promotion
gates pass.
