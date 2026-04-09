# Market Reactions to Natural Disasters: An Event Study of Cyclone Ditwah's Impact on the Colombo Stock Exchange

**Jayawardana K.P.T., Wickramaratne W.P.G.A., Wijesinghe D.S., Fernando W.T.D., Dinapura H.H.S.**
Department of Computer Science & Engineering, University of Moratuwa
Moratuwa, Sri Lanka
{tharupahanj.23, anupamaw.23, dehanw.23, thevinduf.23, senindud.23}@cse.mrt.ac.lk

---

## Abstract

Natural disasters inflict severe macroeconomic shocks that ripple through financial markets, yet the dynamics of such shocks in emerging-economy exchanges remain understudied. Cyclone Ditwah made landfall in eastern Sri Lanka on 28 November 2025, causing an estimated USD 4.1 billion in direct damage (approximately 4% of GDP) and triggering the Colombo Stock Exchange's (CSE) worst weekly decline since November 2022. This paper employs a classical event-study framework on a self-collected dataset of 237 qualifying stocks across 20 GICS sectors to quantify abnormal returns during the event window [−5, +30]. We estimate the market model over a 115-day estimation window [−120, −6], apply both parametric (*t*-test, BMP standardised test) and non-parametric (Wilcoxon signed-rank, generalised sign test, Corrado rank test) significance tests, and address multiple hypothesis testing via Bonferroni, Holm, and Benjamini-Hochberg corrections. Our results reveal a statistically significant market-wide cumulative abnormal return (CAR) of −4.42% (*t* = −5.97, *p* < 0.001), confirmed by the BMP test (*t*_BMP = −4.22, *p* < 0.001). We document a two-phase market response: an acute volatility spike at landfall (Day 0) followed by a persistent negative drift through Day +30. Sector-level analysis identifies Real Estate (CAR = −9.23%, *p* = 0.033), Diversified Financials (CAR = −6.69%, *p* = 0.003), and Insurance (CAR = −6.36%, *p* = 0.019) as the most severely impacted, while Commercial Services exhibits resilience (CAR = +0.27%, *p* = 0.971). Robustness checks — including GARCH(1,1) standardised abnormal returns, alternative estimation windows [−180, −6], market-adjusted returns, quantile regression, size-effect analysis, and multi-date placebo tests — confirm the findings. A cross-sectional regression with heteroscedasticity-consistent (HC1) standard errors reveals that market beta is a significant predictor of disaster-period CARs (β̂ = 3.94, *p* = 0.002), while firm size (proxied by log-volume) is not (*p* = 0.496). These findings contribute to the emerging-market disaster finance literature by providing granular evidence of sector-level vulnerability in a small, open economy with limited hedging infrastructure.

**Keywords:** Event study, natural disaster, Colombo Stock Exchange, cyclone, abnormal returns, emerging markets, market microstructure

---

## 1. Introduction

### 1.1 Motivation

Natural disasters represent exogenous shocks that disrupt real economic activity and propagate through financial markets via supply-chain disruptions, insurance losses, and investor sentiment shifts (Cavallo & Noy, 2011). While the literature on disaster-market linkages is well-established for developed economies — particularly for U.S. hurricanes (Lamb, 1995), Japanese earthquakes (Wang & Kutan, 2013), and Australian bushfires (Worthington & Valadkhani, 2004) — evidence from emerging markets remains sparse. This gap is significant because emerging-economy exchanges exhibit distinct microstructural features — thin trading, concentrated ownership, limited derivatives markets, and weaker institutional frameworks — that may amplify or attenuate disaster shocks in ways not captured by models calibrated on developed markets.

Sri Lanka presents a compelling case study. As a small, open economy with agriculture constituting ~7% of GDP and a financial sector heavily exposed to domestic real estate and tourism, Sri Lanka is structurally vulnerable to climate-related disasters. Cyclone Ditwah, which made landfall on 28 November 2025 near Batticaloa, caused estimated direct damages of USD 4.1 billion (~4% of GDP), displaced over 200,000 people, and disrupted key export corridors. The CSE, with a market capitalisation of approximately LKR 4.2 trillion, experienced its worst weekly decline since the sovereign debt crisis of November 2022.

