"""Zmení surové stiahnuté dáta (data/raw) na čisté mesačné / ročné tabuľky (data/processed).

Zdroj každého radu je v data/SOURCES.md. Nič tu nie je vymyslené: kde rad vyžaduje predpoklad
(dividendy MSCI), je pomenovanou konštantou.
"""
import csv, json, datetime, os
import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

MSCI_NET_DIVIDEND_YIELD = 0.02  # PREDPOKLAD: cenový index MSCI World + ≈ 2 % ročne čisté dividendy


def ecb(fname):
    df = pd.read_csv(os.path.join(RAW, fname))
    s = df.set_index("TIME_PERIOD")["OBS_VALUE"].astype(float)
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s


def monthly():
    m = pd.DataFrame(
        {
            "euribor12m": ecb("euribor12m.csv"),
            "mir_es": ecb("mir_es.csv"),
            "mir_sk": ecb("mir_sk.csv"),
            "hicp_es": ecb("hicp_es.csv"),
            "hicp_sk": ecb("hicp_sk.csv"),
            "hicp_rent_es": ecb("hicp_rent_es.csv"),
            "hicp_rent_sk": ecb("hicp_rent_sk.csv"),
            "eurusd": ecb("eurusd.csv"),
        }
    )
    # MSCI World cenový index (USD), mesačne
    j = json.load(open(os.path.join(RAW, "msci_world_daily.json")))["chart"]["result"][0]
    idx = pd.PeriodIndex(
        [datetime.date.fromtimestamp(t) for t in j["timestamp"]], freq="M"
    )
    # posledná dostupná denná hodnota mesiaca; chýbajúce denné hodnoty sa najprv vyradia
    msci = pd.Series(j["indicators"]["quote"][0]["close"], index=idx).dropna().groupby(level=0).last()
    m["msci_usd_price"] = msci
    m = m.loc["2003-01":]
    m = m[m.index <= pd.Period("2025-12", "M")]  # HICP končí 2025-12: spoločný koniec
    # MSCI v EUR s prirážkou dividend (mesačné úročenie predpokladaného výnosu)
    eur = m["msci_usd_price"] / m["eurusd"]
    m["msci_eur_tr"] = eur * (1 + MSCI_NET_DIVIDEND_YIELD) ** (np.arange(len(m)) / 12)
    # štvrťročný index cien bytov BIS -> mesačný (lineárna interpolácia v logaritmoch)
    bis = pd.read_csv(os.path.join(RAW, "bis_spp.csv"))
    for iso, col in [("ES", "hp_es"), ("SK", "hp_sk")]:
        s = bis[bis.REF_AREA == iso].set_index("TIME_PERIOD")["OBS_VALUE"].astype(float)
        s.index = pd.PeriodIndex(s.index, freq="Q").asfreq("M", "end")
        s = np.log(s).reindex(pd.period_range(s.index.min(), s.index.max(), freq="M")).interpolate()
        m[col] = np.exp(s)
    # MIVAU „valor tasado“ pre obec Málaga (štvrťročne od 2005-Q1) -> mesačne; hodnota sa priradí
    # poslednému mesiacu štvrťroka (rovnako ako pri BIS), medzi nimi lineárna interpolácia v logaritmoch
    ma = pd.read_csv(os.path.join(OUT, "malaga_valor_tasado_quarterly.csv")).set_index("period")["total"]
    ma.index = pd.PeriodIndex(ma.index, freq="Q").asfreq("M", "end")
    ma = np.log(ma).reindex(pd.period_range(ma.index.min(), ma.index.max(), freq="M")).interpolate()
    m["hp_ma"] = np.exp(ma)
    # NBS ponukové ceny bytov a domov, Bratislavský kraj (štvrťročne od 2005-Q1) -> mesačne (rovnako ako vyššie)
    ba = pd.read_csv(os.path.join(OUT, "bratislava_nbs_quarterly.csv")).set_index("period")["ba"]
    ba.index = pd.PeriodIndex(ba.index, freq="Q").asfreq("M", "end")
    ba = np.log(ba).reindex(pd.period_range(ba.index.min(), ba.index.max(), freq="M")).interpolate()
    m["hp_ba"] = np.exp(ba)
    m.index.name = "month"
    m.to_csv(os.path.join(OUT, "monthly_2003_2025.csv"))
    return m


def annual():
    d = pd.read_excel(os.path.join(RAW, "jst.xlsx"))
    cols = [
        "year", "iso", "cpi", "stir", "ltrate", "hpnom", "eq_tr", "housing_capgain",
        "housing_rent_yd", "housing_tr", "bond_tr",
    ]
    d = d[cols]
    d = d[d.iso.isin(["ESP", "DEU", "FRA", "ITA", "PRT", "USA", "GBR"])]
    d.to_csv(os.path.join(OUT, "jst_annual_1870_2020.csv"), index=False)
    return d


if __name__ == "__main__":
    m = monthly()
    print(m.describe().T[["count", "min", "max"]])
    a = annual()
    print(a[a.iso == "ESP"].dropna(subset=["housing_tr"]).tail(3))
