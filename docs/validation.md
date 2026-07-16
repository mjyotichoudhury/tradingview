# Validation and promotion gates

The strategy is promoted by evidence, not by the best historical return.

## 1. Data and execution truthfulness

- Use point-in-time bars from the intended exchange/data feed.
- Include brokerage, exchange fees, taxes, spread, slippage, financing, and
  futures roll costs.
- Generate a signal only on a completed bar. The earliest eligible fill is the
  following bar.
- Validate contract multiplier, minimum contract, tick size, session calendar,
  price bands, and currency conversion for every instrument.
- Test continuous futures for signal generation separately from the executable
  contract and its roll rules.

## 2. Research protocol

1. Register the hypothesis, parameter ranges, data period, and acceptance gates.
2. Use an expanding three-year training window followed by a six-month
   out-of-sample window.
3. Repeat the walk-forward cycle, then run one untouched terminal holdout.
4. Record every parameter trial. Do not delete failed variants.
5. Stress baseline costs at 1.5× and 2× and resample trade sequences with a
   block bootstrap.
6. Report results by year, volatility regime, direction, and contract roll.

## 3. Initial promotion gates

All gates must pass before a paper webhook is considered:

- Net holdout Sharpe ratio at least 0.8, Sortino at least 1.0, Calmar at least
  0.7, and maximum drawdown no greater than 12%.
- At least ten years of representative data or 100 reasonably independent
  trades.
- At least 70% of walk-forward folds profitable and no single year contributing
  more than 35% of total profit.
- Positive expectancy under 2× modeled costs.
- No performance cliff when the 55/20/2.5 parameters move by ±20%.
- Deflated Sharpe Ratio confidence of at least 95% after accounting for all
  tested variants.

## 4. Paper and live gates

- Run paper trading for 8–12 weeks and at least 30 signals where feasible.
- Reconcile every alert, intended order, broker order, fill, position, and P&L.
- Verify stale-data, duplicate-alert, restart, broker-disconnect, and manual
  flatten drills.
- If live trading is later approved, begin at 10–25% of intended risk and scale
  only after 60–90 clean live days.

Any failed gate retires or revises the hypothesis. It does not justify weakening
the gate.