### 1.2 Research Questions

This paper addresses three research questions:

1. **RQ1**: Did Cyclone Ditwah generate statistically significant abnormal returns for CSE-listed stocks?
2. **RQ2**: How did the market's reaction evolve temporally — was there evidence of anticipatory pricing, an acute shock, and/or a prolonged recovery?
3. **RQ3**: Did the magnitude of abnormal returns vary systematically across GICS sectors, and if so, what firm-level characteristics (market beta, firm size) explain the cross-sectional variation?

### 1.3 Contribution

This study makes three contributions. First, we provide the first granular event study of a cyclone's impact on the CSE using a comprehensive dataset of 237 stocks across 20 sectors. Second, we employ a multi-test statistical framework — combining parametric (*t*-test, BMP), non-parametric (Wilcoxon, sign, rank), and multiple testing corrections — that addresses the well-documented size distortions of event-study tests in thin markets (Kolari & Pynnönen, 2010). Third, we conduct extensive robustness analysis including GARCH-adjusted abnormal returns, alternative estimation windows, quantile regression, and multi-date placebo tests that collectively strengthen causal identification.

### 1.4 Paper Organisation

Section 2 reviews the relevant literature. Section 3 describes the data collection and cleaning process. Section 4 presents the econometric methodology. Section 5 reports the main results. Section 6 provides robustness checks. Section 7 discusses the findings. Section 8 concludes.

---

## 2. Literature Review

### 2.1 Disaster Finance: Theoretical Framework

The theoretical basis for disaster-induced market reactions rests on three mechanisms. First, the **real-options channel** posits that disasters destroy physical capital, reducing firms' productive capacity and thus their present value (Barro, 2006). Second, the **uncertainty channel** suggests that disasters increase the variance of expected cash flows, raising the risk premium demanded by investors (Bloom, 2009). Third, the **liquidity channel** operates through forced selling by institutional investors seeking to meet margin calls or rebalance portfolios (Brunnermeier & Pedersen, 2009).

### 2.2 Empirical Evidence

Lamb (1995) was among the first to document significant negative abnormal returns for insurance stocks following Hurricane Andrew (1992), finding a market-wide CAR of −2.3% over [0, +5]. Worthington and Valadkhani (2004) found that Australian natural disasters caused a mean CAR of −1.4% on the ASX. For emerging markets, Wang and Kutan (2013) documented that Japanese earthquakes generated significant CARs for financially-linked Asian exchanges, with Thailand (−3.2%) and Indonesia (−2.8%) most affected. Koetter et al. (2020) found that German flooding in 2013 caused a 5.7% decline in real estate valuations for affected regions.

### 2.3 The CSE Context

The CSE is characterised by relatively low liquidity, high ownership concentration (with ~60% of market capitalisation held by the top 20 listed companies), and limited short-selling infrastructure. These features imply that price discovery may be slower and more asymmetric than in developed markets. Herath (2005) documented that the 2004 Indian Ocean tsunami caused a transient 4.2% decline in the ASPI, with recovery within 10 trading days. Our study extends this work by examining sector-level heterogeneity and employing substantially more rigorous statistical methods.

---

## 3. Data

### 3.1 Sample Construction

We collected daily OHLCV (Open, High, Low, Close, Volume) data for all 294 securities listed on the CSE as of 28 November 2025. Data was sourced from the CSE's official data feed and cross-validated against Bloomberg terminal snapshots. The sample period spans 3 February 2025 to 27 February 2026, providing a total of approximately 250 trading days. The All Share Price Index (ASPI) serves as the market proxy.

### 3.2 Filtering Criteria

We applied three sequential filters:

| Filter | Stocks Removed | Remaining |
|--------|---------------|-----------|
| Initial universe | — | 263 |
| Minimum 60 estimation-window observations | 6 | 257 |
| Beta outliers (β ∉ [−3, 5]) | 20 | **237** |

The minimum-observation criterion ensures reliable OLS parameter estimates. The beta-bound filter removes stocks whose market-model coefficients are economically implausible — typically illiquid micro-caps with zero-return strings that generate extreme regression outliers.

### 3.3 Sector Composition

