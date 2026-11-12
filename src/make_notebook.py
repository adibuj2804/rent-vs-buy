"""Zostaví samostatný notebook (Google Colab) so všetkým: dáta, model, váhy siete, vyhodnotenie.

Nič sa nesťahuje a nič sa neinštaluje: dáta aj váhy siete sú vložené priamo v bunkách."""
import json, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
rd = lambda p: open(os.path.join(ROOT, p), encoding="utf-8").read()

model_src = rd("src/model.py").replace("from __future__ import annotations\n", "")
wf_src = rd("src/walkforward.py").replace("from __future__ import annotations\n", "")
wf_src = wf_src.replace("try:                                  # v notebooku sú tieto funkcie definované v bunke vyššie\n    from model import simulate, tier2_grid, tier2_run, SPAIN\nexcept ImportError:\n    pass\n", "")
assert "from model import" not in wf_src
data_csv = rd("data/processed/spain_annual_1870_2025.csv")
net = json.load(open(os.path.join(ROOT, "site/model/nn_weights.json")))
net_min = json.dumps({k: net[k] for k in ("features", "gapScale", "mu", "sd", "layers")}, separators=(",", ":"))

cells = []
md = lambda t: cells.append({"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(True)})
cd = lambda t: cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": t.strip("\n").splitlines(True)})

md("""# Podnájom alebo hypotéka? – jeden balík
Notebook obsahuje všetko, čo projekt potrebuje – **dáta, kód modelu, váhy neurónovej siete** – a nič sa v ňom nesťahuje ani neinštaluje (stačí Google Colab: *Runtime → Run all*).

Čo robí:
1. **Majetok v oboch scenároch** pre zvolený počiatočný rok (časť A),
2. **rada modelu** pre zadanú situáciu (časť B),
3. **vyhodnotenie na histórii**: pre každý počiatočný rok odpoveď modelu len z dát do tohto roku vs. skutočný víťaz (časť C).

Dáta: Španielsko 1870–2025, ročne (JST Macrohistory do 2020, 2021–2025 predĺženie z ECB/BIS). Zdroje a slabiny: https://github.com/adibuj2804/rent-vs-buy/blob/main/data/SOURCES.md · správa: https://adibuj2804.github.io/rent-vs-buy/sprava.html

*Vzdelávací model, nie finančné poradenstvo.*""")

md("## 0 · Dáta, model, sieť (spusti bez zmien)")
cd("# DÁTA: ročné rady pre Španielsko (vložené; stĺpec `source` hovorí, čo je JST a čo predĺženie)\nimport io, json\nimport numpy as np\nimport pandas as pd\nDATA_CSV = '''" + data_csv + "'''\nannual = pd.read_csv(io.StringIO(DATA_CSV))\nannual.tail(8)")
cd("# MODEL: presný výpočet oboch stratégií (src/model.py)\n" + model_src)
cd("# VÁHY NEURÓNOVEJ SIETE z webu (natrénované na simulovaných scenároch, src/train_nn.py)\nNN_JSON = '" + net_min + "'")
cd("# VYHODNOTENIE A MODELY-PORADCOVIA (src/walkforward.py)\n" + wf_src + "\n\nnet = load_net(json.loads(NN_JSON))")

md("""## A · Majetok v oboch scenároch pre zvolený počiatočný rok
Zmeň `START` (1950–2015), `HORIZON` (roky) a `PRICE` (cena bytu v €).""")
cd("""START, HORIZON, PRICE = 1990, 10, 250_000

w = scenario_wealth(annual, START, HORIZON, PRICE)
print(f"Nákup v roku {START}, byt za {PRICE:,.0f} €, horizont {HORIZON} rokov")
print(f"{'':12}{'v eurách roku '+str(START+HORIZON):>22}{'v eurách roku '+str(START):>22}")
for k, nm in (('prenajom', 'Podnájom'), ('hypoteka', 'Hypotéka'), ('rozdiel', 'Rozdiel (H−P)')):
    print(f"{nm:12}{w['nominal'][k]:>20,.0f} €{w['real'][k]:>20,.0f} €")
print('Víťaz:', w['winner'].upper())""")

md("""## B · Rada modelu pre zadanú situáciu
`YEARS` = koľko rokov plánuješ bývať. Model si odhady (rast cien, nájmov, akcií, sadzbu) vezme z posledných 20 rokov dát; môžeš ich prepísať v `OVERRIDES` (napr. vlastný očakávaný rast cien).""")
cd("""YEARS = 15
OVERRIDES = {}   # napr. {'house_growth': 0.04, 'gross_yield': 0.05, 'mortgage_rate': 0.03}

a = advice_today(annual, net, YEARS, overrides=OVERRIDES)
print('Vstupy modelu:', {k: round(v, 4) for k, v in a['inputs'].items()})
print(f"Model „odhad z histórie“: {a['estimate_answer'].upper()}  (výhoda hypotéky {a['estimate_adv']:+.2f} ceny bytu)")
print(f"Neurónová sieť:           {a['net_answer'].upper()}  (P(hypotéka vyhrá) = {a['net_p_buy']:.0%}; orezaných vstupov: {a['net_clipped_inputs']})")""")

md("""## C · Vyhodnotenie na histórii
Pre každý počiatočný rok XY (v ktorom celé obdobie leží v dátach) sa spočíta, ktorý scenár skutočne vyhral, a porovná s odpoveďou modelu, ktorá využíva **len dáta do roku XY**. Tabuľka ukazuje podiel rokov, v ktorých mal model pravdu, spolu s jednoduchými stratégiami „vždy hypotéka“ a „vždy podnájom“.""")
cd("""ev = evaluate(annual, net)
sm = summarize(ev)
print(f"{'horizont':>9}{'roky':>6}{'vždy hyp.':>11}{'vždy prenáj.':>14}{'odhad':>8}{'návrat k pr.':>14}{'sieť':>7}")
for H, s in sm.items():
    print(f"{H:>7} r.{s['n_years']:>6}{s['always_buy']:>11.0%}{s['always_rent']:>14.0%}{s['estimate']:>8.0%}{s['mean_reversion']:>14.0%}{s['net']:>7.0%}")
print()
print("Sieť bola natrénovaná na rozsahoch z rokov 2005–2025; pre historické vstupy je väčšinou mimo nich (pozri správu).")""")
cd("""# graf: skutočná výhoda hypotéky pre horizont 10 rokov a odpoveď modelu
import matplotlib.pyplot as plt
g = ev[ev.H == 10]
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.bar(g.start, g.actual_adv, color=['tab:orange' if b else 'tab:blue' for b in g.buy_won])
ok = (g.est_buy == g.buy_won)
ax.scatter(g.start[ok], [0]*ok.sum(), marker='o', s=14, color='green', label='odhad správne', zorder=3)
ax.scatter(g.start[~ok], [0]*(~ok).sum(), marker='x', s=22, color='red', label='odhad nesprávne', zorder=3)
ax.set_title('Výhoda hypotéky po 10 rokoch (oranžová = vyhrala hypotéka, modrá = podnájom)')
ax.set_xlabel('počiatočný rok'); ax.set_ylabel('podiel ceny (reálne)'); ax.legend(); plt.show()""")

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}, "colab": {"name": "podnajom_alebo_hypoteka.ipynb"}}, "nbformat": 4, "nbformat_minor": 5}
os.makedirs(os.path.join(ROOT, "notebooks"), exist_ok=True)
out = os.path.join(ROOT, "notebooks", "podnajom_alebo_hypoteka.ipynb")
json.dump(nb, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import shutil
shutil.copy(out, os.path.join(ROOT, "site", "podnajom_alebo_hypoteka.ipynb"))
print("notebook", os.path.getsize(out) // 1024, "KB")
