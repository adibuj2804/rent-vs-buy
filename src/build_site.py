"""Generate the static website (site/*.html). Data and code are embedded so each page also
works when opened straight from disk."""
import json, os, html

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = os.path.join(ROOT, "site")
res = json.load(open(os.path.join(SITE, "data/results.json")))
nn = json.load(open(os.path.join(SITE, "model/nn_weights.json")))
read = lambda p: open(os.path.join(ROOT, p), encoding="utf-8").read()
code = lambda p: html.escape(read(p))
pct = lambda x: "n/a" if x is None else f"{x*100:.0f} %"

CSS = """
:root{--bg:#fbfaf7;--fg:#1d2433;--mut:#5d6677;--card:#fff;--line:#e3e0d8;--acc:#0b6e8a;--buy:#c2561a;--rent:#0b6e8a;--warn:#fff4d6;--warnb:#e0b84c}
@media (prefers-color-scheme:dark){:root{--bg:#12161d;--fg:#e8ebf1;--mut:#9aa4b5;--card:#1a202a;--line:#2b3340;--acc:#5ec0dc;--buy:#f08a52;--rent:#5ec0dc;--warn:#33290f;--warnb:#8a6d1c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc)}header.nav{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);z-index:5}
header.nav div{max-width:1050px;margin:auto;padding:12px 20px;display:flex;gap:22px;flex-wrap:wrap;align-items:center}
header.nav b{margin-right:auto}header.nav a{text-decoration:none;color:var(--fg);padding:2px 0;border-bottom:2px solid transparent}
header.nav a.on{border-color:var(--acc);font-weight:600}
main{max-width:1050px;margin:auto;padding:24px 20px 80px}h1{font-size:2.1rem;line-height:1.2;margin:.2em 0}h2{margin-top:2.2em;font-size:1.5rem}h3{margin-top:1.6em}
.hero{border-radius:14px;overflow:hidden;background:linear-gradient(135deg,#0b6e8a,#173a5e);color:#fff;padding:28px 28px 0;margin-bottom:24px}
.hero p{max-width:640px;opacity:.92}.hero svg{display:block;width:100%;height:90px;margin-top:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.card .n{font-size:2rem;font-weight:700}.card small{color:var(--mut)}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}.chart canvas{max-height:360px}
.note{background:var(--warn);border:1px solid var(--warnb);border-radius:10px;padding:12px 16px;margin:16px 0}
table{border-collapse:collapse;width:100%;font-size:.93rem;background:var(--card)}th,td{border:1px solid var(--line);padding:7px 10px;text-align:left}th{background:rgba(127,127,127,.08)}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin:12px 0}summary{cursor:pointer;font-weight:600}
pre{overflow:auto;font-size:.8rem;line-height:1.45;background:rgba(127,127,127,.09);padding:12px;border-radius:8px;max-height:560px}
label{display:block;font-size:.85rem;color:var(--mut);margin-top:10px}input,select{width:100%;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font-size:1rem}
.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:2px 16px}button{margin-top:18px;background:var(--acc);color:#fff;border:0;border-radius:10px;padding:12px 22px;font-size:1rem;cursor:pointer}
.verdict{font-size:1.5rem;font-weight:700}.bar{height:16px;background:var(--rent);border-radius:8px;overflow:hidden}.bar i{display:block;height:100%;background:var(--buy)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.two{grid-template-columns:1fr}}
.cap{color:var(--mut);font-size:.85rem}
"""

SKY = ('<svg viewBox="0 0 800 90" preserveAspectRatio="none"><path fill="rgba(255,255,255,.14)" d="M0 90V60h40V40h30v20h30V25h35v35h40V50h30V30h25v30h45V45h40v15h35V20h30v40h50V50h35V35h30v25h45V55h60V40h35v20h40V90z"/></svg>')

def page(slug, title, body, script="", extra_head=""):
    nav = [("index", "Overview"), ("malaga", "Málaga"), ("bratislava", "Bratislava"), ("advisor", "Advisor")]
    links = "".join(f'<a href="{s}.html" class="{"on" if s==slug else ""}">{n}</a>' for s, n in nav)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Rent vs Buy</title><style>{CSS}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>{extra_head}</head><body>
