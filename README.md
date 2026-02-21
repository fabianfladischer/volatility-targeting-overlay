# Volatility Targeting Overlay

A research-style Python backtest of a volatility targeting overlay designed to keep portfolio risk more stable through time while remaining implementable (leverage caps, turnover controls, and transaction cost sensitivity).

## What this project does
- Estimates realized volatility (rolling and/or EWMA)
- Computes a target leverage/exposure to reach a chosen volatility target
- Applies implementability constraints (leverage cap, rebalance rules / turnover control)
- Produces backtest diagnostics (performance, drawdowns, turnover, cost sensitivity)

## Outputs (planned)
- Exposure/leverage time series vs realized volatility
- Performance summary (CAGR, volatility, Sharpe, max drawdown)
- Turnover and transaction cost sensitivity
- Stress-window diagnostics (e.g., crisis periods)

## Repository structure
- `notebooks/` — example notebooks and experiments 
- `src/` — reusable functions/modules 
- `docs/` — one-pager and documentation

## One-pager
See: `docs/one_pager.pdf`

## Quickstart (local)
- python -m venv .venv
- source .venv/bin/activate   # Windows: .venv\Scripts\activate
- pip install -r requirements.txt
- python src/run_aapl_ewma_voltarget.py

## Notes
This is a personal research/portfolio project for educational purposes (not investment advice).
