# PortfolioLens — product brief

## Problem hypothesis

A small-firm investment analyst must assemble prices, compare portfolio alternatives, and explain risk in a recurring review. A transparent, repeatable review artifact may reduce manual work and make assumptions easier to inspect. This hypothesis has not yet been validated by interviews.

## First user and workflow

1. Provide holdings and a consistent adjusted daily-price history.
2. Confirm the evaluation window, concentration cap, cost assumption, and risk-free assumption.
3. Compare the supplied allocation, equal weights, and capped minimum variance against a common benchmark.
4. Inspect the decision brief, net performance, drawdown, and trade logs.
5. Share a static HTML review and explain the assumptions.

The first release uses a CLI and notebook to generate an analyst-facing report. There is no interactive upload UI or hosted service yet.

## Prioritization

| Priority | Item | Why |
|---|---|---|
| P0, implemented | Reproducible offline demo | Interview demos should not depend on a live API |
| P0, implemented | Comparable allocation scenarios | Supports a concrete portfolio-review decision |
| P0, implemented | Timing, drift, costs, input validation | Prevents misleading comparisons |
| P0, implemented | Traceable report and metrics | Lets an analyst explain and inspect the result |
| P1, this week | Reconcile one market-data case | Establishes trust in real inputs and calculations |
| P1, this week | Two observed review sessions | Tests usefulness with a small, honest sample |
| P1, this week | Three-minute demo and six-slide case study | Makes the project usable in applications |
| Later | Browser upload and scenario controls | Valuable after validating the workflow |
| Later | Point-in-time universe and factor attribution | Needed for stronger investment research claims |

## Acceptance criteria

- Offline demo completes after installation and labels its data as synthetic throughout.
- Every strategy uses the same evaluation dates and cost convention.
- Changing future prices cannot alter prior optimized targets.
- A reader can distinguish holding-period return from annualized estimates.
- Invalid inputs fail with an actionable error, rather than being silently filled or normalized.
- A reviewer can identify the largest holding, compare drawdowns, and find the assumptions.
- The report has no external network assets and can be shared as a single HTML file.

## Validation plan — not results

Recruit two people familiar with finance coursework or analyst workflows. Ask each to identify the largest concentration, compare alternatives, and explain one limitation using their current approach and then PortfolioLens. Counterbalance the order where feasible.

Record completion time, completion success, calculation/interpretation errors, and a short confidence rating. Keep qualitative notes on confusion. With two participants, report descriptive observations only; do not claim statistically established productivity gains.

**Primary measure:** time to a correctly completed review task. **Guardrail:** financial interpretation errors must not increase. Secondary: ability to locate data provenance and assumptions.

## Product tradeoffs

Minimum variance avoids treating a noisy historical mean as a reliable forecast. Equal weight supplies a simple baseline. A static report is easy to inspect and share; an interactive UI remains a later usability improvement. A synthetic fixture keeps demonstrations reproducible, while the market adapter enables separate real-data validation.