<header class="nav"><div><b>Rent vs Buy: data analysis project</b>{links}</div></header><main>{body}</main>
<script id="results" type="application/json">{json.dumps(res)}</script>
<script>
const R = JSON.parse(document.getElementById('results').textContent);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const COL = {{buy: css('--buy'), rent: css('--rent'), mut: css('--mut')}};
Chart.defaults.color = css('--mut'); Chart.defaults.font.family = 'inherit';
function line(id, labels, sets, opts={{}}) {{
  new Chart(document.getElementById(id), {{type:'line', data:{{labels, datasets: sets.map(s=>({{pointRadius:0, borderWidth:2, tension:0.1, spanGaps:false, ...s}}))}},
    options:{{responsive:true, interaction:{{mode:'index', intersect:false}}, scales:{{x:{{ticks:{{maxTicksLimit:10}}}}, y:{{title:{{display:!!opts.ytitle, text:opts.ytitle}}}}}}, plugins:{{title:{{display:!!opts.title, text:opts.title}}}}}}}});
}}
{script}
</script></body></html>"""

# ------------------------------------------------------------------ shared pieces
def key_cards(city):
    d = res[city]["fixed"]
    ws = d["winshare"]
    n10 = d["n_starts"].get("10")
    return f"""<div class="grid">
<div class="card"><div class="n">{pct(ws.get("5"))}</div><small>of back-tested start months where buying beat renting after <b>5 years</b> ({d["n_starts"].get("5")} start months)</small></div>
<div class="card"><div class="n">{pct(ws.get("10"))}</div><small>… after <b>10 years</b> ({n10} start months)</small></div>
<div class="card"><div class="n">{pct(d["never_wins_share"])}</div><small>of start months where buying <b>never</b> ended up permanently ahead within the window</small></div>
</div>"""

def sens_table(city):
    s = res[city]["sensitivity"]
    rows = "".join(f"<tr><td>{y*100:.1f} %</td><td>{pct(w)}</td></tr>" for y, w in s["yield"])
    rows2 = "".join(f"<tr><td>{c*100:.1f} %</td><td>{pct(w)}</td></tr>" for c, w in s["buy_cost"])
    return f"""<div class="two"><div><h3>Sensitivity: gross rental yield</h3><table><tr><th>First-year rent ÷ price</th><th>Buying wins (10 y, fixed loan)</th></tr>{rows}</table></div>
