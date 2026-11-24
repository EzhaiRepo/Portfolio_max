# Methodology

## Data contract

Input is a sorted, unique, daily adjusted-price table on a common trading calendar. Values must be positive and finite. Missing prices are rejected, not forward-filled or silently dropped. Calendar completeness and provider corporate-action adjustments still require analyst review. A normalized-price-table SHA-256 identifies each input. A download also records its raw-file hash, provider, retrieval timestamp, and date range in a sidecar.

Synthetic fixture: seeded pseudo-random market and idiosyncratic returns, four named series, 1,009 business-day price observations. Symbols are labels only: these are not observations of the named securities. The calendar includes ordinary weekdays, not an exchange-holiday calendar.

## Allocation methods

- **Current allocation:** user-supplied targets, reset monthly.
- **Equal weight:** 1/N targets, reset monthly.
- **Capped minimum variance:** minimize w'Σw subject to sum(w)=1 and 0<=w<=cap; use the trailing 252 returns before the interval being evaluated. Σ is 90% sample covariance plus 10% its diagonal, annualized by 252. Shrinkage and cap are fixed design choices, not tuned to the demo results.
- **SPY:** fully invested benchmark, with the same initial entry cost convention.

SLSQP success, finite weights, constraints, and bounds are checked. There is no silent equal-weight fallback when optimization fails.

This extends rather than reproduces the original project's maximum-Sharpe and CAPM-alpha objectives. Minimum variance removes the need to estimate expected returns for the first release. No statistical alpha inference is reported.

## Timing and transaction model

Prices at t produce return r[t]=P[t]/P[t-1]-1. At a rebalance, the optimized target uses only returns with indices strictly before t, through the preceding close. Trades are assumed executable at that preceding close. This is an idealized close-to-close convention without latency or slippage beyond the cost assumption.

Rebalance before the first observed return in a new calendar month, and before the first evaluation interval. Keep portfolio weights drifting between rebalances:

`next_weight[j] = weight[j] * (1 + asset_return[j]) / (1 + gross_portfolio_return)`

Gross traded notional is `sum(abs(target - drifted_weight))`. Initial investment starts from cash and has gross traded notional 1. A complete switch between assets has gross traded notional 2. This measure is not half-turnover.

`fee = gross_traded_notional * cost_bps / 10000`

`net_return = (1 - fee) * (1 + gross_portfolio_return) - 1`

Costs are modeled using pre-fee weights and NAV; the small feedback from financing the fee into exact traded shares is omitted. All strategies pay initial entry costs; no terminal liquidation cost is included.

## Measures

- Total return: product(1+net_return)-1.
- Annualized geometric return: terminal wealth^(252/N)-1. This uses observation-based annualization, not calendar-time CAGR.
- Annualized volatility: sample standard deviation of net daily returns × sqrt(252).
- Maximum drawdown: minimum wealth/running_peak-1, including initial wealth of 1.
- Sharpe: mean(daily net return - effective daily risk-free rate) / sample standard deviation(net return) × sqrt(252). Effective daily risk-free rate = (1+annual rate)^(1/252)-1.
- Information ratio: mean(portfolio net return - benchmark net return) / sample standard deviation of that active return × sqrt(252). This is distinct from the original notebook's beta-adjusted alpha/residual-risk ratio.
- Beta: sample covariance(portfolio, benchmark) / sample variance(benchmark).
- Undefined ratios are N/A in HTML and null in JSON.
- Summed cost fractions are not exact cumulative return drag. Use a separate zero-cost run to measure the effect on terminal wealth.

## What the evaluation does not establish

The original three securities and supplied allocation were selected retrospectively. Rolling covariance estimation prevents future-data leakage inside each fit but does not establish a point-in-time universe or independent stock-selection test. The original presentation also used later performance in selection. Do not reuse its p-values as evidence of an independently validated strategy.

Vendor data can be revised. The risk-free rate is constant. Taxes, changing spreads, market impact, liquidity limits, exchange-calendar validation, and factor attribution remain outside the MVP. Concentration caps apply at rebalance, not continuously. A low-beta security is not necessarily safe.

## References

- [CFA Institute: active return, tracking error, information ratio, and multifactor models](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/using-multifactor-models)
- [SciPy SLSQP documentation](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html)
- [yfinance download parameters and exclusive end date](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)
