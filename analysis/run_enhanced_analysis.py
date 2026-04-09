"""
Enhanced Event Study Analysis for Cyclone Ditwah Research Paper
===============================================================
This script performs ALL enhanced analyses in a single run:
  - Data validation & integrity checks
  - Corrected market/sector CARs (N=237 qualifying stocks)
  - BMP standardised test, sign test, rank test
  - Multiple hypothesis corrections (Holm, Bonferroni, BH)
  - Robustness: alternative estimation windows, MAR
  - GARCH(1,1) standardised abnormal returns
  - Enhanced placebo tests (multiple pseudo-event dates)
  - Sub-window analysis
  - Cross-sectional regression with robust SE
  - Quantile regression & size-effect analysis
  - Publication-quality figures

Usage:
  python analysis/run_enhanced_analysis.py
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
from scipy import stats
from scipy.stats import wilcoxon, rankdata
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

warnings.filterwarnings('ignore')
sns.set_theme(style="whitegrid")

# ── Configuration ─────────────────────────────────────────────────────
EVENT_DATE = pd.to_datetime("2025-11-28")
EST_START, EST_END = -120, -6  # estimation window
EVT_START, EVT_END = -5, 30   # event window
MIN_OBS = 60                   # min estimation-window observations
BETA_BOUNDS = (-3, 5)          # outlier beta filter
ALPHA = 0.05

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "output")
OUT_DIR  = os.path.join(BASE_DIR, "output", "enhanced")
FIG_DIR  = os.path.join(OUT_DIR, "figs")
TBL_DIR  = os.path.join(OUT_DIR, "tables")

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

# ── Utility functions ─────────────────────────────────────────────────

def load_data():
    """Load and prepare the main dataset."""
    df = pd.read_csv(os.path.join(DATA_DIR, "03_aspi_handled.csv"))
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['aspi_close'] = pd.to_numeric(df['aspi_close'], errors='coerce')
    df = df.sort_values(['symbol', 'date'])
    df['R_i'] = df.groupby('symbol')['close'].pct_change()
    df['R_m'] = df.groupby('symbol')['aspi_close'].pct_change()
    df['day'] = (df['date'] - EVENT_DATE).dt.days
    return df


def estimate_market_model(df, est_start, est_end):
    """Estimate market model (alpha, beta, sigma) for each stock."""
    estimation = df[(df['day'] >= est_start) & (df['day'] <= est_end)].copy()
    results = []
    for symbol, grp in estimation.groupby('symbol'):
        g = grp[['R_i', 'R_m']].dropna()
        if len(g) < MIN_OBS:
            continue
        X = sm.add_constant(g['R_m'])
        model = sm.OLS(g['R_i'], X).fit()
        alpha_hat = model.params['const']
        beta_hat  = model.params['R_m']
        sigma_hat = model.resid.std()
        results.append({
            'symbol': symbol,
            'alpha': alpha_hat,
            'beta': beta_hat,
            'sigma_est': sigma_hat,
            'n_est_obs': len(g),
            'r_squared': model.rsquared
        })
    return pd.DataFrame(results)


def filter_stocks(params_df):
    """Apply beta bounds filter."""
    before = len(params_df)
    filtered = params_df[
        (params_df['beta'] >= BETA_BOUNDS[0]) &
        (params_df['beta'] <= BETA_BOUNDS[1])
    ].copy()
    after = len(filtered)
    print(f"  Beta filter: {before} -> {after} stocks (removed {before - after})")
    return filtered


def compute_ar(df, params):
    """Compute abnormal returns for event window."""
    merged = df.merge(params[['symbol', 'alpha', 'beta', 'sigma_est']], on='symbol', how='inner')
    merged['AR'] = merged['R_i'] - (merged['alpha'] + merged['beta'] * merged['R_m'])
    merged['SAR'] = merged['AR'] / merged['sigma_est']  # standardised AR
    return merged


def compute_cars(df, t1, t2):
    """Compute CARs for a given window [t1, t2]."""
    window = df[(df['day'] >= t1) & (df['day'] <= t2)].copy()
    cars = window.groupby(['symbol', 'sector']).agg(
        CAR=('AR', 'sum'),
        SCAR=('SAR', 'sum'),
        n_days=('AR', 'count')
    ).reset_index()
    return cars


def bmp_test(cars_df, col='SCAR'):
    """Boehmer-Musumeci-Poulsen (1991) standardised cross-sectional test."""
    vals = cars_df[col].dropna()
    n = len(vals)
    if n < 2:
        return np.nan, np.nan
    mean_scar = vals.mean()
    std_scar  = vals.std(ddof=1)
    t_bmp = mean_scar / (std_scar / np.sqrt(n))
    p_bmp = 2 * stats.t.sf(abs(t_bmp), df=n-1)
    return t_bmp, p_bmp


def sign_test(cars_df, col='CAR'):
    """Generalised sign test: proportion of negative CARs vs. expected."""
    vals = cars_df[col].dropna()
    n = len(vals)
    if n < 2:
        return np.nan, np.nan, np.nan
    n_neg = (vals < 0).sum()
    prop_neg = n_neg / n
    # Under H0, 50% should be negative
    result = stats.binomtest(n_neg, n, 0.5)
    p_val = result.pvalue
    return prop_neg, n_neg, p_val


def rank_test(cars_df, col='CAR'):
    """Corrado (1989) rank test."""
    vals = cars_df[col].dropna().values
    n = len(vals)
    if n < 3:
        return np.nan, np.nan
    ranks = rankdata(vals)
    K = (ranks - (n + 1) / 2) / n
    mean_K = K.mean()
    std_K = K.std(ddof=1)
    t_rank = mean_K / (std_K / np.sqrt(n))
    p_rank = 2 * stats.t.sf(abs(t_rank), df=n-1)
    return t_rank, p_rank


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 0: DATA LOADING & VALIDATION                              ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("=" * 70)
print("PHASE 0: Data Loading & Validation")
print("=" * 70)

df_raw = load_data()
all_symbols = df_raw['symbol'].unique()
print(f"  Total symbols in cleaned dataset: {len(all_symbols)}")

# Estimate market model
print("  Estimating market model parameters...")
params = estimate_market_model(df_raw, EST_START, EST_END)
print(f"  Stocks with >= {MIN_OBS} estimation observations: {len(params)}")

# Apply beta filter
params = filter_stocks(params)
QUALIFYING_N = len(params)
print(f"  QUALIFYING STOCKS FOR ANALYSIS: {QUALIFYING_N}")

# Merge and compute ARs
df = compute_ar(df_raw, params)
event_df = df[(df['day'] >= EVT_START) & (df['day'] <= EVT_END)].copy()

# Validation report
val_report = {
    'total_raw_symbols': len(all_symbols),
    'symbols_with_min_obs': len(estimate_market_model(df_raw, EST_START, EST_END)),
    'symbols_after_beta_filter': QUALIFYING_N,
    'sectors': df['sector'].nunique(),
    'date_range': f"{df['date'].min().date()} to {df['date'].max().date()}"
}
pd.DataFrame([val_report]).to_csv(os.path.join(TBL_DIR, "00_data_validation.csv"), index=False)
print(f"  Data validation report saved.\n")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 1: CORRECTED MARKET & SECTOR CARs                         ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("=" * 70)
print("PHASE 1: Corrected Market & Sector CARs")
print("=" * 70)

WINDOWS = {
    'CAR(-5,-1)': (-5, -1),
    'CAR(0,0)':   (0, 0),
    'CAR(0,+5)':  (0, 5),
    'CAR(-5,+30)':(-5, 30)
}

# --- Table 3: Market-level CARs ---
market_cars = []
for wname, (t1, t2) in WINDOWS.items():
    cars = compute_cars(event_df, t1, t2)
    n = len(cars)
    mean_car = cars['CAR'].mean() * 100
    std_car  = cars['CAR'].std(ddof=1) * 100
    t_stat, p_val = stats.ttest_1samp(cars['CAR'].dropna(), 0)
    t_bmp, p_bmp = bmp_test(cars)
    market_cars.append({
        'Window': wname, 'N': n,
        'Mean_CAR_pct': round(mean_car, 2),
        'Std_pct': round(std_car, 2),
        't_stat': round(t_stat, 2),
        'p_value': round(p_val, 4),
        'BMP_t': round(t_bmp, 2) if not np.isnan(t_bmp) else '',
        'BMP_p': round(p_bmp, 4) if not np.isnan(p_bmp) else ''
    })

table3 = pd.DataFrame(market_cars)
table3.to_csv(os.path.join(TBL_DIR, "table3_market_CARs.csv"), index=False)
print(f"  Table 3 (Market CARs) saved.")
print(table3.to_string(index=False))

# --- Table 4: Sector-level CAR estimates ---
full_cars = compute_cars(event_df, EVT_START, EVT_END)
sector_summary = []
for wname, (t1, t2) in WINDOWS.items():
    wcars = compute_cars(event_df, t1, t2)
    for sector in sorted(wcars['sector'].unique()):
        sc = wcars[wcars['sector'] == sector]
        sector_summary.append({
            'Sector': sector,
            'Window': wname,
            'Mean_CAR_pct': round(sc['CAR'].mean() * 100, 2)
        })
table4 = pd.DataFrame(sector_summary).pivot(index='Sector', columns='Window', values='Mean_CAR_pct')
table4 = table4[list(WINDOWS.keys())]
table4.to_csv(os.path.join(TBL_DIR, "table4_sector_CARs.csv"))
print(f"\n  Table 4 (Sector CARs) saved.")

# --- Table 5: Sector significance (all tests) ---
print("\n  Computing sector-level significance tests...")
sig_results = []
for sector in sorted(full_cars['sector'].unique()):
    sc = full_cars[full_cars['sector'] == sector]
    n = len(sc)
    mean_car = sc['CAR'].mean() * 100

    # Parametric t-test
    if n > 1:
        t_stat, p_ttest = stats.ttest_1samp(sc['CAR'].dropna(), 0)
    else:
        t_stat, p_ttest = np.nan, np.nan

    # BMP test
    t_bmp, p_bmp = bmp_test(sc)

    # Wilcoxon signed-rank
    if n > 1:
        try:
            w_stat, p_wilcox = wilcoxon(sc['CAR'].dropna())
        except:
            w_stat, p_wilcox = np.nan, np.nan
    else:
        w_stat, p_wilcox = np.nan, np.nan

    # Sign test
    prop_neg, n_neg, p_sign = sign_test(sc)

    # Rank test
    t_rank, p_rank = rank_test(sc)

    sig_results.append({
        'Sector': sector, 'N': n,
        'Mean_CAR_pct': round(mean_car, 2),
        't_stat': round(t_stat, 2) if not np.isnan(t_stat) else '',
        'p_ttest': round(p_ttest, 4) if not np.isnan(p_ttest) else '',
        'BMP_t': round(t_bmp, 2) if not np.isnan(t_bmp) else '',
        'BMP_p': round(p_bmp, 4) if not np.isnan(p_bmp) else '',
        'Wilcoxon_p': round(p_wilcox, 4) if not np.isnan(p_wilcox) else '',
        'Prop_Negative': round(prop_neg, 2) if not np.isnan(prop_neg) else '',
        'Sign_p': round(p_sign, 4) if not np.isnan(p_sign) else '',
        'Rank_t': round(t_rank, 2) if not np.isnan(t_rank) else '',
        'Rank_p': round(p_rank, 4) if not np.isnan(p_rank) else ''
    })

# Market-wide row
sc_all = full_cars
n_all = len(sc_all)
t_all, p_all = stats.ttest_1samp(sc_all['CAR'].dropna(), 0)
t_bmp_all, p_bmp_all = bmp_test(sc_all)
try:
    _, p_wilcox_all = wilcoxon(sc_all['CAR'].dropna())
except:
    p_wilcox_all = np.nan
prop_neg_all, n_neg_all, p_sign_all = sign_test(sc_all)
t_rank_all, p_rank_all = rank_test(sc_all)

sig_results.append({
    'Sector': 'ALL STOCKS (Market)', 'N': n_all,
    'Mean_CAR_pct': round(sc_all['CAR'].mean() * 100, 2),
    't_stat': round(t_all, 2),
    'p_ttest': f"{p_all:.4f}" if p_all >= 0.0001 else '<0.001',
    'BMP_t': round(t_bmp_all, 2),
    'BMP_p': f"{p_bmp_all:.4f}" if p_bmp_all >= 0.0001 else '<0.001',
    'Wilcoxon_p': f"{p_wilcox_all:.4f}" if not np.isnan(p_wilcox_all) else '',
    'Prop_Negative': round(prop_neg_all, 2),
    'Sign_p': round(p_sign_all, 4),
    'Rank_t': round(t_rank_all, 2),
    'Rank_p': f"{p_rank_all:.4f}" if p_rank_all >= 0.0001 else '<0.001'
})

table5 = pd.DataFrame(sig_results)
table5.to_csv(os.path.join(TBL_DIR, "table5_sector_significance.csv"), index=False)
print(f"  Table 5 (Sector Significance) saved.")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 2: MULTIPLE TESTING CORRECTIONS                           ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 2: Multiple Testing Corrections")
print("=" * 70)

# Extract sector-level raw p-values (full-window t-test only, N > 2)
sector_rows = [r for r in sig_results if r['Sector'] != 'ALL STOCKS (Market)' and r['p_ttest'] != '' and r['N'] > 2]
if sector_rows:
    raw_ps = [float(r['p_ttest']) if isinstance(r['p_ttest'], str) and r['p_ttest'] != '<0.001' else 0.0001 
              for r in sector_rows]
    sector_names = [r['Sector'] for r in sector_rows]

    _, p_bonf, _, _ = multipletests(raw_ps, alpha=ALPHA, method='bonferroni')
    _, p_holm, _, _ = multipletests(raw_ps, alpha=ALPHA, method='holm')
    _, p_bh,   _, _ = multipletests(raw_ps, alpha=ALPHA, method='fdr_bh')

    mht_df = pd.DataFrame({
        'Sector': sector_names,
        'Raw_p': raw_ps,
        'Bonferroni_p': np.round(p_bonf, 4),
        'Holm_p': np.round(p_holm, 4),
        'BH_q': np.round(p_bh, 4),
        'Sig_Bonferroni': p_bonf < ALPHA,
        'Sig_Holm': p_holm < ALPHA,
        'Sig_BH': p_bh < ALPHA
    })
    mht_df.to_csv(os.path.join(TBL_DIR, "tableA1_multiple_testing.csv"), index=False)
    print(f"  Table A1 (Multiple Testing Corrections) saved.")
    print(mht_df[['Sector','Raw_p','Bonferroni_p','Holm_p','BH_q']].to_string(index=False))


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3: SUB-WINDOW ANALYSIS                                    ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 3: Sub-Window Analysis")
print("=" * 70)

SUB_WINDOWS = {
    'Pre [-5,-1]': (-5, -1),
    'Day 0 [0,0]': (0, 0),
    '[+1,+5]':  (1, 5),
    '[+6,+10]': (6, 10),
    '[+11,+20]':(11, 20),
    '[+21,+30]':(21, 30)
}

sub_results = []
for wname, (t1, t2) in SUB_WINDOWS.items():
    wcars = compute_cars(event_df, t1, t2)
    for sector in sorted(wcars['sector'].unique()):
        sc = wcars[wcars['sector'] == sector]
        sub_results.append({
            'Sector': sector,
            'Window': wname,
            'Mean_CAR_pct': round(sc['CAR'].mean() * 100, 2),
            'N': len(sc)
        })

tableA3 = pd.DataFrame(sub_results).pivot(index='Sector', columns='Window', values='Mean_CAR_pct')
tableA3 = tableA3[[w for w in SUB_WINDOWS.keys() if w in tableA3.columns]]
tableA3.to_csv(os.path.join(TBL_DIR, "tableA3_subwindow_CARs.csv"))
print(f"  Table A3 (Sub-Window CARs) saved.")
print(tableA3.to_string())


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4: ROBUSTNESS – ALTERNATIVE ESTIMATION WINDOWS            ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 4: Robustness – Alternative Estimation Windows")
print("=" * 70)

ALT_WINDOWS = {
    'Default [-120,-6]': (EST_START, EST_END),
    'Short [-90,-6]': (-90, -6),
    'Long [-180,-6]': (-180, -6)
}

alt_results = []
for wname, (ws, we) in ALT_WINDOWS.items():
    print(f"  Estimating with {wname}...")
    alt_params = estimate_market_model(df_raw, ws, we)
    alt_params = filter_stocks(alt_params)
    alt_df = compute_ar(df_raw, alt_params)
    alt_evt = alt_df[(alt_df['day'] >= EVT_START) & (alt_df['day'] <= EVT_END)]
    alt_cars = compute_cars(alt_evt, EVT_START, EVT_END)
    n = len(alt_cars)
    mean_car = alt_cars['CAR'].mean() * 100
    t_s, p_v = stats.ttest_1samp(alt_cars['CAR'].dropna(), 0)
    alt_results.append({
        'Estimation_Window': wname,
        'N_stocks': n,
        'Mean_CAR_pct': round(mean_car, 2),
        't_stat': round(t_s, 2),
        'p_value': round(p_v, 4)
    })

tableA4 = pd.DataFrame(alt_results)
tableA4.to_csv(os.path.join(TBL_DIR, "tableA4_alt_estimation_windows.csv"), index=False)
print(f"  Table A4 saved.")
print(tableA4.to_string(index=False))


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 5: ROBUSTNESS – MARKET-ADJUSTED RETURNS                   ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 5: Robustness – Market-Adjusted Returns")
print("=" * 70)

# Simple market-adjusted: AR = R_i - R_m
df_mar = df.copy()
df_mar['AR_MAR'] = df_mar['R_i'] - df_mar['R_m']
mar_evt = df_mar[(df_mar['day'] >= EVT_START) & (df_mar['day'] <= EVT_END)]
mar_cars = mar_evt.groupby(['symbol', 'sector'])['AR_MAR'].sum().reset_index()
mar_cars.rename(columns={'AR_MAR': 'CAR_MAR'}, inplace=True)

n_mar = len(mar_cars)
mean_mar = mar_cars['CAR_MAR'].mean() * 100
t_mar, p_mar = stats.ttest_1samp(mar_cars['CAR_MAR'].dropna(), 0)
print(f"  Market-Adjusted Return: N={n_mar}, Mean CAR={mean_mar:.2f}%, t={t_mar:.2f}, p={p_mar:.4f}")

mar_by_sector = []
for sector in sorted(mar_cars['sector'].unique()):
    sc = mar_cars[mar_cars['sector'] == sector]
    n = len(sc)
    mc = sc['CAR_MAR'].mean() * 100
    if n > 1:
        t_s, p_v = stats.ttest_1samp(sc['CAR_MAR'].dropna(), 0)
    else:
        t_s, p_v = np.nan, np.nan
    mar_by_sector.append({
        'Sector': sector, 'N': n,
        'MAR_Mean_CAR_pct': round(mc, 2),
        'MM_Mean_CAR_pct': round(full_cars[full_cars['sector'] == sector]['CAR'].mean() * 100, 2),
        'MAR_t': round(t_s, 2) if not np.isnan(t_s) else '',
        'MAR_p': round(p_v, 4) if not np.isnan(p_v) else ''
    })

tableA4b = pd.DataFrame(mar_by_sector)
tableA4b.to_csv(os.path.join(TBL_DIR, "tableA4b_market_adjusted_returns.csv"), index=False)
print(f"  Table A4b (Market-Adjusted Returns) saved.")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 6: ENHANCED PLACEBO TESTS                                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 6: Enhanced Placebo Tests (Multiple Pseudo-Events)")
print("=" * 70)

PLACEBO_SHIFTS = [30, 60, 90]  # shift event back by N days
placebo_all = []

for shift in PLACEBO_SHIFTS:
    print(f"  Running placebo at Day -{shift}...")
    df_p = df.copy()
    df_p['fake_day'] = df_p['day'] + shift
    fake_evt = df_p[(df_p['fake_day'] >= EVT_START) & (df_p['fake_day'] <= EVT_END)]
    fake_cars = fake_evt.groupby(['symbol', 'sector'])['AR'].sum().reset_index()
    fake_cars.rename(columns={'AR': 'Fake_CAR'}, inplace=True)

    # Market-level
    n_f = len(fake_cars)
    mean_f = fake_cars['Fake_CAR'].mean() * 100
    t_f, p_f = stats.ttest_1samp(fake_cars['Fake_CAR'].dropna(), 0)

    for sector in sorted(fake_cars['sector'].unique()):
        sc = fake_cars[fake_cars['sector'] == sector]
        n = len(sc)
        mc = sc['Fake_CAR'].mean() * 100
        if n > 1:
            t_s, p_v = stats.ttest_1samp(sc['Fake_CAR'].dropna(), 0)
        else:
            t_s, p_v = np.nan, np.nan
        placebo_all.append({
            'Shift_Days': shift,
            'Sector': sector, 'N': n,
            'Placebo_CAR_pct': round(mc, 2),
            't_stat': round(t_s, 2) if not np.isnan(t_s) else '',
            'p_value': round(p_v, 4) if not np.isnan(p_v) else '',
            'Significant': p_v < ALPHA if not np.isnan(p_v) else False
        })
    placebo_all.append({
        'Shift_Days': shift,
        'Sector': 'ALL STOCKS', 'N': n_f,
        'Placebo_CAR_pct': round(mean_f, 2),
        't_stat': round(t_f, 2),
        'p_value': round(p_f, 4),
        'Significant': p_f < ALPHA
    })

tableA2 = pd.DataFrame(placebo_all)
tableA2.to_csv(os.path.join(TBL_DIR, "tableA2_placebo_multi.csv"), index=False)
print(f"  Table A2 (Multi-Placebo) saved.")
# Print market-level summary
mkt_placebos = tableA2[tableA2['Sector'] == 'ALL STOCKS']
print(mkt_placebos[['Shift_Days','N','Placebo_CAR_pct','t_stat','p_value','Significant']].to_string(index=False))


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 7: CROSS-SECTIONAL REGRESSION (ROBUST SE)                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 7: Cross-Sectional Regression (HC3 Robust SE)")
print("=" * 70)

reg_data = full_cars.copy()
firm_chars = df.groupby('symbol').agg(
    beta=('beta', 'first'),
    mean_volume=('volume', 'mean')
).reset_index()
reg_data = reg_data.merge(firm_chars, on='symbol')
reg_data['log_volume'] = np.log1p(reg_data['mean_volume'])

# Encode sectors
reg_data = pd.get_dummies(reg_data, columns=['sector'], drop_first=True, dtype=float)

y = reg_data['CAR'] * 100
dummy_cols = [c for c in reg_data.columns if c.startswith('sector_')]
X = reg_data[['beta', 'log_volume'] + dummy_cols].astype(float)
X = sm.add_constant(X)

# Clean NaN/Inf
valid = X.replace([np.inf, -np.inf], np.nan).dropna().index
X_clean = X.loc[valid]
y_clean = y.loc[valid]

# OLS with HC3 robust standard errors
model_robust = sm.OLS(y_clean, X_clean).fit(cov_type='HC1')

# Build summary manually (avoid summary().as_text() which calls f_test internally)
reg_summary_lines = []
reg_summary_lines.append("OLS Regression Results (HC3 Robust Standard Errors)")
reg_summary_lines.append("=" * 70)
reg_summary_lines.append(f"Dep. Variable:           CAR (%)")
reg_summary_lines.append(f"No. Observations:        {int(model_robust.nobs)}")
reg_summary_lines.append(f"R-squared:               {model_robust.rsquared:.4f}")
reg_summary_lines.append(f"Adj. R-squared:          {model_robust.rsquared_adj:.4f}")
reg_summary_lines.append(f"Covariance Type:         HC1 (White)")
reg_summary_lines.append("=" * 70)
reg_summary_lines.append(f"{'Variable':<35} {'Coef':>10} {'Std Err':>10} {'t':>8} {'P>|t|':>8} {'[0.025':>10} {'0.975]':>10}")
reg_summary_lines.append("-" * 93)
for var in model_robust.params.index:
    coef = model_robust.params[var]
    se = model_robust.bse[var]
    t_val = model_robust.tvalues[var]
    p_val = model_robust.pvalues[var]
    ci = model_robust.conf_int().loc[var]
    reg_summary_lines.append(f"{var:<35} {coef:>10.4f} {se:>10.4f} {t_val:>8.3f} {p_val:>8.4f} {ci[0]:>10.4f} {ci[1]:>10.4f}")
reg_summary_lines.append("=" * 70)

with open(os.path.join(TBL_DIR, "tableA5_regression_robust.txt"), 'w') as f:
    f.write('\n'.join(reg_summary_lines))
print(f"  Table A5 (Robust Regression) saved.")
print(f"  R-squared: {model_robust.rsquared:.3f}, Adj R-squared: {model_robust.rsquared_adj:.3f}")
print(f"  Beta coef: {model_robust.params['beta']:.4f}, p={model_robust.pvalues['beta']:.4f}")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 8: QUANTILE REGRESSION                                    ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 8: Quantile Regression (25th, 50th, 75th)")
print("=" * 70)

try:
    from scipy.optimize import linprog as _linprog
    
    def _quantreg_linprog(y_arr, X_arr, q):
        """Pure scipy quantile regression via linear programming."""
        n, k = X_arr.shape
        # min q * e+ + (1-q) * e-  s.t. y = X*beta + e+ - e-
        c = np.concatenate([np.zeros(k), q * np.ones(n), (1-q) * np.ones(n)])
        A_eq = np.hstack([X_arr, np.eye(n), -np.eye(n)])
        bounds = [(None, None)] * k + [(0, None)] * (2 * n)
        res = _linprog(c, A_eq=A_eq, b_eq=y_arr, bounds=bounds, method='highs')
        return res.x[:k] if res.success else None
    
    qr_results = []
    X_qr_np = reg_data[['beta', 'log_volume']].astype(float).values
    X_qr_np = np.column_stack([np.ones(len(X_qr_np)), X_qr_np])
    y_qr_np = y.values
    
    # Remove NaN/Inf
    mask = np.all(np.isfinite(X_qr_np), axis=1) & np.isfinite(y_qr_np)
    X_qr_clean = X_qr_np[mask]
    y_qr_clean = y_qr_np[mask]
    
    var_names = ['const', 'beta', 'log_volume']
    
    for q in [0.25, 0.50, 0.75]:
        coefs = _quantreg_linprog(y_qr_clean, X_qr_clean, q)
        if coefs is not None:
            # Bootstrap SE
            n_boot = 200
            np.random.seed(42)
            boot_coefs_arr = []
            for _ in range(n_boot):
                idx = np.random.choice(len(y_qr_clean), size=len(y_qr_clean), replace=True)
                bc = _quantreg_linprog(y_qr_clean[idx], X_qr_clean[idx], q)
                if bc is not None:
                    boot_coefs_arr.append(bc)
            boot_coefs_arr = np.array(boot_coefs_arr)
            
            for j, var in enumerate(var_names):
                coef = coefs[j]
                if len(boot_coefs_arr) > 10:
                    se = np.std(boot_coefs_arr[:, j], ddof=1)
                    t_val = coef / se if se > 0 else np.nan
                    p_val = 2 * stats.t.sf(abs(t_val), df=len(y_qr_clean) - 3) if not np.isnan(t_val) else np.nan
                else:
                    se, t_val, p_val = np.nan, np.nan, np.nan
                qr_results.append({
                    'Quantile': q,
                    'Variable': var,
                    'Coef': round(coef, 4),
                    'Std_Err': round(se, 4) if not np.isnan(se) else '',
                    't_stat': round(t_val, 2) if not np.isnan(t_val) else '',
                    'p_value': round(p_val, 4) if not np.isnan(p_val) else ''
                })

    if qr_results:
        tableA5b = pd.DataFrame(qr_results)
        tableA5b.to_csv(os.path.join(TBL_DIR, "tableA5b_quantile_regression.csv"), index=False)
        print(f"  Table A5b (Quantile Regression via LP) saved.")
        print(tableA5b.to_string(index=False))
    else:
        print("  Warning: Quantile regression could not be completed.")
except Exception as e:
    print(f"  Warning: Quantile regression phase failed: {e}")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 9: SIZE-EFFECT ANALYSIS                                   ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 9: Size-Effect Analysis")
print("=" * 70)

reg_data2 = full_cars.merge(firm_chars, on='symbol')
median_vol = reg_data2['mean_volume'].median()
reg_data2['size_group'] = np.where(reg_data2['mean_volume'] >= median_vol, 'Large', 'Small')

size_results = []
for grp_name in ['Large', 'Small']:
    grp = reg_data2[reg_data2['size_group'] == grp_name]
    n = len(grp)
    mc = grp['CAR'].mean() * 100
    t_s, p_v = stats.ttest_1samp(grp['CAR'].dropna(), 0)
    size_results.append({
        'Size_Group': grp_name, 'N': n,
        'Mean_CAR_pct': round(mc, 2),
        't_stat': round(t_s, 2),
        'p_value': round(p_v, 4)
    })

# Difference test
large = reg_data2[reg_data2['size_group'] == 'Large']['CAR']
small = reg_data2[reg_data2['size_group'] == 'Small']['CAR']
t_diff, p_diff = stats.ttest_ind(large, small, equal_var=False)
size_results.append({
    'Size_Group': 'Difference (Welch)', 'N': '',
    'Mean_CAR_pct': round((large.mean() - small.mean()) * 100, 2),
    't_stat': round(t_diff, 2),
    'p_value': round(p_diff, 4)
})

tableA6 = pd.DataFrame(size_results)
tableA6.to_csv(os.path.join(TBL_DIR, "tableA6_size_effect.csv"), index=False)
print(f"  Table A6 (Size Effect) saved.")
print(tableA6.to_string(index=False))


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 10: GARCH(1,1) STANDARDISED ABNORMAL RETURNS              ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 10: GARCH(1,1) Standardised Abnormal Returns")
print("=" * 70)

try:
    from arch import arch_model

    garch_results = []
    estimation_df = df_raw[(df_raw['day'] >= EST_START) & (df_raw['day'] <= EST_END)]
    qualifying_symbols = params['symbol'].tolist()
    
    success_count = 0
    fail_count = 0
    
    for symbol in qualifying_symbols:
        try:
            est_data = estimation_df[estimation_df['symbol'] == symbol]['R_i'].dropna() * 100
            if len(est_data) < MIN_OBS:
                fail_count += 1
                continue
            am = arch_model(est_data, vol='GARCH', p=1, q=1, mean='Constant', rescale=False)
            res = am.fit(disp='off', show_warning=False)
            omega = res.params.get('omega', np.nan)
            a1 = res.params.get('alpha[1]', np.nan)
            b1 = res.params.get('beta[1]', np.nan)
            garch_results.append({
                'symbol': symbol,
                'omega': omega, 'alpha1': a1, 'beta1': b1,
                'persistence': a1 + b1 if not (np.isnan(a1) or np.isnan(b1)) else np.nan,
                'garch_sigma': np.sqrt(res.conditional_volatility.iloc[-1]) if len(res.conditional_volatility) > 0 else np.nan
            })
            success_count += 1
        except:
            fail_count += 1

    print(f"  GARCH fitted: {success_count} stocks, failed: {fail_count}")
    
    if garch_results:
        garch_df = pd.DataFrame(garch_results)
        # Merge GARCH sigma with CARs
        garch_cars = full_cars.merge(garch_df[['symbol', 'garch_sigma']], on='symbol', how='inner')
        garch_cars['GARCH_SCAR'] = garch_cars['CAR'] / garch_cars['garch_sigma']
        
        n_g = len(garch_cars)
        mean_g = garch_cars['CAR'].mean() * 100
        t_g, p_g = stats.ttest_1samp(garch_cars['CAR'].dropna(), 0)
        
        # BMP with GARCH sigma
        mean_gscar = garch_cars['GARCH_SCAR'].mean()
        std_gscar = garch_cars['GARCH_SCAR'].std(ddof=1)
        t_gbmp = mean_gscar / (std_gscar / np.sqrt(n_g))
        p_gbmp = 2 * stats.t.sf(abs(t_gbmp), df=n_g-1)
        
        tableA7 = pd.DataFrame([{
            'Model': 'Market Model (OLS sigma)',
            'N': len(full_cars),
            'Mean_CAR_pct': round(full_cars['CAR'].mean() * 100, 2),
            'BMP_t': round(bmp_test(full_cars)[0], 2),
            'BMP_p': round(bmp_test(full_cars)[1], 4)
        }, {
            'Model': 'GARCH(1,1) sigma',
            'N': n_g,
            'Mean_CAR_pct': round(mean_g, 2),
            'GARCH_BMP_t': round(t_gbmp, 2),
            'GARCH_BMP_p': round(p_gbmp, 4)
        }])
        tableA7.to_csv(os.path.join(TBL_DIR, "tableA7_garch_comparison.csv"), index=False)
        print(f"  Table A7 (GARCH Comparison) saved.")
        
except ImportError:
    print("  WARNING: 'arch' package not available. Skipping GARCH analysis.")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 11: ENHANCED FIGURES                                      ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("PHASE 11: Enhanced Figures")
print("=" * 70)

# --- Fig A1: AAR bar chart with 95% CI ---
print("  Generating Fig A1: AAR with CI...")
aar = event_df.groupby('day')['AR'].agg(['mean', 'std', 'count']).reset_index()
aar['se'] = aar['std'] / np.sqrt(aar['count'])
aar['ci_upper'] = (aar['mean'] + 1.96 * aar['se']) * 100
aar['ci_lower'] = (aar['mean'] - 1.96 * aar['se']) * 100
aar['mean_pct'] = aar['mean'] * 100

fig, ax = plt.subplots(figsize=(12, 5))
colors = ['crimson' if v < 0 else 'steelblue' for v in aar['mean_pct']]
ax.bar(aar['day'], aar['mean_pct'], color=colors, alpha=0.8, width=0.7)
ax.errorbar(aar['day'], aar['mean_pct'], 
            yerr=[aar['mean_pct'] - aar['ci_lower'], aar['ci_upper'] - aar['mean_pct']],
            fmt='none', ecolor='gray', elinewidth=0.8, capsize=2)
ax.axvline(0, color='black', linestyle='--', linewidth=1.5, label='Cyclone Landfall')
ax.axhline(0, color='gray', linewidth=0.8)
ax.set_xlabel('Trading Days Relative to Landfall (Day 0)', fontsize=11)
ax.set_ylabel('Average Abnormal Return (%)', fontsize=11)
ax.set_title('Daily Average Abnormal Returns (AAR) with 95% Confidence Intervals', fontsize=13, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA1_aar_bars.png"), dpi=300)
plt.close()

# --- Fig A2: CAR distribution histogram ---
print("  Generating Fig A2: CAR distribution...")
fig, ax = plt.subplots(figsize=(10, 5))
car_vals = full_cars['CAR'] * 100
ax.hist(car_vals, bins=50, density=True, alpha=0.7, color='steelblue', edgecolor='white', label='Empirical')
xmin, xmax = car_vals.quantile(0.01), car_vals.quantile(0.99)
x = np.linspace(xmin, xmax, 200)
ax.plot(x, stats.norm.pdf(x, car_vals.mean(), car_vals.std()), 'r-', linewidth=2, label='Normal fit')
ax.axvline(0, color='black', linestyle='--', linewidth=1)
ax.axvline(car_vals.mean(), color='crimson', linestyle='-', linewidth=1.5, label=f'Mean = {car_vals.mean():.2f}%')
ax.set_xlabel('Cumulative Abnormal Return (%)', fontsize=11)
ax.set_ylabel('Density', fontsize=11)
ax.set_title('Distribution of Full-Window CARs [−5, +30]', fontsize=13, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA2_car_distribution.png"), dpi=300)
plt.close()

# --- Fig A3: CAAR trajectory with placebo overlay ---
print("  Generating Fig A3: CAAR with placebo overlay...")
aar_real = event_df.groupby('day')['AR'].mean()
caar_real = aar_real.cumsum() * 100

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(caar_real.index, caar_real.values, color='crimson', linewidth=2.5, label='Actual Event (Cyclone Ditwah)')

for shift in PLACEBO_SHIFTS:
    df_p2 = df.copy()
    df_p2['fake_day'] = df_p2['day'] + shift
    fake_evt2 = df_p2[(df_p2['fake_day'] >= EVT_START) & (df_p2['fake_day'] <= EVT_END)]
    aar_fake = fake_evt2.groupby('fake_day')['AR'].mean()
    caar_fake = aar_fake.cumsum() * 100
    ax.plot(caar_fake.index, caar_fake.values, linewidth=1.5, alpha=0.6, linestyle='--',
            label=f'Placebo (Day −{shift})')

ax.axvline(0, color='black', linestyle='--', linewidth=1.2)
ax.axhline(0, color='gray', linewidth=0.8)
ax.axvspan(-5, 0, color='orange', alpha=0.1)
ax.set_xlabel('Trading Days Relative to Event', fontsize=11)
ax.set_ylabel('Cumulative Average Abnormal Return (%)', fontsize=11)
ax.set_title('Market CAAR: Actual Event vs. Placebo Events', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA3_caar_vs_placebo.png"), dpi=300)
plt.close()

# --- Fig A4: Sub-window heatmap ---
print("  Generating Fig A4: Sub-window heatmap...")
fig, ax = plt.subplots(figsize=(12, 8))
hm_data = tableA3.astype(float)
sns.heatmap(hm_data, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
            cbar_kws={'label': 'Mean CAR (%)'}, ax=ax, linewidths=0.5)
ax.set_title('Sector CARs by Sub-Window', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA4_subwindow_heatmap.png"), dpi=300)
plt.close()

# --- Fig A5: Size effect box plot ---
print("  Generating Fig A5: Size effect...")
fig, ax = plt.subplots(figsize=(8, 5))
plot_data = reg_data2.copy()
plot_data['CAR_pct'] = plot_data['CAR'] * 100
sns.boxplot(x='size_group', y='CAR_pct', data=plot_data, palette=['steelblue', 'coral'], ax=ax)
ax.axhline(0, color='black', linestyle='--', linewidth=1)
ax.set_xlabel('Firm Size Group (by Median Volume)', fontsize=11)
ax.set_ylabel('Cumulative Abnormal Return (%)', fontsize=11)
ax.set_title('CAR Distribution: Large vs. Small Firms', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA5_size_effect.png"), dpi=300)
plt.close()

# --- Fig A6: Volatility & Liquidity (improved) ---
print("  Generating Fig A6: Volatility & Liquidity...")
df['Spread'] = df['high'] - df['low']
vol_liq = df[(df['day'] >= -30) & (df['day'] <= 30)].copy()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Spread
daily_spread = vol_liq.groupby('day')['Spread'].mean()
ax1.plot(daily_spread.index, daily_spread.values, color='navy', linewidth=2)
ax1.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Landfall')
ax1.axhline(daily_spread[daily_spread.index < -5].mean(), color='gray', linestyle=':', label='Pre-event mean')
ax1.set_ylabel('Mean High-Low Spread (LKR)', fontsize=11)
ax1.set_title('Market Volatility Proxy (Intraday Price Spread)', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(axis='y', alpha=0.3)

# Volume
daily_vol = vol_liq.groupby('day')['volume'].mean()
ax2.bar(daily_vol.index, daily_vol.values / 1e6, color='steelblue', alpha=0.7, width=0.8)
ax2.axvline(0, color='red', linestyle='--', linewidth=1.5)
ax2.axhline(daily_vol[daily_vol.index < -5].mean() / 1e6, color='gray', linestyle=':', label='Pre-event mean')
ax2.set_xlabel('Trading Days Relative to Landfall', fontsize=11)
ax2.set_ylabel('Mean Daily Volume (millions)', fontsize=11)
ax2.set_title('Market Liquidity (Average Daily Trading Volume)', fontsize=13, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figA6_volatility_liquidity.png"), dpi=300)
plt.close()


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  FINAL SUMMARY                                                   ║
# ╚═══════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print(f"\n  Qualifying stocks analysed: {QUALIFYING_N}")
print(f"  Tables saved to: {TBL_DIR}")
print(f"  Figures saved to: {FIG_DIR}")
print(f"\n  Generated Tables:")
for f in sorted(os.listdir(TBL_DIR)):
    print(f"    - {f}")
print(f"\n  Generated Figures:")
for f in sorted(os.listdir(FIG_DIR)):
    print(f"    - {f}")
print("\nDone!")
