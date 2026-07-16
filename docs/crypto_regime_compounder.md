# Crypto Regime Compounder: design and validation

`strategies/crypto_regime_compounder.pine` is a higher-compounding crypto
research strategy. It does not promise a particular return and it is not a
claim of future profitability. The default is the balanced profile; leverage is
not required. Short trades must be disabled on spot markets.

## Recommended setup

- Primary timeframe: **1 day**.
- Secondary robustness timeframe: **12 hours**.
- Use standard candles, not Heikin Ashi, Renko, range, or other synthetic bars.
- Use the exchange feed on which orders would actually be placed.
- Keep commission at 0.1% and slippage at one tick in the Pine declaration.
- Add spread, funding, liquidation, tax, and alert latency outside Pine.

Start with `BTCUSD`, `ETHUSD`, `SOLUSD`, `XRPUSD`, and `BNBUSD`. A result on one
symbol is not enough to promote the strategy.

## Architecture

The strategy has four layers:

1. A confirmed weekly 10/30 EMA regime decides whether long or short entries
   are eligible. Every weekly request uses the previous completed weekly bar.
2. A daily 21/55/200 EMA structure, a recent EMA or RSI reclaim, momentum
   scoring, volume, and ATR filters select pullbacks or early regime turns.
3. Position size is the smaller of stop-distance risk size and the maximum
   exposure cap. The intended loss at the initial stop is approximately the
   chosen equity-risk percentage before gaps and fees.
4. Smart Hold widens the ATR trail while weekly regime, EMA structure, ADX/DI,
   and RSI agree. Break-even, optional partial profit, structure failure,
   two-signal deterioration, and maximum holding time provide independent exits.

The strategy never pyramids, averages down, doubles after a loss, or reads an
unfinished higher-timeframe candle. Signals are evaluated only on confirmed
chart bars and market orders fill on the next available tick in TradingView's
broker emulator.

## Risk profiles

These are starting points, not promises. Change the three settings together.

| Profile | Risk / position | Exposure cap | Drawdown breaker | Short mode |
| --- | ---: | ---: | ---: | --- |
| Balanced default | 3% | 100% | 25% | On for perpetuals |
| Spot defensive | 2% | 100% | 20% | Off |
| New-listing probation | 1% | 25% | 15% | Paper only initially |
| Growth research | 6% | 175% | 35% | Perpetuals only |

The growth profile can lose roughly twice as fast as the default and can suffer
funding and liquidation effects that a bar backtest does not reproduce. It is
included to test the return/drawdown frontier, not as a live recommendation.

## Independent implementation sanity check

An independent daily-bar approximation was run with next-open market fills,
intrabar protective stops, and 0.1% commission per fill. It is not TradingView's
engine and did not model funding, spread, liquidation, or the Pine one-tick
slippage setting. Reproduce every result in TradingView.

### Full-cycle proxy feeds, 2018 through 16 July 2026

| Profile / symbol | Net profit | Max drawdown | Profit factor | Positions | Win rate | Largest winner / gross profit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Balanced `BTCUSDT` | 120.7% | 16.2% | 3.00 | 40 | 47.5% | 14.8% |
| Balanced `ETHUSDT` | 172.7% | 17.2% | 2.49 | 46 | 47.8% | 29.3% |
| Growth `BTCUSDT` | 324.9% | 29.0% | 2.86 | 40 | 47.5% | 15.0% |
| Growth `ETHUSDT` | 450.9% | 31.4% | 2.11 | 46 | 47.8% | 22.9% |

The balanced profile was selected because its result is distributed across more
than forty positions on both symbols. The growth profile crosses 400% only on
the ETH approximation and does so with much higher drawdown. It is not evidence
that the strategy will exceed any external benchmark.

### Delta Exchange India feed check

Delta's available contract history is much shorter than a full crypto cycle:
the retrieved BTC daily series began on 29 December 2023 and ETH on 6 February
2024. With the balanced settings, the independent approximation returned:

