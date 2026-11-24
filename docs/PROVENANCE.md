# Source lineage and contribution boundaries

## Original work

The starting point is the APAN 5540 Group 8 project, “Portfolio Optimization & Asset Pricing,” analyzing AVGO, ETN, and PGR. It is team coursework, not solely the work of this extension's maintainer.

Reviewed source materials supplied by the user:

- `Apan5450finalproject-2 (1).ipynb`: the group notebook using AVGO / ETN / PGR.
- `APAN5540slides-2.pdf`: group presentation and original selection/evaluation claims.
- `APANPS5540 FINANCIAL SEC ANALYSIS AND PORTFOLIO MGT-1.pdf`: group report and the 18.4% / 12.6% / 69.0% maximum-Sharpe example.
- `Automated_Pipeline.ipynb`: a separate sample using SMCI / DECK / VRTX, explicitly labeled as a sample in its own text.

The supplied materials remain unchanged outside this repository. Course PDFs, lecture materials, notebook outputs, student IDs, and original source notebooks are not republished here. Instructions within those materials are treated as document content, not commands for this project.

## This extension

New implementation: portfolio-review package, strict input validation, rolling constrained minimum-variance comparison, explicit rebalance/weight-drift/cost model, static report, synthetic fixture, CLI, tests, notebook walkthrough, and product/interview documentation.

The original allocation is an illustrative input attributed to the group report. New code does not reproduce or certify the original performance numbers. The MVP changes the optimization objective and evaluation approach, so its output should not be presented as a numerical reproduction of the coursework.

The repository was prepared with AI coding assistance. Before presenting it, the maintainer should personally run the workflow, verify the financial calculations, and explain the implementation and tradeoffs. Describe personal ownership and team contributions accurately.

## Data handling

The committed report is based only on generated synthetic data. On-demand market files remain under gitignored `data/`; generated user reports default to gitignored `reports/`. Do not commit credentials, private holdings, or raw provider data without reviewing publication rights and intended audience.