<div><h3>Sensitivity: purchase costs</h3><table><tr><th>Taxes + fees, share of price</th><th>Buying wins (10 y, fixed loan)</th></tr>{rows2}</table></div></div>
<p class="cap">All else equal. Rent level is the most uncertain input (see data limits), so it is the first thing to stress-test.</p>"""

ASSUMP = """<table><tr><th>Assumption</th><th>Spain / Málaga</th><th>Slovakia / Bratislava</th><th>Source / basis</th></tr>
<tr><td>Loan-to-value</td><td colspan="2">80 %</td><td>Typical bank practice (ES); NBS limit 80–90 % (SK)</td></tr>
<tr><td>Purchase taxes + fees</td><td>10 %</td><td>0.6 %</td><td>ITP 7 % + notary/registry (Junta de Andalucía); no transfer tax in SK, cadastre fee + lawyer</td></tr>
<tr><td>Selling costs</td><td>4 %</td><td>3 % (+19 % tax on gain if sold within 5 y)</td><td>Agent fee, municipal plusvalía</td></tr>
<tr><td>Upkeep + property tax</td><td>1.2 % of value / yr</td><td>1.05 % of value / yr</td><td>IBI, community fees, repairs</td></tr>
<tr><td>Loan term</td><td>25 y</td><td>30 y</td><td>INE (avg. term), NBS max term</td></tr>
<tr><td>First-year gross yield (rent ÷ price)</td><td>5.0 %</td><td>4.5 %</td><td>Portal asking rents (idealista, realitymap) – <b>not official</b>; stress-tested above</td></tr>
<tr><td>Rent growth</td><td colspan="2">Actual HICP “actual rentals for housing” index</td><td>ECB / Eurostat</td></tr>
<tr><td>Mortgage rate</td><td colspan="2">ECB new-business house-purchase rate at purchase date; fixed for life, or Euribor 12M + original spread</td><td>ECB MIR statistics, Euribor</td></tr>
<tr><td>Investment</td><td colspan="2">MSCI World (EUR) + 2 % assumed net dividends</td><td>MSCI price index, <b>dividend add-on is an assumption</b></td></tr>
<tr><td>Tax on investment gains</td><td>21 % at liquidation (flat approximation of 19–30 % savings scale)</td><td>0 % (exempt after 1 y)</td><td>AEAT; Slovak income-tax act</td></tr>
<tr><td>Fair-comparison rule</td><td colspan="3">Both households spend the same cash each month; whoever has the lower housing cost invests the difference. The renter also invests the down payment and purchase costs on day 0.</td></tr></table>"""

SOURCES = """<ul>
<li>ECB Data Portal (SDMX API): Euribor 12M (FM), mortgage rates (MIR: ES from 2003, SK from 2008), HICP all items and “actual rentals” (ICP), EUR/USD (EXR) – <a href="https://data.ecb.europa.eu">data.ecb.europa.eu</a></li>
<li>BIS Residential Property Price Statistics (WS_SPP), nominal index, Spain from 1971, Slovakia from 2006 – <a href="https://data.bis.org/topics/RPP">data.bis.org</a></li>
<li>MSCI World price index (USD), daily from 1972 via Yahoo Finance chart API; converted to EUR with ECB rates; 2 %/yr net dividends added (assumption)</li>
<li>Jordà–Schularick–Taylor Macrohistory Database, release R6 (1870–2020) – <a href="https://www.macrohistory.net/database/">macrohistory.net</a>. Jordà, Knoll, Kuvshinov, Schularick, Taylor (2019), “The Rate of Return on Everything, 1870–2015”, <i>Quarterly Journal of Economics</i></li>
<li>Tax and cost parameters: Junta de Andalucía (ITP), AEAT, Slovak cadastre / NBS – see the earlier research report (<code>Claude.pdf</code>); press-reported values should be re-verified on the primary portals.</li></ul>"""

def code_block(title, path):
    return f"<details><summary>{title}</summary><pre>{code(path)}</pre></details>"

# ------------------------------------------------------------------ pages
def city_page(city):
    ES = city == "ES"
    name = "Málaga" if ES else "Bratislava"
    slug = "malaga" if ES else "bratislava"
    hp_key, rent_key, mir_key = ("hp_es", "rent_es", "mir_es") if ES else ("hp_sk", "rent_sk", "mir_sk")
    series_note = ("""<div class="note"><b>Data scope:</b> The house-price series here is the <b>Spain national index</b> (BIS), not a Málaga-only series. The Málaga-specific series (MIVAU <i>valor tasado</i> from 2005, Notariado, SERPAVI rents) are the next data layer to load; Málaga-level prices have behaved differently from the national average since 2015, so read these results as “Spain-wide, Málaga cost structure”.</div>"""
        if ES else """<div class="note"><b>Data scope:</b> House prices are the <b>Slovakia national index</b> (BIS, from 2006) and rents are national HICP rents; neither is Bratislava-only. A 1950+ model is <b>not possible</b>: Slovakia is not in the long-run databases and had no housing market before about 1990.</div>""")
    tier2 = ""
    if ES:
        dec = res["tier2"]["decades"]
        fmt = lambda v: "n/a" if v is None else "%+.0f %%" % (v * 100)
        drows = "".join("<tr><td>%ss</td><td>%s</td><td>%s</td></tr>" % (k, pct(v["winshare10"]), fmt(v["median10"])) for k, v in dec.items())
        tier2 = f"""<h2>Tier 2 · Long history 1950–2020 (Spain, national)</h2>
