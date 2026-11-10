"""Forward test of the 'flat or inverted VIX term structure' lead (see PREREGISTRATION.md, protocol 3).

Each run appends the trading days not yet logged to forward_log.csv: VIX, VIX3M, their ratio, the past-only
expanding percentile of the ratio (minimum 504 days, history from Yahoo since 2006) and whether the rule is ON
(percentile <= 0.20). COR3M is recorded as the strike a correlation buyer would face that day.
Nothing is ever rewritten: rows already in the log are kept as they were first recorded.
"""
import io
import os
import sys

import pandas as pd

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forward_log.csv")
START = "2026-11-11"          # first day of the forward test (date of the pre-registration)
MIN_HISTORY, THRESHOLD = 504, 0.20
COR3M_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/COR3M_History.csv"


def fetch():
    """VIX and VIX3M closes from Yahoo (same source and history as the search), COR3M from Cboe."""
    import requests
    import yfinance as yf
    px = yf.download(["^VIX", "^VIX3M"], start="2006-01-01", auto_adjust=True, progress=False)["Close"]
    px.index = pd.to_datetime(px.index).tz_localize(None)
    r = requests.get(COR3M_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    c = pd.read_csv(io.StringIO(r.text))
    cor = pd.Series(pd.to_numeric(c["CLOSE"], errors="coerce").values, index=pd.to_datetime(c["DATE"])).dropna()
    return px["^VIX"].dropna(), px["^VIX3M"].dropna(), cor


def build(vix, vix3m, cor3m):
    ratio = (vix3m / vix).dropna().sort_index()
    pct = ratio.expanding(min_periods=MIN_HISTORY).rank(pct=True)
    out = pd.DataFrame({"vix": vix.reindex(ratio.index), "vix3m": vix3m.reindex(ratio.index), "ratio": ratio.round(4),
                        "percentile": pct.round(4), "signal_on": (pct <= THRESHOLD).astype(int),
                        "cor3m": cor3m.reindex(ratio.index)})
    out.index.name = "date"
    return out.loc[START:].dropna(subset=["percentile"])


def append(new, path=LOG):
    old = pd.read_csv(path, index_col="date", parse_dates=True) if os.path.exists(path) else new.iloc[:0]
    add = new.loc[~new.index.isin(old.index)]
    if len(old):
        add = add.loc[add.index > old.index.max()]          # never back-fill or rewrite
    if len(add):
        pd.concat([old, add]).to_csv(path, date_format="%Y-%m-%d")
    return len(add)


if __name__ == "__main__":
    today = pd.Timestamp.now(tz="America/New_York")
    table = build(*fetch())
    if today.hour < 17:                                       # drop today's unfinished bar
        table = table.loc[table.index < today.normalize().tz_localize(None)]
    n = append(table)
    print(f"{n} day(s) added; last logged: {table.index[-1].date() if len(table) else 'none'}")
    sys.exit(0)
