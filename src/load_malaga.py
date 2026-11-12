"""Načíta oficiálny rad MIVAU „valor tasado“ (priemerná hodnota tasovaného bytu, €/m²) pre obec Málaga.

Zdroj: Ministerio de Vivienda y Agenda Urbana (dnes MIVAU; dáta z Boletín Online),
tabuľka „Valor tasado medio de vivienda libre de municipios mayores de 25.000 habitantes“,
štvrťročne od 2005-Q1. Súbor: data/raw/mivau_valor_tasado.xls
Výstup: data/processed/malaga_valor_tasado_quarterly.csv
"""
import os, re
import pandas as pd
import xlrd

ROOT = os.path.join(os.path.dirname(__file__), "..")


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", ".").strip())
    except ValueError:
        return None  # napr. „n.r“ (nedostatočný počet tasácií)


def load():
    b = xlrd.open_workbook(os.path.join(ROOT, "data/raw/mivau_valor_tasado.xls"))
    rows = []
    for sn in b.sheet_names():
        m = re.match(r"T(\d)A(\d{4})", sn.strip())
        if not m:
            continue
        q, y = int(m.group(1)), int(m.group(2))
        sh = b.sheet_by_name(sn)
        prov = None
        for r in range(sh.nrows):
            row = sh.row_values(r)
            if str(row[1]).strip():
                prov = str(row[1]).strip()
            if prov == "Málaga" and str(row[2]).strip() == "Málaga":
                if sh.ncols <= 6:        # starý formát (2005–2010): len „Total“
                    rows.append(dict(period=f"{y}-Q{q}", total=num(row[3]), new5=None, old=None, n=num(row[5])))
                else:                    # nový formát: do 5 rokov / nad 5 rokov / spolu
                    rows.append(dict(period=f"{y}-Q{q}", total=num(row[5]), new5=num(row[3]), old=num(row[4]), n=num(row[9])))
                break
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "data/processed/malaga_valor_tasado_quarterly.csv"), index=False)
    return df


if __name__ == "__main__":
    df = load()
    print(df.head(4).to_string()); print(df.tail(3).to_string())
    print(len(df), "štvrťrokov; chýbajúce:", int(df.total.isna().sum()))
    print("max", df.loc[df.total.idxmax(), ["period", "total"]].tolist(), "min", df.loc[df.total.idxmin(), ["period", "total"]].tolist())
    print(df[df.period.isin(["2007-Q2", "2008-Q4", "2014-Q1", "2024-Q4", "2025-Q4"])].to_string())
