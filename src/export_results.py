"""Run the back-tests + sensitivity checks and write site/data/results.json."""
import json, os
from dataclasses import replace
import numpy as np
import pandas as pd
import model as M

ROOT = os.path.join(os.path.dirname(__file__), "..")
m = pd.read_csv(os.path.join(ROOT, "data/processed/monthly_2003_2025.csv"), index_col=0)
m.index = pd.PeriodIndex(m.index, freq="M")
jst = pd.read_csv(os.path.join(ROOT, "data/processed/spain_annual_1870_2025.csv"))

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

# porovnanie pre Slovensko: celoštátny index BIS namiesto cien Bratislavského kraja (NBS)
res["SK_national"] = {}
for rt in ["fixed", "variable"]:
    g = M.tier1_grid(m, "SK", rt, sk_prices="hp_sk")
    res["SK_national"][rt] = {
        "winshare": {str(y): r((g[y].dropna() > 0).mean()) for y in g.columns if g[y].notna().sum()},
        "n_starts": {str(y): int(g[y].notna().sum()) for y in g.columns if g[y].notna().sum()},
    }

# porovnanie: rovnaký model, ale s celoštátnym španielskym indexom BIS namiesto cien pre Málagu
res["ES_national"] = {}
for rt in ["fixed", "variable"]:
    g = M.tier1_grid(m, "ES", rt, es_prices="hp_es")
    res["ES_national"][rt] = {
        "winshare": {str(y): r((g[y].dropna() > 0).mean()) for y in g.columns if g[y].notna().sum()},
        "n_starts": {str(y): int(g[y].notna().sum()) for y in g.columns if g[y].notna().sum()},
    }

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
    "hp_ma": [r(v) for v in s["hp_ma"] / s["hp_ma"].loc["2005-03"] * 100],
    "hp_ma_eur_m2": [r(v) for v in s["hp_ma"]],
    "hp_ba": [r(v) for v in (s["hp_ba"] / s["hp_ba"].loc["2006-03"] * 100).where(s.index >= pd.Period("2006-03", "M"))],
    "hp_ba_eur_m2": [r(v) for v in s["hp_ba"]],
    "hp_sk": [r(v) for v in (s["hp_sk"] / s["hp_sk"].loc["2006-01"] * 100).where(s.index >= pd.Period("2006-01", "M"))],
    "rent_es": [r(v) for v in s["hicp_rent_es"] / s["hicp_rent_es"].iloc[0] * 100],
    "rent_sk": [r(v) for v in s["hicp_rent_sk"] / s["hicp_rent_sk"].iloc[0] * 100],
    "msci": [r(v) for v in s["msci_eur_tr"] / s["msci_eur_tr"].iloc[0] * 100],
    "euribor": [r(v) for v in s["euribor12m"]],
    "mir_es": [r(v) for v in s["mir_es"]],
    "mir_sk": [r(v) for v in s["mir_sk"]],
}
d = jst[jst.iso == "ESP"].set_index("year").loc[1950:2025]
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
    "house_growth_ES": r(cagr(m["hp_ma"], a, b)), "house_growth_ES_national": r(cagr(m["hp_es"], a, b)), "house_growth_SK": r(cagr(m["hp_ba"], a, b)), "house_growth_SK_national": r(cagr(m["hp_sk"], m["hp_sk"].first_valid_index(), b)),
    "rent_growth_ES": r(cagr(m["hicp_rent_es"], a, b)), "rent_growth_SK": r(cagr(m["hicp_rent_sk"], a, b)),
    "equity_return": r(cagr(m["msci_eur_tr"], a, b)),
    "mortgage_rate_ES": r(m["mir_es"].iloc[-1] / 100), "mortgage_rate_SK": r(m["mir_sk"].iloc[-1] / 100),
    "last_month": str(m.index[-1]),
}
hm = m["hp_ma"].dropna()
pk = hm.loc[:"2012"].idxmax(); tr = hm.loc[pk:"2018"].idxmin()
q = pd.read_csv(os.path.join(ROOT, "data/processed/malaga_valor_tasado_quarterly.csv"))
v23 = q[q.period.str.startswith("2023")].total.mean()
res["malaga_facts"] = {
    "first": [str(hm.index[0]), r(hm.iloc[0])], "last_quarter": [q.period.iloc[-1], r(q.total.iloc[-1])],
    "peak": [str(pk), r(hm[pk])], "trough": [str(tr), r(hm[tr])], "peak_to_trough": r(hm[tr] / hm[pk] - 1),
    "valor_tasado_2023": r(v23), "implied_yield_2023": r(8.9 * 12 / v23),   # 8,9 EUR/m2 = SERPAVI 2023 podľa rešerše
}
qb = pd.read_csv(os.path.join(ROOT, "data/processed/bratislava_nbs_quarterly.csv"))
hb = m["hp_ba"].dropna()
pk2 = hb.loc[:"2023"].idxmax(); tr2 = hb.loc[pk2:"2025"].idxmin()
pk1 = hb.loc[:"2012"].idxmax(); tr1 = hb.loc[pk1:"2018"].idxmin()
res["bratislava_facts"] = {
    "first": [qb.period.iloc[0], r(qb.ba.iloc[0])], "last_quarter": [qb.period.iloc[-1], r(qb.ba.iloc[-1])],
    "peak1": [str(pk1), r(hb[pk1])], "trough1": [str(tr1), r(hb[tr1])],      # povojnový cyklus 2008–2013
    "peak2": [str(pk2), r(hb[pk2])], "trough2": [str(tr2), r(hb[tr2])], "peak2_to_trough2": r(hb[tr2] / hb[pk2] - 1),  # šok sadzieb 2022–2024
    "q4_2025": r(qb[qb.period == "2025-Q4"].ba.iloc[0]),
    # nájom z rešerše (ponukový, vrátane energií): Bencont 17,37 EUR/m2 a realitymap 15,7 EUR/m2 mesačne
    "yield_bencont": r(17.37 * 12 / qb[qb.period == "2025-Q4"].ba.iloc[0]), "yield_realitymap": r(15.7 * 12 / qb[qb.period == "2025-Q4"].ba.iloc[0]),
}

