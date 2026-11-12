"""Run the back-tests + sensitivity checks and write site/data/results.json."""
import json, os
from dataclasses import replace
import numpy as np
import pandas as pd
import model as M

ROOT = os.path.join(os.path.dirname(__file__), "..")
m = pd.read_csv(os.path.join(ROOT, "data/processed/monthly_2003_2025.csv"), index_col=0)
m.index = pd.PeriodIndex(m.index, freq="M")
jst = pd.read_csv(os.path.join(ROOT, "data/processed/jst_annual_1870_2020.csv"))

r = lambda x: None if pd.isna(x) else round(float(x), 4)
HORIZONS = [3, 5, 7, 10, 15]
res = {"horizons": HORIZONS}

for city in ["ES", "SK"]:
    res[city] = {}
    base = M.SPAIN if city == "ES" else M.SLOVAKIA
    for rt in ["fixed", "variable"]:
        g = M.tier1_grid(m, city, rt)
        res[city][rt] = {
            "winshare": {str(y): r((g[y].dropna() > 0).mean()) for y in g.columns if g[y].notna().sum()},
            "median_adv": {str(y): r(g[y].median()) for y in g.columns if g[y].notna().sum()},
            "n_starts": {str(y): int(g[y].notna().sum()) for y in g.columns if g[y].notna().sum()},
            "by_start": {str(y): [[str(k), r(v)] for k, v in g[y].dropna().items()] for y in (5, 10)},
            "breakeven_years": [[str(k), M.break_even(row)] for k, row in g.iterrows()],
            "never_wins_share": r(g.apply(M.break_even, axis=1).isna().mean()),
        }
    # sensitivity (fixed-rate loans, 10-year horizon): win share of buying
    sens = {"yield": [], "buy_cost": [], "invest_return_gap": []}
    for y in [0.035, 0.045, 0.055, 0.065]:
        g = M.tier1_grid(m, city, "fixed", replace(base, gross_yield=y))
        sens["yield"].append([y, r((g[10].dropna() > 0).mean())])
    costs = [0.06, 0.10, 0.13] if city == "ES" else [0.003, 0.006, 0.02]
    for c in costs:
        g = M.tier1_grid(m, city, "fixed", replace(base, buy_cost=c))
        sens["buy_cost"].append([c, r((g[10].dropna() > 0).mean())])
    res[city]["sensitivity"] = sens

# long history, Spain, annual, real (deflated), 1950+
t2 = M.tier2_grid(jst)
res["tier2"] = {
    "winshare": {str(h): r((t2[h].dropna() > 0).mean()) for h in (5, 10, 15, 20, 25, 30) if h in t2},
    "n_starts": {str(h): int(t2[h].notna().sum()) for h in (5, 10, 15, 20, 25, 30) if h in t2},
    "by_start": {str(h): [[int(k), r(v)] for k, v in t2[h].dropna().items()] for h in (10, 20)},
    "breakeven_years": [[int(k), M.break_even(row)] for k, row in t2.iterrows()],
    "decades": {},
}
for dec in range(1950, 2020, 10):
    sub = t2.loc[dec:dec + 9]
    res["tier2"]["decades"][str(dec)] = {
        "winshare10": r((sub[10].dropna() > 0).mean()) if 10 in sub and sub[10].notna().any() else None,
        "median10": r(sub[10].median()) if 10 in sub and sub[10].notna().any() else None,
    }

# chart series (monthly, rebased where useful)
s = m.loc["2005-01":]
res["series"] = {
    "months": [str(i) for i in s.index],
    "hp_es": [r(v) for v in s["hp_es"] / s["hp_es"].iloc[0] * 100],
    "hp_sk": [r(v) for v in (s["hp_sk"] / s["hp_sk"].loc["2006-01"] * 100).where(s.index >= pd.Period("2006-01", "M"))],
    "rent_es": [r(v) for v in s["hicp_rent_es"] / s["hicp_rent_es"].iloc[0] * 100],
    "rent_sk": [r(v) for v in s["hicp_rent_sk"] / s["hicp_rent_sk"].iloc[0] * 100],
    "msci": [r(v) for v in s["msci_eur_tr"] / s["msci_eur_tr"].iloc[0] * 100],
    "euribor": [r(v) for v in s["euribor12m"]],
    "mir_es": [r(v) for v in s["mir_es"]],
    "mir_sk": [r(v) for v in s["mir_sk"]],
}
d = jst[jst.iso == "ESP"].set_index("year").loc[1950:2020]
res["series_long"] = {
    "years": [int(y) for y in d.index],
    "housing_capgain": [r(v) for v in d["housing_capgain"]],
    "eq_tr": [r(v) for v in d["eq_tr"]],
    "ltrate": [r(v) for v in d["ltrate"]],
    "rent_yield": [r(v) for v in d["housing_rent_yd"]],
}
# defaults for the advisor page: compound annual growth over the whole common window
cagr = lambda x, a, b: (x.loc[b] / x.loc[a]) ** (1 / ((b.year - a.year) + (b.month - a.month) / 12)) - 1
a, b = pd.Period("2006-01", "M"), pd.Period("2025-12", "M")
res["defaults"] = {
    "house_growth_ES": r(cagr(m["hp_es"], a, b)), "house_growth_SK": r(cagr(m["hp_sk"], m["hp_sk"].first_valid_index(), b)),
    "rent_growth_ES": r(cagr(m["hicp_rent_es"], a, b)), "rent_growth_SK": r(cagr(m["hicp_rent_sk"], a, b)),
    "equity_return": r(cagr(m["msci_eur_tr"], a, b)),
    "mortgage_rate_ES": r(m["mir_es"].iloc[-1] / 100), "mortgage_rate_SK": r(m["mir_sk"].iloc[-1] / 100),
    "last_month": str(m.index[-1]),
}
os.makedirs(os.path.join(ROOT, "site/data"), exist_ok=True)
json.dump(res, open(os.path.join(ROOT, "site/data/results.json"), "w"))
print(json.dumps(res["defaults"], indent=1))
for c in ("ES", "SK"):
    for rt in ("fixed", "variable"):
        print(c, rt, "win share by horizon", {k: v for k, v in res[c][rt]["winshare"].items() if k in ("3", "5", "10", "15")})
    print(c, "sensitivity", res[c]["sensitivity"])
print("tier2", res["tier2"]["winshare"], res["tier2"]["decades"])
