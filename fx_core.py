"""
G10 FX option pricing core (Garman-Kohlhagen / Black-76 on the forward).

Pure functions, no UI: used by the Streamlit app (app.py) and easy to test.

Conventions
- Pair BASE/QUOTE (e.g. EUR/USD): spot = QUOTE units per 1 BASE.
- Forward from forward points: F = S + points * pip.
- Domestic (quote ccy) rate r_d is an input; the foreign (base ccy) rate is implied
  by covered interest parity: r_f = r_d - ln(F / S) / T.
- Premium is the present value (discounted with r_d), i.e. what is paid at spot date.
- Volatility smile built from ATM, 25-delta and 10-delta risk reversals / butterflies.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.stats import norm

# ---------------------------------------------------------------------------
# Market data
# ---------------------------------------------------------------------------

def load_market(path: str | Path = "fx-market-data.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pip_size(pair: str) -> float:
    return 0.01 if pair.endswith("JPY") else 0.0001


def year_fraction(tenor: str) -> float:
    t = tenor.strip().upper()
    if t in ("ON", "TN", "SN", "1D"):
        return 1 / 365
    n = float(t[:-1])
    unit = t[-1]
    if unit == "D":
        return n / 365
    if unit == "W":
        return 7 * n / 365
    if unit == "M":
        return n / 12
    if unit == "Y":
        return n
    raise ValueError(f"Unsupported tenor: {tenor}")


def _tenor_alias(tenor: str) -> list[str]:
    # vol grid uses 1Y / 18M / 2Y, forward grid uses 12M / 2Y
    aliases = {"1Y": ["1Y", "12M"], "12M": ["12M", "1Y"]}
    return aliases.get(tenor, [tenor])


def common_tenors(market: dict, pair: str) -> list[str]:
    fwd = market["forwards"][pair]
    vols = market["vols"][pair]
    out = []
    for t in vols:
        if t == "1D":
            continue
        if any(a in fwd for a in _tenor_alias(t)):
            out.append(t)
    return sorted(out, key=year_fraction)


@dataclass
class MarketPoint:
    pair: str
    base: str
    quote: str
    tenor: str
    T: float
    spot: float
    forward: float
    atm: float      # in decimals
    rr25: float
    bf25: float
    rr10: float
    bf10: float
    premium_ccy: str


def market_point(market: dict, pair: str, tenor: str) -> MarketPoint:
    spot = market["spots"][pair]["mid"]
    fwd_grid = market["forwards"][pair]
    pts = next(fwd_grid[a] for a in _tenor_alias(tenor) if a in fwd_grid)
    v = market["vols"][pair][tenor]
    conv = market["conventions"][pair]
    return MarketPoint(
        pair=pair, base=conv["base"], quote=conv["quote"], tenor=tenor, T=year_fraction(tenor),
        spot=spot, forward=spot + pts * pip_size(pair),
        atm=v["atm"] / 100, rr25=v["rr25"] / 100, bf25=v["bf25"] / 100,
        rr10=v.get("rr10", 0) / 100, bf10=v.get("bf10", 0) / 100,
        premium_ccy=conv["premiumCurrency"],
    )

# ---------------------------------------------------------------------------
# Black-76 on the forward
# ---------------------------------------------------------------------------

def d1_d2(F: float, K: float, sigma: float, T: float) -> tuple[float, float]:
    s = sigma * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * s * s) / s
    return d1, d1 - s


def undiscounted_price(F: float, K: float, sigma: float, T: float, is_call: bool) -> float:
    d1, d2 = d1_d2(F, K, sigma, T)
    if is_call:
        return F * norm.cdf(d1) - K * norm.cdf(d2)
    return K * norm.cdf(-d2) - F * norm.cdf(-d1)


def strike_from_forward_delta(F: float, sigma: float, T: float, delta: float, is_call: bool) -> float:
    """Strike for a given (non premium-adjusted) forward delta, e.g. 0.25 call or 0.25 put."""
    s = sigma * math.sqrt(T)
    d1 = norm.ppf(delta) if is_call else -norm.ppf(delta)
    return F * math.exp(-d1 * s + 0.5 * s * s)

# ---------------------------------------------------------------------------
# Volatility smile (5 delta pillars -> interpolation in log-moneyness)
# ---------------------------------------------------------------------------

def smile_pillars(m: MarketPoint) -> list[tuple[str, float, float]]:
    """Return [(label, strike, vol)] for 10P, 25P, ATM, 25C, 10C (market quoting approximation)."""
    v25c = m.atm + m.bf25 + m.rr25 / 2
    v25p = m.atm + m.bf25 - m.rr25 / 2
    v10c = m.atm + m.bf10 + m.rr10 / 2
    v10p = m.atm + m.bf10 - m.rr10 / 2
    F, T = m.forward, m.T
    return [
        ("10D put", strike_from_forward_delta(F, v10p, T, 0.10, False), v10p),
        ("25D put", strike_from_forward_delta(F, v25p, T, 0.25, False), v25p),
        ("ATM", F, m.atm),
        ("25D call", strike_from_forward_delta(F, v25c, T, 0.25, True), v25c),
        ("10D call", strike_from_forward_delta(F, v10c, T, 0.10, True), v10c),
    ]


class Smile:
    def __init__(self, m: MarketPoint):
        p = smile_pillars(m)
        self.F = m.forward
        self.pillars = p
        x = np.array([math.log(k / self.F) for _, k, _ in p])
        y = np.array([v for _, _, v in p])
        order = np.argsort(x)
        self._x, self._y = x[order], y[order]
        self._interp = PchipInterpolator(self._x, self._y, extrapolate=False)

    def vol(self, K: float) -> float:
        x = math.log(K / self.F)
        if x <= self._x[0]:
            return float(self._y[0])   # flat extrapolation beyond the 10-delta wings
        if x >= self._x[-1]:
            return float(self._y[-1])
        return float(self._interp(x))

# ---------------------------------------------------------------------------
# Pricing a leg / a structure
# ---------------------------------------------------------------------------

@dataclass
class Leg:
    side: str        # "Buy" / "Sell"
    option: str      # "Call" / "Put"
    strike: float
    notional: float  # in BASE currency
    vol_override: float | None = None   # in decimals


def price_leg(leg: Leg, m: MarketPoint, smile: Smile, r_d: float, use_smile: bool = True) -> dict:
    F, T, S = m.forward, m.T, m.spot
    is_call = leg.option == "Call"
    sign = 1 if leg.side == "Buy" else -1
    sigma = leg.vol_override if leg.vol_override else (smile.vol(leg.strike) if use_smile else m.atm)
    r_f = r_d - math.log(F / S) / T
    df_d, df_f = math.exp(-r_d * T), math.exp(-r_f * T)
    d1, _ = d1_d2(F, leg.strike, sigma, T)

    pv_quote_per_base = df_d * undiscounted_price(F, leg.strike, sigma, T, is_call)   # QUOTE per 1 BASE
    pv_quote = pv_quote_per_base * leg.notional
    fwd_delta = norm.cdf(d1) if is_call else norm.cdf(d1) - 1
    spot_delta = df_f * fwd_delta
    vega = df_d * F * norm.pdf(d1) * math.sqrt(T) / 100 * leg.notional       # QUOTE ccy per 1 vol point
    gamma = df_f * norm.pdf(d1) / (S * sigma * math.sqrt(T)) * leg.notional    # BASE per 1 unit of spot

    return {
        "Side": leg.side, "Option": leg.option, "Strike": leg.strike, "Notional": leg.notional,
        "Vol (%)": sigma * 100,
        "Premium (QUOTE)": sign * pv_quote,
        "Premium (BASE)": sign * pv_quote / S,
        "Premium (% notional)": sign * pv_quote_per_base / S * 100,
        "Spot delta": sign * spot_delta,
        "Delta notional (BASE)": sign * spot_delta * leg.notional,
        "Fwd delta": sign * fwd_delta,
        "Vega (QUOTE / vol pt)": sign * vega,
        "Gamma (BASE / 1% spot)": sign * gamma * S / 100,
    }


def payoff_at_expiry(legs: list[Leg], spots: np.ndarray) -> np.ndarray:
    total = np.zeros_like(spots, dtype=float)
    for leg in legs:
        sign = 1 if leg.side == "Buy" else -1
        intrinsic = np.maximum(spots - leg.strike, 0) if leg.option == "Call" else np.maximum(leg.strike - spots, 0)
        total += sign * intrinsic * leg.notional
    return total  # QUOTE ccy


def preset_legs(name: str, m: MarketPoint, notional: float, smile: Smile) -> list[Leg]:
    F = m.forward
    k25c = next(k for lab, k, _ in smile.pillars if lab == "25D call")
    k25p = next(k for lab, k, _ in smile.pillars if lab == "25D put")
    if name == "Call (ATM)":
        return [Leg("Buy", "Call", F, notional)]
    if name == "Put (ATM)":
        return [Leg("Buy", "Put", F, notional)]
    if name == "Straddle (ATM)":
        return [Leg("Buy", "Call", F, notional), Leg("Buy", "Put", F, notional)]
    if name == "Strangle (25D)":
        return [Leg("Buy", "Call", k25c, notional), Leg("Buy", "Put", k25p, notional)]
    if name == "Risk reversal (25D)":
        return [Leg("Buy", "Call", k25c, notional), Leg("Sell", "Put", k25p, notional)]
    if name == "Call spread (ATM / 25D)":
        return [Leg("Buy", "Call", F, notional), Leg("Sell", "Call", k25c, notional)]
    if name == "Put spread (ATM / 25D)":
        return [Leg("Buy", "Put", F, notional), Leg("Sell", "Put", k25p, notional)]
    raise ValueError(name)


PRESETS = ["Call (ATM)", "Put (ATM)", "Straddle (ATM)", "Strangle (25D)", "Risk reversal (25D)",
           "Call spread (ATM / 25D)", "Put spread (ATM / 25D)"]
