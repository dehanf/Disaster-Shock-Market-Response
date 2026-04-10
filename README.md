# Market Reactions to Natural Disasters: An Event Study of Cyclone Ditwah's Impact on the Colombo Stock Exchange

**Authors:** Jayawardana K.P.T., Wickramaratne W.P.G.A., Wijesinghe D.S., Fernando W.T.D., Dinapura H.H.S.

Department of Computer Science & Engineering, University of Moratuwa, Sri Lanka

---

## Overview

This project applies a classical event-study framework to measure how Cyclone Ditwah — which struck eastern Sri Lanka on 28 November 2025 — affected stock returns on the Colombo Stock Exchange (CSE). Using a self-collected dataset of 70,413 daily OHLCV records for 268 CSE-listed stocks (February 2025 – February 2026), the study estimates market-model parameters for 237 qualifying stocks, computes sector-level cumulative abnormal returns (CARs) across 20 CSE sectors, and tests for statistical significance using both parametric and non-parametric methods.

Key findings:
- Transportation (−10.03%) and Real Estate (−9.23%) recorded the largest full-window CARs.
- Three sectors showed statistically significant negative median CARs: Insurance (*p* = 0.009), Real Estate (*p* = 0.017), and Diversified Financials (*p* = 0.034).
- The market-wide shock is highly significant (*p* < 0.001).
- A two-phase market microstructure response was identified: an intraday volatility spike at landfall followed by a persistent ~35% decline in daily trading volume.

---

## Project Structure

```
.
├── data/
│   ├── stock_prices.csv          # Raw daily OHLCV data for all CSE-listed stocks
│   ├── aspi.csv                  # All Share Price Index (market benchmark) data
│   ├── sector_mapping.csv        # Ticker-to-sector mapping for 268 stocks
│   └── Sectors/                  # Per-sector raw data files (20 sectors)
│
├── notebooks/
│   ├── 01 Data cleaning/
│   │   ├── 01_sector_imputing.ipynb    # Impute missing sector labels
│   │   ├── 02_handling_suffix.ipynb    # Standardise ticker suffixes
│   │   └── 03_aspi_add.ipynb           # Merge ASPI benchmark into stock data
│   ├── 02 Model Building/
│   │   └── 04_Regression.ipynb         # Estimate market-model (alpha, beta) and compute CARs
│   ├── 03 Visualizations/
│   │   └── 05_paper_figures.ipynb      # Generate all figures used in the paper
│   └── 04 Stats/
│       ├── 06_stat_testing.ipynb       # Parametric t-tests on CARs
│       └── 07_Wilcoxon_and_Volatility.ipynb  # Wilcoxon signed-rank tests and volatility/liquidity analysis
│
├── output/
│   ├── processed_data/           # Intermediate CSVs produced by each notebook step
│   ├── figs/                     # Publication-ready figures (PDF)
│   └── tables/                   # Result tables (CSV) — CARs, t-tests, Wilcoxon, robustness
│
└── paper.tex                     # LaTeX source for the research paper
```

---

## Methodology

1. **Data cleaning** — Missing sector labels are imputed, ticker suffixes are standardised, and the ASPI index is merged as the market benchmark.
2. **Market model estimation** — OLS regression of each stock's returns on ASPI returns over the pre-event estimation window to obtain stock-specific α and β.
3. **Abnormal returns** — Expected returns are projected into the event window; abnormal returns (AR) and cumulative abnormal returns (CAR) are computed per stock and aggregated by sector.
4. **Statistical testing** — Cross-sectional *t*-tests and Wilcoxon signed-rank tests assess whether sector-level CARs are significantly different from zero.
5. **Market microstructure** — Volatility (standard deviation of returns) and liquidity (daily trading volume) are analysed pre- and post-event.

---

## Data

| File | Description |
|------|-------------|
| `data/stock_prices.csv` | Daily OHLCV for 268 CSE-listed stocks, Feb 2025 – Feb 2026 |
| `data/aspi.csv` | Daily ASPI index OHLCV (market benchmark) |
| `data/sector_mapping.csv` | Maps each ticker to one of 20 CSE sectors |
| `data/Sectors/` | Individual sector-level stock files |

The event date is **28 November 2025** (landfall of Cyclone Ditwah).

---

## Running the Analysis

Run the notebooks in order:

```bash
# 1. Data cleaning
notebooks/01 Data cleaning/01_sector_imputing.ipynb
notebooks/01 Data cleaning/02_handling_suffix.ipynb
notebooks/01 Data cleaning/03_aspi_add.ipynb

# 2. Model building & CARs
notebooks/02 Model Building/04_Regression.ipynb

# 3. Figures
notebooks/03 Visualizations/05_paper_figures.ipynb

# 4. Statistical tests
notebooks/04 Stats/06_stat_testing.ipynb
notebooks/04 Stats/07_Wilcoxon_and_Volatility.ipynb
```

Each notebook reads from `output/processed_data/` (or `data/` for the first step) and writes its outputs back to `output/processed_data/`, `output/figs/`, or `output/tables/`.

---

## Dependencies

The analysis is written in Python. Core libraries used:

- `pandas`, `numpy` — data manipulation
- `scipy`, `statsmodels` — regression and statistical tests
- `matplotlib`, `seaborn` — visualisation

---

## Citation

> Jayawardana K.P.T., Wickramaratne W.P.G.A., Wijesinghe D.S., Fernando W.T.D., Dinapura H.H.S. (2026). *Market Reactions to Natural Disasters: An Event Study of Cyclone Ditwah's Impact on the Colombo Stock Exchange.* Department of Computer Science & Engineering, University of Moratuwa.
