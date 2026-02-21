"""EWMA Volatility Targeting Overlay (AAPL example)

This script mirrors the notebook logic and writes charts to ./results.
Data inputs are expected in ./data (semicolon-delimited Bloomberg-style CSV).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["figure.figsize"] = (12, 5)

DATA_DIR = Path("data")
OUT_DIR = Path("results")
OUT_DIR.mkdir(exist_ok=True)

def load_bbg_csv(path: Path, value_candidates):
    df = pd.read_csv(path, sep=";", engine="python")
    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col).set_index(date_col)

    value_col = None
    for c in value_candidates:
        if c in df.columns:
            value_col = c
            break
    if value_col is None:
        raise ValueError(f"No value column found in {path}. Available columns: {list(df.columns)}")

    s = pd.to_numeric(df[value_col], errors="coerce").dropna()
    s.name = value_col
    return s

def kpis(returns, rf=None):
    r = returns.dropna()
    if rf is None:
        rf = 0.0
        ex = r
    else:
        ex = (r - rf.loc[r.index]).dropna()

    ann_ret = (1.0 + r).prod() ** (252.0 / len(r)) - 1.0
    ann_vol = r.std() * np.sqrt(252.0)
    sharpe = (ex.mean() / r.std()) * np.sqrt(252.0) if r.std() > 0 else np.nan

    eq = (1.0 + r).cumprod()
    dd = eq / eq.cummax() - 1.0
    maxdd = dd.min()
    calmar = ann_ret / abs(maxdd) if maxdd < 0 else np.nan

    return {
        "CAGR": ann_ret,
        "AnnVol": ann_vol,
        "Sharpe": sharpe,
        "MaxDD": maxdd,
        "Calmar": calmar
    }

def drawdown(eq):
    return eq / eq.cummax() - 1.0

def main():
    aapl = load_bbg_csv(
        DATA_DIR / "AAPL_daily_adj_20190101_today.csv",
        value_candidates=["LAST", "PX_LAST", "Close", "close", "Adj Close", "adj_close"]
    ).rename("aapl_close")

    vix = load_bbg_csv(
        DATA_DIR / "VIX_daily_adj_20190101_today.csv",
        value_candidates=["PX_LAST", "LAST", "Close", "close"]
    ).rename("vix")

    us2y = load_bbg_csv(
        DATA_DIR / "US2Y_daily_adj_20190101_today.csv",
        value_candidates=["PX_LAST", "LAST", "Close", "close", "yield", "Yield"]
    ).rename("us2y_yield")

    df = pd.concat([aapl, vix, us2y], axis=1).sort_index()
    df[["vix", "us2y_yield"]] = df[["vix", "us2y_yield"]].ffill()
    df = df.dropna()

    df["ret"] = df["aapl_close"].pct_change()
    df["rf_daily"] = (df["us2y_yield"] / 100.0) / 252.0
    df = df.dropna()

    # --- parameters
    lookback_vol = 20
    target_vol = 0.40
    lev_cap = 1.3
    sma_window = 20
    sma_band = -0.02
    vix_cut = 35.0
    vix_width = 10.0
    cost_bps = 1.0

    # trend filter
    df["sma20"] = df["aapl_close"].rolling(sma_window).mean()
    df["trend_ok"] = (df["aapl_close"] > (1.0 + sma_band) * df["sma20"]).astype(float)

    # EWMA variance/vol
    alpha = 2.0 / (lookback_vol + 1.0)
    df["ewma_var"] = (df["ret"]**2).ewm(alpha=alpha, adjust=False).mean()
    df["vol_hat_ann"] = np.sqrt(252.0 * df["ewma_var"]).replace(0, np.nan)

    df["w_raw"] = (target_vol / df["vol_hat_ann"]).clip(lower=0.0, upper=lev_cap).fillna(0.0)
    df["g_vix"] = (1.0 - (df["vix"] - vix_cut) / vix_width).clip(lower=0.0, upper=1.0)
    df["w"] = (df["w_raw"] * df["trend_ok"] * df["g_vix"]).clip(lower=0.0, upper=lev_cap)

    w_prev = df["w"].shift(1).fillna(0.0)
    gross = w_prev * df["ret"] + (1.0 - w_prev) * df["rf_daily"]
    turnover = (df["w"] - w_prev).abs()
    cost = (cost_bps / 10000.0) * turnover

    df["strat_ret"] = gross - cost
    df["bh_ret"] = df["ret"]

    df["eq_strat"] = (1.0 + df["strat_ret"]).cumprod()
    df["eq_bh"] = (1.0 + df["bh_ret"]).cumprod()

    # vol-matched buy&hold
    bh_vol = df["bh_ret"].std() * np.sqrt(252.0)
    strat_vol = df["strat_ret"].std() * np.sqrt(252.0)
    w_bh = float(np.clip(strat_vol / bh_vol if bh_vol > 0 else 1.0, 0.0, 3.0))

    df["bh_vm_ret"] = w_bh * df["ret"] + (1.0 - w_bh) * df["rf_daily"]
    df["eq_bh_vm"] = (1.0 + df["bh_vm_ret"]).cumprod()

    print("Strategy KPIs:", kpis(df["strat_ret"], rf=df["rf_daily"]))
    print("Buy&Hold KPIs:", kpis(df["bh_ret"], rf=df["rf_daily"]))
    print("Vol-matched Buy&Hold KPIs:", kpis(df["bh_vm_ret"], rf=df["rf_daily"]))

    # Charts
    plt.figure()
    plt.plot(df.index, df["eq_strat"], label="Strategy (EWMA VolTarget + Trend)")
    plt.plot(df.index, df["eq_bh"], label="Buy & Hold AAPL (100%)")
    plt.plot(df.index, df["eq_bh_vm"], label=f"Buy & Hold vol-matched (w={w_bh:.2f})")
    plt.title("Equity Curves")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "equity_curves.png", dpi=160)

    plt.figure()
    plt.plot(df.index, drawdown(df["eq_strat"]), label="Strategy DD")
    plt.plot(df.index, drawdown(df["eq_bh"]), label="Buy&Hold 100% DD")
    plt.plot(df.index, drawdown(df["eq_bh_vm"]), label="Buy&Hold vol-matched DD")
    plt.title("Drawdowns")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "drawdowns.png", dpi=160)

    plt.figure()
    plt.plot(df.index, df["w"], label="Strategy weight w")
    plt.title("Strategy Exposure Weight")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "weights.png", dpi=160)

    plt.figure()
    plt.plot(df.index, df["aapl_close"], label="AAPL")
    plt.plot(df.index, df["sma20"], label="SMA20")
    plt.title("AAPL Price and SMA20")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "price_sma.png", dpi=160)

    print(f"Saved charts to: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