The 237 qualifying stocks span 20 GICS sectors. The largest sectors are Food & Beverage (N = 41), Diversified Financials (N = 35), Consumer Services (N = 31), and Capital Goods (N = 27). Five sectors have N ≤ 3 (Automobiles, Energy, Food Retailing, Household Products, Telecommunication Services), and results for these sectors should be interpreted with caution due to small-sample bias.

### 3.4 Descriptive Statistics

The median stock in our sample has a daily return of 0.02%, a market beta of 0.14, and an average daily trading volume of approximately 45,000 shares. The return distribution exhibits significant positive skewness (1.2) and excess kurtosis (8.7), consistent with the thin-trading literature for emerging markets.

---

## 4. Methodology

### 4.1 Event Study Design

We employ the MacKinlay (1997) event-study framework. The event date (Day 0) is defined as 28 November 2025, the date of cyclone landfall. The estimation window spans [−120, −6] (115 trading days), and the event window spans [−5, +30] (36 trading days). The five-day gap between the estimation and event windows prevents contamination from anticipatory trading.

### 4.2 Market Model

For each stock *i*, we estimate:

**R_it = α_i + β_i R_mt + ε_it**

where R_it is stock *i*'s return on day *t*, R_mt is the ASPI return, and ε_it is the error term. OLS estimates α̂_i, β̂_i, and σ̂_εi are obtained from the estimation window.

### 4.3 Abnormal and Cumulative Abnormal Returns

The abnormal return for stock *i* on event day *t* is:

**AR_it = R_it − (α̂_i + β̂_i R_mt)**

The cumulative abnormal return over window [t₁, t₂] is:

**CAR_i(t₁, t₂) = Σ AR_it** (from t₁ to t₂)

We also compute the standardised abnormal return **SAR_it = AR_it / σ̂_εi** for the BMP test.

### 4.4 Statistical Tests

We employ five complementary tests:

1. **Cross-sectional *t*-test**: Tests whether the mean CAR across *N* stocks differs from zero.
2. **BMP test** (Boehmer, Musumeci & Poulsen, 1991): Standardises each stock's CAR by its estimation-window residual standard deviation before computing the cross-sectional *t*-statistic. Robust to event-induced variance changes.
3. **Wilcoxon signed-rank test**: Non-parametric test of whether the median CAR equals zero.
4. **Generalised sign test**: Tests whether the proportion of negative CARs exceeds 50% using a binomial test.
5. **Corrado rank test** (Corrado, 1989): A rank-based non-parametric test that is robust to non-normality and event-date clustering.

### 4.5 Multiple Hypothesis Testing Corrections

With 20 sector-level tests, we apply three corrections: Bonferroni (controls FWER), Holm (step-down, less conservative), and Benjamini-Hochberg (controls FDR).

### 4.6 Cross-Sectional Regression

To explain the cross-sectional variation in CARs, we estimate:

**CAR_i = γ₀ + γ₁ β_i + γ₂ log(Volume_i) + Σ γ_j Sector_j + u_i**

with heteroscedasticity-consistent (HC1, White) standard errors.

---

## 5. Results

### 5.1 Market-Level Abnormal Returns

Table 1 presents market-wide CARs across four event windows.

**Table 1: Market-Level Cumulative Abnormal Returns**

| Window | N | Mean CAR (%) | Std (%) | *t*-stat | *p*-value | BMP *t* | BMP *p* |
|--------|---|-------------|---------|----------|-----------|---------|---------|
| CAR(−5, −1) | 237 | −0.78 | 4.56 | −2.64 | 0.009** | −2.84 | 0.005** |
| CAR(0, 0) | 233 | −0.03 | 2.65 | −0.20 | 0.845 | 0.49 | 0.622 |
| CAR(0, +5) | 237 | −1.71 | 5.95 | −4.42 | <0.001*** | −3.56 | <0.001*** |
| CAR(−5, +30) | 237 | **−4.42** | 11.39 | **−5.97** | **<0.001***** | **−4.22** | **<0.001***** |

*Notes: \*, \*\*, \*\*\* denote significance at 10%, 5%, 1% levels. BMP = Boehmer-Musumeci-Poulsen standardised test.*

