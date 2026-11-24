import numpy as np
import pandas as pd
import pytest

from portfoliolens.data import demo_prices, read_holdings
from portfoliolens.engine import Config, min_variance_weights, performance, review, simulate, validate_prices

HOLDINGS = {"AVGO": .184, "ETN": .126, "PGR": .69}


def test_weights_drift_between_rebalances():
    returns = pd.DataFrame([[1., 0.], [0., 1.]], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), columns=["A", "B"])
    path, trades = simulate(returns, 0, lambda i: np.array([.5, .5]), 0)
    assert path.net_return.iloc[0] == pytest.approx(.5)
    assert path.net_return.iloc[1] == pytest.approx(1 / 3)
    assert (1 + path.net_return).prod() == pytest.approx(2)
    assert len(trades) == 1


def test_costs_include_initial_entry_and_gross_traded_notional():
    returns = pd.DataFrame([[0., 0.], [0., 0.]], index=pd.to_datetime(["2024-01-31", "2024-02-01"]), columns=["A", "B"])
    path, _ = simulate(returns, 0, lambda i: np.array([1., 0.]) if i == 0 else np.array([0., 1.]), 10)
    np.testing.assert_allclose(path.gross_turnover, [1, 2])
    np.testing.assert_allclose(path.net_return, [-.001, -.002])


def test_drawdown_includes_first_period_loss():
    r = pd.Series([-.1, .05])
    metrics = performance(r, pd.Series([-.05, .01]), 0)
    assert metrics["Maximum drawdown"] == pytest.approx(-.1)
    assert metrics["Total return"] == pytest.approx(-.055)


def test_annualization_and_information_ratio():
    r = pd.Series([.01, -.02, .03])
    benchmark = pd.Series([.0, -.01, .01])
    m = performance(r, benchmark, 0)
    assert m["Annualized geometric return"] == pytest.approx((1 + r).prod() ** (252 / 3) - 1)
    active = r - benchmark
    assert m["Information ratio"] == pytest.approx(active.mean() / active.std() * np.sqrt(252))
    assert np.isnan(performance(benchmark, benchmark, 0)["Information ratio"])


def test_optimizer_cap_and_budget():
    h = demo_prices().pct_change().dropna().iloc[:252, :3]
    w = min_variance_weights(h, .4)
    assert w.sum() == pytest.approx(1)
    assert w.min() >= -1e-7
    assert w.max() <= .4000001


def test_future_prices_do_not_change_previous_targets():
    prices = demo_prices().iloc[:370].copy()
    before = review(prices, HOLDINGS, Config(lookback=60))
    cut = prices.index[250]
    changed = prices.copy()
    changed.loc[cut:, "PGR"] *= 3
    after = review(changed, HOLDINGS, Config(lookback=60))
    a = before["trades"]["Capped min variance"]
    b = after["trades"]["Capped min variance"]
    pd.testing.assert_frame_equal(a[a.return_date <= cut], b[b.return_date <= cut])


def test_more_costs_reduce_terminal_wealth():
    prices = demo_prices().iloc[:370]
    free = review(prices, HOLDINGS, Config(lookback=60, cost_bps=0))
    paid = review(prices, HOLDINGS, Config(lookback=60, cost_bps=25))
    assert (paid["metrics"]["Total return"] < free["metrics"]["Total return"]).all()


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "negative", "unsorted", "infinite"])
def test_invalid_prices_rejected(mutation):
    p = demo_prices().iloc[:10].copy()
    if mutation == "missing": p.iloc[2, 0] = np.nan
    if mutation == "negative": p.iloc[2, 0] = -1
    if mutation == "infinite": p.iloc[2, 0] = np.inf
    if mutation == "duplicate": p.index = [p.index[0]] * len(p)
    if mutation == "unsorted": p = p.iloc[::-1]
    with pytest.raises(ValueError): validate_prices(p)


@pytest.mark.parametrize("config", [Config(max_weight=.2), Config(cost_bps=-1), Config(annual_rf=np.nan), Config(lookback=2)])
def test_invalid_configuration_rejected(config):
    with pytest.raises(ValueError): review(demo_prices(), HOLDINGS, config)


def test_invalid_holdings_rejected():
    with pytest.raises(ValueError, match="sum to 1"):
        review(demo_prices(), {"AVGO": .7, "PGR": .7})


def test_duplicate_holdings_rejected(tmp_path):
    path = tmp_path / "holdings.csv"
    path.write_text("ticker,weight\nAVGO,.5\nAVGO,.5\n")
    with pytest.raises(ValueError, match="unique"): read_holdings(path)


def test_short_history_rejected():
    with pytest.raises(ValueError, match="price rows"):
        review(demo_prices().iloc[:254], HOLDINGS, Config(lookback=252))
