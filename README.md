# Kúpa alebo prenájom: Málaga a Bratislava

Statický web + kód v Pythone, ktorý porovnáva „kúpu s hypotékou“ a „prenájom a investovanie rozdielu“.

**Web:** https://adibuj2804.github.io/rent-vs-buy/

* `site/` – otvorte `site/index.html` (funguje aj zo súboru; na zdieľanie sa publikuje priečinok `site/`, napr. cez GitHub Pages)
* `src/build_data.py` – surové dáta → čisté tabuľky (`data/processed`)
* `src/load_malaga.py` – oficiálny rad cien MIVAU pre Málagu z Excelu ministerstva
* `src/load_bratislava.py` – rad NBS pre Bratislavský kraj
* `src/model.py` – výpočet kúpa vs. prenájom (mesačne pre úroveň 1, ročne pre úroveň 2)
* `src/export_results.py` – spätné testy a citlivosť → `site/data/results.json`
* `src/extend_spain.py` – predĺženie španielskeho ročného radu JST (končí 2020) do 2025 z ECB/BIS
* `src/walkforward.py` – modely-poradcovia a vyhodnotenie pre každý počiatočný rok (len dáta do roku XY vs. skutočný víťaz)
* `src/make_notebook.py` – zostaví `notebooks/podnajom_alebo_hypoteka.ipynb` (Google Colab, dáta a váhy siete vložené, bez inštalácie)
* `src/train_nn.py` – simulované scenáre, označenie, neurónová sieť v numpy → `site/model/nn_weights.json`
* `src/build_site.py` – generuje HTML stránky
* `data/SOURCES.md` – každý rad, jeho zdroj a slabiny

Opätovné zostavenie: `pip install -r requirements.txt`, potom v priečinku `src/` spustite `build_data.py`, `extend_spain.py`, `train_nn.py`, `export_results.py`, `build_site.py`, `make_notebook.py`.

**Správa k zadaniu** (stratégie, dáta, model, vyhodnotenie): https://adibuj2804.github.io/rent-vs-buy/sprava.html · **Balík:** `notebooks/podnajom_alebo_hypoteka.ipynb` (otvoriť v Google Colab → Run all).
Nejde o finančné poradenstvo.
