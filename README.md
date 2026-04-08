# Leveraged Portfolio Backtester

Simple backtest comparing **SPY buy-and-hold** to an **original “Gayed-style” Leverage Rotation Strategy (LRS)** using daily ETF data.

## Strategy (this implementation)

The script implements a two-regime rotation:

1. **Risk-on** — When **SPY’s closing price is above its 200-day simple moving average**, the portfolio holds **UPRO** (3× daily S&P 500 ETF) and earns UPRO’s daily return. The signal uses **yesterday’s** regime (no look-ahead: the MA comparison is shifted by one day before applying today’s return).
2. **Risk-off** — When SPY is **at or below** the 200-day SMA, the portfolio holds **BIL** (short-term Treasury ETF) and earns BIL’s daily return.

**Benchmark:** SPY buy-and-hold with the same start capital.

The idea matches the paper’s theme: use **leverage when the broad equity trend filter suggests a favorable environment**, and **step down to cash-like Treasuries** when the filter turns defensive—rather than staying fully leveraged through deep drawdowns.

## Paper and background

The logic is inspired by **Michael Gayed**, *Leverage for the Long Run: A Systematic Approach to Managing Risk and Magnifying Returns in Stocks* (SSRN), which won the **2016 Charles H. Dow Award**. The paper argues for a systematic way to add leverage when conditions (e.g. trend / moving-average regimes) are more supportive, and reduce leverage when they are not.

- SSRN: [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2741701](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2741701)

This repository is an **educational backtest**, not a replication of every detail in the paper (which explores multiple leverage levels, MA lengths, and statistics). Here we use **200-day SMA**, **UPRO**, and **BIL** only.

## Requirements

- Python 3.9+ (typical; adjust if your environment differs)
- Install dependencies:

```bash
pip install -r requirements.txt
```

## How to run the backtest

From the project root:

```bash
python lrs_original_gayed_vs_spy.py
```

The script will:

1. Download **SPY**, **UPRO**, and **BIL** from Yahoo Finance (default range is set in the file: `START` / `END`).
2. Print a small performance table (annualized return, volatility, Sharpe-style ratio, max drawdown, final value) and time spent in UPRO vs BIL.
3. Save a chart to **`outputs/lrs_original_gayed_vs_spy.png`** (equity curves on a log scale and drawdown panel).
4. Open an interactive plot window if your environment supports `matplotlib` display.

You can change the backtest window, starting capital, or SMA length by editing the constants at the top of `lrs_original_gayed_vs_spy.py` (`START`, `END`, `INITIAL`, `SPY_SMA`).

## Limitations

- **No transaction costs, slippage, or taxes** are modeled.
- **UPRO** is a daily-reset leveraged ETF; path dependency and volatility drag differ from continuous leverage in the paper’s framing.
- **Past performance does not guarantee future results.** This is not investment advice.
