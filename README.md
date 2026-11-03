# Quantitative Finance Projects

**Jonathan Phung** · Master in Management (Market Finance), ESCP Business School · ex-Société Générale FIC Trading intern

Derivatives pricing and implied volatility projects in Python and JavaScript.

| Project | What it shows | Link |
|---|---|---|
| G10 FX Option Pricer | Multi-leg FX option strategies: premium, Greeks, P&L at expiry | [Live demo](https://jojolap1.github.io/quant-finance-projects/fx-pricer.html) |
| SPX Implied Volatility Surface | Implied vol surface rebuilt from listed SPX option quotes | [Notebook](spx_implied_volatility_surface.ipynb) |
| Black-Scholes vs Heston | How stochastic volatility creates smiles and skew | [Results](#3-black-scholes-vs-heston) |

---

## 1. G10 FX Option Pricer

**[Open the live pricer](https://jojolap1.github.io/quant-finance-projects/fx-pricer.html)**, no installation needed.

Build vanilla FX option strategies (calls, puts, straddles, strangles, up to five legs) on nine G10 currency pairs. Each leg is priced with a forward Black model; the tool aggregates premium, delta, delta notional and vega across legs and plots the strategy P&L at expiry.

*Limitations:* static market snapshot, a single ATM volatility for all strikes (no smile), simplified FX delta conventions.

## 2. SPX Implied Volatility Surface

![SPX implied volatility surface](spx_implied_volatility_surface_3d.png)

Notebook: [`spx_implied_volatility_surface.ipynb`](spx_implied_volatility_surface.ipynb). It downloads a live SPX option chain (Yahoo Finance) or reads `Chain.csv` / `Meta.csv`.

Pipeline: liquidity filters, call/put matching by strike and expiry, forward estimation through put-call parity, out-of-the-money selection, Black-76 inversion, calendar and butterfly arbitrage checks.

![SPX smiles by expiry](spx_implied_volatility_smiles.png)

*Limitations:* single snapshot, mid prices, flat interest rate, no dividend curve, arbitrage diagnosed but not repaired.

## 3. Black-Scholes vs Heston

Comparison of a constant-volatility Black-Scholes surface with a Heston stochastic-volatility surface, priced with the semi-closed form and with Monte Carlo, plus sensitivity of the 1M smile to vol-of-vol and correlation.

![Black-Scholes vs Heston smiles, 3M](smiles_comparison_3M.png)

| Heston, semi-closed form | Heston, Monte Carlo |
|---|---|
| ![](heston_semiclosed_surface.png) | ![](heston_montecarlo_surface.png) |

| Vol-of-vol sensitivity (1M) | Correlation sensitivity (1M) |
|---|---|
| ![](heston_xi_sensitivity_1M.png) | ![](heston_rho_sensitivity_1M.png) |

---

**Tools:** Python (NumPy, pandas, SciPy, Matplotlib), JavaScript, VBA

**Contact:** jonathan.phung@edu.escp.eu
