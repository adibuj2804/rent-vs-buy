"""Turn raw downloads (data/raw) into clean monthly / annual tables (data/processed).

Every series keeps its source in data/SOURCES.md. Nothing here is invented: where a
series needs an assumption (MSCI dividend add-on) it is a named constant.
"""
import csv, json, datetime, os
import numpy as np
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

MSCI_NET_DIVIDEND_YIELD = 0.02  # ASSUMPTION: MSCI World price index + ~2 %/yr net dividends


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
    # MSCI World price index (USD), monthly
    j = json.load(open(os.path.join(RAW, "msci_world_daily.json")))["chart"]["result"][0]
    idx = pd.PeriodIndex(
        [datetime.date.fromtimestamp(t) for t in j["timestamp"]], freq="M"
    )
    # last available daily close of each month; missing daily values are dropped first
    msci = pd.Series(j["indicators"]["quote"][0]["close"], index=idx).dropna().groupby(level=0).last()
    m["msci_usd_price"] = msci
    m = m.loc["2003-01":]
    m = m[m.index <= pd.Period("2025-12", "M")]  # HICP ends 2025-12: common end date
    # MSCI in EUR with dividend add-on (monthly compounding of the assumed yield)
    eur = m["msci_usd_price"] / m["eurusd"]
    m["msci_eur_tr"] = eur * (1 + MSCI_NET_DIVIDEND_YIELD) ** (np.arange(len(m)) / 12)
    # BIS quarterly house price index -> monthly (linear interpolation in logs)
    bis = pd.read_csv(os.path.join(RAW, "bis_spp.csv"))
    for iso, col in [("ES", "hp_es"), ("SK", "hp_sk")]:
        s = bis[bis.REF_AREA == iso].set_index("TIME_PERIOD")["OBS_VALUE"].astype(float)
        s.index = pd.PeriodIndex(s.index, freq="Q").asfreq("M", "end")
        s = np.log(s).reindex(pd.period_range(s.index.min(), s.index.max(), freq="M")).interpolate()
        m[col] = np.exp(s)
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
