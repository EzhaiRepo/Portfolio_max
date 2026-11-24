# Validation record

## Verified for the initial MVP

- Installed the package through its `pyproject.toml` editable-install path in an isolated Python 3.13 environment.
- All 20 automated tests passed locally.
- Ran the offline CLI end to end: 756 evaluation returns and four comparable strategies.
- Executed all five code cells of the demo notebook, including the cost-sensitivity comparison and report generation.
- Opened the generated HTML in a browser and visually inspected the complete report, chart, tables, and assumptions.
- Exercised the optional market downloader and CSV review path locally: 1,984 downloaded daily price rows and 1,731 evaluation returns. Market files and reports are gitignored and are not included in the public demo.

## What the tests cover

Hand-calculated checks cover drift between rebalances, entry and round-trip cost conventions, the first-period drawdown, return annualization, and benchmark information ratio. Additional tests cover cap/budget constraints, unchanged prior targets after future data are modified, higher costs reducing terminal wealth, invalid inputs, short history, and the self-contained synthetic report.

## Still to validate

Market-data availability can vary, and successful ingestion is not independent verification of vendor prices. Independently reconcile sample prices, monthly trades, and output measures before presenting a real-data performance case. User interviews, usability outcomes, production readiness, and investment alpha have not been established.

A GitHub Actions workflow runs the offline tests and demo on pushes and pull requests. Consult the repository's Actions tab for remote status; local test results are not a substitute for a completed remote run.
