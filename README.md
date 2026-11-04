# Quantitative Finance Projects

**Jonathan Phung** · Master in Management (Market Finance), ESCP Business School · ex-Société Générale FIC Trading intern & ex-Pictet 
Product Sales 

Derivatives pricing and implied volatility projects in Python.

| Project | What it shows | Link |
|---|---|---|
| G10 FX Option Pricer | Interactive Python app: multi-leg FX options with a volatility smile, premium and Greeks | [Live app](https://jonathan-fx-pricer.streamlit.app) |
| SPX Implied Volatility Surface | Implied vol surface rebuilt from listed SPX option quotes | [Notebook](spx_implied_volatility_surface.ipynb) |

---

## 1. G10 FX Option Pricer

**[Open the live app](https://jonathan-fx-pricer.streamlit.app)**, no installation needed.

Interactive Python app (Streamlit) to price vanilla FX option structures on nine G10 currency pairs: calls, puts, straddles, strangles, risk reversals and spreads, up to five editable legs.

- **Pricing:** Garman-Kohlhagen (Black-76 on the forward), premium discounted to today, foreign rate implied from the forward by covered interest parity
- **Volatility smile:** built from ATM, 25-delta and 10-delta risk reversals and butterflies, interpolated in log-moneyness
- **Outputs:** premium (base ccy and % of notional), spot delta, vega, gamma, P&L at expiry and the smile with your strikes

Code: [`fx_core.py`](fx_core.py) (pricing and smile) and [`app.py`](app.py) (interface). Run locally with `pip install -r requirements.txt` then `streamlit run app.py`.

*Limitations:* static market snapshot, quote-currency rate is an assumption, simplified smile construction (no full calibration, non premium-adjusted deltas).

## 2. SPX Implied Volatility Surface

![SPX implied volatility surface](spx_implied_volatility_surface_3d.png)

Notebook: [`spx_implied_volatility_surface.ipynb`](spx_implied_volatility_surface.ipynb). It downloads a live SPX option chain (Yahoo Finance) or reads `Chain.csv` / `Meta.csv`.

Pipeline: liquidity filters, call/put matching by strike and expiry, forward estimation through put-call parity, out-of-the-money selection, Black-76 inversion, calendar and butterfly arbitrage checks.

![SPX smiles by expiry](spx_implied_volatility_smiles.png)

*Limitations:* single snapshot, mid prices, flat interest rate, no dividend curve, arbitrage diagnosed but not repaired.

---

**Tools:** Python (NumPy, pandas, SciPy, Matplotlib, Plotly, Streamlit), VBA

**Contact:** jonathan.phung@edu.escp.eu
