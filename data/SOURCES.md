# Zdroje dát (všetko stiahnuté 2026-11-12; surové súbory v data/raw)

| Súbor | Rad | Zdroj | Pokrytie |
|---|---|---|---|
| euribor12m.csv | Euribor 12M, mesačne | ECB Data Portal, dataset FM, key M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA | 1994 -> 2026-10 |
| mir_es.csv / mir_sk.csv | Sadzba nových hypoték na bývanie, Španielsko / Slovensko | ECB, dataset MIR, M.ES|SK.B.A2C.AM.R.A.2250.EUR.N | ES 2003 ->, SK 2008 -> |
| hicp_es.csv / hicp_sk.csv | HICP – index všetkých položiek | ECB, dataset ICP, M.ES|SK.N.000000.4.INX | 1996 -> 2025-12 |
| hicp_rent_es.csv / hicp_rent_sk.csv | HICP – index „skutočné nájomné za bývanie“ | ECB, dataset ICP, M.ES|SK.N.041000.4.INX | 1996 -> 2025-12 |
| eurusd.csv | EUR/USD mesačný priemer | ECB, dataset EXR | 1999 -> 2026-10 |
| bis_spp.csv | Ceny rezidenčných nehnuteľností, nominálny index (celoštátne) | BIS WS_SPP, Q.ES+SK.N.628 | ES 1971 ->, SK 2006 -> |
| msci_world_daily.json | MSCI World cenový index (USD) | Yahoo Finance chart API, ticker ^990100-USD-STRD | 1972 -> 2026 |
| mivau_valor_tasado.xls | Priemerná hodnota tasovaného bytu (valor tasado, €/m²), obec Málaga a ďalšie obce >25 000 obyvateľov | MIVAU (Ministerio de Vivienda y Agenda Urbana), Boletín Online, tabuľka 35103500 (apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS) | 2005-Q1 -> 2026-Q2, štvrťročne |
| nbs_prices_by_region.csv | Ceny nehnuteľností na bývanie podľa krajov, €/m² (ponukové ceny; byty aj domy), Bratislavský kraj a ďalšie | Národná banka Slovenska, nbs.sk/export/sk/real-estate-price-by-region/csv | 2005-Q1 -> 2026-Q3, štvrťročne |
| jst.xlsx | Macrohistory Database R6 (ceny bytov, výnosy z nájmu, výnosy akcií/dlhopisov, sadzby, CPI) | macrohistory.net (Jorda-Schularick-Taylor) | 1870 -> 2020, 18 krajín |

## Známe slabiny
- Celková návratnosť MSCI je **odhad**: cenový index + 2 % ročne čisté dividendy (konštanta MSCI_NET_DIVIDEND_YIELD v src/build_data.py). Skutočný index čistej návratnosti sa z voľného zdroja stiahnuť nepodarilo.
- Ceny pre **Málagu** sú oficiálne MIVAU valor tasado (hodnoty z tasácií, nie z kúpnych zmlúv; load_malaga.py). Ceny pre **Bratislavu** sú rad NBS za Bratislavský kraj (ponukové ceny z inzercie, byty aj domy, celý kraj; load_bratislava.py). Celoštátny index BIS slúži len na porovnanie.
- **Nájmy**: lokálny oficiálny rad SERPAVI sa nedá stiahnuť automaticky (aplikácia s reCAPTCHA); používa sa celoštátny HICP rast nájmov a počiatočný výnos ako predpoklad (pre Bratislavu neexistuje žiadny oficiálny rad nájmov; ponukové nájmy z rešerše voči cenám NBS dávajú 5,1–5,6 % hrubého výnosu). Kontrola: SERPAVI 8,9 €/m² (2023, údaj z rešerše) / valor tasado 2023 ≈ 4,7 % hrubého výnosu.
- Španielske údaje JST o bývaní z rokov 1950–1970 sú dopočítané a „skákavé“; úrovne cien existujú od 1971.
- Výnosy z nájmu (5,0 % Málaga, 4,5 % Bratislava) sú predpoklady z portálov podľa úvodnej rešerše (Claude.pdf).
