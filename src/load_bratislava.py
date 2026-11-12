"""Načíta rad NBS „Ceny nehnuteľností na bývanie podľa krajov v €/m²“ a vyberie Bratislavský kraj.

Zdroj: Národná banka Slovenska, https://nbs.sk/export/sk/real-estate-price-by-region/csv
NBS rad vychádza z PONUKOVÝCH cien (inzercia), nie z cien v kúpnych zmluvách, a pokrýva byty aj domy.
V súbore sú štvrťročné aj ročné riadky; berieme len štvrťročné.
Výstup: data/processed/bratislava_nbs_quarterly.csv
"""
import csv, io, os, re
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")


def load():
    raw = open(os.path.join(ROOT, "data/raw/nbs_prices_by_region.csv"), encoding="utf-8-sig").read()
    rows = list(csv.reader(io.StringIO(raw), delimiter=";"))
    head = next(i for i, r in enumerate(rows) if r and r[0].startswith("Rok"))
    cols = rows[head]
    out = []
    for r in rows[head + 1:]:
        if not r or not r[0]:
            continue
        m = re.fullmatch(r"([1-4])Q (\d{4})", r[0].strip())
        if not m:
            continue  # ročný riadok (napr. „2025“)
        val = lambda c: float(r[cols.index(c)].replace(" ", "").replace(" ", "").replace(",", "."))
        out.append(dict(period=f"{m.group(2)}-Q{m.group(1)}", ba=val("BA"), sr=val("SR spolu")))
    df = pd.DataFrame(out).sort_values("period").reset_index(drop=True)
    df.to_csv(os.path.join(ROOT, "data/processed/bratislava_nbs_quarterly.csv"), index=False)
    return df


if __name__ == "__main__":
    df = load()
    print(df.head(3).to_string()); print(df.tail(3).to_string())
    print(len(df), "štvrťrokov, od", df.period.iloc[0], "do", df.period.iloc[-1])
    per = pd.PeriodIndex(df.period, freq="Q")
    print("medzery v rade:", [str(p) for p in pd.period_range(per.min(), per.max(), freq="Q").difference(per)])
    print(df[df.period.isin(["2022-Q3", "2024-Q1", "2025-Q4", "2026-Q3"])].to_string())
