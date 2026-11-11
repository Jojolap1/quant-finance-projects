"""Temporary runner: executes section 6C of the notebook, unchanged, on public data. Removed before merging."""
import ast, json, os, shutil
import matplotlib
matplotlib.use("Agg")
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = "2026-11-09"                      # date of the published levels: same data vintage as the rest of the README
nb = json.load(open(os.path.join(HERE, "long_correlation_trade_idea.ipynb"), encoding="utf-8"))
src = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
find = lambda start: next(s for s in src if s.startswith(start))
g = {"__name__": "__main__"}
out = os.path.join(HERE, "_tmp_sell_out"); os.makedirs(out, exist_ok=True); os.chdir(out)
exec(find("import os, io, json"), g); exec(find("def fetch_close"), g)
CFG = g["CFG"]
px = g["fetch_close"]([CFG["INDEX_PRICE_TICKER"]], CFG["HIST_START"])
vol = g["fetch_close"](["^VIX", "^VIX3M"], CFG["HIST_START"])
px, vol = px[px.index <= CUT], vol[vol.index <= CUT]
px = px.dropna(subset=[CFG["INDEX_PRICE_TICKER"]])
r_idx = np.log(px).diff().iloc[1:][CFG["INDEX_PRICE_TICKER"]]
cboe = vol.reindex(r_idx.index).ffill(limit=3) / 100.0
g.update(r_idx=r_idx, cboe=cboe, VIXP=cboe["^VIX"] * 100, SG=CFG["SIGNAL"], HV=CFG["VAR_TENOR"])
def pick(start, names):
    for node in ast.parse(find(start)).body:
        nm = node.name if isinstance(node, ast.FunctionDef) else (node.targets[0].id if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) else None)
        if nm in names:
            exec(compile(ast.Module([node], []), "nb", "exec"), g)
pick("SG = CFG", {"expanding_pct", "episodes"}); pick("def ladder(", {"STRESS", "window_pnl"})
exec(find("SELL = {}\ndef sell_ladder"), g)
S = g["SELL"]
assert S and "md" in S, "section 6C did not run"
# consistency with the published README: every-day ladder since 2001-01-22 (published: buyer -649.2 in total, -25.22 a year)
off0 = pd.Series(False, index=r_idx.index).where((r_idx.index >= "2001-01-22") & g["VIXP"].notna().values)
m0, t0, e0 = g["sell_ladder"](r_idx, g["VIXP"], off0)
ts = g["ts_pct"].dropna()
chk = {"first": str(r_idx.index[0].date()), "last": str(r_idx.index[-1].date()), "rows": int(len(r_idx)),
       "vix_last": float(g["VIXP"].iloc[-1]), "vix3m_last": float(cboe["^VIX3M"].iloc[-1] * 100),
       "vix3m_first": str(cboe["^VIX3M"].dropna().index[0].date()), "pct_first": str(ts.index[0].date()), "pct_last": float(ts.iloc[-1]),
       "every_day_2001_total": float(m0.iloc[-1] - m0.iloc[0]), "every_day_2001_ann": float(m0.diff().dropna().mean() * 252),
       "every_day_2001_start": str(m0.index[0].date())}
json.dump({"SELL": {k: v for k, v in S.items()}, "chk": chk}, open("sell.json", "w"), indent=1)
shutil.copy(os.path.join("output", "figures", "06_sell_premium_switch.png"), "06_sell_premium_switch.png")
shutil.rmtree("output")
print(json.dumps(chk, indent=1))