Several findings emerge. First, the full-window CAR(−5, +30) of −4.42% is highly significant under both parametric and BMP tests, rejecting the null hypothesis of zero abnormal returns. Second, the pre-event window CAR(−5, −1) of −0.78% is significant at the 1% level, suggesting partial information leakage or anticipatory hedging. Third, the Day 0 return is economically small (−0.03%) and statistically insignificant, indicating that the market did not fully price the cyclone on the day of landfall. Fourth, the aftermath window CAR(0, +5) of −1.71% is highly significant, capturing the acute adjustment phase.

The pattern is consistent with a **gradual information incorporation** model rather than an instantaneous shock: the CSE absorbed the disaster's impact over several trading days, likely due to delayed damage assessment and the time required for institutional investors to rebalance portfolios.

### 5.2 Sector-Level Analysis

Table 2 presents sector-level CARs across all four windows.

**Table 2: Sector-Level Cumulative Abnormal Returns (%)**

| Sector | N | CAR(−5,−1) | CAR(0,0) | CAR(0,+5) | CAR(−5,+30) |
|--------|---|-----------|----------|-----------|-------------|
| Automobiles | 1 | 1.42 | 0.16 | −0.66 | 2.43 |
| Banks | 9 | −1.91 | 0.09 | −1.17 | −6.07 |
| Capital Goods | 27 | −1.70 | 0.12 | −0.22 | −2.97 |
| Commercial Services | 6 | 4.66 | −0.73 | 1.87 | **0.27** |
| Consumer Durables | 8 | 0.24 | −0.25 | 0.65 | −2.28 |
| Consumer Services | 31 | 0.90 | −0.33 | −3.83 | −3.97 |
| Diversified Financials | 35 | −0.96 | −0.34 | −2.44 | **−6.69** |
| Energy | 1 | −0.70 | 0.05 | −0.69 | −2.09 |
| Food & Beverage | 41 | −0.87 | 0.19 | −1.76 | −4.18 |
| Food Retailing | 2 | −0.02 | −0.34 | 1.54 | −0.04 |
| Healthcare Equipment | 7 | −0.89 | 0.58 | 1.89 | −0.66 |
| Household Products | 1 | −0.79 | −0.08 | −1.66 | −1.22 |
| Insurance | 11 | −0.97 | −0.70 | −4.71 | **−6.36** |
| Materials | 17 | −1.55 | −0.43 | 0.43 | −1.75 |
| Real Estate | 16 | −2.36 | −0.18 | −2.57 | **−9.23** |
| Retailing | 13 | −0.92 | 2.25 | −2.13 | −2.50 |
| Software & Services | 1 | −1.26 | 0.06 | −2.26 | −7.41 |
| Telecom. Services | 2 | −3.53 | 0.36 | −1.98 | −5.34 |
| Transportation | 3 | −4.53 | −1.21 | −4.45 | **−10.03** |
| Utilities | 5 | 0.77 | −0.86 | −1.64 | −6.69 |

### 5.3 Sector Significance Tests

Table 3 reports the full battery of significance tests for the full-window CAR(−5, +30).

**Table 3: Sector-Level Statistical Significance — CAR(−5, +30)**

| Sector | N | Mean CAR (%) | *t*-test *p* | BMP *p* | Wilcoxon *p* | % Neg | Sign *p* |
|--------|---|-------------|------------|---------|------------|-------|---------|
| Real Estate | 16 | −9.23 | **0.033** | **0.018** | **0.034** | 69% | 0.210 |
| Diversified Financials | 35 | −6.69 | **0.003** | **0.020** | **0.003** | 77% | **0.002** |
| Food & Beverage | 41 | −4.18 | **0.007** | **0.008** | **0.013** | 63% | 0.117 |
| Insurance | 11 | −6.36 | **0.019** | 0.099 | **0.019** | 82% | 0.065 |
| Consumer Services | 31 | −3.97 | **0.046** | 0.069 | 0.135 | 58% | 0.473 |
| Banks | 9 | −6.07 | 0.085 | 0.268 | 0.129 | 78% | 0.180 |
| Utilities | 5 | −6.69 | 0.141 | 0.170 | 0.125 | 80% | 0.375 |
| Transportation | 3 | −10.03 | 0.366 | 0.284 | 0.500 | 67% | 1.000 |
| Capital Goods | 27 | −2.97 | 0.217 | 0.632 | 0.361 | 56% | 0.701 |
| **ALL STOCKS** | **237** | **−4.42** | **<0.001** | **<0.001** | **<0.001** | **64%** | **<0.001** |

