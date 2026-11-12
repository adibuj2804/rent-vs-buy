"""Kúpa s hypotékou vs. prenájom a investovanie: jeden výpočtový model pre obe úrovne.

Pravidlo férovosti: obe domácnosti míňajú v každom období rovnako. Kto má v danom období
lacnejšie bývanie, rozdiel investuje do rovnakého akciového indexu. Pre každý horizont h obe
domácnosti „speňažíme“ a porovnáme čistý majetok:

    kupujúci = predajná cena - náklady na predaj - zostatok hypotéky + jeho portfólio (po zdanení)
    nájomník = portfólio (po zdanení)

    výhoda = kupujúci - nájomník      (> 0  ->  kúpa vyhráva)

Všetko je vyjadrené na 1,0 kúpnej ceny, takže výsledok nezávisí od výšky ceny.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Params:
    ltv: float = 0.80            # pomer úveru k cene (LTV)
    buy_cost: float = 0.10       # dane a poplatky pri kúpe (podiel ceny)
    sell_cost: float = 0.04      # makléri + miestne dane pri predaji (podiel ceny)
    upkeep: float = 0.012        # údržba + daň z nehnuteľnosti + poistenie, ročne, z aktuálnej hodnoty
    gross_yield: float = 0.05    # nájom v 1. roku / cena
    term_years: int = 25
    spread: float = 0.0          # variabilné úvery: Euribor + marža (určená pri čerpaní)
    invest_tax: float = 0.21     # daň zo zisku portfólia pri speňažení
    invest_tax_free_after: int = 0  # po koľkých obdobiach je zisk z portfólia bez dane (0 = nikdy)
    home_gain_tax: float = 0.0   # daň zo zisku z predaja bytu (v Španielsku sa predpokladá úľava na hlavné bývanie)
    home_gain_tax_free_after: int = 0  # po koľkých obdobiach je zisk z bytu oslobodený od dane (SK: 5 rokov)


SPAIN = Params()
SLOVAKIA = Params(
    buy_cost=0.006,          # poplatok katastru + právnik; bez dane z prevodu od 2005
    sell_cost=0.03,          # provízia makléra
    upkeep=0.0105,           # údržba ≈ 1 % + veľmi nízka daň z nehnuteľnosti
    gross_yield=0.045,
    term_years=30,
    invest_tax=0.0,          # zisky z ETF bez dane po viac ako 1 roku ...
    home_gain_tax=0.19,      # ... zisk z bytu zdanený 19 % pri predaji do 5 rokov
)


def annuity(rate_per_period: float, n: int) -> float:
    """Splátka na 1,0 úveru."""
    if abs(rate_per_period) < 1e-12:
        return 1.0 / n
    return rate_per_period / (1 - (1 + rate_per_period) ** -n)


def simulate(price_g, rent_g, eq_r, mort_rate_path, p: Params, ppy: int, horizon: int):
    """Simuluje jeden dátum nákupu na `horizon` období.

    price_g, rent_g, eq_r : rast cien / nájmov / výnos investície za obdobie (desatinné čísla)
    mort_rate_path        : ROČNÁ sadzba hypotéky v každom období (pri fixnej konštantná)
    Vracia pole adv[1..horizon] = majetok kupujúceho - nájomníka (na 1,0 ceny).
    """
    n_total = p.term_years * ppy
    price = 1.0
    rent = p.gross_yield / ppy
    loan = p.ltv * 1.0
    bal = loan
    pay_n_left = n_total
    # počiatočná hotovosť: akontácia + náklady na kúpu idú do portfólia nájomníka
    renter = (1 - p.ltv) + p.buy_cost
    renter_contrib = renter
    buyer_port = 0.0
    buyer_contrib = 0.0
    adv = np.zeros(horizon)
    prices = [1.0]
    for t in range(horizon):
        r_per = mort_rate_path[t] / ppy
        pay = annuity(r_per, pay_n_left) * bal if bal > 1e-12 else 0.0
        interest = bal * r_per
        bal = max(bal - (pay - interest), 0.0)
        pay_n_left = max(pay_n_left - 1, 1)
        buy_out = pay + p.upkeep / ppy * price
        rent_out = rent
        diff = buy_out - rent_out
        # najprv rast existujúcich portfólií, potom nový vklad na konci obdobia
        renter *= 1 + eq_r[t]
        buyer_port *= 1 + eq_r[t]
        if diff > 0:               # kúpa stojí viac hotovosti -> nájomník investuje rozdiel
            renter += diff
            renter_contrib += diff
        else:                      # prenájom stojí viac hotovosti -> rozdiel investuje kupujúci
            buyer_port += -diff
            buyer_contrib += -diff
        price *= 1 + price_g[t]
        rent *= 1 + rent_g[t]
        periods = t + 1
        # hodnoty po speňažení
        tax_free = p.invest_tax_free_after and periods > p.invest_tax_free_after
        tr = 0.0 if tax_free else p.invest_tax
        r_net = renter - tr * max(renter - renter_contrib, 0)
        b_net = buyer_port - tr * max(buyer_port - buyer_contrib, 0)
        home_tax_free = p.home_gain_tax_free_after and periods > p.home_gain_tax_free_after
        hg = 0.0 if home_tax_free else p.home_gain_tax
        gain = max(price - 1.0, 0)
        home_net = price * (1 - p.sell_cost) - hg * gain - bal
        adv[t] = home_net + b_net - r_net
    return adv


def slovakia_flags(p: Params, ppy: int) -> Params:
    """SK: zisky z ETF bez dane po 1 roku; zisk z bytu bez dane po 5 rokoch."""
    return replace(p, invest_tax_free_after=ppy, home_gain_tax_free_after=5 * ppy)


# ---------------------------------------------------------------- úroveň 1 (mesačne)
def tier1_grid(monthly: pd.DataFrame, city: str, rate_type: str, p: Params | None = None,
               max_years: int = 20, start_from: str | None = None):
    """Spätný test pre každý mesiac nákupu. Riadky = mesiac nákupu, stĺpce = horizont v rokoch."""
    if city == "ES":
        hp, hicp_rent, mir = monthly["hp_es"], monthly["hicp_rent_es"], monthly["mir_es"]
        p = p or SPAIN
        start_from = start_from or "2005-01"
    else:
        hp, hicp_rent, mir = monthly["hp_sk"], monthly["hicp_rent_sk"], monthly["mir_sk"]
        p = slovakia_flags(p or SLOVAKIA, 12)
        start_from = start_from or "2008-01"
    eq = monthly["msci_eur_tr"]
    ph = hp.pct_change().shift(-1)           # rast z t na t+1
    rg = hicp_rent.pct_change().shift(-1)
    er = eq.pct_change().shift(-1)
    idx = monthly.index
    out = {}
    for i, m in enumerate(idx):
        if m < pd.Period(start_from, "M"):
            continue
        H = min(max_years * 12, len(idx) - i - 1)
        if H < 12:
            break
        rate0 = mir.iloc[i] / 100
        if rate_type == "fixed":
            path = np.full(H, rate0)
        else:
            spread = rate0 - monthly["euribor12m"].iloc[i] / 100
            path = np.clip(monthly["euribor12m"].iloc[i:i + H].values / 100 + spread, 0.005, None)
        adv = simulate(ph.iloc[i:i + H].values, rg.iloc[i:i + H].values, er.iloc[i:i + H].values,
                       path, p, 12, H)
        out[m] = {y: adv[y * 12 - 1] for y in range(1, max_years + 1) if y * 12 <= H}
    return pd.DataFrame(out).T


# ---------------------------------------------------------------- úroveň 2 (ročne, JST)
def tier2_grid(jst: pd.DataFrame, iso: str = "ESP", p: Params | None = None,
               start_from: int = 1950, max_years: int = 30, rate_spread: float = 0.015):
    """Ročný spätný test od `start_from` na národných dátach JST (nominálne, v miestnej mene)."""
    d = jst[jst.iso == iso].set_index("year").sort_index()
    p = p or SPAIN
    # rast cien bytov: JST rad kapitálových ziskov
    g = d["housing_capgain"]
    ry = d["housing_rent_yd"]            # nájom / cena (JST)
    rate = (d["ltrate"] / 100 + rate_spread).clip(lower=0.01)
    eq = d["eq_tr"]
    cols = pd.concat([g, ry, rate, eq], axis=1, keys=["g", "ry", "rate", "eq"]).dropna()
    years = cols.index.values
    out = {}
    for i, y in enumerate(years):
        if y < start_from:
            continue
        H = min(max_years, len(years) - i - 1)
        if H < 5:
            break
        # rent grows with house prices times yield drift: rent_t = yield_t * price_t
        P = np.r_[1.0, np.cumprod(1 + cols["g"].values[i + 1:i + H + 1])]   # cena na začiatku roka k
        rent_path = cols["ry"].values[i:i + H + 1] * P                       # nájom_k = výnos_k * cena_k
        rg = rent_path[1:] / rent_path[:-1] - 1
        pp = replace(p, gross_yield=cols["ry"].values[i])
        adv = simulate(cols["g"].values[i + 1:i + H + 1], rg, cols["eq"].values[i + 1:i + H + 1],
                       np.full(H, cols["rate"].values[i]), pp, 1, H)
        # prepočet na peniaze východiskového roku, aby boli desaťročia s vysokou infláciou porovnateľné
        cpi = d["cpi"].reindex(years).values
        out[int(y)] = {h: adv[h - 1] / (cpi[i + h] / cpi[i]) for h in range(1, H + 1)}
    return pd.DataFrame(out).T


def break_even(row: pd.Series):
    """Prvý horizont, od ktorého kúpa ostáva vpredu (None, ak nikdy)."""
    ok = row.dropna()
    wins = ok > 0
    for h in ok.index:
        if wins.loc[h:].all():
            return h
    return None


# ---------------------------------------------------------------- vektorizovaný model (pre sieť)
def simulate_batch(g, rg, eq, rate, ltv, buy_cost, sell_cost, upkeep, gross_yield, term_years,
                   invest_tax, inv_free_after, home_tax, home_free_after, years):
    """Rovnaká ekonomika ako `simulate`, mesačne, konštantné ročné sadzby, pre N scenárov naraz.

    Všetky argumenty sú polia tvaru (N,). `years` je horizont v rokoch; vracia výhodu
    (kupujúci - nájomník) na 1,0 ceny v danom horizonte.
    """
    N = len(g)
    gm = (1 + g) ** (1 / 12) - 1
    rgm = (1 + rg) ** (1 / 12) - 1
    em = (1 + eq) ** (1 / 12) - 1
    r = rate / 12
    n_left = (term_years * 12).astype(float)
    price = np.ones(N)
    rent = gross_yield / 12
    bal = ltv.copy()
    renter = (1 - ltv) + buy_cost
    renter_c = renter.copy()
    bport = np.zeros(N)
    bport_c = np.zeros(N)
    H = (years * 12).astype(int)
    result = np.zeros(N)
    for t in range(int(H.max())):
        # anuitná splátka zo zostatku
        pay = np.where(np.abs(r) < 1e-12, 1.0 / n_left, r / (1 - (1 + r) ** (-n_left))) * bal
        interest = bal * r
        bal = np.maximum(bal - (pay - interest), 0)
        n_left = np.maximum(n_left - 1, 1)
        diff = pay + upkeep / 12 * price - rent
        renter = renter * (1 + em)
        bport = bport * (1 + em)
        pos = diff > 0
        renter = renter + np.where(pos, diff, 0)
        renter_c = renter_c + np.where(pos, diff, 0)
        bport = bport + np.where(pos, 0, -diff)
        bport_c = bport_c + np.where(pos, 0, -diff)
        price = price * (1 + gm)
        rent = rent * (1 + rgm)
        done = (H == t + 1)
        if done.any():
            per = t + 1
            tr = np.where((inv_free_after > 0) & (per > inv_free_after), 0.0, invest_tax)
            hg = np.where((home_free_after > 0) & (per > home_free_after), 0.0, home_tax)
            r_net = renter - tr * np.maximum(renter - renter_c, 0)
            b_net = bport - tr * np.maximum(bport - bport_c, 0)
            home_net = price * (1 - sell_cost) - hg * np.maximum(price - 1, 0) - bal
            result = np.where(done, home_net + b_net - r_net, result)
    return result
