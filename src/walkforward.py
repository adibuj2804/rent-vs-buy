"""Vyhodnotenie poradcu na histórii: pre každý počiatočný rok XY model odpovie len z dát známych do XY.

Pre každý XY a horizont H:
  1. skutočný víťaz  = ktorý scenár mal po H rokoch väčší majetok (model.tier2_grid, skutočné dáta XY+1..XY+H),
  2. odpoveď modelu  = „kúpa“ / „prenájom“ vypočítaná z dát <= XY,
  3. porovnanie      = podiel rokov, v ktorých mal model pravdu (spolu so základnými stratégiami
                        „vždy kúpa“, „vždy prenájom“).

Modely:
  odhad2 – ten istý, ale polovica odhadu sa vracia k dlhodobému priemeru (MEAN_REVERSION).
  odhad  – „sústava malých modelov“ (poznámka 1B): z posledných L rokov histórie odhadne rast cien,
           rast nájmov a výnos akcií, nasimuluje oba scenáre s týmito konštantnými hodnotami a porovná.
  sieť   – neurónová sieť z webu, dostane tie isté odhadnuté vstupy (orezané na rozsah, v ktorom sa učila).
Nič z budúcnosti XY nevstupuje do odpovede (okrem parametrov siete – viď správa, kapitola o obmedzeniach).
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd

try:                                  # v notebooku sú tieto funkcie definované v bunke vyššie
    from model import simulate, tier2_grid, tier2_run, SPAIN
except ImportError:
    pass

LOOKBACK = 20                         # dĺžka okna histórie pre odhad (určená vopred, nelaďovaná na výsledkoch)
HORIZONS = (10, 20, 30)
MEAN_REVERSION = 0.5                  # druhý model: polovica odhadu sa vracia k dlhodobému priemeru (zvolené až po prvom behu, viď správa)
RATE_SPREAD = 0.015                   # marža hypotéky nad dlhodobou sadzbou (rovnako ako v tier2_grid)


def known_inputs(d: pd.DataFrame, year: int, lookback: int = LOOKBACK, shrink: float = 0.0) -> dict:
    """Odhady z dát <= year. d: ročná tabuľka s indexom year (stĺpce housing_capgain, housing_rent_yd, eq_tr, ltrate).

    shrink = 0: čistý priemer z posledných `lookback` rokov. shrink = w > 0: podiel w sa „vráti k dlhodobému
    priemeru“ (všetky roky v dátach až do `year`, od roku 1901) – ochrana proti extrapolácii boomu."""
    full = d.loc[:year]
    h = full.tail(lookback + 1)
    geo = lambda x: float(np.exp(np.log1p(x).mean()) - 1)

    def est(df):
        g = df["housing_capgain"].iloc[1:]
        r = (df["housing_rent_yd"] / df["housing_rent_yd"].shift(1) * (1 + df["housing_capgain"]) - 1).iloc[1:]
        return geo(g), max(geo(r), 0.0), geo(df["eq_tr"].iloc[1:])
    g, rent_g, eq = est(h)
    if shrink:
        g2, r2, e2 = est(full.dropna(subset=["housing_capgain", "housing_rent_yd", "eq_tr"]))
        g, rent_g, eq = [(1 - shrink) * a + shrink * b for a, b in ((g, g2), (rent_g, r2), (eq, e2))]
    return {
        "house_growth": g, "rent_growth": rent_g, "equity_return": eq,
        "gross_yield": float(h["housing_rent_yd"].iloc[-1]),
        "mortgage_rate": max(float(h["ltrate"].iloc[-1]) / 100 + RATE_SPREAD, 0.01),
    }


def advise_estimate(inp: dict, years: int, p=None) -> float:
    """Model „odhad“: výhoda kupujúceho po `years` rokoch pri konštantných odhadnutých hodnotách (> 0 = kúpa)."""
    from dataclasses import replace
    p = replace(p or SPAIN, gross_yield=inp["gross_yield"])
    n = years
    adv = simulate(np.full(n, inp["house_growth"]), np.full(n, inp["rent_growth"]),
                   np.full(n, inp["equity_return"]), np.full(n, inp["mortgage_rate"]), p, 1, n)
    return float(adv[-1])


# ------------------------------------------------------------------ neurónová sieť (numpy)
RANGES = {"gross_yield": (0.03, 0.07), "house_growth": (-0.02, 0.08), "rent_growth": (0.0, 0.06),
          "equity_return": (0.02, 0.10), "mortgage_rate": (0.015, 0.07)}


def load_net(path_or_dict):
    w = path_or_dict if isinstance(path_or_dict, dict) else json.load(open(path_or_dict))
    return {k: (np.array(v) if k in ("mu", "sd") else v) for k, v in w.items()}


def advise_net(net: dict, inp: dict, years: int, p=None):
    """Vráti (P(kúpa vyhráva), počet vstupov, ktoré bolo treba orezať na tréningový rozsah)."""
    p = p or SPAIN
    clipped = 0
    v = {}
    for k, (lo, hi) in RANGES.items():
        v[k] = min(max(inp[k], lo), hi)
        clipped += v[k] != inp[k]
    x = np.array([0, years, p.ltv, v["gross_yield"], p.buy_cost, v["house_growth"], v["rent_growth"],
                  v["equity_return"], v["mortgage_rate"]], float)
    a = (x - net["mu"]) / net["sd"]
    for i, L in enumerate(net["layers"]):
        a = a @ np.array(L["W"]) + np.array(L["b"])
        if i < len(net["layers"]) - 1:
            a = np.maximum(a, 0)
    return float(1 / (1 + np.exp(-a[0]))), int(clipped)


# ------------------------------------------------------------------ vyhodnotenie
def evaluate(annual: pd.DataFrame, net: dict | None = None, horizons=HORIZONS, first=1950, lookback=LOOKBACK):
    """annual: tabuľka ako spain_annual_1870_2025.csv. Vracia DataFrame: jeden riadok na (rok, horizont)."""
    actual = tier2_grid(annual, start_from=first, max_years=max(horizons))
    d = annual.set_index("year").sort_index()
    rows = []
    for H in horizons:
        for y in actual.index:
            if H not in actual.columns or pd.isna(actual.loc[y, H]):
                continue
            inp = known_inputs(d, int(y), lookback)
            adv_est = advise_estimate(inp, H)
            adv_mr = advise_estimate(known_inputs(d, int(y), lookback, MEAN_REVERSION), H)
            row = {"start": int(y), "H": H, "actual_adv": float(actual.loc[y, H]), "buy_won": bool(actual.loc[y, H] > 0),
                   "est_adv": adv_est, "est_buy": adv_est > 0, "mr_adv": adv_mr, "mr_buy": adv_mr > 0, **{"in_" + k: v for k, v in inp.items()}}
            if net is not None:
                pb, clipped = advise_net(net, inp, H)
                row.update(net_p=pb, net_buy=pb > 0.5, net_clipped=clipped)
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(ev: pd.DataFrame) -> dict:
    out = {}
    for H, g in ev.groupby("H"):
        s = {"n_years": int(len(g)), "first": int(g.start.min()), "last": int(g.start.max()),
             "buy_won_share": float(g.buy_won.mean()),
             "always_buy": float(g.buy_won.mean()), "always_rent": float(1 - g.buy_won.mean()),
             "estimate": float((g.est_buy == g.buy_won).mean()),
             "mean_reversion": float((g.mr_buy == g.buy_won).mean())}
        if "net_buy" in g:
            s["net"] = float((g.net_buy == g.buy_won).mean())
            ind = g[g.net_clipped == 0]
            s["net_in_domain"] = {"n": int(len(ind)), "acc": float((ind.net_buy == ind.buy_won).mean()) if len(ind) else None}
        for a, b, nm in ((1950, 1979, "1950-79"), (1980, 1999, "1980-99"), (2000, 2020, "2000+")):
            k = g[(g.start >= a) & (g.start <= b)]
            if len(k):
                s.setdefault("by_period", {})[nm] = {"n": int(len(k)), "buy_won": float(k.buy_won.mean()),
                                                     "estimate": float((k.est_buy == k.buy_won).mean()),
                                                     "mean_reversion": float((k.mr_buy == k.buy_won).mean())}
        out[int(H)] = s
    return out


# ------------------------------------------------------------------ majetok v oboch scenároch pre zvolený rok
def scenario_wealth(annual: pd.DataFrame, start: int, horizon: int, price: float = 250_000, p=None) -> dict:
    """Majetok oboch domácností po `horizon` rokoch pre nákup v roku `start` (skutočné dáta), v eurách.

    nominal = v eurách roku start+horizon, real = v eurách roku `start` (po odpočítaní inflácie)."""
    buyer, renter, adv, defl = tier2_run(annual, start, horizon, parts=True, p=p)
    f = lambda x: float(x[-1] * price)
    return {"start": start, "horizon": horizon, "price": price,
            "nominal": {"hypoteka": f(buyer), "prenajom": f(renter), "rozdiel": f(adv)},
            "real": {"hypoteka": f(buyer / defl), "prenajom": f(renter / defl), "rozdiel": f(adv / defl)},
            "winner": "hypotéka" if adv[-1] > 0 else "prenájom"}


def advice_today(annual: pd.DataFrame, net: dict | None, years: int, year: int | None = None, overrides: dict | None = None) -> dict:
    """Rada pre dnešok: odhady z posledných LOOKBACK rokov (alebo vlastné `overrides`) -> obe odpovede."""
    d = annual.set_index("year").sort_index()
    inp = known_inputs(d, int(year or d.index.max()))
    inp.update(overrides or {})
    adv = advise_estimate(inp, years)
    out = {"inputs": inp, "years": years, "estimate_adv": adv, "estimate_answer": "hypotéka" if adv > 0 else "prenájom"}
    if net is not None:
        pb, clipped = advise_net(net, inp, years)
        out.update(net_p_buy=pb, net_answer="hypotéka" if pb > 0.5 else "prenájom", net_clipped_inputs=clipped)
    return out
