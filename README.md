# TradingView Strategy Research Lab

Reviewable Pine Script v6 strategies with explicit execution assumptions,
anti-repainting checks, risk controls, and evidence-based promotion gates.

> **Research only.** This repository does not connect to a broker or place live
> trades. Historical results do not guarantee future performance.

## Strategies

### Crypto Regime Compounder + Smart Hold

`strategies/crypto_regime_compounder.pine` is the higher-compounding crypto
challenger. It adds confirmed bull/bear regimes, optional perpetual shorts,
stop-distance risk sizing, exposure caps, symmetric Smart Hold exits, and a
minimum-history gate for new listings.

| Control | Balanced default |
| --- | ---: |
| Primary chart timeframe | 1 day |
| Backtest start | 1 January 2018 |
| Commission / slippage | 0.1% / 1 tick |
| Weekly / daily EMA structure | 10/30 weekly; 21/55/200 daily |
| Risk / maximum exposure | 3% / 100% |
| Initial stop | 2.8 ATR, bounded to 4–12% |
| Break-even / trail activation | +8% / +12% |
| Maximum strategy drawdown | 25% |

The current Delta Exchange India snapshot includes 182 crypto perpetuals,
including a separate probation tier for recent listings. See
`docs/crypto_regime_compounder.md` for test evidence, risk profiles, the Delta
universe, and promotion gates.

### Crypto Cycle Pullback + Smart Hold

`strategies/crypto_cycle_smart_hold.pine` is a long-only crypto strategy built
for full market cycles and low turnover. It combines a confirmed weekly cycle,
daily trend structure, pullback/reclaim entries, momentum scoring, volume and
volatility filters, and an adaptive Smart Hold runner.

| Control | Default |
| --- | ---: |
| Primary chart timeframe | 1 day |
| Backtest start | 1 January 2018 |
| Commission / slippage | 0.1% / 1 tick |
| Position size | 30% of equity |
| Weekly cycle EMA | 20 / 40 |
| Pullback / trend EMA | 50 / 200 |
| Initial protection | tighter of 12% or 3 ATR |
| Partial profit | 25% at +20% |
| Break-even / trail activation | +10% / +15% |
| Maximum strategy drawdown | 20% |
| Loss-streak protection | 3 losses, then 30-bar cooldown |

Use `docs/crypto_optimization.md` for symbols, parameter neighborhoods,
walk-forward testing, evaluation metrics, and known weaknesses.

### Gold Trend Breakout

`strategies/gold_trend_breakout.pine` is a symmetric 55-bar breakout research
baseline with a confirmed daily trend filter, volatility-scaled sizing, ATR
protection, channel exits, and hard loss controls. Its primary timeframe is four
hours. See `docs/validation.md` for its validation and promotion methodology.

## Use in TradingView

1. Open **Pine Editor**, paste the selected `.pine` file, save it, and click
   **Add to chart**.
2. Use standard candles and the intended exchange feed.
3. Confirm the Properties tab shows the expected commission and slippage.
4. Review the Overview, Performance Summary, List of Trades, and Properties.
5. Export and compare walk-forward results before changing defaults.
6. Create an order-fill alert only after paper validation. Use
   `{{strategy.order.alert_message}}` as the alert message.

## Local validation

```bash
python scripts/validate_strategy.py strategies/gold_trend_breakout.pine
python scripts/validate_crypto_strategy.py strategies/crypto_cycle_smart_hold.pine
python scripts/validate_crypto_regime_strategy.py strategies/crypto_regime_compounder.pine
python -m unittest discover -s tests -v
```

The local checks are not a Pine compiler. They enforce reviewed invariants such
as Pine v6, confirmed-bar decisions, confirmed higher-timeframe data, realistic
next-tick execution, explicit costs, disabled pyramiding, and hard risk limits.

## Promotion path

Pine compilation -> historical walk-forward tests -> untouched holdout -> cost
stress -> paper alerts -> operational reconciliation. Live execution remains out
of scope until every gate passes.