<div class="note"><b>Data quality:</b> Spanish house-price <i>levels</i> exist only from 1971. For 1950–1970 the JST database reconstructs housing returns from rent benchmarks; the year-to-year jumps (e.g. +45 % then −23 %) show it is noisy. Treat the 1950s–60s as indicative only. All results are <b>real</b> (deflated with CPI to start-year money), use modern tax and cost rules throughout, a mortgage rate of long-term government yield + 1.5 pp, and local equity total returns.</div>
<div class="chart"><canvas id="t2"></canvas></div>
<div class="two"><table><tr><th>Start decade</th><th>Buying wins (10 y)</th><th>Median advantage (% of price)</th></tr>{drows}</table>
<div><p>Reading: buying was strongly favoured in the 1950s–70s (negative real rates, rapid price growth), clearly <b>not</b> favoured for starts in the high-rate 1980s and the 2000s boom-and-bust, and mixed in the 1990s. Over all {res['tier2']['n_starts']['10']} start years the share of 10-year windows won by buying is {pct(res['tier2']['winshare']['10'])}; at 30 years it is {pct(res['tier2']['winshare']['30'])}.</p></div></div>"""
    body = f"""<div class="hero"><h1>{name}: rent and invest, or buy with a mortgage?</h1><p>Back-test of every possible purchase month using real data: what would a household have in net wealth after 3–20 years, buying versus renting and investing the difference?</p>{SKY}</div>
{series_note}
<h2>Tier 1 · Detailed model {'2005' if ES else '2008'}–2025</h2>
{key_cards(city)}
<p class="cap">The start-month count shrinks for long horizons (only purchases made early enough have a 15-year outcome), so the long-horizon numbers rest on few, strongly overlapping windows – they are <i>not</i> independent observations.</p>
<h3>What the markets did</h3><div class="chart"><canvas id="c1"></canvas></div>
<h3>How often buying wins, by holding period</h3><div class="chart"><canvas id="c2"></canvas></div>
<h3>Buyer’s advantage after 10 years, by purchase month</h3><div class="chart"><canvas id="c3"></canvas></div>
<p class="cap">Positive = the buyer ends up richer. Unit: share of the purchase price (0.5 = 50 % of the price).</p>
{sens_table(city)}
{tier2}
<h2>Assumptions</h2>{ASSUMP}
<h2>Code</h2>{code_block("model.py: the buy-vs-rent engine", "src/model.py")}{code_block("build_data.py: raw data → clean tables", "src/build_data.py")}
<h2>Sources</h2>{SOURCES}"""
    tier2_js = """
const T = R.tier2.by_start;
line('t2', T['10'].map(x=>x[0]), [
 {label:'10-year horizon', data:T['10'].map(x=>x[1]), borderColor:COL.buy},
 {label:'20-year horizon (aligned by start year)', data:T['10'].map(x=>{const f=T['20'].find(y=>y[0]===x[0]);return f?f[1]:null}), borderColor:COL.rent}],
 {ytitle:'Real buyer advantage, share of price', title:'Spain: buy-vs-rent advantage by purchase year (real)'});""" if ES else ""
    script = f"""
const S = R.series; const E = R.{city};
line('c1', S.months, [
 {{label:'House price index', data:S.{hp_key}, borderColor:COL.buy}},
 {{label:'Rent index (HICP)', data:S.{rent_key}, borderColor:COL.rent}},
 {{label:'MSCI World EUR (est. total return)', data:S.msci, borderColor:COL.mut, borderDash:[5,4]}}], {{ytitle:'Index, first month = 100'}});
const hs = Object.keys(E.fixed.winshare);
new Chart(document.getElementById('c2'), {{type:'bar', data:{{labels:hs.map(h=>h+' y'), datasets:[
 {{label:'Fixed-rate loan', data:hs.map(h=>E.fixed.winshare[h]*100), backgroundColor:COL.buy}},
 {{label:'Variable (Euribor-linked)', data:hs.map(h=>E.variable.winshare[h]*100), backgroundColor:COL.rent}}]}},
 options:{{scales:{{y:{{min:0,max:100,title:{{display:true,text:'% of start months where buying wins'}}}}}}}}}});
const b10 = E.fixed.by_start['10'], v10 = E.variable.by_start['10'];
line('c3', b10.map(x=>x[0]), [
 {{label:'Fixed', data:b10.map(x=>x[1]), borderColor:COL.buy}},
 {{label:'Variable', data:v10.map(x=>x[1]), borderColor:COL.rent}}], {{ytitle:'Buyer minus renter, share of price'}});
{tier2_js}
"""
    return page(slug, name, body, script)

def index_page():
    m = nn["metrics"]
    body = f"""<div class="hero"><h1>Mortgage or rent-and-invest?</h1><p>A data-driven comparison for Málaga and Bratislava, built from official series, plus a neural-network advisor. Every number on these pages can be traced to a source, and all code is shown.</p>{SKY}</div>