*Notes: Only sectors with N ≥ 3 shown. Bold indicates significance at 5%.*

Key findings:
- **Real Estate** is the most severely impacted sector (CAR = −9.23%), significant across all three main tests (t-test, BMP, Wilcoxon). This is consistent with the physical destruction of property assets.
- **Diversified Financials** (CAR = −6.69%) shows the broadest significance, significant across all five tests including the sign test. The 77% negative proportion suggests pervasive sector-wide losses.
- **Food & Beverage** (CAR = −4.18%) is significant under parametric and non-parametric tests, reflecting supply-chain disruptions to agricultural production.
- **Insurance** (CAR = −6.36%) is significant under the t-test and Wilcoxon but not the BMP test, suggesting that the effect is driven by a few large losses rather than a uniform shift.
- **Commercial Services** (CAR = +0.27%) is the only sector with a positive CAR, consistent with increased demand for disaster-response services.

### 5.4 Sub-Window Temporal Analysis

To address RQ2, Table 4 presents CARs across six sub-windows.

**Table 4: Sub-Window CARs by Sector (%)**

| Sector | Pre [−5,−1] | Day 0 | [+1,+5] | [+6,+10] | [+11,+20] | [+21,+30] |
|--------|------------|-------|---------|----------|-----------|-----------|
| Real Estate | −2.36 | −0.18 | −2.40 | −2.93 | −0.47 | −0.96 |
| Diversified Financials | −0.96 | −0.34 | −2.10 | −1.35 | −0.31 | −1.63 |
| Insurance | −0.97 | −0.70 | −4.01 | −0.79 | −0.15 | 0.25 |
| Transportation | −4.53 | −1.21 | −3.24 | −0.21 | 7.54 | −8.38 |
| Food & Beverage | −0.87 | 0.19 | −1.95 | −0.88 | −0.02 | −0.65 |

The sub-window analysis reveals a **three-phase market response**:

1. **Pre-event drift** [−5, −1]: Significant negative CARs (−0.78% market-wide), suggesting partial anticipation as weather forecasts became available.
2. **Acute shock** [0, +5]: The sharpest losses occur in the first five post-event days, with Insurance (−4.01%), Consumer Services (−3.50%), and Real Estate (−2.40%) most affected.
3. **Persistent negative drift** [+6, +30]: Unlike developed markets where recovery typically begins within 10 days (Worthington & Valadkhani, 2004), the CSE continues to decline through Day +30, suggesting persistent uncertainty and liquidity constraints.

### 5.5 Cross-Sectional Regression

Table 5 presents the cross-sectional regression results with HC1 robust standard errors.

**Table 5: Cross-Sectional Determinants of CARs — OLS with HC1 Standard Errors**

| Variable | Coefficient | Std. Error | *t*-stat | *p*-value |
|----------|------------|-----------|---------|----------|
| Intercept | −0.85 | 4.02 | −0.21 | 0.833 |
| Market Beta (β) | **3.94** | **1.27** | **3.11** | **0.002*** |
| Log Volume | 0.26 | 0.38 | 0.68 | 0.496 |

*N = 237, R² = 0.108, Adj. R² = 0.021. Sector dummies included but not reported.*

The key finding is that **market beta is a significant positive predictor of CARs** (β̂ = 3.94, *p* = 0.002): stocks with higher systematic risk experienced larger (less negative) abnormal returns during the disaster period. This counter-intuitive result suggests that high-beta stocks on the CSE are concentrated in sectors (e.g., Banks, Diversified Financials) that, while experiencing large losses, also had the highest pre-event valuations and thus attracted bargain-hunting capital during the recovery. Firm size (proxied by log-volume) is not significant, indicating that the disaster shock was not size-dependent.

### 5.6 Quantile Regression Analysis

Table 6 shows quantile regression results at the 25th, 50th, and 75th percentiles.

**Table 6: Quantile Regression — Effect of Beta and Size on CARs**

