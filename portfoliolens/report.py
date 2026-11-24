"""Generate a portable, static review report with no external assets."""
import html
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "portfoliolens-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PERCENT_METRICS = {"Total return", "Annualized geometric return", "Annualized volatility",
                   "Maximum drawdown", "Cost fractions (sum)"}
COLORS = ["#94a3b8", "#0f766e", "#c77730", "#6366f1"]


def format_metric(key, value):
    if not np.isfinite(value):
        return "N/A"
    return f"{value:.2%}" if key in PERCENT_METRICS else f"{value:.3f}"


def table_html(metrics):
    header = "<tr><th>Measure</th>" + "".join(f"<th>{html.escape(s)}</th>" for s in metrics.index) + "</tr>"
    rows = []
    for key in metrics.columns:
        cells = "".join(f"<td>{format_metric(key, metrics.loc[s, key])}</td>" for s in metrics.index)
        rows.append(f"<tr><th>{html.escape(key)}</th>{cells}</tr>")
    return "<table><thead>" + header + "</thead><tbody>" + "".join(rows) + "</tbody></table>"


def write_report(result, output, source, price_hash):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    metrics = result["metrics"]
    net = result["net_returns"]
    config = result["config"]
    wealth = (1 + net).cumprod()
    # Plot includes initial invested value, so first-interval losses remain visible.
    import pandas as pd
    initial = pd.DataFrame([np.ones(len(wealth.columns))], index=[result["training_end"]], columns=wealth.columns)
    wealth_plot = pd.concat([initial, wealth])
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "portfoliolens", "svg.fonttype": "none"}):
        fig, axes = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
        fig.set_facecolor("#ffffff")
        for i, name in enumerate(wealth_plot):
            series = wealth_plot[name]
            axes[0].plot(series.index, series, label=name, color=COLORS[i], linewidth=1.8)
            axes[1].plot(series.index, 100 * (series / series.cummax() - 1), color=COLORS[i], linewidth=1.2)
        axes[0].set_ylabel("Growth of $1, net of costs")
        axes[1].set_ylabel("Drawdown (%)")
        axes[0].legend(loc="upper left", ncol=2, frameon=False)
        for ax in axes:
            ax.grid(alpha=.15)
            ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(output / "performance.svg", metadata={"Date": None}, bbox_inches="tight")
        plt.close(fig)
    svg = "\n".join(line.rstrip() for line in (output / "performance.svg").read_text().splitlines()) + "\n"
    (output / "performance.svg").write_text(svg)
    svg = svg[svg.index("<svg"):]
    current = metrics.loc["Current allocation"]
    capped = metrics.loc["Capped min variance"]
    largest = max(result["holdings"], key=result["holdings"].get)
    reduction = current["Annualized volatility"] - capped["Annualized volatility"]
    volatility_word = "lower" if reduction >= 0 else "higher"
    first_weights = result["trades"]["Capped min variance"].iloc[0]
    weights_html = "".join(
        f"<tr><th>{html.escape(t)}</th><td>{w:.1%}</td><td>{1 / len(result['holdings']):.1%}</td>"
        f"<td>{first_weights[t]:.1%}</td></tr>" for t, w in result["holdings"].items())
    start, end = result["evaluation_start"].date(), result["evaluation_end"].date()
    source_safe = html.escape(source)
    markup = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PortfolioLens | Portfolio review</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f5f7;color:#172a3a;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1120px;margin:0 auto;padding:42px 30px}}.eyebrow{{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#64748b;font-weight:700}}
