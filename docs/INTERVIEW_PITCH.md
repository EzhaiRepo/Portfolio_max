# Interview narrative

## Positioning

PortfolioLens is a portfolio-review workflow prototype. Its value proposition is clearer, more repeatable comparison of financial tradeoffs. It is best aligned with fintech product management and investment-oriented financial analysis. An FP&A application would need a different financial use case, such as budgets and cash flow.

## 30-second pitch — current, supportable scope

> I extended the concept of an APAN 5540 team project into PortfolioLens, a reproducible portfolio-review prototype. It compares a supplied allocation with equal weights and a constrained minimum-variance alternative, models monthly rebalancing and trading costs, and generates an analyst-facing decision brief. I focused on making the assumptions visible and the calculations testable. User validation and a fully reconciled market-data case are the next milestones.

Adjust first-person wording to match the work you personally understand, directed, and verified. Be ready to explain where coding assistance was used.

## Product manager version

Lead with the provisional user and their recurring review task. Explain why the MVP prioritizes scenario comparison, transparent assumptions, and a shareable report. Show one explicit tradeoff: a static artifact shipped first, while a browser interface and advanced factor models were deferred. Discuss the validation plan as a plan until sessions are completed.

Potential resume wording after personally validating the implementation:

- Developed a portfolio-review prototype translating concentration and allocation analysis into a repeatable analyst workflow with scenario comparisons and a shareable decision brief.
- Scoped a one-week MVP, defined acceptance criteria, and designed usability measures around correct task completion and review time.

Do not claim adoption, customer interviews, time savings, or commercial impact until measured.

## Financial analyst version

Lead with the 69% starting allocation to PGR and the decision to assess concentration. Explain how the capped minimum-variance alternative differs from equal weighting and the original maximum-Sharpe objective. Walk through a trade log, distinguish annualized from realized returns, and show a cost sensitivity.

Potential resume wording after personally validating the implementation:

- Extended a team portfolio-analysis project into a Python workflow comparing three allocation methods against SPY with rolling covariance estimates, monthly rebalancing, weight drift, and transaction costs.
- Added reproducible reports and automated checks for input integrity, drawdown calculation, allocation constraints, and future-data leakage in portfolio fitting.

Do not cite synthetic returns as investment outcomes or attribute the team's original research exclusively to yourself.

## Six-slide case study

1. **User and decision:** who prepares the review, what they need to decide, and which evidence is still a hypothesis.
2. **Starting point:** original team project, 69% PGR example, and limitations of its selection/evaluation process.
3. **Product scope:** holdings → comparison → decision brief; why these features came first.
4. **Financial method:** simple baseline, rolling estimation, explicit timing, costs, and limitations.
5. **Demonstration and validation:** one report, automated test evidence, real-data reconciliation status, and actual user findings if available.
6. **Tradeoffs and next steps:** where the prototype helps, what it cannot establish, and the next experiment.

## Three-minute demo

- 0:00–0:30 — Introduce the analyst's review task and the source lineage.
- 0:30–1:00 — Show holdings and the concentration issue.
- 1:00–1:45 — Compare allocations, net performance, and drawdown.
- 1:45–2:15 — Change a cost or cap assumption and inspect the tradeoff.
- 2:15–2:45 — Show a trade log and explain prior-data-only fitting.
- 2:45–3:00 — State one finding, one limitation, and the next validation step.

Use the offline report if market services are unavailable. State clearly when the demonstration is synthetic.
