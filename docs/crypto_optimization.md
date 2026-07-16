# Crypto Cycle Smart Hold: testing and optimization

This strategy is a transparent research baseline, not a claim of optimized or
future profitability. Pine compilation and Strategy Tester results must be
verified in TradingView for each exchange feed.

## Intended use

- Primary timeframe: **1 day**.
- Secondary robustness timeframe: **12 hours**.
- Primary symbols: `BINANCE:BTCUSDT` and `BINANCE:ETHUSDT`.
- Cross-feed checks: `COINBASE:BTCUSD` and `COINBASE:ETHUSD`.
- Start date: 1 January 2018 where the selected feed has sufficient history.
- Use standard candles, 0.1% commission, one tick of slippage, and realistic
  spread/funding assumptions outside Pine where applicable.

Avoid selecting only surviving altcoins. Assets without a complete 2018 history
must be reported separately and cannot validate the full-cycle hypothesis.

## Logic summary

The long-only entry requires a rising confirmed weekly cycle, aligned chart
EMAs, a recent pullback plus an EMA reclaim, oversold RSI recovery, or early
bullish-cycle turn, a non-extended price, at least two of three momentum
confirmations, adequate volume, and a bounded ATR percentage.

The Smart Hold state widens the ATR trail while the weekly cycle, EMA structure,
ADX/DI direction, and RSI remain strong. The stop can only rise. Break-even and
partial-profit protection activate after configurable gains. A market exit
requires two deterioration signals unless price breaks major support or reaches
the maximum holding period.

## Coarse robustness ranges

Do not search every possible combination. Change one parameter family at a time
and record every trial.

| Parameter | Coarse values |
| --- | --- |
| Weekly cycle EMA pair | 16/36, 20/40, 24/48 |
| Pullback / trend EMA | 34/150, 50/200, 65/250 |
| Position size | 20%, 30%, 40% |
| Entry RSI floor | 48, 50, 52 |
| ADX floor | 14, 18, 22 |
| Volume multiplier | 0.8, 1.0, 1.2 |
| Maximum stop | 8%, 12%, 16% |
| Initial ATR stop | 2.5, 3.0, 3.5 |
| Trail activation | 10%, 15%, 20% |
| Trailing ATR distance | 3.0, 4.0, 5.0 |
| Partial take-profit | 15%, 20%, 30% |

## Walk-forward protocol

1. Use an expanding training window and the following untouched calendar year
   as out-of-sample data.
2. Repeat through all available years, then reserve the latest period as a final
   holdout.
3. Rank candidates primarily by profit-to-drawdown and recovery factor, then
   confirm profit factor, Sharpe, Sortino, average trade, and trade count.
4. Reject candidates whose result depends on one trade, one year, one exchange,
   or one exact parameter value.
5. Repeat with 1.5x and 2x costs and shift every important parameter by about
   20%. A robust region should degrade gradually rather than collapse.
6. Compare against buy-and-hold. A long-only strategy may earn less in a bull
   market; its purpose is to improve drawdown and risk-adjusted consistency.

For every run, export net profit, maximum drawdown, profit factor, win rate,
average trade, completed trades, Sharpe, Sortino, recovery factor, and the share
of profit contributed by the largest trade. Require at least two completed
trades per symbol, but use the combined cross-symbol and walk-forward sample for
any serious conclusion.

## Independent implementation sanity check

Before publication, the default logic was independently approximated on daily
`BTCUSDT` and `ETHUSDT` Binance bars from 2018 with 0.1% per-order commission.
The first 95%-allocation version was rejected because early losses could trigger
the portfolio drawdown lock before later bull cycles. A coarse, 81-combination
neighborhood screen also rejected variants dominated by a single trade.

The selected 30%-allocation design added two economically motivated entry paths:
oversold RSI recovery and an early confirmed-cycle turn. In the independent
approximation it produced 24 completed BTC trades and 16 completed ETH trades,
with positive net results and profit factors above 2 on both. The largest winner
contributed about 54% and 50% of gross profit respectively. These figures are a
design sanity check only—not TradingView results, not an untouched holdout, and
not evidence of future performance. Reproduce the test in TradingView before
accepting or changing any default.

## Known weaknesses

- The weekly cycle filter reacts slowly after sharp V-shaped reversals.
- Long-only logic can remain flat through extended bear markets.
- EMA pullbacks can whipsaw during sideways high-volatility regimes.
- Volume differs across exchanges and spot/derivative feeds.
- Fixed percentage sizing does not equalize volatility across assets.
- Stop fills, gaps, funding, spread, taxes, and exchange outages can be worse
  than the broker emulator shows.
