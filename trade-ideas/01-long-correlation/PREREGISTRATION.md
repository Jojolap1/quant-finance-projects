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

### Protocol 4 — amendment before running (public data only)
*Written after checking which public files exist and what dates they cover, and before computing any outcome.*

No Bloomberg access, and no public history of single-stock implied volatilities in Europe: the **fallback outcome applies** (P&L of buying 1M variance at the VSTOXX, against days in the same VSTOXX quintile). Three deviations from the text above, imposed by the data:

1. **Sources.** STOXX public files: `h_vstoxx.txt` (VSTOXX and its sub-indices, 1999-01-04 to 2016-02-12) and `hbrbcpe.txt` (EURO STOXX 50 price index, to 2016-10-04).
2. **Term structure.** The 90-day main index is not in the public file. The ratio is the **3-month sub-index (V6I3) over the VSTOXX (V2TX)**.
3. **Sample.** It ends in February 2016 because the public file stops there. It overlaps the discovery years of the US search, and European and US volatility move together, so this is a different market but not an independent period.

Everything else is unchanged: ON at or below the 20th past-only percentile (minimum 504 days), realized variance over the next 21 trading days, one-sided time-shift test at 5%, positive edge over the same VSTOXX quintile, and survival when any one episode is left out. One run.

### Protocol 4 — result
Run once on 2026-11-11, after the amendment commit. Sample 2000-12-20 to 2016-01-13: 3,771 days, rule ON on 233 days in 41 episodes. P&L of buying 1M variance at the VSTOXX, in vol points per trade.

| Criterion | Result | Met? |
|---|---|---|
| Time-shift test, one-sided | signal +1.37 vs all days -2.24, p = 0.007 (0.009 in a first run with a different random seed) | yes |
| Edge over the same VSTOXX quintile | +1.37 vs -2.81 | yes |
| Survives leaving any one episode out | worst case -3.0, below the all-day mean | **no** |

**Not retained.** The day-weighted average is carried by a single episode; averaged per episode the P&L is -3.8 and only 7 of 41 episodes are positive. Buying variance when the term structure is flat or inverted lost money most of the time and paid very large in one crisis. That is the profile of crash insurance bought late, not of a timing signal.

Status of the lead after protocols 2 and 4: suggestive on day-weighted averages in two markets, not robust to removing one episode in Europe, not testable on correlation itself outside the US. Protocol 3 (forward test) remains open.

## Protocol 5 — the other side: selling the premium with a term-structure switch
*Written on 2026-11-11, before computing any figure of this protocol.*

**Why.** Every test above looked for the right moment to *buy* correlation or variance. The most stable figures of the whole study are the benchmarks: buying 1M variance at the VIX every day, or 3M correlation at COR3M every day, loses on average. The seller collects that premium and carries the crash risk. This protocol tests the seller's side, with one rule to stand aside.

* **Trade.** Sell 1M S&P 500 variance at the VIX, one tranche of 1/21 unit of vega notional per trading day. P&L of a tranche in vol points: (VIX² − realized variance over the next 21 trading days) / (2 × VIX), zero-mean realized variance, 252-day annualization. This is backtest A of the notebook with the sign reversed.
* **Switch.** No new tranche on a day when, at the previous close, VIX3M / VIX was at or below the 20th percentile of its own past (expanding, minimum 504 days, Yahoo history from 2006). It is the rule of protocol 3, unchanged, used as an OFF signal for the seller.
* **Primary version.** Entry filter only: tranches already sold are held to expiry.
* **Benchmark.** The same ladder sold every day, over the same dates.
* **Sample.** From the first day the percentile exists to the last day with a completed 21-day outcome. Taken whole.
* **Decision.** The switch is retained only if all four hold:
  1. the maximum drawdown of the daily marked ladder is at least one third smaller than for the every-day seller;
  2. annual P&L divided by maximum drawdown is higher than for the every-day seller;
  3. the seller's P&L per tranche on OFF days is lower than on all days, one-sided time-shift test p ≤ 0.05 (2,000 circular shifts of at least 252 days, seed 7);
  4. leaving out any one OFF episode (episodes separated by 21 trading days), the seller's average on the remaining OFF days stays below the all-day average.
