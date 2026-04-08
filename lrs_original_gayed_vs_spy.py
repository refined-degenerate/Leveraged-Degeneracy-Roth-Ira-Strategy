"""
Leverage Rotation Strategy — Original Gayed vs SPY Buy & Hold
==============================================================
Two-way comparison:

  1. SPY buy & hold   — passive benchmark           (amber dashed)
  2. Original LRS     — UPRO above SPY 200-day SMA  (blue solid)
                        BIL below SPY 200-day SMA

Requirements:  pip install yfinance pandas matplotlib numpy
"""

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import yfinance as yf

# ── Configuration ─────────────────────────────────────────────────────────────

START   = "2010-01-01"
END     = "2024-12-31"
INITIAL = 10_000
SPY_SMA = 200

COLORS = {
    "Original LRS": "#4fc3f7",
    "SPY":          "#ffb74d",
}
STYLES = {
    "Original LRS": ("-",  2.4),
    "SPY":          ("--", 1.8),
}

# ── Data ──────────────────────────────────────────────────────────────────────

print("Downloading data...")
raw = yf.download(
    ["SPY", "UPRO", "BIL"],
    start=START, end=END, auto_adjust=True, progress=False
)
prices = raw["Close"].copy()
prices.dropna(how="all", inplace=True)
ret = prices.pct_change()
print(f"Data: {prices.index[0].date()} to {prices.index[-1].date()}  ({len(prices)} days)\n")

# ── Signal ────────────────────────────────────────────────────────────────────

spy_above_200 = (prices["SPY"] > prices["SPY"].rolling(SPY_SMA).mean()).shift(1)

# ── Strategy ──────────────────────────────────────────────────────────────────

def run_lrs():
    daily = pd.Series(0.0, index=ret.index)
    for date in ret.index:
        r_spy = spy_above_200.get(date)
        if pd.isna(r_spy):
            continue
        if r_spy:
            daily[date] = ret.loc[date, "UPRO"]
        else:
            daily[date] = ret.loc[date, "BIL"]
    return daily

series = {
    "Original LRS": run_lrs(),
    "SPY":          ret["SPY"],
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def equity_curve(r):
    return INITIAL * (1 + r).cumprod()

def drawdown_series(r):
    cum = (1 + r).cumprod()
    return (cum - cum.cummax()) / cum.cummax()

# ── Performance summary ───────────────────────────────────────────────────────

print(f"{'Strategy':<16} {'Ann. Return':>12} {'Ann. Vol':>10} "
      f"{'Sharpe':>8} {'Max DD':>10} {'Final Value':>14}")
print("─" * 74)
for name, r in series.items():
    ann_ret = (1 + r.mean()) ** 252 - 1
    ann_vol = r.std() * np.sqrt(252)
    sharpe  = ann_ret / ann_vol if ann_vol else 0
    max_dd  = drawdown_series(r).min()
    final   = equity_curve(r).iloc[-1]
    print(f"{name:<16} {ann_ret*100:>11.1f}%  {ann_vol*100:>8.1f}%  "
          f"{sharpe:>7.2f}  {max_dd*100:>8.1f}%  ${final:>13,.0f}")

valid    = spy_above_200.notna()
risk_on  = spy_above_200[valid].sum()
risk_off = (~spy_above_200[valid]).sum()
total    = valid.sum()
print(f"\nTime in UPRO (risk-on):  {risk_on} days ({risk_on/total*100:.1f}%)")
print(f"Time in BIL  (risk-off): {risk_off} days ({risk_off/total*100:.1f}%)")

# ── Plot ──────────────────────────────────────────────────────────────────────

BG   = "#0f1117"
GRID = "#1a1a2a"
SPIN = "#2a2a3a"
TXTM = "#e0e0e0"
TXTD = "#888899"

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(13, 11),
    gridspec_kw={"height_ratios": [3, 2]}
)
fig.patch.set_facecolor(BG)

