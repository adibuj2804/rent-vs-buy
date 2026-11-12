"""Natrénuje neurónovú sieť poradcu na simulovaných scenároch označených presným modelom.

Prečo simulácia: ~20 rokov lokálnej histórie dáva len pár nezávislých výsledkov „kúpa vs. prenájom“,
čo je pre sieť príliš málo. Preto:
  1. z histórie odmeriame vierohodné rozsahy a volatility každého vstupu,
  2. z týchto rozsahov vylosujeme desaťtisíce scenárov,
  3. k *realizovanému* priebehu pridáme šum historickej veľkosti (domácnosť pozná len očakávania),
  4. každý scenár označíme presným modelom (src/model.py) -> „vyhrala kúpa?“,
  5. natrénujeme malú sieť MLP (čisté numpy, bez ML knižnice) na P(kúpa vyhráva) a rozdiel majetku.
Váhy sa exportujú do JSON a web robí rovnaký dopredný prechod v JavaScripte.
"""
import json, os
import numpy as np
import pandas as pd
import model as M

ROOT = os.path.join(os.path.dirname(__file__), "..")
rng = np.random.default_rng(42)

GAP_SCALE = 1.5   # cieľ „rozdiel majetku“ sa orezáva na ±1,5× ceny a delí touto hodnotou
FEATURES = ["city_SK", "years", "ltv", "gross_yield", "buy_cost", "house_growth",
            "rent_growth", "equity_return", "mortgage_rate"]


# ---- 1. čo hovorí história o volatilite (pre šum na realizovaných priebehoch) -------------
m = pd.read_csv(os.path.join(ROOT, "data/processed/monthly_2003_2025.csv"), index_col=0)
def annual_sd(series, months=12):
    r = (series.shift(-months) / series - 1).dropna()
    return float(r.std())
SD_HOUSE = np.mean([annual_sd(m["hp_es"]), annual_sd(m["hp_sk"])])
SD_EQ = annual_sd(m["msci_eur_tr"])
SD_RATE = 0.012   # smerodajná odchýlka zmien Euriboru za desaťročie, zaokrúhlená
print(f"historical annual sd  house={SD_HOUSE:.3f}  equity={SD_EQ:.3f}")


# ---- 2/3/4. scenáre + označenie ------------------------------------------------------------
def make(n):
    city = rng.integers(0, 2, n)                     # 0 = Španielsko/Málaga, 1 = Slovensko/Bratislava
    years = rng.integers(2, 31, n)
    ltv = rng.uniform(0.5, 0.9, n)
    yld = rng.uniform(0.03, 0.07, n)
    buy_cost = np.where(city == 0, rng.uniform(0.055, 0.13, n), rng.uniform(0.003, 0.02, n))
    house_g = rng.uniform(-0.02, 0.08, n)
    rent_g = np.clip(house_g * rng.uniform(0.3, 1.0, n) + rng.uniform(0, 0.02, n), 0, 0.06)
    eq = rng.uniform(0.02, 0.10, n)
    rate = rng.uniform(0.015, 0.07, n)
    X = np.c_[city, years, ltv, yld, buy_cost, house_g, rent_g, eq, rate]

    # realizovaný výsledok = očakávanie + šum, ktorý s horizontom klesá (sd/sqrt(roky))
    z1, z2 = rng.standard_normal(n), rng.standard_normal(n)
    corr = 0.3
    g_real = house_g + SD_HOUSE / np.sqrt(years) * z1
    e_real = eq + SD_EQ / np.sqrt(years) * (corr * z1 + np.sqrt(1 - corr ** 2) * z2)
    r_real = np.clip(rent_g + 0.5 * (g_real - house_g), 0, None)

    sk = city == 1
    pick = lambda a, b: np.where(sk, b, a)
    P, S = M.SPAIN, M.SLOVAKIA
    args = dict(
        ltv=ltv, buy_cost=buy_cost,
        sell_cost=pick(P.sell_cost, S.sell_cost), upkeep=pick(P.upkeep, S.upkeep),
        gross_yield=yld, term_years=pick(P.term_years, S.term_years).astype(float),
        invest_tax=pick(P.invest_tax, S.invest_tax),
        inv_free_after=pick(0, 12).astype(float),
        home_tax=pick(P.home_gain_tax, S.home_gain_tax),
        home_free_after=pick(0, 60).astype(float),
    )
    adv_noisy = M.simulate_batch(g_real, r_real, e_real, rate, years=years, **args)
    adv_exact = M.simulate_batch(house_g, rent_g, eq, rate, years=years, **args)
    return X, adv_noisy, adv_exact


# ---- 5. malá sieť MLP v numpy -----------------------------------------------------------
def init(sizes):
    return [(rng.standard_normal((a, b)) * np.sqrt(2 / a), np.zeros(b)) for a, b in zip(sizes[:-1], sizes[1:])]