* **Reported, not used to decide.** Annual P&L, worst tranche, time in the market, P&L in the stress windows of the notebook, the number of OFF episodes in which selling would have lost money, and three variants: thresholds of 10% and 30%, the switch read the same day instead of the day before, and closing open tranches at their approximate mark on the first OFF day (realized variance so far plus VIX² for the remaining days, no bid-offer). None of these variants can rescue a failed primary test.
* **Known weaknesses, stated now.** (a) The switch was found on these same years (protocol 2), on the buyer's correlation P&L: this is not an out-of-sample test, and the forward log of protocol 3 remains the only clean evidence. (b) VIX² is not an executable variance strike and the seller gets the bid; no costs are modelled. (c) The curve usually inverts after volatility has already jumped, when variance is expensive: the naive high-VIX rule of the README shows that buying then is a bad trade, so the switch may well take the seller out at the wrong time. (d) Only the index-variance leg is tested; selling correlation itself (long dispersion) needs single-stock implied volatilities that are not public.
* One run, reported whatever it gives.

### Protocol 5 — result
Run on 2026-11-11, after the protocol commit, on Yahoo data cut at 2026-11-09 (the date of the published levels). The run executed section 6C of the notebook unchanged; a second execution with the same data and seed, made only to reword the generated paragraph, returned identical figures. Sample 2008-07-17 to 2026-11-09: 4,587 days, switch OFF on 544 days in 53 episodes (12% of the time). Check against the published tables: the every-day ladder since 2001-01-22 gives 649.2 vol pts in total and 25.22 a year, the figures of backtest A with the sign reversed.

| | P&L per year (vol pts) | Max drawdown | P&L per year / max drawdown | Worst tranche |
|---|---|---|---|---|
| Sell every day | +21.2 | -173.8 | 0.12 | -252.2 |
| Sell with the switch | +22.9 | -111.6 | 0.21 | -252.2 |

| Criterion | Result | Met? |
|---|---|---|
| 1. Max drawdown at least one third smaller | -173.8 → -111.6 (-36%) | yes |
| 2. P&L per year / max drawdown higher | 0.12 → 0.21 | yes |
| 3. Seller's P&L per tranche lower on OFF days, time-shift p ≤ 0.05 | -1.19 vs +1.80 on all days, p = 0.051 | **no** |
| 4. Still lower leaving any one OFF episode out | worst case +1.44 vs +1.80 | yes |

**Not retained.** Three criteria are met and the third is missed by one thousandth, inside the Monte-Carlo error of a p-value drawn from 2,000 shifts (about ±0.005). The rule was "all four", so the switch fails as written and no other seed or number of draws was tried. Three things temper the three criteria that pass: the switch was found on these same years; selling on OFF days lost money in only 4 of 53 episodes (the average per episode is +4.8), so the benefit comes from a handful of crises; and the worst tranche is identical with and without the switch, because the crash hits tranches sold before the curve inverts. The variant that closes open tranches on the first OFF day shows a maximum drawdown of -37.5, but it assumes closing at VIX² with no bid-offer in the middle of a crash and was declared in advance as unable to rescue the test.

What stands: the every-day seller's premium (+21.2 vol pts a year on this sample, with a -173.8 drawdown) and, before costs, a smaller drawdown with the switch. What does not: a validated rule to stop.

**Forward evaluation, fixed now.** The log of protocol 3 records this same rule from 2026-11-11. At the evaluation date of protocol 3, the four criteria above will be computed for the seller on the forward days only, once.

### Protocol 5 — note on later runs of the notebook
The notebook was run again the same day on data to 2026-11-10, one trading day more than the registered run. The four figures of the table are unchanged to the digits shown, except the time-shift p-value: 0.050 instead of 0.051, which on its own would meet criterion 3. That does not change the verdict. The protocol allowed one run, and a result that crosses the bar with one more day of data, by one thousandth and inside the Monte-Carlo error, is a result on the bar. The registered verdict (**not retained**) is now written in the notebook's configuration (`SELL_REGISTERED`), so later runs report their own p-value next to it without overwriting it.