# vyhodnotenie poradcu na histórii (zadanie, časť 4): odpoveď len z dát <= XY vs. skutočný víťaz
import walkforward as W
net = W.load_net(os.path.join(ROOT, "site/model/nn_weights.json"))
annual = pd.read_csv(os.path.join(ROOT, "data/processed/spain_annual_1870_2025.csv"))
ev = W.evaluate(annual, net)
sens = {str(L): W.summarize(W.evaluate(annual, None, lookback=L)) for L in (10, 20, 30)}
res["walkforward"] = {
    "lookback": W.LOOKBACK, "summary": W.summarize(ev),
    "lookback_sensitivity": {L: {H: v["estimate"] for H, v in s_.items()} for L, s_ in sens.items()},
    "rows": {str(H): [[int(r.start), bool(r.buy_won), bool(r.est_buy), bool(r.net_buy), int(r.net_clipped), bool(r.mr_buy),
                       round(float(r.actual_adv), 3)] for r in g.itertuples()] for H, g in ev.groupby("H")},
}
ev.to_csv(os.path.join(ROOT, "data/processed/walkforward_spain.csv"), index=False)
os.makedirs(os.path.join(ROOT, "site/data"), exist_ok=True)
json.dump(res, open(os.path.join(ROOT, "site/data/results.json"), "w"))
print(json.dumps(res["defaults"], indent=1))
for c in ("ES", "SK"):
    for rt in ("fixed", "variable"):
        print(c, rt, "win share by horizon", {k: v for k, v in res[c][rt]["winshare"].items() if k in ("3", "5", "10", "15")})
    print(c, "sensitivity", res[c]["sensitivity"])
print("tier2", res["tier2"]["winshare"], res["tier2"]["decades"])