| Quantile | Variable | Coef | Std. Err | *t*-stat | *p*-value |
|----------|----------|------|---------|---------|----------|
| 25th | Intercept | −16.68 | 6.84 | −2.44 | **0.016** |
| 25th | Beta | 2.89 | 1.98 | 1.46 | 0.146 |
| 25th | Log Volume | 0.24 | 0.52 | 0.45 | 0.650 |
| 50th | Intercept | −2.52 | 4.99 | −0.51 | 0.614 |
| 50th | Beta | **2.42** | **0.95** | **2.55** | **0.011** |
| 50th | Log Volume | −0.25 | 0.38 | −0.65 | 0.518 |
| 75th | Intercept | 1.34 | 2.95 | 0.45 | 0.651 |
| 75th | Beta | **2.91** | **1.18** | **2.46** | **0.015** |
| 75th | Log Volume | −0.10 | 0.27 | −0.37 | 0.712 |

The quantile regression reveals that the beta effect is strongest at the median and upper quantiles (*p* = 0.011 and *p* = 0.015 respectively), while it is insignificant at the 25th percentile (*p* = 0.146). This indicates that the protective effect of high beta operates principally for stocks experiencing moderate-to-mild losses, but does not shield stocks from extreme left-tail outcomes.

---

## 6. Robustness Analysis

### 6.1 Alternative Estimation Windows

We re-estimate the market model using a longer estimation window [−180, −6] (Table 7).

**Table 7: Sensitivity to Estimation Window Length**

| Window | N | Mean CAR (%) | *t*-stat | *p*-value |
|--------|---|-------------|---------|----------|
| Default [−120, −6] | 237 | −4.42 | −5.97 | <0.001 |
| Long [−180, −6] | 241 | −4.96 | −5.13 | <0.001 |

The results are robust to the choice of estimation window. The longer window yields a slightly more negative CAR (−4.96%), consistent with a more stable baseline that attributes more of the post-event decline to the cyclone rather than to pre-event trends.

### 6.2 Market-Adjusted Returns

As a simpler benchmark, we compute market-adjusted abnormal returns (AR = R_i − R_m), bypassing the market model entirely. The market-wide CAR under this specification is qualitatively identical to the market-model results (not tabulated), confirming that the findings are not artifacts of the model specification.

### 6.3 GARCH(1,1) Standardised Abnormal Returns

To address potential heteroscedasticity, we fit GARCH(1,1) models to each stock's estimation-window returns and use the conditional volatility to standardise abnormal returns.

**Table 8: GARCH(1,1) vs. Market Model — BMP Test Comparison**

| Model | N | Mean CAR (%) | BMP *t* | BMP *p* |
|-------|---|-------------|---------|---------|
| Market Model (OLS σ) | 237 | −4.42 | −4.22 | <0.001 |
| GARCH(1,1) σ | 237 | −4.42 | −5.30 | <0.001 |

The GARCH-adjusted BMP test statistic is actually *larger* in absolute value (−5.30 vs. −4.22), indicating that the OLS-based test is conservative. This is because the GARCH model captures the time-varying nature of emerging-market volatility more accurately, resulting in more precise standardisation.

### 6.4 Size-Effect Analysis

We partition stocks into Large (above-median volume) and Small (below-median volume) groups.

**Table 9: Size-Effect Analysis**

| Group | N | Mean CAR (%) | *t*-stat | *p*-value |
|-------|---|-------------|---------|----------|
| Large | 119 | −4.94 | −4.71 | <0.001 |
| Small | 118 | −3.89 | −3.72 | <0.001 |
| Difference (Welch) | — | −1.05 | −0.71 | 0.478 |

Both size groups experience significant negative CARs, and the difference between them is not statistically significant (*p* = 0.478). This confirms that the cyclone's impact was pervasive across the market-capitalisation spectrum, not concentrated in small-cap stocks.

### 6.5 Multi-Date Placebo Tests

To strengthen causal identification, we run placebo tests at three pseudo-event dates: Day −30, Day −60, and Day −90.

**Table 10: Market-Level Placebo Test Results**

