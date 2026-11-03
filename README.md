# Quantitative Finance Projects

Jonathan Phung, Master in Management (Market Finance), ESCP Business School.

This repository gathers quantitative finance projects on derivatives pricing and implied volatility.

## 1. G10 FX Option Pricer

A browser-based tool to build vanilla FX option strategies (calls, puts, straddles, strangles, up to five legs) on nine G10 currency pairs. Each leg is priced with a forward Black model; the tool aggregates premium, delta, delta notional and vega across legs and plots the strategy P&L at expiry.

Files: `fx-pricer.html`, `fx-pricer.js`, `fx-pricer.css`, `fx-market-data.json`. Open `fx-pricer.html` in a browser, no installation needed.

Limitations: static market snapshot, a single ATM volatility for all strikes (no smile), simplified FX delta conventions.

## 2. SPX Implied Volatility Surface

Reconstruction of an SPX implied volatility surface from a snapshot of listed option quotes: liquidity filters, call/put matching by strike and expiry, forward estimation through put-call parity, selection of out-of-the-money options, Black-76 inversion, then smiles and 3D surface.

Outputs: `spx_implied_volatility_smiles.png`, `spx_implied_volatility_surface_3d.png`, `spx_iv_surface_scatter_heatmap.png`.

Limitations: mid prices, flat interest rate, single snapshot, no dividend curve, no full arbitrage repair.

## 3. Black-Scholes vs Heston Volatility Surfaces

Comparison of a constant-volatility Black-Scholes surface with a Heston stochastic-volatility surface, priced both with the semi-closed form and with Monte Carlo simulation, plus sensitivity of the 1M smile to the vol-of-vol and correlation parameters.

Outputs: `heston_*.png`, `black_scholes_surface.png`, `smiles_comparison_*.png`.

## Tools

Python (NumPy, pandas, Matplotlib), JavaScript, VBA.

## Contact

Jonathan Phung, jonathan.phung@edu.escp.eu