<div class="grid"><a class="card" href="malaga.html"><b>Málaga →</b><br><small>Main case. High purchase costs (≈10 %), tax on investment gains. Tier 1 back-test 2005–2025 plus Tier 2 long history 1950–2020.</small></a>
<a class="card" href="bratislava.html"><b>Bratislava →</b><br><small>Contrast case. Near-zero transaction costs and tax-free ETF gains. Tier 1 only (2008–2025).</small></a>
<a class="card" href="advisor.html"><b>Advisor →</b><br><small>Enter your situation; a neural network trained on simulated scenarios estimates which option is likelier to leave you richer.</small></a></div>
<h2>Question</h2><p>Assume income is sufficient for either route. Under which circumstances (holding period, purchase costs, mortgage rate, rent level, market timing) does buying with a mortgage leave a household richer than renting and investing the cash that would have gone into the home?</p>
<h2>Method in one picture</h2>
<table><tr><th>Tier</th><th>Window</th><th>Frequency</th><th>Coverage</th><th>Purpose</th></tr>
<tr><td><b>1 · Detailed</b></td><td>2005 (ES) / 2008 (SK) → 2025</td><td>Monthly</td><td>Málaga &amp; Bratislava cost structures, real mortgage rates, rent index, ETF returns</td><td>Precise break-even analysis and sensitivity</td></tr>
<tr><td><b>2 · Long history</b></td><td>1950 → 2020</td><td>Annual</td><td>Spain national (JST database). Bratislava/Slovakia not available.</td><td>Does the conclusion survive other eras (inflation, high rates, crises)?</td></tr></table>
<p>Both tiers use the same engine (<code>model.py</code>): equal cash spending each month, the cheaper option invests the difference, both households are liquidated at each horizon, and the wealth gap is the result.</p>
<h2>Advisor network</h2>
<p>Because only ~20 years of local data exist, a network trained on real outcomes alone would overfit. Instead, scenarios are drawn from historically measured ranges, noise of historical size is added to the realised path, and each is labelled by the exact model. On unseen scenarios the network scores <b>{m['holdout_accuracy']*100:.1f} %</b> accuracy (always guessing the majority answer: {m['majority_baseline']*100:.1f} %) and agrees with the exact expected-value model <b>{m['agreement_with_exact']*100:.1f} %</b> of the time. It is a fast surrogate for the model, <b>not</b> an independent forecaster.</p>
<h2>Known limitations</h2><ul>
<li>Málaga prices/rents use national Spanish series for now; local official series are not yet loaded.</li>
<li>Rental yield inputs come from portals (asking rents); official SERPAVI rents are much lower. Treat yield as the key uncertainty.</li>
<li>MSCI total return is estimated (price index + 2 % dividends).</li>
<li>Long-horizon back-tests have few, overlapping windows; one decade of data is one observation.</li>
<li>Modern tax rules are applied retroactively; Spanish pre-1971 housing data is reconstructed.</li>
<li>Not personal financial advice.</li></ul>
<h2>Sources</h2>{SOURCES}"""
    return page("index", "Overview", body)

def advisor_page():
    m = nn["metrics"]
    js_predict = """// Forward pass of the trained network (9 inputs -> 64 -> 64 -> 2 outputs)
function predict(w, x) {
  let a = x.map((v, i) => (v - w.mu[i]) / w.sd[i]);           // standardise inputs
  w.layers.forEach((L, k) => {
    const out = L.b.slice();
    for (let j = 0; j < out.length; j++)
      for (let i = 0; i < a.length; i++) out[j] += a[i] * L.W[i][j];
    a = (k < w.layers.length - 1) ? out.map(v => Math.max(0, v)) : out;   // ReLU on hidden layers
  });
  return { pBuyWins: 1 / (1 + Math.exp(-a[0])),                // sigmoid -> probability
           gap: a[1] * w.gapScale };                            // wealth gap, share of price
}"""
    d = res["defaults"]
    body = f"""<div class="hero"><h1>Advisor: which option fits your case?</h1><p>Enter your situation. The network estimates the probability that buying with a mortgage leaves you richer than renting and investing after your holding period.</p>{SKY}</div>
