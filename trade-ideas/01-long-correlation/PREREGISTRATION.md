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
*(to be appended)*
