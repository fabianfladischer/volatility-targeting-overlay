# Volatility Targeting Overlay

A research-style Python backtest of a volatility targeting overlay designed to keep portfolio risk more stable through time while remaining implementable (leverage caps, turnover controls, and transaction cost sensitivity).

This repository contains:
- a runnable script (`src/run_aapl_ewma_voltarget.py`) and
- a companion notebook (`notebooks/01_aapl_ewma_vol_target.ipynb`)

The example strategy uses an **EWMA realized volatility estimator** and applies practical implementation constraints.

---

## What this project does
- Estimates realized volatility (rolling and/or EWMA)
- Computes a target leverage/exposure to reach a chosen volatility target
- Applies implementability constraints (leverage cap, rebalance rules / turnover control)
- Produces backtest diagnostics (performance, drawdowns, turnover, cost sensitivity)

---

## Outputs
The script/notebook generates typical backtest diagnostics such as:
- exposure/leverage time series vs realized volatility
- performance summary (CAGR, volatility, Sharpe, max drawdown)
- turnover and transaction cost sensitivity
- stress-window diagnostics (when enabled)

If you export charts, they should be written to `results/`.

---

## Repository structure
- `notebooks/` — example notebooks and experiments
- `src/` — runnable script and reusable modules
- `docs/` — one-pager and documentation
- `data/` — local input data (kept private; not committed)
- `results/` — generated plots and outputs

---

## One-pager
See: `docs/one_pager.pdf`

---

## Quickstart (local)

### 1) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
### 2) Install dependencies
pip install -r requirements.txt
### 3) Run the example backtest
python src/run_aapl_ewma_voltarget.py

## Data Requirements
The example expects input CSVs in data/ (kept local and ignored by git).
### Typical files:
data/AAPL_daily_adj_20190101_today.csv
data/VIX_daily_adj_20190101_today.csv
(optional) data/US2Y_daily_adj_20190101_today.csv
### Your CSVs should contain:
a date column (first column), and
a price/value column such as PX_LAST / LAST / similar.
If your files have different column names, update the column mapping in src/run_aapl_ewma_voltarget.py.

## Notes
This is a personal research/portfolio project for educational purposes (not investment advice).