| Delta contract | Net profit | Max drawdown | Profit factor | Positions |
| --- | ---: | ---: | ---: | ---: |
| `BTCUSD` | 14.9% | 7.4% | 2.68 | 11 |
| `ETHUSD` | 10.3% | 6.1% | 2.13 | 8 |

These results include the 250-bar history gate and one adverse tick of slippage
per fill. They prevent the full-cycle bull markets from hiding a weak recent
regime, but remain in-sample design checks rather than an untouched holdout.
The complete five-contract run is in `docs/backtest_2026-07-16.md`.

## Delta Exchange India universe

The snapshot in `data/delta_crypto_perpetuals_2026-07-16.json` was built from
Delta Exchange India's public products endpoint on 16 July 2026. The catalogue
contained 927 products and 210 live perpetual futures. The crypto-only filter
kept 182 contracts and excluded 28 tokenized stocks, indices, and gold/silver
linked instruments.

### Recommended core contracts

`BTCUSD`, `ETHUSD`, `SOLUSD`, `XRPUSD`, `BNBUSD`, `DOGEUSD`, `ADAUSD`,
`LTCUSD`, `BCHUSD`, `LINKUSD`, `AVAXUSD`, `DOTUSD`, `TRXUSD`, `SUIUSD`,
`POLUSD`, `APTUSD`, `NEARUSD`, `UNIUSD`, `AAVEUSD`, and `HYPEUSD`.

### Recent crypto listings in the snapshot

The 90-day recent tier contains `GRAMUSD`, `INUSD`, `TACUSD`, `VELVETUSD`,
`OPNUSD`, `ALLOUSD`, `BILLUSD`, `AIGENSYNUSD`, `BUSD` (BUILDon), `SKYAIUSD`,
`LABUSD`, `PIEVERSEUSD`, `CHIPUSD`, `ENJUSD`, and `BASEDUSD`.

Recent listings are included, but not optimized. Keep them in paper/probation
until all of these gates pass:

- at least 250 daily history bars and a fully formed weekly slow EMA;
- at least two completed strategy positions;
- adequate spread, order-book depth, and 30-day notional volume;
- positive results after 2x commission/slippage stress;
- no single position contributing more than 50% of gross profit;
- stable behavior on nearby settings and an untouched forward period.

The Pine history gate deliberately produces no immediate trades on the newest
contracts. That is a safety feature, not an omission. To refresh the universe:

```bash
python scripts/snapshot_delta_universe.py \
  --output data/delta_crypto_perpetuals_latest.json
```

If TradingView's `syminfo.pointvalue` does not match Delta's contract value,
copy `contract_value` from the snapshot into **Contract point value override**.
Verify order quantity and P&L on paper before creating alerts.

## Walk-forward promotion gates

1. Use expanding training windows and untouched annual or six-month validation
   windows. Keep the latest period sealed as the final holdout.
2. Rank by median profit-to-drawdown and recovery factor across symbols, then
   check profit factor, Sharpe, Sortino, average position, and trade count.
3. Stress commission and slippage to 1.5x and 2x. Include perpetual funding.
4. Perturb weekly EMAs, daily EMAs, RSI, ADX, stop, and trail by about 15–20%.
   A robust neighborhood should fade gradually rather than collapse.
5. Reject a candidate if one symbol, one calendar year, or the largest position
   supplies most of its profit.
6. Paper trade alerts and reconcile every TradingView order with exchange fills
   before considering live use.

## Known weaknesses

- Confirmed weekly regimes react late to violent V-shaped reversals.
- Long entries can still whipsaw after a mature bull market rolls over.
- Short squeezes, gaps, thin books, and funding can exceed the modeled stop.
- Volume varies by exchange and can be unreliable on young contracts.
- New listings do not have enough history to establish long-term robustness.
- A portfolio running the script on many correlated coins can exceed the risk
  implied by a single-chart drawdown breaker. Portfolio-level exposure and
  correlation limits must be enforced by the execution layer.