for ax in (ax1, ax2):
    ax.set_facecolor(BG)
    ax.tick_params(colors=TXTD, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(SPIN)
    ax.grid(axis="y", color=GRID, linewidth=0.7, zorder=0)
    ax.grid(axis="x", color=GRID, linewidth=0.4, zorder=0)

bears = [
    ("2010-04-23", "2010-07-02"),
    ("2011-05-02", "2011-10-03"),
    ("2015-08-18", "2015-09-29"),
    ("2018-10-03", "2018-12-24"),
    ("2020-02-19", "2020-03-23"),
    ("2022-01-03", "2022-10-12"),
]
for ax in (ax1, ax2):
    for s, e in bears:
        ax.axvspan(pd.Timestamp(s), pd.Timestamp(e),
                   alpha=0.10, color="#ef5350", zorder=0)

# ── Panel 1: Equity curves ────────────────────────────────────────────────────

for name, r in series.items():
    ls, lw = STYLES[name]
    curve = equity_curve(r)
    ax1.plot(curve.index, curve.values,
             color=COLORS[name], linewidth=lw, linestyle=ls,
             label=name, alpha=0.92, zorder=3)
    ax1.annotate(f"  ${curve.iloc[-1]:,.0f}",
                 xy=(curve.index[-1], curve.iloc[-1]),
                 color=COLORS[name], fontsize=9.5, va="center")

ax1.set_yscale("log")
ax1.set_title("Equity curve  (log scale, $10,000 start)",
              color=TXTM, fontsize=13, pad=10, loc="left")
ax1.set_ylabel("Portfolio value", color=TXTD, fontsize=10)
ax1.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax1.legend(facecolor="#1a1a2e", edgecolor=SPIN,
           labelcolor=TXTM, fontsize=10, loc="upper left", framealpha=0.8)

# ── Panel 2: Drawdown ─────────────────────────────────────────────────────────

ax2.set_title("Drawdown from peak",
              color=TXTM, fontsize=13, pad=10, loc="left")
ax2.set_ylabel("Drawdown", color=TXTD, fontsize=10)

label_offsets = {
    "Original LRS": 0.06,
    "SPY":          -0.07,
}

for name, r in series.items():
    ls, lw = STYLES[name]
    dd          = drawdown_series(r)
    max_dd      = dd.min()
    max_dd_date = dd.idxmin()

    ax2.fill_between(dd.index, dd.values, 0,
                     alpha=0.15, color=COLORS[name], zorder=2)
    ax2.plot(dd.index, dd.values,
             color=COLORS[name], linewidth=lw, linestyle=ls,
             alpha=0.9, zorder=3, label=name)
    ax2.scatter(max_dd_date, max_dd, color=COLORS[name], s=50, zorder=5)
    ax2.annotate(
        f"{name}  {max_dd*100:.1f}%",
        xy=(max_dd_date, max_dd),
        xytext=(max_dd_date, max_dd + label_offsets.get(name, 0.04)),
        color=COLORS[name], fontsize=9.5,
        ha="center", va="bottom",
    )

ax2.axhline(-0.40, color="#ffffff", linewidth=0.7,
            linestyle="--", alpha=0.22, zorder=1)
ax2.text(prices.index[SPY_SMA + 20], -0.415,
         "–40%  rough psychological survival threshold",
         color=TXTD, fontsize=8.5, va="top")

ax2.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
ax2.legend(facecolor="#1a1a2e", edgecolor=SPIN,
           labelcolor=TXTM, fontsize=10, loc="lower left", framealpha=0.8)

# ── Footer ────────────────────────────────────────────────────────────────────

fig.text(
    0.5, 0.004,
    "Original Gayed LRS: UPRO when SPY above 200-day SMA, BIL when below  |  "
    "No transaction costs or tax modelled  |  UPRO inception Jul 2009",
    ha="center", color="#555566", fontsize=8.5,
)

plt.tight_layout(rect=[0, 0.018, 1, 1])
_out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(_out_dir, exist_ok=True)
_png = os.path.splitext(os.path.basename(__file__))[0] + ".png"
out = os.path.join(_out_dir, _png)
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"\nSaved → {out}")
plt.show()