h1{{font-size:38px;letter-spacing:-.04em;margin:6px 0}}h2{{font-size:22px;margin:0 0 12px}}p{{margin:10px 0}}.sub{{color:#526475;max-width:760px}}
.notice{{background:#fff5df;border-left:4px solid #c77730;padding:14px 18px;margin:24px 0}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.card,section{{background:white;border:1px solid #e0e6eb;border-radius:12px;padding:24px;margin-bottom:20px}}.value{{font-size:30px;font-weight:650;letter-spacing:-.03em}}.label{{font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.05em}}
section svg{{width:100%;height:auto}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:11px 12px;border-bottom:1px solid #e8edf1;text-align:right}}th:first-child{{text-align:left}}thead{{background:#f0f5f6}}.small{{font-size:12px;color:#64748b}}ul{{padding-left:20px}}li{{margin:7px 0}}.tag{{display:inline-block;background:#e4f2ef;color:#0f766e;padding:4px 10px;border-radius:5px;font-size:12px;font-weight:650}}
@media(max-width:700px){{main{{padding:22px 14px}}.cards{{grid-template-columns:1fr}}h1{{font-size:30px}}.card{{margin-bottom:0}}section{{padding:16px}}}}
@media print{{body{{background:white}}main{{padding:0}}section,.card{{break-inside:avoid}}.notice{{background:#fff}}}}
</style></head><body><main>
<div class="eyebrow">PortfolioLens / Analyst review / v0.1</div>
<h1>Understand the allocation tradeoff.</h1>
<p class="sub">Compare the supplied allocation with simple alternatives. Every strategy follows an explicit rebalance schedule, with costs and assumptions visible.</p>
<div class="notice"><strong>{source_safe}</strong><br>Historical or synthetic scenario analysis; no result here establishes stock-selection skill. The asset universe and supplied allocation were chosen retrospectively.</div>
<div class="cards">
<div class="card"><div class="label">Largest supplied holding</div><div class="value">{result['holdings'][largest]:.0%}</div><div>{html.escape(largest)} at each scheduled rebalance</div></div>
<div class="card"><div class="label">Alternative allocation limit</div><div class="value">{config.max_weight:.0%}</div><div>Maximum target per asset; weights can drift</div></div>
<div class="card"><div class="label">Evaluation observations</div><div class="value">{len(net):,}</div><div>{start} through {end}</div></div>
</div>
<section><span class="tag">Decision brief</span><h2 style="margin-top:12px">What changes when concentration is constrained?</h2>
<p>The capped minimum-variance scenario has annualized volatility <strong>{abs(reduction) * 100:.2f} percentage points {volatility_word}</strong> than the supplied allocation in this evaluation.</p>
<p>Its total net return is <strong>{capped['Total return']:.2%}</strong>, versus <strong>{current['Total return']:.2%}</strong> for the supplied allocation. Compare the full return, drawdown, and turnover tradeoff before choosing an allocation.</p>
<p class="small">This difference reflects both the covariance-based allocation method and the cap; it does not isolate the causal effect of the cap.</p></section>
<section><h2>Performance and drawdown</h2><p class="small">Net of modeled trading costs. Starting wealth = $1. All series use the same evaluation dates.</p>{svg}</section>
<section><h2>Comparable measures</h2><div class="scroll">{table_html(metrics)}</div>
<p class="small">Annualization uses 252 observations per year. Total return is the compounded return over the actual evaluation window. Information ratio for the benchmark itself is undefined. Cost fractions are summed relative to each trade's NAV, not a dollar cost or an exact return drag.</p></section>
<section><h2>First evaluation allocation</h2><div class="scroll"><table><thead><tr><th>Asset</th><th>Supplied</th><th>Equal weight</th><th>Capped min variance</th></tr></thead><tbody>{weights_html}</tbody></table></div>
<p class="small">The capped portfolio is refitted monthly; these are its first targets, not its targets for every date. Downloadable trade logs contain every rebalance.</p></section>
<section><h2>Assumptions that matter</h2><ul>
<li>Targets are executed at the prior close before the first observed return of each month. Training uses only the previous {config.lookback} returns; no same-interval or future return enters that fit.</li>
<li>Weights drift between rebalances. Costs are {config.cost_bps:g} basis points per dollar of gross traded notional (buys + sells), including initial entry. The benchmark pays the same entry cost; no terminal liquidation is modeled.</li>
<li>Long-only and fully invested. A 10% diagonal covariance shrinkage and {config.max_weight:.0%} target cap apply only to the optimized alternative.</li>
<li>The annual risk-free rate is a constant scenario assumption of {config.annual_rf:.2%}, not an observed historical rate series.</li>
<li>No taxes, bid/ask variation, market impact, execution delay, or point-in-time universe reconstruction. Low beta does not establish capital safety; past scenarios do not forecast performance.</li>
</ul><p class="small">Data fingerprint (normalized price table SHA-256): {price_hash}<br>Source: {source_safe}</p></section>
<footer class="small">PortfolioLens · Portfolio review prototype · Built from an APAN 5540 team-project concept. User interviews and measured workflow impact are pending.</footer>
</main></body></html>'''
    (output / "review.html").write_text(markup)
    metrics.to_csv(output / "metrics.csv", index_label="strategy")
    net.to_csv(output / "net_returns.csv", index_label="date")
    for name, frame in result["trades"].items():
        safe_name = "".join(c if c.isalnum() else "_" for c in name).lower()
        frame.to_csv(output / f"trades_{safe_name}.csv", index=False)
    payload = {"source": source, "price_sha256": price_hash, "config": asdict(config),
               "holdings": result["holdings"], "observations": len(net),
               "training_end": str(result["training_end"].date()),
               "evaluation_start": str(start), "evaluation_end": str(end),
               "metrics": json.loads(metrics.T.to_json())}
    (output / "run.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return output / "review.html"
