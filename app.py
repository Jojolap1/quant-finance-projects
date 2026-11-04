"""
G10 FX Option Pricer - interactive Streamlit app.
Run locally:  pip install -r requirements.txt  &&  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import fx_core as fx

st.set_page_config(page_title="G10 FX Option Pricer", page_icon="💱", layout="wide")

DATA = Path(__file__).parent / "fx-market-data.json"
market = fx.load_market(DATA)

# Default quote-currency rates (editable assumptions, not market data)
DEFAULT_RATES = {"USD": 4.00, "JPY": 0.50, "CAD": 2.75, "CHF": 0.00, "NOK": 4.00, "SEK": 2.00}

st.title("G10 FX Option Pricer")
st.caption(
    f"Jonathan Phung · Garman-Kohlhagen pricing with a delta-quoted volatility smile · "
    f"market snapshot {market['metadata'].get('snapshot', '')} (static, educational)"
)

# ---------------- Sidebar: market and structure ----------------
with st.sidebar:
    st.header("Market")
    pair = st.selectbox("Currency pair", market["pairs"], index=0)
    tenors = fx.common_tenors(market, pair)
    tenor = st.selectbox("Tenor", tenors, index=tenors.index("3M") if "3M" in tenors else 0)
    m = fx.market_point(market, pair, tenor)
    r_d = st.number_input(
        f"{m.quote} interest rate (%) — assumption", value=DEFAULT_RATES.get(m.quote, 3.0), step=0.25,
        help="Used to discount the premium. The base-currency rate is implied from the forward (covered interest parity).",
    ) / 100
    use_smile = st.toggle("Use volatility smile", value=True,
                          help="Off = a single ATM volatility for every strike.")

    st.header("Structure")
    preset = st.selectbox("Preset", fx.PRESETS, index=2)
    notional = st.number_input(f"Notional per leg ({m.base})", value=1_000_000, step=100_000, min_value=1_000)

smile = fx.Smile(m)
digits = 3 if pair.endswith("JPY") else 5

# ---------------- Market snapshot ----------------
c = st.columns(6)
c[0].metric("Spot", f"{m.spot:.{digits}f}")
c[1].metric(f"Forward {tenor}", f"{m.forward:.{digits}f}")
c[2].metric("Fwd points", f"{(m.forward - m.spot) / fx.pip_size(pair):.1f}")
c[3].metric("ATM vol", f"{m.atm * 100:.2f}%")
c[4].metric("25D risk reversal", f"{m.rr25 * 100:+.2f}%")
c[5].metric("25D butterfly", f"{m.bf25 * 100:.2f}%")

# ---------------- Legs editor ----------------
st.subheader("Legs")
st.caption("Edit sides, strikes and notionals, or add / remove rows (up to 5 legs). "
           "Leave 'Vol override' empty to use the smile.")
legs0 = fx.preset_legs(preset, m, float(notional), smile)
df0 = pd.DataFrame([{"Side": l.side, "Option": l.option, "Strike": round(l.strike, digits),
                     "Notional": l.notional, "Vol override (%)": None} for l in legs0])
edited = st.data_editor(
    df0,
    key=f"legs-{pair}-{tenor}-{preset}-{notional}",
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Side": st.column_config.SelectboxColumn(options=["Buy", "Sell"], required=True),
        "Option": st.column_config.SelectboxColumn(options=["Call", "Put"], required=True),
        "Strike": st.column_config.NumberColumn(format=f"%.{digits}f", min_value=0.0, required=True),
        "Notional": st.column_config.NumberColumn(format="%d", min_value=0.0, required=True),
        "Vol override (%)": st.column_config.NumberColumn(format="%.2f", min_value=0.0),
    },
)

legs = []
for _, r in edited.head(5).iterrows():
    if pd.isna(r["Strike"]) or pd.isna(r["Notional"]) or r["Strike"] <= 0 or r["Notional"] <= 0:
        continue
    vo = r["Vol override (%)"]
    legs.append(fx.Leg(r["Side"] or "Buy", r["Option"] or "Call", float(r["Strike"]), float(r["Notional"]),
                       float(vo) / 100 if pd.notna(vo) and vo > 0 else None))

if not legs:
    st.info("Add at least one leg with a positive strike and notional.")
    st.stop()

rows = [fx.price_leg(l, m, smile, r_d, use_smile) for l in legs]
res = pd.DataFrame(rows)

# ---------------- Results ----------------
st.subheader("Structure analytics")
prem_quote = res["Premium (QUOTE)"].sum()
prem_base = res["Premium (BASE)"].sum()
ref_notional = max(l.notional for l in legs)
k = st.columns(5)
if m.premium_ccy == m.base:
    k[0].metric(f"Premium ({m.base})", f"{prem_base:,.0f}", f"{prem_base / ref_notional * 100:.3f}% of notional",
                delta_color="off")
else:
    k[0].metric(f"Premium ({m.quote})", f"{prem_quote:,.0f}")
k[1].metric(f"Premium ({m.quote})", f"{prem_quote:,.0f}")
k[2].metric(f"Spot delta ({m.base})", f"{res['Delta notional (BASE)'].sum():,.0f}")
k[3].metric(f"Vega ({m.quote} / vol pt)", f"{res['Vega (QUOTE / vol pt)'].sum():,.0f}")
k[4].metric(f"Gamma ({m.base} / 1% spot)", f"{res['Gamma (BASE / 1% spot)'].sum():,.0f}")
st.caption("Positive premium = paid (long the structure). Delta, vega and gamma are signed from the holder's view.")

show = res.copy()
show["Strike"] = show["Strike"].map(lambda x: f"{x:.{digits}f}")
st.dataframe(
    show.style.format({
        "Notional": "{:,.0f}", "Vol (%)": "{:.2f}", "Premium (QUOTE)": "{:,.0f}", "Premium (BASE)": "{:,.0f}",
        "Premium (% notional)": "{:.3f}", "Spot delta": "{:.3f}", "Delta notional (BASE)": "{:,.0f}",
        "Fwd delta": "{:.3f}", "Vega (QUOTE / vol pt)": "{:,.0f}", "Gamma (BASE / 1% spot)": "{:,.0f}",
    }),
    use_container_width=True, hide_index=True,
)

# ---------------- Charts ----------------
left, right = st.columns(2)

with left:
    st.markdown("**P&L at expiry** (net of premium, in " + m.quote + ")")
    strikes = [l.strike for l in legs]
    lo = min(min(strikes), m.forward) * 0.92
    hi = max(max(strikes), m.forward) * 1.08
    grid = np.linspace(lo, hi, 400)
    fwd_value_premium = prem_quote / np.exp(-r_d * m.T)   # premium carried to expiry
    pnl = fx.payoff_at_expiry(legs, grid) - fwd_value_premium
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid, y=pnl, mode="lines", name="Structure P&L", line=dict(width=3)))
    fig.add_hline(y=0, line_color="grey", line_width=1)
    fig.add_vline(x=m.forward, line_dash="dash", line_color="grey", annotation_text="Forward")
    for s in sorted(set(strikes)):
        fig.add_vline(x=s, line_dash="dot", line_color="lightgrey")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis_title=f"{pair} at expiry", yaxis_title=f"P&L ({m.quote})", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown(f"**Volatility smile** ({pair} {tenor})")
    kg = np.linspace(smile.pillars[0][1] * 0.97, smile.pillars[-1][1] * 1.03, 300)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=kg, y=[smile.vol(x) * 100 for x in kg], mode="lines", name="Smile"))
    fig2.add_trace(go.Scatter(x=[p[1] for p in smile.pillars], y=[p[2] * 100 for p in smile.pillars],
                              mode="markers+text", text=[p[0] for p in smile.pillars], textposition="top center",
                              name="Market pillars", marker=dict(size=9)))
    fig2.add_trace(go.Scatter(x=res["Strike"], y=res["Vol (%)"], mode="markers", name="Your legs",
                              marker=dict(size=12, symbol="x")))
    fig2.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                       xaxis_title="Strike", yaxis_title="Implied vol (%)", legend=dict(orientation="h"))
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("Method and limitations"):
    st.markdown(f"""
- **Model:** Garman-Kohlhagen, written as Black-76 on the forward: premium = DF({m.quote}) × Black(F, K, σ, T).
- **Forward:** spot + forward points from the snapshot. The {m.base} rate is implied by covered interest parity:
  r_base = r_{m.quote.lower()} − ln(F/S)/T.
- **Smile:** vols at 10D/25D puts, ATM, 25D/10D calls from risk reversals and butterflies
  (σ25C = ATM + BF + RR/2, σ25P = ATM + BF − RR/2), converted to strikes with the forward delta and interpolated
  in log-moneyness (PCHIP), flat beyond the 10-delta wings.
- **Greeks:** spot delta = DF({m.base}) × N(d1); vega per 1 vol point; gamma per 1% move in spot.
- **Limitations:** static snapshot, rate of the quote currency is an assumption, non premium-adjusted deltas
  for the smile strikes, simple-butterfly approximation instead of a full smile calibration, ACT/365 tenors.
""")