def forward(params, X):
    acts = [X]
    for i, (W, b) in enumerate(params):
        z = acts[-1] @ W + b
        acts.append(np.maximum(z, 0) if i < len(params) - 1 else z)
    return acts

def train(Xtr, ytr, ctr, epochs=120, lr=2e-3, batch=512, hidden=(64, 64)):
    params = init([Xtr.shape[1], *hidden, 2])
    m_ = [[np.zeros_like(W), np.zeros_like(b)] for W, b in params]
    v_ = [[np.zeros_like(W), np.zeros_like(b)] for W, b in params]
    t = 0
    for ep in range(epochs):
        order = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            idx = order[s:s + batch]
            x, yc, yr = Xtr[idx], ctr[idx], ytr[idx]
            acts = forward(params, x)
            out = acts[-1]
            p = 1 / (1 + np.exp(-out[:, 0]))
            # strata = BCE(výhra) + 0.5*MSE(škálovaný rozdiel majetku)
            d = np.c_[(p - yc) / len(idx), 0.5 * 2 * (out[:, 1] - yr) / len(idx)]
            t += 1
            for i in reversed(range(len(params))):
                W, b = params[i]
                gW, gb = acts[i].T @ d, d.sum(0)
                if i > 0:
                    d = (d @ W.T) * (acts[i] > 0)
                for k, (g_, P_) in enumerate([(gW, 0), (gb, 1)]):
                    mm = m_[i][k] = 0.9 * m_[i][k] + 0.1 * g_
                    vv = v_[i][k] = 0.999 * v_[i][k] + 0.001 * g_ ** 2
                    upd = lr * (mm / (1 - 0.9 ** t)) / (np.sqrt(vv / (1 - 0.999 ** t)) + 1e-8)
                    (W if k == 0 else b)[...] -= upd
        if ep % 10 == 9:
            print(f"  epoch {ep+1}/{epochs}")
    return params


if __name__ == "__main__":
    N = 120_000
    X, adv_n, adv_e = make(N)
    y_win = (adv_n > 0).astype(float)
    y_gap = np.clip(adv_e, -GAP_SCALE, GAP_SCALE) / GAP_SCALE                # regresný cieľ: rozdiel pri zadaných predpokladoch (bez šumu)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xn = (X - mu) / sd
    cut = int(0.85 * N)
    params = train(Xn[:cut], y_gap[:cut], y_win[:cut])
    out = forward(params, Xn[cut:])[-1]
    p = 1 / (1 + np.exp(-out[:, 0]))
    acc = ((p > 0.5) == (y_win[cut:] > 0.5)).mean()
    brier = ((p - y_win[cut:]) ** 2).mean()
    # ako často sa sieť zhoduje s *presným modelom očakávaných hodnôt*?
    agree = ((p > 0.5) == (adv_e[cut:] > 0)).mean()
    gap_err = np.abs(out[:, 1] * GAP_SCALE - np.clip(adv_e[cut:], -GAP_SCALE, GAP_SCALE))
    print(f"gap head: median abs error {np.median(gap_err):.3f} of price, 90th pct {np.percentile(gap_err, 90):.3f}")
    base = max(y_win[cut:].mean(), 1 - y_win[cut:].mean())
    print(f"hold-out accuracy {acc:.3f} (majority baseline {base:.3f}); Brier {brier:.3f}; "
          f"agreement with deterministic exact model {agree:.3f}")
    # tabuľka kalibrácie
    bins = np.linspace(0, 1, 11)
    cal = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        k = (p >= lo) & (p < hi + (hi == 1))
        if k.sum() > 50:
            cal.append({"bin": f"{lo:.1f}-{hi:.1f}", "predicted": float(p[k].mean()),
                        "observed": float(y_win[cut:][k].mean()), "n": int(k.sum())})
    os.makedirs(os.path.join(ROOT, "site/model"), exist_ok=True)
    json.dump({
        "features": FEATURES, "gapScale": GAP_SCALE, "mu": mu.tolist(), "sd": sd.tolist(),
        "layers": [{"W": W.round(6).tolist(), "b": b.round(6).tolist()} for W, b in params],
        "metrics": {"holdout_accuracy": float(acc), "majority_baseline": float(base),
                    "brier": float(brier), "gap_mae_median": float(np.median(gap_err)), "gap_mae_p90": float(np.percentile(gap_err, 90)), "agreement_with_exact": float(agree),
                    "n_train": int(cut), "n_test": int(N - cut),
                    "sd_house": SD_HOUSE, "sd_equity": SD_EQ},
        "calibration": cal,
    }, open(os.path.join(ROOT, "site/model/nn_weights.json"), "w"))
    print("saved site/model/nn_weights.json")
