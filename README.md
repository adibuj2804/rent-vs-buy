# Kúpa alebo prenájom: Málaga a Bratislava

Statický web + kód v Pythone, ktorý porovnáva „kúpu s hypotékou“ a „prenájom a investovanie rozdielu“.

**Web:** https://adibuj2804.github.io/rent-vs-buy/

* `site/` – otvorte `site/index.html` (funguje aj zo súboru; na zdieľanie sa publikuje priečinok `site/`, napr. cez GitHub Pages)
* `src/build_data.py` – surové dáta → čisté tabuľky (`data/processed`)
* `src/load_malaga.py` – oficiálny rad cien MIVAU pre Málagu z Excelu ministerstva
* `src/model.py` – výpočet kúpa vs. prenájom (mesačne pre úroveň 1, ročne pre úroveň 2)
* `src/export_results.py` – spätné testy a citlivosť → `site/data/results.json`
* `src/train_nn.py` – simulované scenáre, označenie, neurónová sieť v numpy → `site/model/nn_weights.json`
* `src/build_site.py` – generuje HTML stránky
* `data/SOURCES.md` – každý rad, jeho zdroj a slabiny

Opätovné zostavenie: `pip install -r requirements.txt`, potom v priečinku `src/` spustite `build_data.py`, `export_results.py`, `train_nn.py`, `build_site.py`.
Nejde o finančné poradenstvo.
