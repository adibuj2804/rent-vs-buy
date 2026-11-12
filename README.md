# Rent vs Buy: Malaga and Bratislava

Static website + Python code comparing "buy with a mortgage" against "rent and invest the difference".

* `site/` - open `site/index.html` (works from disk; for sharing, publish `site/` e.g. with GitHub Pages)
* `src/build_data.py` - raw downloads -> clean tables (`data/processed`)
* `src/model.py` - the buy-vs-rent engine (monthly for Tier 1, annual for Tier 2)
* `src/export_results.py` - back-tests and sensitivity -> `site/data/results.json`
* `src/train_nn.py` - simulated scenarios, labelling, numpy neural network -> `site/model/nn_weights.json`
* `src/build_site.py` - generates the HTML pages
* `data/SOURCES.md` - every series, its source and weaknesses

Rebuild: `pip install -r requirements.txt`, then from `src/` run `build_data.py`, `export_results.py`, `train_nn.py`, `build_site.py`.
Not financial advice.