<div class="note"><b>Read this first:</b> this is an educational model, not financial advice. The network imitates the project’s exact model on simulated scenarios (see below); the answer is only as good as the assumptions you enter. Defaults are the 2006–2025 historical averages from the data. Past averages are not forecasts.</div>
<div class="card"><div class="form">
<div><label>City</label><select id="city"><option value="0">Málaga (Spain)</option><option value="1">Bratislava (Slovakia)</option></select></div>
<div><label>Net monthly income (€)</label><input id="inc" type="number" value="3200"></div>
<div><label>Property price (€)</label><input id="price" type="number" value="280000"></div>
<div><label>Savings available for deposit + costs (€)</label><input id="dep" type="number" value="70000"></div>
<div><label>Holding period (years, 2–25)</label><input id="yrs" type="number" value="10" min="2" max="25"></div>
<div><label>Mortgage rate (% / yr, fixed)</label><input id="rate" type="number" step="0.05" value="{d['mortgage_rate_ES']*100:.2f}"></div>
<div><label>Expected house price growth (% / yr)</label><input id="hg" type="number" step="0.1" value="{d['house_growth_ES']*100:.1f}"></div>
<div><label>Expected rent growth (% / yr)</label><input id="rg" type="number" step="0.1" value="{d['rent_growth_ES']*100:.1f}"></div>
<div><label>Expected investment return (% / yr)</label><input id="eq" type="number" step="0.1" value="{d['equity_return']*100:.1f}"></div>
<div><label>Gross rental yield (annual rent ÷ price, %)</label><input id="yld" type="number" step="0.1" value="5.0"></div>
<div><label>Buyer under 35 (Andalucía reduced transfer tax)?</label><select id="u35"><option value="0">No</option><option value="1">Yes</option></select></div>
</div><button id="go">Estimate</button></div>
<div id="out" class="card" style="margin-top:16px;display:none"></div>
<h2>How the network works</h2>
<p>Nine inputs → two hidden layers of 64 ReLU units → two outputs (probability that buying wins; expected wealth gap). Trained with Adam on {m['n_train']:,} simulated scenarios; evaluated on {m['n_test']:,} unseen ones: <b>{m['holdout_accuracy']*100:.1f} %</b> accuracy vs {m['majority_baseline']*100:.1f} % baseline, Brier score {m['brier']:.3f}, agreement with the exact deterministic model {m['agreement_with_exact']*100:.1f} %. The wealth-gap output is trained on the noise-free exact result: median error {m['gap_mae_median']*100:.1f} % of the price, 90 % of cases within {m['gap_mae_p90']*100:.0f} % of the price (≈ {m['gap_mae_p90']*280000:,.0f} € on a 280,000 € home). When the probability is below 50 % but the gap is positive, that is not a contradiction: gains from buying in good scenarios can be larger than losses in bad ones. Noise in the realised paths uses historical volatility (house {m['sd_house']*100:.1f} %/yr, equity {m['sd_equity']*100:.1f} %/yr), so the output probability reflects market uncertainty.</p>
<div class="chart"><canvas id="cal"></canvas></div><p class="cap">Calibration on unseen scenarios: when the network says 70 %, buying wins about 70 % of the time if the points follow the diagonal.</p>
<h2>Code</h2>
<details open><summary>Browser inference (runs this page)</summary><pre id="jscode">{html.escape(js_predict)}</pre></details>
{code_block("train_nn.py: simulation, labelling and training (numpy)", "src/train_nn.py")}
{code_block("model.py: the exact engine that labels the scenarios", "src/model.py")}
<h2>Limits of the advisor</h2><ul><li>It ignores your personal tax situation beyond the city rules, job risk, and what else you could do with the money.</li><li>Inputs outside the training ranges (e.g. LTV below 50 % or above 90 %, horizons beyond 25 years) are clamped and flagged.</li><li>Two decades of local history cannot validate the network against real outcomes; it is validated against the exact model.</li></ul>"""
    script = f"""