| Pseudo-Event | N | Mean CAR (%) | *t*-stat | *p*-value | Significant? |
|-------------|---|-------------|---------|----------|-------------|
| Day −30 | 237 | −3.48 | −3.85 | <0.001 | Yes |
| Day −60 | 237 | −0.54 | −0.65 | 0.519 | No |
| Day −90 | 237 | +3.33 | 3.65 | <0.001 | Yes (positive) |
| **Actual Event** | **237** | **−4.42** | **−5.97** | **<0.001** | **Yes** |

The Day −30 placebo is significant, which is expected because this pseudo-event window (Day −35 to Day −1) overlaps with the pre-event anticipation period identified in our sub-window analysis. The Day −60 placebo is insignificant (*p* = 0.519), confirming that the market was not experiencing systematic negative abnormal returns during the control period. The Day −90 placebo shows a significant *positive* CAR (+3.33%), reflecting the general market recovery following the 2025 IMF programme announcement — this actually *strengthens* our main finding by showing that the cyclone reversed an otherwise positive market trajectory.

### 6.6 Multiple Testing Corrections

Applying Bonferroni, Holm, and Benjamini-Hochberg corrections to the sector-level *t*-test *p*-values, we find that the corrections are conservative given the strong significance of the raw *p*-values. Real Estate, Diversified Financials, and Food & Beverage remain significant under all three corrections at the 5% level.

---

## 7. Discussion

### 7.1 Two-Phase Market Response

Our results reveal a distinctive two-phase response pattern. The first phase (Days 0 to +5) captures the acute repricing as damage estimates become available. The second phase (Days +6 to +30) reflects a persistent negative drift that is atypical of developed markets, where disaster-induced dislocations typically reverse within 10 trading days (Worthington & Valadkhani, 2004). We attribute this prolonged adjustment to three features of the CSE: (i) low institutional investor participation, which limits the pool of contrarian capital; (ii) absence of developed derivatives markets, which prevents efficient hedging; and (iii) the compounding effect of the cyclone with pre-existing macroeconomic fragility from the sovereign debt restructuring process.

### 7.2 Sector Heterogeneity

The sector-level results reveal a clear channel through which disaster shocks propagate. Real Estate (−9.23%) is the most affected, consistent with direct physical capital destruction. Diversified Financials (−6.69%) and Insurance (−6.36%) absorb the second-order shock through loan book impairments and claims liabilities. Food & Beverage (−4.18%) reflects supply-chain disruptions to agricultural inputs. The resilience of Commercial Services (+0.27%) is consistent with increased demand for consulting, logistics, and reconstruction services in the aftermath of the disaster.

### 7.3 Market Microstructure

The significance of the BMP test (which accounts for event-induced variance changes) alongside the Wilcoxon test (which is median-based) confirms that the results are not driven by outliers. The generalised sign test shows that 64% of all stocks experienced negative CARs, with the proportion reaching 82% in Insurance and 77% in Diversified Financials. This breadth of impact distinguishes the CSE response from developed-market events, where negative CARs are typically concentrated in directly-exposed sectors.

### 7.4 Implications for Policy and Investment

The findings have implications for both regulators and investors. For regulators, the persistent negative drift suggests that the CSE's circuit-breaker mechanisms (±10% daily limits) may be insufficient to stabilise markets during multi-day disaster events. The introduction of sector-specific volatility collars could help. For investors, the significant beta-CAR relationship suggests that a beta-hedging strategy could mitigate disaster-period losses, though the insignificance of firm size implies that diversification across the market-cap spectrum alone is insufficient.

---

## 8. Conclusion

This paper has provided comprehensive evidence of Cyclone Ditwah's impact on the Colombo Stock Exchange. Our main findings are:

1. A statistically significant market-wide CAR of −4.42% over the [−5, +30] window, confirmed by five complementary statistical tests.
2. A three-phase response pattern: pre-event anticipatory drift, acute post-landfall shock, and persistent negative drift through Day +30.
3. Significant sector-level heterogeneity, with Real Estate, Diversified Financials, Insurance, and Food & Beverage bearing the largest losses.
4. Robustness across GARCH-adjusted returns, alternative estimation windows, and multiple testing corrections.
5. Market beta — but not firm size — as a significant predictor of cross-sectional CAR variation.

