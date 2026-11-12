"""Predĺži ročný španielsky rad JST (končí 2020) do roku 2025 z mesačných dát projektu.

Výstup: data/processed/spain_annual_1870_2025.csv so stĺpcom `source` ("JST" / "extension").
Rozšírenie je len približné a je tak označené:
  * ceny bytov  = ročný priemer indexu BIS pre Španielsko (JST rovnako používa ročné priemery),
  * nájom       = ročný priemer HICP „skutočné nájmy“; výnos z nájmu = predošlý výnos × rast nájmu / rast cien,
  * akcie       = MSCI World v EUR + 2 % dividend (JST má španielske akcie, tu je svetový index!),
  * dlhodobá sadzba = ECB 10-ročný výnos španielskych dlhopisov (rovnaký typ ako JST, v roku 2015–2020 sedí),
  * CPI         = ročný priemer HICP Španielsko, napojený na JST.
"""
import os
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
P = os.path.join(ROOT, "data", "processed")

jst = pd.read_csv(os.path.join(P, "jst_annual_1870_2020.csv"))
esp = jst[jst.iso == "ESP"].set_index("year").sort_index()
m = pd.read_csv(os.path.join(P, "monthly_2003_2025.csv"), index_col=0)
m.index = pd.PeriodIndex(m.index, freq="M")
avg = m.groupby(m.index.year)[["hp_es", "hicp_es", "hicp_rent_es"]].mean()
dec = m[m.index.month == 12].set_index(m[m.index.month == 12].index.year)["msci_eur_tr"]
lt = pd.read_csv(os.path.join(ROOT, "data", "raw", "ltrate_es_ecb.csv"))
lt = lt.groupby(lt.TIME_PERIOD.str[:4].astype(int)).OBS_VALUE.mean()

rows = []
last = esp.loc[2020]
cpi, ry = last["cpi"], last["housing_rent_yd"]
for y in range(2021, 2026):
    g = avg.hp_es[y] / avg.hp_es[y - 1] - 1
    rg = avg.hicp_rent_es[y] / avg.hicp_rent_es[y - 1] - 1
    ry = ry * (1 + rg) / (1 + g)
    cpi = cpi * avg.hicp_es[y] / avg.hicp_es[y - 1]
    rows.append({"year": y, "iso": "ESP", "cpi": cpi, "ltrate": lt[y], "housing_capgain": g,
                 "housing_rent_yd": ry, "eq_tr": dec[y] / dec[y - 1] - 1, "source": "extension"})
base = esp.reset_index()[["year", "iso", "cpi", "ltrate", "housing_capgain", "housing_rent_yd", "eq_tr"]]
base["source"] = "JST"
out = pd.concat([base, pd.DataFrame(rows)], ignore_index=True)
out.to_csv(os.path.join(P, "spain_annual_1870_2025.csv"), index=False)
print(out.tail(7).round(4).to_string())