const W = {json.dumps(nn)};
{js_predict}
const D = {json.dumps(d)};
const $ = id => document.getElementById(id);
$('city').onchange = () => {{
  const sk = $('city').value === '1';
  $('rate').value = ((sk ? D.mortgage_rate_SK : D.mortgage_rate_ES)*100).toFixed(2);
  $('hg').value = ((sk ? D.house_growth_SK : D.house_growth_ES)*100).toFixed(1);
  $('rg').value = ((sk ? D.rent_growth_SK : D.rent_growth_ES)*100).toFixed(1);
  $('yld').value = sk ? 4.5 : 5.0;
}};
$('go').onclick = () => {{
  const sk = +$('city').value, price = +$('price').value, dep = +$('dep').value, inc = +$('inc').value;
  const warn = [];
  const buyCost = sk ? 0.006 : ($('u35').value === '1' ? 0.065 : 0.10);
  // savings cover deposit AND purchase costs; the rest of the price is the loan
  let ltv = 1 - (dep - buyCost*price) / price;
  if (ltv > 0.9) {{ warn.push('Your savings are below a 10 % deposit plus costs; LTV clamped to 90 %.'); ltv = 0.9; }}
  if (ltv < 0.5) {{ warn.push('Deposit is above 50 % of the price; LTV clamped to 50 % (training range).'); ltv = 0.5; }}
  const yrs = Math.min(25, Math.max(2, Math.round(+$('yrs').value)));
  const x = [sk, yrs, ltv, +$('yld').value/100, buyCost, +$('hg').value/100, +$('rg').value/100, +$('eq').value/100, +$('rate').value/100];
  const r = predict(W, x);
  const term = sk ? 30 : 25, i = x[8]/12, n = term*12;
  const pay = price*ltv * (i/(1-Math.pow(1+i,-n)));
  const dsti = pay/inc;
  if (dsti > 0.40) warn.push('Mortgage payment is ' + (dsti*100).toFixed(0) + ' % of your net income; the project assumes income is sufficient, so check affordability.');
  const p = r.pBuyWins, gap = r.gap*price;
  const verdict = p > 0.6 ? 'Buying is likelier to leave you richer' : p < 0.4 ? 'Renting and investing is likelier to leave you richer' : 'Too close to call';
  $('out').style.display = 'block';
  $('out').innerHTML = `<div class="verdict">${{verdict}}</div>
   <p>Probability buying wins after ${{yrs}} years: <b>${{(p*100).toFixed(0)}} %</b></p>
   <div class="bar"><i style="width:${{p*100}}%"></i></div><p class="cap">Orange = buy, blue = rent and invest</p>
   <p>Expected wealth gap (buyer − renter): <b>${{gap>=0?'+':''}}${{Math.round(gap).toLocaleString('en')}} €</b> (nominal, at the end).</p>
   <p class="cap">Loan: ${{Math.round(price*ltv).toLocaleString('en')}} € at LTV ${{(ltv*100).toFixed(0)}} %, monthly payment ≈ ${{Math.round(pay).toLocaleString('en')}} € (${{(dsti*100).toFixed(0)}} % of net income).</p>
   ${{warn.map(w=>'<div class="note">'+w+'</div>').join('')}}`;
}};
new Chart($('cal'), {{type:'line', data:{{labels:W.calibration.map(c=>c.predicted.toFixed(2)), datasets:[
 {{label:'Observed frequency', data:W.calibration.map(c=>c.observed), borderColor:COL.buy, pointRadius:4}},
 {{label:'Perfect calibration', data:W.calibration.map(c=>c.predicted), borderColor:COL.mut, borderDash:[5,4], pointRadius:0}}]}},
 options:{{scales:{{x:{{title:{{display:true,text:'Predicted probability buying wins'}}}},y:{{min:0,max:1}}}}}}}});
"""
    return page("advisor", "Advisor", body, script)

for slug, content in [("index", index_page()), ("malaga", city_page("ES")), ("bratislava", city_page("SK")), ("advisor", advisor_page())]:
    open(os.path.join(SITE, f"{slug}.html"), "w", encoding="utf-8").write(content)
    print("wrote", slug, len(content) // 1024, "KB")