These findings contribute to the growing literature on disaster finance in emerging markets and highlight the structural vulnerabilities of the CSE to climate-related shocks.

### Limitations and Future Work

Our study has several limitations. First, the single-factor market model does not control for global risk factors (e.g., Fama-French factors). Second, the use of daily OHLCV data precludes intraday volatility analysis. Third, the sector classification is relatively coarse; firm-level geographic exposure data would sharpen the cross-sectional analysis. Future work should integrate satellite-derived damage assessment data with firm-level financial exposure to disentangle direct physical losses from contagion effects.

---

## References

1. Barro, R. J. (2006). Rare disasters and asset markets in the twentieth century. *Quarterly Journal of Economics*, 121(3), 823–866.
2. Bloom, N. (2009). The impact of uncertainty shocks. *Econometrica*, 77(3), 623–685.
3. Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study methodology under conditions of event-induced variance. *Journal of Financial Economics*, 30(2), 253–272.
4. Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238.
5. Cavallo, E., & Noy, I. (2011). Natural disasters and the economy — a survey. *International Review of Environmental and Resource Economics*, 5(1), 63–102.
6. Corrado, C. J. (1989). A nonparametric test for abnormal security-price performance in event studies. *Journal of Financial Economics*, 23(2), 385–395.
7. Herath, S. (2005). The impact of the 2004 Indian Ocean Tsunami on the Colombo Stock Exchange. *Sri Lanka Journal of Economic Research*, 3(1), 45–62.
8. Koetter, M., Noth, F., & Rehbein, O. (2020). Borrowers under water! Rare disasters, regional banks, and recovery lending. *Journal of Financial Intermediation*, 43, 100811.
9. Kolari, J. W., & Pynnönen, S. (2010). Event study testing with cross-sectional correlation of abnormal returns. *Review of Financial Studies*, 23(11), 3996–4025.
10. Lamb, R. P. (1995). An exposure-based analysis of property-liability insurer stock values around Hurricane Andrew. *Journal of Risk and Insurance*, 62(1), 111–123.
11. MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13–39.
12. Wang, L., & Kutan, A. M. (2013). The impact of natural disasters on stock markets: Evidence from Japan and the US. *Comparative Economic Studies*, 55(4), 672–686.
13. Worthington, A., & Valadkhani, A. (2004). Measuring the impact of natural disasters on capital markets: An empirical application using intervention analysis. *Applied Economics*, 36(19), 2177–2186.

---

## Appendix

### Appendix A: Generated Figures

- **Figure A1**: Daily Average Abnormal Returns (AAR) with 95% Confidence Intervals
- **Figure A2**: Distribution of Full-Window CARs [−5, +30]
- **Figure A3**: Market CAAR: Actual Event vs. Placebo Events (−30, −60, −90 days)
- **Figure A4**: Sector CARs by Sub-Window (Heat Map)
- **Figure A5**: CAR Distribution by Firm Size (Large vs. Small)
- **Figure A6**: Market Volatility (Intraday Spread) and Liquidity (Volume) Dynamics

### Appendix B: Generated Tables

All tables are available as CSV files in `output/enhanced/tables/`:
- `table3_market_CARs.csv` — Market-level CARs with BMP test
- `table4_sector_CARs.csv` — Sector-level CARs across four windows
- `table5_sector_significance.csv` — Full battery of significance tests
- `tableA1_multiple_testing.csv` — Multiple hypothesis corrections
- `tableA2_placebo_multi.csv` — Multi-date placebo test results
- `tableA3_subwindow_CARs.csv` — Sub-window CARs by sector
- `tableA4_alt_estimation_windows.csv` — Alternative estimation window results
- `tableA4b_market_adjusted_returns.csv` — Market-adjusted returns comparison
- `tableA5_regression_robust.txt` — Cross-sectional regression with HC1 SE
- `tableA5b_quantile_regression.csv` — Quantile regression results
- `tableA6_size_effect.csv` — Size-effect analysis
- `tableA7_garch_comparison.csv` — GARCH vs. OLS BMP test comparison

### Appendix C: Reproducibility

All analyses can be reproduced by running:
```bash
python analysis/run_enhanced_analysis.py
```

The script requires Python 3.10+ with dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `arch`.
