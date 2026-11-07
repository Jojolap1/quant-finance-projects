# Proportional vega-neutral sizing (= theta-neutral)

How the two legs of a dispersion trade are sized so that the book bets on correlation only. All numbers below are illustrative, not market data.

## 1. Two definitions of "vega-neutral"

| | Condition | Flat to… |
|---|---|---|
| **Vega-neutral in points** | Σ vegaᵢ = vega_index | every vol moving by the **same number of points** (+1 pt everywhere) |
| **Proportional vega-neutral** | Σ vegaᵢ × σᵢ = vega_index × σ_index | every vol moving by the **same percentage** (+10% everywhere) |

vegaᵢ is in $ per vol point, and σ is in vol points.

## 2. Proportional vega-neutral = theta-neutral

For an at-the-money option, in Black-Scholes:

```
theta ≈ − vega × σ / (2T)
```

Both legs have the same maturity T, so the 2T cancels:

```
theta_stocks = theta_index   ⟺   Σ vegaᵢ × σᵢ = vega_index × σ_index
```

This is exactly the proportional vega-neutral condition. The two conditions cannot both hold with the **point** definition, because stock vols are above index vol whenever correlation is below 1.

## 3. Why the book is flat in a proportional shock

In a shock where every vol rises by x% (Δσ = x × σ), each leg moves by vega × x × σ:

```
P&L_book = x × (vega_index × σ_index − Σ vegaᵢ × σᵢ) = 0
```

This holds for any x, up or down. A proportional shock leaves the ratio σ_index / Σwᵢσᵢ unchanged. Implied correlation is roughly the square of that ratio, so it does not move either. **The book only moves when correlation moves.**

## 4. Worked example (long correlation: long index straddles, short stock straddles)

Index vol 15%, stock vol 30%, index vega $100k per vol point. Sizing: stock vega = 100k × 15/30 = **$50k**.

| Shock | Index leg (long, $100k vega) | Stock leg (short, $50k vega) | Book |
|---|---|---|---|
| All vols +10% | 15 → 16.5: **+$150k** | 30 → 33: **−$150k** | **0** |
| All vols +50% | 15 → 22.5: +$750k | 30 → 45: −$750k | **0** |
| All vols −20% | 15 → 12: −$300k | 30 → 24: +$300k | **0** |
| All vols +1 point | +$100k | −$50k | +$50k (residual long vega in points) |
| Crash: index 15 → 20, stocks 30 → 33 | +$500k | −$150k | **+$350k** (correlation ≈ 0.25 → 0.37) |

For comparison, a book that is vega-neutral **in points** (stock vega $100k) makes −$150k (long dispersion side) or +$150k (long correlation side) on the +10% shock, with no change in correlation. It is also betting on the level of volatility.

## 5. Theta check (same example, 3M SPX straddles at 6,000)

| | Approach 1: vega | Approach 2: gamma |
|---|---|---|
| Formula | θ_day = − vega × σ / (2T) × Δt | θ_day = − ½ × Γ × S² × σ² × Δt |
| Per straddle | vega ≈ 0.8 × S × √T | Γ ≈ 0.8 / (S × σ × √T) |
| ATM simplification | 0.4 × S × σ / √T × Δt | 0.4 × S × σ / √T × Δt |
| 42 straddles, Δt = 1/365 | ≈ $8,285 per day | ≈ $8,263 per day |

The gap comes only from rounding 2 × 0.3989 = 0.7978 to 0.8. The premium check gives the same picture: straddle ≈ 0.8 × S × σ × √T = 360 index points ≈ $36,000 per contract, and 42 contracts ≈ $1.5M = vega × σ.

## 6. Limits

- **The neutrality holds at inception only.** When spot and vols move, vegas drift (vanna, volga), so large moves break it.
- **It requires ATM options of the same maturity on both legs.**
- **The approximations are first order and assume Black-Scholes.** The smile and skew make them approximate.
