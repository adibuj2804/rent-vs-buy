# Data sources (all downloaded 2026-11-12; raw files in data/raw)

| File | Series | Source | Coverage |
|---|---|---|---|
| euribor12m.csv | Euribor 12M, monthly | ECB Data Portal, dataset FM, key M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA | 1994 -> 2026-10 |
| mir_es.csv / mir_sk.csv | New-business house-purchase loan rate, Spain / Slovakia | ECB, dataset MIR, M.ES|SK.B.A2C.AM.R.A.2250.EUR.N | ES 2003 ->, SK 2008 -> |
| hicp_es.csv / hicp_sk.csv | HICP all items index | ECB, dataset ICP, M.ES|SK.N.000000.4.INX | 1996 -> 2025-12 |
| hicp_rent_es.csv / hicp_rent_sk.csv | HICP "actual rentals for housing" index | ECB, dataset ICP, M.ES|SK.N.041000.4.INX | 1996 -> 2025-12 |
| eurusd.csv | EUR/USD monthly average | ECB, dataset EXR | 1999 -> 2026-10 |
| bis_spp.csv | Residential property prices, nominal index (national) | BIS WS_SPP, Q.ES+SK.N.628 | ES 1971 ->, SK 2006 -> |
| msci_world_daily.json | MSCI World price index (USD) | Yahoo Finance chart API, ticker ^990100-USD-STRD | 1972 -> 2026 |
| jst.xlsx | Macrohistory Database R6 (house prices, rent yields, equity/bond returns, rates, CPI) | macrohistory.net (Jorda-Schularick-Taylor) | 1870 -> 2020, 18 countries |

## Known weaknesses
- MSCI total return is **estimated**: price index + 2 %/yr net dividends (constant MSCI_NET_DIVIDEND_YIELD in src/build_data.py). The real net-return index could not be downloaded from a free source.
- House prices are **national** (BIS), not Malaga- or Bratislava-specific.
- Spain 1950-1970 housing returns in JST are reconstructed and noisy; price levels exist from 1971.
- Rental yields (5.0 % Malaga, 4.5 % Bratislava) are portal-based assumptions from the earlier research report (Claude.pdf).
