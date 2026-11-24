import argparse
from pathlib import Path

from .data import demo_prices, download_prices, fingerprint, read_holdings, read_prices
from .engine import Config, review
from .report import write_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="PortfolioLens: reproducible portfolio review")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("review", help="Compare allocations and generate an HTML review")
    source = run.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="Use explicitly synthetic offline prices")
    source.add_argument("--prices", type=Path, help="Wide daily adjusted-price CSV: date,tickers...")
    run.add_argument("--holdings", type=Path, help="CSV with ticker,weight; required with --prices")
    run.add_argument("--output", type=Path, default=Path("reports/latest"))
    run.add_argument("--lookback", type=int, default=252)
    run.add_argument("--max-weight", type=float, default=.5)
    run.add_argument("--cost-bps", type=float, default=10)
    run.add_argument("--annual-rf", type=float, default=.04)
    run.add_argument("--benchmark", default="SPY")
    download = commands.add_parser("download", help="Opt-in adjusted market-price download")
    download.add_argument("--tickers", nargs="+", default=["AVGO", "ETN", "PGR", "SPY"])
    download.add_argument("--start", default="2019-01-01")
    download.add_argument("--end", required=True, help="Exclusive end date, YYYY-MM-DD")
    download.add_argument("--output", type=Path, default=Path("data/prices.csv"))
    args = parser.parse_args(argv)
    try:
        if args.command == "download":
            prices = download_prices(args.tickers, args.start, args.end, args.output)
            print(f"Saved {len(prices):,} daily observations to {args.output}")
            return
        if not args.demo and args.holdings is None:
            parser.error("--holdings is required with --prices")
        holdings = read_holdings(args.holdings) if args.holdings else {"AVGO": .184, "ETN": .126, "PGR": .69}
        prices = demo_prices() if args.demo else read_prices(args.prices)
        source = ("SYNTHETIC DEMO - simulated prices, not historical market results"
                  if args.demo else "USER-SUPPLIED PRICE CSV - verify adjustment, provenance, and sampling")
        config = Config(args.lookback, args.max_weight, args.cost_bps, args.annual_rf, args.benchmark)
        result = review(prices, holdings, config)
        path = write_report(result, args.output, source, fingerprint(prices))
        print(source)
        print(f"Review saved to {path.resolve()}")
        print(f"Evaluation: {len(result['net_returns'])} daily observations; risk-free rate is a scenario assumption")
    except (ValueError, OSError, ImportError) as error:
        parser.exit(2, f"PortfolioLens: {error}\n")
