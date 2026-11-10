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


## Amendment — a second, separate protocol: search with a holdout
*Written and committed before this search was run on real data.*

The statement above ("no further candidate is tried on this sample") applied to hand-picked candidates judged on the whole sample. A wider search is legitimate only if the sample used to choose a signal is not the one used to judge it. Protocol:

* **Family.** Eleven indicators, as past-only expanding percentiles: sector dispersion, sector correlation, point-in-time stock dispersion and correlation, VIX, COR3M, VIX3M/VIX, COR3M minus trailing realized correlation, 21-day change in the Baa–Treasury spread, 21-day S&P 500 return, 21-day S&P 500 realized volatility. Each is taken "high" (≥ 80th percentile) or "low" (≤ 20th), alone or in pairs.
* **Discovery sample.** Start of COR3M to 2016-12-31, minus the last 63 trading days. Score: signal-day mean of the primary outcome minus the mean on days with the same COR3M level, divided by its standard error computed with the number of episodes. Minimum 100 signal days and 8 episodes.
* **Validation sample.** 2017-01-01 onwards. Only the top-ranked candidate is tested, once. It is retained if the one-sided time-shift test p-value is ≤ 0.05, the edge over days with the same COR3M level is positive, and the signal-day mean stays above the all-day mean when any one episode is left out.
* **Known weakness.** The validation years were already looked at for the sector signal, the stock signal and C1–C3 above, so the holdout is clean for the selection but not untouched. Its power is low (nine years).
* This is the last search on this sample. Its result is reported in the README, whatever it is.

## Result of the search with a holdout
242 candidates were scored on 2006–2016. The top-ranked one, "COR3M high AND VIX3M/VIX low", fired in only 2 episodes after 2016 (shift-test p = 0.51) and is **not retained**. All ten best candidates keep a positive edge after the split and "VIX3M/VIX low" appears in eight of them. That pattern was not the designated test, so it is a lead, not a result. The two protocols below are the only legitimate ways left to test it; both were written before any of their data was looked at.

## Protocol 3 — forward test on the US market
* **Rule.** ON when VIX3M / VIX is at or below the 20th percentile of its own past (expanding, minimum 504 days, Yahoo history from 2006, i.e. exactly the series used in the search).
* **Start.** 2026-11-11. Nothing before that date counts.
* **Log.** `forward_log.py` appends one row per trading day to `forward_log.csv` (VIX, VIX3M, ratio, percentile, ON/OFF, COR3M) and never rewrites a row. The scheduled workflow commits it, so each row carries a public timestamp.
* **Primary outcome.** P&L of buying 3M correlation at COR3M on the point-in-time basket, as in the notebook; compared with days at the same COR3M level over the same forward period.
* **Evaluation.** Once, when ten completed episodes have accumulated after the start date, or on 2029-12-31 at the latest. Retained if the one-sided time-shift test p-value is ≤ 0.05, the edge over the same COR3M level is positive, and it survives leaving any one episode out.

## Protocol 4 — out-of-sample test on the euro area
* **Rule.** ON when VSTOXX 90 days / VSTOXX 30 days is at or below the 20th percentile of its own past (expanding, minimum 504 days).
* **Primary outcome.** P&L of buying 3M implied correlation on the EURO STOXX 50: implied correlation computed with the COR formula from 3M at-the-money implied volatilities of the index and of its constituents (weights and membership of each date), against the realized correlation of the basket frozen at entry over the next 63 trading days. Benchmark: days in the same quintile of implied correlation.
* **Fallback, fixed now.** If constituent implied volatilities cannot be obtained, the primary outcome becomes the P&L of buying 1M variance at the VSTOXX 30 days, against days in the same VSTOXX quintile. The fallback is weaker (it is not a correlation trade) and will be labelled as such.
* **Sample.** All available history, taken whole; no split, no threshold change.
* **Decision.** Same three criteria as protocol 3. One test, reported whatever it gives.
