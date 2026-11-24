"""Long-only, monthly-rebalanced portfolio simulation with explicit timing."""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass(frozen=True)
class Config:
    lookback: int = 252
    max_weight: float = 0.50
    cost_bps: float = 10.0
    annual_rf: float = 0.04
    benchmark: str = "SPY"

    def validate(self, n_assets):
        if not isinstance(self.lookback, int) or self.lookback < 20:
            raise ValueError("lookback must be an integer of at least 20 observations")
        if not np.isfinite(self.max_weight) or not 0 < self.max_weight <= 1:
            raise ValueError("max_weight must be between 0 and 1")
        if n_assets * self.max_weight < 1 - 1e-9:
            raise ValueError("Weight cap is infeasible: number of assets × cap must be >= 1")
        if not np.isfinite(self.cost_bps) or not 0 <= self.cost_bps <= 100:
            raise ValueError("cost_bps must be between 0 and 100")
        if not np.isfinite(self.annual_rf) or not -1 < self.annual_rf <= 1:
            raise ValueError("annual_rf must be greater than -1 and at most 1")


def validate_prices(prices):
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("Prices need a DatetimeIndex")
    if prices.empty or prices.shape[1] == 0:
        raise ValueError("Prices are empty")
    if prices.index.hasnans or prices.index.has_duplicates or not prices.index.is_monotonic_increasing:
        raise ValueError("Price dates must be valid, unique, and increasing")
    if prices.index.normalize().has_duplicates:
        raise ValueError("Only one price observation per date is supported")
    if prices.columns.has_duplicates:
        raise ValueError("Duplicate ticker columns")
    try:
        values = prices.to_numpy(dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError("Prices must be numeric") from e
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Prices must be finite and positive; missing values are not filled")


def validate_holdings(holdings):
    values = np.asarray(list(holdings.values()), dtype=float)
    if len(values) < 2 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Provide at least two assets with finite, nonnegative weights")
    if not np.isclose(values.sum(), 1, atol=1e-8, rtol=0):
        raise ValueError("Holdings weights must sum to 1 (use decimals, not percentages)")


def min_variance_weights(history, cap):
    """Fit only the supplied history; shrink 10% toward diagonal for stability."""
    n = history.shape[1]
    if n * cap < 1 - 1e-9:
        raise ValueError("Infeasible weight cap")
    cov = history.cov().to_numpy() * 252
    cov = 0.9 * cov + 0.1 * np.diag(np.diag(cov))
    if not np.isfinite(cov).all():
        raise ValueError("Covariance is not finite")
    result = minimize(
        lambda w: float(w @ cov @ w), np.full(n, 1 / n),
        jac=lambda w: 2 * cov @ w,
        method="SLSQP", bounds=[(0, cap)] * n,
        constraints={"type": "eq", "fun": lambda w: w.sum() - 1,
                     "jac": lambda w: np.ones(n)},
        options={"ftol": 1e-12, "maxiter": 1000},
    )
    if (not result.success or not np.isfinite(result.x).all()
            or abs(result.x.sum() - 1) > 1e-7
            or result.x.min() < -1e-7 or result.x.max() > cap + 1e-7):
        raise ValueError(f"Optimizer failed: {result.message}")
    return result.x


def simulate(returns, start, target, cost_bps):
    """Choose targets using observations strictly before each return interval.

    Trades occur at the prior close before the first interval of each month.
    Costs apply to gross traded notional (buys + sells), as a fraction of
    pre-trade NAV. Initial investment is a 100% purchase from cash.
    """
    if not 0 <= start < len(returns):
        raise ValueError("Simulation start is outside returns")
    drifted = np.zeros(returns.shape[1])
    previous_month = None
    rows, trades = [], []
    for i in range(start, len(returns)):
        date = returns.index[i]
        month = (date.year, date.month)
        turnover, fee = 0.0, 0.0
        if month != previous_month:
            weights = np.asarray(target(i), dtype=float)
            if (weights.shape != drifted.shape or not np.isfinite(weights).all()
                    or weights.min() < -1e-7 or abs(weights.sum() - 1) > 1e-7):
                raise ValueError("Invalid target weights")
            turnover = float(np.abs(weights - drifted).sum())
            fee = turnover * cost_bps / 10_000
            drifted = weights.copy()
            trades.append({"return_date": date, "gross_turnover": turnover,
                           "cost_fraction": fee,
                           **dict(zip(returns.columns, weights))})
            previous_month = month
        r = returns.iloc[i].to_numpy(dtype=float)
        gross = float(drifted @ r)
        net = (1 - fee) * (1 + gross) - 1
        rows.append({"date": date, "net_return": net, "gross_return": gross,
                     "gross_turnover": turnover, "cost_fraction": fee})
        drifted = drifted * (1 + r) / (1 + gross)
    return pd.DataFrame(rows).set_index("date"), pd.DataFrame(trades)


def performance(net, benchmark, annual_rf):
    """Arithmetic risk ratios annualized with 252 observations per year."""
    if len(net) < 2:
        raise ValueError("At least two evaluation observations are required")
    wealth = (1 + net).cumprod()
    peak = wealth.cummax().clip(lower=1.0)  # include the initial $1
    excess = net - ((1 + annual_rf) ** (1 / 252) - 1)
    vol = float(net.std(ddof=1))
    active = net - benchmark
    tracking_error = float(active.std(ddof=1))
    market_variance = float(benchmark.var(ddof=1))
    beta = float(net.cov(benchmark) / market_variance) if market_variance > 1e-15 else np.nan
    return {
        "Total return": float(wealth.iloc[-1] - 1),
        "Annualized geometric return": float(wealth.iloc[-1] ** (252 / len(net)) - 1),
        "Annualized volatility": vol * np.sqrt(252),
        "Maximum drawdown": float((wealth / peak - 1).min()),
        "Sharpe ratio": float(excess.mean() / vol * np.sqrt(252)) if vol > 1e-15 else np.nan,
        "Information ratio": float(active.mean() / tracking_error * np.sqrt(252)) if tracking_error > 1e-15 else np.nan,
        "Beta": beta,
    }


def review(prices, holdings, config=Config()):
    validate_prices(prices)
    validate_holdings(holdings)
    config.validate(len(holdings))
    assets = list(holdings)
    if config.benchmark in assets:
        raise ValueError("Benchmark must be separate from portfolio assets in this MVP")
    missing = set(assets + [config.benchmark]) - set(prices.columns)
    if missing:
        raise ValueError(f"Missing price columns: {', '.join(sorted(missing))}")
    returns = prices[assets + [config.benchmark]].astype(float).pct_change(fill_method=None).iloc[1:]
    if len(returns) < config.lookback + 2:
        raise ValueError("Need lookback + 3 price rows for at least two evaluation returns")
    stock_returns = returns[assets]
    targets = {
        "Current allocation": lambda i: np.asarray(list(holdings.values())),
        "Equal weight": lambda i: np.full(len(assets), 1 / len(assets)),
        "Capped min variance": lambda i: min_variance_weights(
            stock_returns.iloc[i - config.lookback:i], config.max_weight),
    }
    benchmark, benchmark_trades = simulate(
        returns[[config.benchmark]], config.lookback, lambda i: np.ones(1), config.cost_bps)
    paths, trades, rows = {config.benchmark: benchmark}, {config.benchmark: benchmark_trades}, {}
    for name, target in targets.items():
        path, trade = simulate(stock_returns, config.lookback, target, config.cost_bps)
        paths[name], trades[name] = path, trade
    benchmark_net = benchmark.net_return
    for name, path in paths.items():
        rows[name] = performance(path.net_return, benchmark_net, config.annual_rf)
        rows[name]["Gross traded notional / NAV (sum)"] = float(path.gross_turnover.sum())
        rows[name]["Cost fractions (sum)"] = float(path.cost_fraction.sum())
    net_returns = pd.DataFrame({name: path.net_return for name, path in paths.items()})
    return {"metrics": pd.DataFrame(rows).T, "net_returns": net_returns,
            "trades": trades, "holdings": holdings, "config": config,
            "training_end": returns.index[config.lookback - 1],
            "evaluation_start": net_returns.index[0], "evaluation_end": net_returns.index[-1]}
