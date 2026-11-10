# Pre-registration — additional signals for Trade Idea #01

*Written and committed before any of the three signals below was computed. Results are appended at the bottom afterwards, whatever they are.*

## Why this file exists
Searching for signals until one works guarantees a false discovery. This test is therefore limited to three candidates, each with a mechanism, a threshold and an expected sign fixed in advance, one primary outcome, and one decision rule corrected for the three tests.

## Primary outcome
P&L of buying 3M correlation at COR3M on the point-in-time basket (top 50 US companies of each day, frozen at entry, index-based realized correlation): `corr_pnl_pit`. Sample: COR3M history ∩ CRSP file (2006–2025).

Secondary outcomes, reported but not used for the decision: P&L of buying 1M variance at the VIX; frequency of a ≥10% S&P 500 fall within 63 days.

## Candidates
Percentiles are expanding (past only, minimum 504 days), as everywhere in the notebook.

| # | Signal ON when | Mechanism | Expected sign |
|---|---|---|---|
| C1 | COR3M minus trailing 3M realized correlation (point-in-time) is at or below its 20th percentile | The correlation risk premium is the price of the insurance; when implied is low relative to realized, the insurance is cheap | Higher correlation P&L than base |
| C2 | 21-day change in the Moody's Baa minus 10-year Treasury spread (FRED `BAA10Y`) at or above its 80th percentile **and** VIX at or below its median | Credit stress that equity volatility has not priced yet | Higher correlation P&L than base |
| C3 | VIX3M / VIX at or above its 80th percentile | Steep volatility term structure: spot volatility is low relative to what is expected later, so short-dated insurance is cheap | Higher correlation P&L than base |

## Decision rule
A candidate is retained only if all three hold:
1. one-sided time-shift test p-value on the primary outcome ≤ 0.05 / 3 = 0.0167 (Bonferroni);
2. signal-day mean above the mean on days with the same COR3M level (quintile of the past-only percentile);
3. leaving out any one episode, the signal-day mean stays above the all-day mean.

No threshold, window or definition will be changed after seeing the results. If none passes, the conclusion is that none of the three adds anything, and no further candidate is tried on this sample.

## Results
Run on 2026-11-10, data as of 2026-11-09, after the pre-registration commit. Correlation P&L in correlation points per trade, variance P&L in vol points.

| # | Days ON | Episodes | Correlation P&L: signal / all days / same COR3M level | Shift-test p (bar: 0.0167) | Signal minus all days, 95% interval | Worst leave-one-episode-out mean | Variance P&L: signal / all days (p) | ≥10% fall: signal / all days |
|---|---|---|---|---|---|---|---|---|
| C1 implied minus realized low | 747 | 19 | -6.2 / -4.8 / -5.4 | 0.69 | -5.3 to +2.5 | -8.1 | -3.54 / -1.71 (0.87) | 19% / 16% |
| C2 credit widening, VIX low | 195 | 27 | -3.4 / -4.2 / -4.7 | 0.41 | -4.0 to +5.2 | -4.7 | -1.91 / -2.56 (0.22) | 12% / 14% |
| C3 steep VIX term structure | 1475 | 33 | -6.0 / -4.8 / -4.3 | 0.82 | -3.8 to +1.4 | -6.9 | -2.61 / -1.80 (0.81) | 9% / 14% |

**None of the three candidates is retained.** None meets the first criterion; C1 and C3 are worse than a random day, against the expected sign. As stated above, no further candidate is tried on this sample.

For reference, the original sector-dispersion signal on the same outcome: +2.4 / -4.2 / -2.2, shift-test p 0.03 (0.15 after a correction for five outcomes), worst leave-one-episode-out mean -0.7.

