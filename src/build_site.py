"""Vygeneruje statický web (site/*.html) po slovensky. Dáta a kód sú vložené priamo do stránok,
takže fungujú aj po otvorení zo súboru."""
import json, os, html

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = os.path.join(ROOT, "site")
res = json.load(open(os.path.join(SITE, "data/results.json")))
nn = json.load(open(os.path.join(SITE, "model/nn_weights.json")))
read = lambda p: open(os.path.join(ROOT, p), encoding="utf-8").read()
code = lambda p: html.escape(read(p))
NB = " "


def pct(x):
    return "n/a" if x is None else "%.0f%s%%" % (x * 100, NB)


def dec(x, nd=1):
    return (("%." + str(nd) + "f") % x).replace(".", ",")


CSS = """
:root{--bg:#faf8f4;--fg:#1c2331;--mut:#5b6474;--card:#fff;--line:#e4e0d6;--acc:#0b6e8a;--buy:#c2561a;--rent:#0b6e8a;--warn:#fff4d6;--warnb:#e0b84c;--ok:#e6f3ee;--okb:#7fb8a2}
@media (prefers-color-scheme:dark){:root{--bg:#12161d;--fg:#e8ebf1;--mut:#9aa4b5;--card:#1a202a;--line:#2b3340;--acc:#5ec0dc;--buy:#f08a52;--rent:#5ec0dc;--warn:#33290f;--warnb:#8a6d1c;--ok:#16302a;--okb:#3d7a66}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc)}
header.nav{position:sticky;top:0;background:var(--card);border-bottom:1px solid var(--line);z-index:20}
header.nav div{max-width:1080px;margin:auto;padding:10px 20px;display:flex;gap:8px 22px;flex-wrap:wrap;align-items:center}
header.nav b{margin-right:auto;font-size:.95rem}header.nav a{text-decoration:none;color:var(--fg);padding:4px 2px;border-bottom:3px solid transparent}
header.nav a.on{border-color:var(--acc);font-weight:700}
nav.toc{position:sticky;top:53px;background:var(--bg);z-index:10;border-bottom:1px solid var(--line)}
nav.toc div{max-width:1080px;margin:auto;padding:8px 20px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:.88rem}
nav.toc span{color:var(--mut);margin-right:4px}nav.toc a{text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:2px 12px;color:var(--fg)}
nav.toc a:hover{border-color:var(--acc)}
main{max-width:1080px;margin:auto;padding:22px 20px 90px}
section{scroll-margin-top:112px}h1{font-size:2.2rem;line-height:1.15;margin:.1em 0 .3em}h2{margin:2.2em 0 .5em;font-size:1.6rem}h2 small{display:block;font-size:.9rem;font-weight:400;color:var(--mut)}h3{margin:1.6em 0 .4em}
.hero{position:relative;border-radius:16px;overflow:hidden;color:#fff;padding:54px 30px 34px;margin-bottom:22px;background:#173a5e center/cover}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,25,45,.25),rgba(10,25,45,.78))}.hero>*{position:relative}
.hero p{max-width:660px;font-size:1.1rem;margin:.4em 0 0}.hero .tag{display:inline-block;background:rgba(255,255,255,.2);border-radius:999px;padding:2px 12px;font-size:.85rem}
.split{display:grid;grid-template-columns:1fr 1fr;gap:0;min-height:300px;padding:0;align-items:end}
.split .half{background:center/cover;min-height:300px;position:relative;z-index:0}.split:before{display:none}.split .txt{position:absolute;left:0;right:0;bottom:0;padding:30px;background:linear-gradient(180deg,transparent,rgba(10,25,45,.85));z-index:1}
.strip{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}@media(max-width:700px){.strip{grid-template-columns:1fr}.split{grid-template-columns:1fr}}
figure{margin:0;border-radius:12px;overflow:hidden;background:var(--card);border:1px solid var(--line)}figure img{display:block;width:100%;height:260px;object-fit:cover}figcaption{padding:8px 12px;font-size:.85rem;color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;display:block;color:inherit;text-decoration:none}.card .n{font-size:2.2rem;font-weight:800;line-height:1.1}.card small{color:var(--mut)}
a.card:hover{border-color:var(--acc);transform:translateY(-2px)}a.card{transition:.15s}
.photo-card{padding:0;overflow:hidden}.photo-card img{width:100%;height:190px;object-fit:cover;display:block}.photo-card div{padding:14px 18px 18px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin:12px 0}.chart canvas{max-height:360px}
.note{background:var(--warn);border:1px solid var(--warnb);border-radius:12px;padding:12px 16px;margin:16px 0}
.sum{background:var(--ok);border:1px solid var(--okb);border-radius:14px;padding:16px 20px;margin:18px 0}.sum b.h{display:block;font-size:1.05rem;margin-bottom:4px}
.read{color:var(--mut);font-size:.9rem;margin:-4px 0 10px}.read:before{content:"Ako to čítať: ";font-weight:700}
table{border-collapse:collapse;width:100%;font-size:.93rem;background:var(--card)}th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}th{background:rgba(127,127,127,.09)}
.tw{overflow-x:auto}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 16px;margin:12px 0}summary{cursor:pointer;font-weight:600}
pre{overflow:auto;font-size:.8rem;line-height:1.45;background:rgba(127,127,127,.09);padding:12px;border-radius:8px;max-height:540px}
label{display:block;font-size:.88rem;font-weight:600;margin-top:12px}label small{display:block;font-weight:400;color:var(--mut)}
input,select{width:100%;padding:9px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);font-size:1rem}
fieldset{border:1px solid var(--line);border-radius:14px;padding:6px 18px 16px;margin:0 0 16px;background:var(--card)}legend{font-weight:800;padding:0 8px}
button.go{background:var(--acc);color:#fff;border:0;border-radius:12px;padding:14px 26px;font-size:1.05rem;cursor:pointer;width:100%;font-weight:700}
.verdict{font-size:1.5rem;font-weight:800;line-height:1.25}.bar{height:16px;background:var(--rent);border-radius:8px;overflow:hidden;margin:8px 0 2px}.bar i{display:block;height:100%;background:var(--buy)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:800px){.two{grid-template-columns:1fr}}
.adv{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:20px;align-items:start}@media(max-width:900px){.adv{grid-template-columns:1fr}}.adv .res{position:sticky;top:120px}
.cap{color:var(--mut);font-size:.86rem}ol.steps{padding-left:1.2em}ol.steps li{margin:.5em 0}
@media print{header.nav,nav.toc,footer,.btn,#wfh,.hero:before{display:none!important}.hero{background:none!important;color:var(--fg)!important;min-height:0!important;padding:0!important}.hero p,.hero h1{color:var(--fg)!important}main{max-width:none!important;padding:0 6mm!important}
h2,h3{break-after:avoid}tr,.chart,.card,.note,.sum{break-inside:avoid}details>summary{font-weight:700}a{color:inherit;text-decoration:none}body{font-size:11pt}.tw{overflow:visible!important}#wfstrip>div{white-space:normal!important}}
footer{margin-top:60px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:.86rem}
"""

NAV = [("index", "Úvod"), ("data", "Dáta"), ("sprava", "Správa a overenie"), ("advisor", "Poradca"), ("malaga", "Málaga (mesačný model)")]


def page(slug, title, body, script="", toc=None):
    links = "".join('<a href="%s.html" class="%s">%s</a>' % (s, "on" if s == slug else "", n) for s, n in NAV)
    tocnav = ""
    if toc:
        tocnav = '<nav class="toc"><div><span>Na tejto stránke:</span>%s</div></nav>' % "".join(
            '<a href="#%s">%s</a>' % t for t in toc)
    return """<!doctype html><html lang="sk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Kúpa alebo prenájom</title><style>__CSS__</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script></head><body>
<header class="nav"><div><b>Kúpa alebo prenájom? Dátová analýza</b>__LINKS__</div></header>__TOC__<main>__BODY__
<footer>Vzdelávací projekt. Nejde o finančné poradenstvo. Dáta: ECB, BIS, MSCI, Jordà–Schularick–Taylor – podrobnosti v sekcii „Zdroje“ na úvodnej stránke.</footer></main>
<script id="results" type="application/json">__DATA__</script>
<script>
const R = JSON.parse(document.getElementById('results').textContent);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const COL = {buy: css('--buy'), rent: css('--rent'), mut: css('--mut')};
Chart.defaults.color = css('--mut'); Chart.defaults.font.family = 'inherit';
function line(id, labels, sets, opts={}) {
  new Chart(document.getElementById(id), {type:'line', data:{labels, datasets: sets.map(s=>({pointRadius:0, borderWidth:2, tension:0.1, spanGaps:false, ...s}))},
    options:{responsive:true, interaction:{mode:'index', intersect:false}, scales:{x:{ticks:{maxTicksLimit:10}}, y:{title:{display:!!opts.ytitle, text:opts.ytitle}}}, plugins:{title:{display:!!opts.title, text:opts.title}}}});
}
__SCRIPT__
</script></body></html>""".replace("__TITLE__", title).replace("__CSS__", CSS).replace("__LINKS__", links) \
        .replace("__TOC__", tocnav).replace("__BODY__", body).replace("__DATA__", json.dumps(res)).replace("__SCRIPT__", script)


def bg(img):
    return 'style="background-image:url(img/%s)"' % img


def fig(img, cap):
    return '<figure><img src="img/%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>' % (img, cap, cap)


def code_block(title, path):
    return "<details><summary>%s</summary><pre>%s</pre></details>" % (title, code(path))


GLOSAR = """<details><summary>Slovníček pojmov (kliknite pre rozbalenie)</summary><table>
<tr><th>Pojem</th><th>Význam</th></tr>
<tr><td><b>Horizont</b></td><td>Koľko rokov bývanie plánujete – po tomto čase byt predáte a porovnáme majetok oboch domácností.</td></tr>
<tr><td><b>Bod zvratu</b> (break-even)</td><td>Najkratší horizont, od ktorého je kúpa trvalo lepšia než prenájom.</td></tr>
<tr><td><b>LTV</b></td><td>Pomer úveru k cene nehnuteľnosti. LTV 80 % = 20 % ceny platíte z vlastných.</td></tr>
<tr><td><b>Hrubý výnos z prenájmu</b></td><td>Ročný nájom ÷ cena bytu. Pri 5 % a byte za 200 000 € je ročný nájom 10 000 €.</td></tr>
<tr><td><b>Fixná / variabilná hypotéka</b></td><td>Fixná má sadzbu pevnú; variabilná sleduje Euribor (trhovú sadzbu) a mení sa.</td></tr>
<tr><td><b>Euribor</b></td><td>Medzibanková sadzba v eurách – základ pre ceny variabilných hypoték.</td></tr>
<tr><td><b>MSCI World</b></td><td>Akciový index veľkých firiem z rozvinutých krajín; modelujeme ním „investovanie rozdielu“ (napr. cez ETF).</td></tr>
<tr><td><b>Reálne hodnoty</b></td><td>Prepočítané na peniaze východiskového roku (očistené o infláciu).</td></tr>
<tr><td><b>Výhoda kúpy</b></td><td>Majetok kupujúceho mínus majetok nájomníka na konci horizontu. Kladné číslo = kúpa vyhráva. Uvádza sa ako podiel kúpnej ceny.</td></tr></table></details>"""

ASSUMP = """<div class="tw"><table><tr><th>Predpoklad</th><th>Hodnota (Španielsko / Málaga)</th><th>Zdroj / základ</th></tr>
<tr><td>LTV</td><td>80 %</td><td>Bežná prax bánk</td></tr>
<tr><td>Dane a poplatky pri kúpe</td><td>10 %</td><td>Daň z prevodu ITP 7 % + notár, register (Junta de Andalucía)</td></tr>
<tr><td>Náklady pri predaji</td><td>4 %</td><td>Provízia makléra, obecná plusvalía</td></tr>
<tr><td>Údržba + daň z nehnuteľnosti</td><td>1,2 % hodnoty ročne</td><td>IBI, poplatky spoločenstva, opravy</td></tr>
<tr><td>Splatnosť úveru</td><td>30 rokov</td><td>Zadanie projektu</td></tr>
<tr><td>Hrubý výnos z prenájmu v 1. roku</td><td>5,0 % (mesačný model); v dlhej histórii skutočný výnos z JST</td><td>Ponukové nájmy z portálov (idealista) – <b>nie oficiálne dáta</b>; preto robíme test citlivosti</td></tr>
<tr><td>Rast nájmu</td><td>Skutočný index HICP „skutočné nájomné za bývanie“</td><td>ECB / Eurostat</td></tr>
<tr><td>Sadzba hypotéky</td><td>Sadzba nových hypoték v čase kúpy (ECB MIR), fixná alebo Euribor 12M + marža; v dlhej histórii dlhodobá sadzba + 1,5 p. b.</td><td>ECB MIR, Euribor, JST</td></tr>
<tr><td>Investovanie</td><td>MSCI World v EUR + 2 % odhadované čisté dividendy (mesačný model); španielske akcie (JST) v dlhej histórii</td><td>Cenový index MSCI, <b>dividendy sú náš odhad</b></td></tr>
<tr><td>Daň zo ziskov z investícií</td><td>21 % pri speňažení (plochá aproximácia 19–30 %)</td><td>AEAT</td></tr>
<tr><td>Pravidlo férovosti</td><td colspan="2">Obe domácnosti míňajú na bývanie rovnako. Kto má bývanie lacnejšie, rozdiel investuje. Nájomník navyše hneď na začiatku investuje vlastné zdroje a poplatky, ktoré by išli do kúpy.</td></tr></table></div>"""

ZDROJE = """<ul>
<li><b>ECB Data Portal</b> (SDMX API): Euribor 12M, sadzby hypoték (od 2003), inflácia HICP a „skutočné nájomné“, kurz EUR/USD – <a href="https://data.ecb.europa.eu">data.ecb.europa.eu</a></li>
<li><b>MIVAU (Ministerio de Vivienda y Agenda Urbana)</b> – <i>valor tasado</i> priemerná hodnota tasovaného bytu v obci Málaga, štvrťročne od 2005-Q1 do 2026-Q2 – <a href="https://apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS">tabuľka v Exceli</a></li>
<li><b>BIS</b> – ceny rezidenčných nehnuteľností (nominálny index; Španielsko od 1971) – <a href="https://data.bis.org/topics/RPP">data.bis.org</a></li>
<li><b>MSCI World</b> – cenový index v USD, denné údaje od 1972 (Yahoo Finance), prepočet na EUR podľa ECB; dividendy 2 % ročne sú <i>odhad</i></li>
<li><b>Jordà–Schularick–Taylor Macrohistory Database</b>, vydanie R6 (1870–2020) – <a href="https://www.macrohistory.net/database/">macrohistory.net</a>. Jordà, Knoll, Kuvshinov, Schularick, Taylor (2019): „The Rate of Return on Everything, 1870–2015“, <i>Quarterly Journal of Economics</i></li>
<li><b>Dane a náklady</b>: Junta de Andalucía (ITP), AEAT; hodnoty sú zjednodušené predpoklady (pozri tabuľku predpokladov na stránke Dáta a Správa), nie dáta.</li>
<li>Úplný zoznam sérií so začiatkami a slabinami: <a href="https://github.com/adibuj2804/rent-vs-buy/blob/main/data/SOURCES.md">data/SOURCES.md</a></li></ul>"""


# ------------------------------------------------------------------ pomocné bloky
def key_cards(city):
    d = res[city]["fixed"]
    ws = d["winshare"]
    return """<div class="grid">
<div class="card"><div class="n">%s</div><small>testovaných mesiacov nákupu, v ktorých kúpa po <b>5 rokoch</b> predbehla prenájom (%s mesiacov)</small></div>
<div class="card"><div class="n">%s</div><small>… po <b>10 rokoch</b> (%s mesiacov)</small></div>
<div class="card"><div class="n">%s</div><small>mesiacov, v ktorých kúpa <b>nikdy</b> nebola trvalo vpredu</small></div></div>
<p class="cap">Fixná hypotéka. Pri dlhých horizontoch ostáva málo mesiacov nákupu a tie sa silno prekrývajú – nejde o nezávislé pozorovania.</p>""" % (
        pct(ws.get("5")), d["n_starts"].get("5"), pct(ws.get("10")), d["n_starts"].get("10"), pct(d["never_wins_share"]))


def sens_table(city):
    s = res[city]["sensitivity"]
    r1 = "".join("<tr><td>%s %%</td><td>%s</td></tr>" % (dec(y * 100), pct(w)) for y, w in s["yield"])
    r2 = "".join("<tr><td>%s %%</td><td>%s</td></tr>" % (dec(c * 100), pct(w)) for c, w in s["buy_cost"])
    return """<div class="two"><div><h3>Čo ak je nájom vyšší či nižší?</h3><table><tr><th>Ročný nájom ÷ cena</th><th>Kúpa vyhráva (10 r., fixná)</th></tr>%s</table></div>
<div><h3>Čo ak sú náklady pri kúpe iné?</h3><table><tr><th>Dane a poplatky, %% ceny</th><th>Kúpa vyhráva (10 r., fixná)</th></tr>%s</table></div></div>
<p class="cap">Ostatné predpoklady sú rovnaké. Výška nájmu je najneistejší vstup (oficiálne dáta sú slabé), preto je prvý na stres-test.</p>""" % (r1, r2)


# ------------------------------------------------------------------ stránky mesta
def city_page(city):
    ES = True
    name = "Málaga"
    slug = "malaga"
    hp, rent = "hp_ma", "rent_es"
    E = res[city]["fixed"]
    s = res[city]["sensitivity"]
    w5, w10 = E["winshare"]["5"], E["winshare"]["10"]
    if ES:
        zhrnutie = ("Pri hypotéke s fixnou sadzbou bola kúpa lepšia než prenájom s investovaním v <b>%s</b> testovaných mesiacov pri 5-ročnom horizonte a len v <b>%s</b> pri 10-ročnom. "
                    "Nákupné náklady okolo 10 %% ceny sa vracajú dlho a investície do svetových akcií v rokoch 2005–2025 rástli rýchlejšie než byty. "
                    "Výsledok je veľmi citlivý na výšku nájmu (pri výnose %s %% vyhráva kúpa v %s, pri %s %% v %s). "
                    "Dlhá história od roku 1950 ukazuje, že to nie je pravidlo: v 50.–70. rokoch sa kúpa jasne oplácala.") % (
            pct(w5), pct(w10), dec(s["yield"][0][0] * 100), pct(s["yield"][0][1]), dec(s["yield"][3][0] * 100), pct(s["yield"][3][1]))
        hero_img, lead = "ma-malagueta.jpg", "Hlavný prípad: vysoké náklady pri kúpe (≈ 10 %), zdanené zisky z investícií."
        photos = fig("ma-katedrala.jpg", "Katedrála v Málage") + fig("ma-malagueta.jpg", "Pláž La Malagueta") + fig("ma-pobrezie.jpg", "Pobrežie pri Málage")
        mf = res["malaga_facts"]
        nat = res["ES_national"]["fixed"]["winshare"]
        scope = """<div class="sum"><b class="h">Aké dáta sú oficiálne pre Málagu</b>
<ul><li><b>Ceny:</b> oficiálny rad ministerstva (MIVAU) <i>valor tasado</i> – priemerná hodnota tasovaného bytu v obci Málaga, štvrťročne od 2005-Q1 (%s €/m²) do %s (%s €/m²). Sú to hodnoty z bankových tasácií, nie ceny z kúpnych zmlúv.</li>
<li><b>Prepad a oživenie:</b> od vrcholu (%s, %s €/m²) po dno (%s, %s €/m²) ceny klesli o <b>%s %%</b>; dnes sú o %s %% nad vrcholom z roku 2007.</li>
<li><b>Nájmy:</b> oficiálny lokálny rad (SERPAVI) sa automaticky stiahnuť nedá (aplikácia chránená reCAPTCHA). Preto rast nájmov je celoštátny index HICP a <b>počiatočný výnos 5 %% je predpoklad</b>. Kontrola: nájom 8,9 €/m² mesačne (SERPAVI 2023) voči oficiálnej cene za 2023 dáva výnos <b>%s %%</b>, teda blízko predpokladu.</li>
<li><b>Porovnanie s celoštátnym indexom:</b> keby sme použili ceny celého Španielska (BIS), kúpa by vyhrala v %s mesiacov po 5 rokoch a v %s po 10 rokoch – záver sa teda nemení.</li></ul></div>""" % (
            dec(mf["first"][1], 0), mf["last_quarter"][0].replace("-", " "), dec(mf["last_quarter"][1], 0), mf["peak"][0], dec(mf["peak"][1], 0), mf["trough"][0], dec(mf["trough"][1], 0),
            dec(abs(mf["peak_to_trough"]) * 100, 0), dec((mf["last_quarter"][1] / mf["peak"][1] - 1) * 100, 0), dec(mf["implied_yield_2023"] * 100), pct(nat["5"]), pct(nat["10"]))
        tier_note = "2005"

    tier2 = ""
    toc = [("zhrnutie", "V skratke"), ("trh", "Čo sa dialo na trhu"), ("horizont", "Kedy sa kúpa oplatí"), ("citlivost", "Citlivosť")]
    if ES:
        d = res["tier2"]["decades"]
        fmt = lambda v: "n/a" if v is None else ("%+.0f %%" % (v * 100))
        rows = "".join("<tr><td>%s. roky</td><td>%s</td><td>%s</td></tr>" % (k, pct(v["winshare10"]), fmt(v["median10"])) for k, v in d.items())
        tier2 = '<section id="historia"><h2>Dlhá história 1950–2025</h2><p>Dlhá história, stratégie a vyhodnotenie modelu pre každý počiatočný rok sú v <a href="sprava.html">Správe a overení</a> (jadro projektu).</p></section>'
        toc.append(("historia", "Dlhá história 1950+"))

    body = """<div class="hero" __BG__><span class="tag">__TAG__</span><h1>__NAME__: kúpa s hypotékou, alebo prenájom a investovanie?</h1>
<p>__LEAD__ Pre každý možný mesiac nákupu porovnávame, aký majetok by domácnosť mala po 3–20 rokoch.</p></div>
<div class="strip">__PHOTOS__</div>
<section id="zhrnutie"><div class="sum"><b class="h">V skratke</b>__ZHR__</div>__SCOPE__
<h2>Úroveň 1 · Podrobný model __T__–2025 <small>mesačné údaje, skutočné sadzby, nájmy a výnosy akcií</small></h2>__CARDS__</section>
<section id="trh"><h2>Čo sa dialo na trhu</h2><div class="chart"><canvas id="c1"></canvas></div>__EURCHART__
<p class="read">Všetky rady sú prepočítané tak, aby prvý mesiac = 100. Čím vyššia čiara, tým viac daná vec vyrástla.</p></section>
<section id="horizont"><h2>Kedy sa kúpa oplatí <small>podľa počtu rokov, ktoré v byte bývate</small></h2>
<div class="chart"><canvas id="c2"></canvas></div><p class="read">Stĺpec ukazuje, v koľkých percentách testovaných mesiacov nákupu bola kúpa po danom počte rokov lepšia než prenájom. Nad 50 % = kúpa vyhráva častejšie.</p>
<h3>Výhoda kúpy po 10 rokoch podľa mesiaca nákupu</h3><div class="chart"><canvas id="c3"></canvas></div>
<p class="read">Kladná hodnota = kupujúci skončil bohatší. Jednotka: podiel kúpnej ceny (0,5 = 50 % ceny).</p></section>
<section id="citlivost"><h2>Citlivosť <small>čo sa stane, keď zmeníme najneistejšie vstupy</small></h2>__SENS__</section>
__TIER2__
<p><a href="sprava.html">→ Správa a overenie (jadro projektu)</a> · <a href="advisor.html">Poradca</a> · <a href="index.html#zdroje">Zdroje dát</a></p>"""
    body = body.replace("__BG__", bg(hero_img)).replace("__TAG__", "Hlavný prípad").replace("__NAME__", name) \
        .replace("__LEAD__", lead).replace("__PHOTOS__", photos).replace("__ZHR__", zhrnutie).replace("__SCOPE__", scope) \
        .replace("__T__", tier_note).replace("__CARDS__", key_cards(city)).replace("__SENS__", sens_table(city)) \
        .replace("__TIER2__", tier2).replace("__ASSUMP__", ASSUMP) \
        .replace("__EURCHART__", '<div class="chart"><canvas id="c4"></canvas></div><p class="read">' + "Priemerná tasovaná hodnota bytu v obci Málaga v eurách na m² (oficiálny rad MIVAU)." + '</p>') \
        .replace("__CODE__", code_block("model.py – výpočet kúpa vs. prenájom", "src/model.py") + code_block("build_data.py – surové dáta → čisté tabuľky", "src/build_data.py") + code_block("load_malaga.py – oficiálny rad cien pre Málagu z Excelu ministerstva", "src/load_malaga.py"))

    eurjs = """
line('c4', S.months, [{label:'__EURLABEL__', data:S.__EURKEY__, borderColor:COL.buy}], {ytitle:'€/m²'});""".replace("__EURLABEL__", "Valor tasado, Málaga (€/m²)").replace("__EURKEY__", "hp_ma_eur_m2")
    script = """
const S = R.series; const E = R.__C__;
line('c1', S.months, [
 {label:'__HPLABEL__', data:S.__HP__, borderColor:COL.buy},
 {label:'Nájomné (HICP)', data:S.__RENT__, borderColor:COL.rent},
 {label:'MSCI World v EUR (odhad s dividendami)', data:S.msci, borderColor:COL.mut, borderDash:[5,4]}], {ytitle:'Index, prvý mesiac = 100'});
const hs = Object.keys(E.fixed.winshare);
new Chart(document.getElementById('c2'), {type:'bar', data:{labels:hs.map(h=>h+' r.'), datasets:[
 {label:'Fixná hypotéka', data:hs.map(h=>E.fixed.winshare[h]*100), backgroundColor:COL.buy},
 {label:'Variabilná (Euribor)', data:hs.map(h=>E.variable.winshare[h]*100), backgroundColor:COL.rent}]},
 options:{scales:{y:{min:0,max:100,title:{display:true,text:'% mesiacov nákupu, v ktorých vyhráva kúpa'}}}}});
const b10 = E.fixed.by_start['10'], v10 = E.variable.by_start['10'];
line('c3', b10.map(x=>x[0]), [
 {label:'Fixná', data:b10.map(x=>x[1]), borderColor:COL.buy},
 {label:'Variabilná', data:v10.map(x=>x[1]), borderColor:COL.rent}], {ytitle:'Kupujúci − nájomník, podiel ceny'});
""".replace("__C__", city).replace("__HP__", hp).replace("__RENT__", rent).replace("__HPLABEL__", "Ceny bytov v Málage (MIVAU)") + eurjs
    return page(slug, name, body, script, toc)


# ------------------------------------------------------------------ úvod
def index_page():
    m = nn["metrics"]
    e = res["ES"]["fixed"]["winshare"]
    body = """<div class="hero split"><div class="half" __B1__></div><div class="half" __B2__></div>
<div class="txt"><h1>Hypotéka, alebo prenájom a investovanie?</h1><p>Dátová analýza pre Španielsko a Málagu: čo sa viac oplatí a za akých podmienok.</p></div></div>
<section id="start"><h2>Začnite tu <small>stránky odporúčame prejsť v tomto poradí</small></h2>
<div class="grid">
<a class="card photo-card" href="data.html"><img src="img/ma-katedrala.jpg" alt="Dáta"><div><b>1 · Dáta →</b><br><small>Aké rady sme použili, čo v nich je, odkiaľ sú a čo sme museli odhadnúť. Dáta na stiahnutie.</small></div></a>
<a class="card photo-card" href="sprava.html"><img src="img/ma-malagueta.jpg" alt="Správa"><div><b>2 · Správa a overenie →</b><br><small>Jadro projektu: presné stratégie, model-poradca a jeho vyhodnotenie pre každý počiatočný rok od 1950. Výpočet si spustíte priamo na stránke.</small></div></a>
<a class="card photo-card" href="advisor.html"><img src="img/ma-pobrezie.jpg" alt="Poradca"><div><b>3 · Poradca →</b><br><small>Zadajte vlastnú situáciu; neurónová sieť odhadne, ktorá možnosť vás s väčšou pravdepodobnosťou nechá bohatším.</small></div></a>
<a class="card photo-card" href="malaga.html"><img src="img/ma-katedrala.jpg" alt="Málaga"><div><b>4 · Málaga →</b><br><small>Podrobný mesačný model 2005–2025 s oficiálnymi cenami MIVAU.</small></div></a>
</div></section>
<section id="zistenia"><h2>Hlavné zistenia</h2>
<div class="tw"><table><tr><th>Mesto</th><th>Kúpa vyhráva po 5 rokoch</th><th>Kúpa vyhráva po 10 rokoch</th><th>Čo za tým stojí</th></tr>
<tr><td><b>Málaga</b> (Španielsko)</td><td>__E5__</td><td>__E10__</td><td>Nákupné náklady ≈ 10 %, dane z výnosov investícií, výdatný rast svetových akcií.</td></tr>
</table></div>
<p class="cap">Podiel testovaných mesiacov nákupu (fixná hypotéka), v ktorých mal kupujúci na konci vyšší majetok než nájomník. Nad 50 % = kúpa vyhráva častejšie.</p>
<div class="sum"><b class="h">Hlavná myšlienka</b>O výsledku nerozhoduje „kúpa verzus prenájom“ samo osebe, ale <b>koľko rokov v byte ostanete</b>, <b>aké sú náklady pri kúpe</b>, <b>akú sadzbu získate</b> a <b>aký je nájom vzhľadom na cenu bytu</b>. V Málage prenájom v posledných 20 rokoch zvyčajne vyhrával, a výsledok veľmi závisí od výšky nájmu.</div></section>
<section id="postup"><h2>Ako analýza funguje <small>štyri kroky</small></h2>
<ol class="steps"><li><b>Dáta.</b> Sťahujeme oficiálne rady: sadzby hypoték a Euribor (ECB), ceny bytov (BIS), nájomné a inflácia (Eurostat/ECB), akciový index MSCI World a dlhú históriu od roku 1870 (databáza JST).</li>
<li><b>Model.</b> Dve domácnosti míňajú mesačne rovnako. Jedna kúpi byt s hypotékou, druhá prenajíma a rozdiel investuje. Na konci horizontu obe „speňažíme“ a porovnáme majetok.</li>
<li><b>Spätný test.</b> Model spustíme pre každý možný mesiac nákupu v histórii a pre horizonty 1–20 rokov.</li>
<li><b>Neurónová sieť.</b> Sieť sa naučí odhadovať výsledok pre ľubovoľné vstupy – aj ktoré v histórii nenastali (poradca).</li></ol>
<div class="tw"><table><tr><th>Úroveň</th><th>Obdobie</th><th>Frekvencia</th><th>Pokrytie</th><th>Na čo slúži</th></tr>
<tr><td><b>1 · Podrobná</b></td><td>2005 → 2025</td><td>mesačne</td><td>Málaga, skutočné sadzby, nájom, výnosy akcií</td><td>Presný bod zvratu a testy citlivosti</td></tr>
<tr><td><b>2 · Dlhá história</b></td><td>1950 → 2025</td><td>ročne</td><td>Španielsko celoštátne (JST do 2020, potom ECB/BIS – predĺženie).</td><td>Platí záver aj v iných obdobiach (inflácia, vysoké sadzby, krízy)?</td></tr></table></div>
__GLOS__</section>
<section id="siet"><h2>Neurónová sieť poradcu</h2>
<p>Z lokálnej histórie máme len ~20 rokov, čo je pre sieť príliš málo. Preto scenáre simulujeme: rozsahy vstupov berieme z histórie, k „skutočnému“ priebehu pridávame šum historickej veľkosti a každý scenár označí presný model. Na neviditeľných scenároch dosahuje sieť presnosť <b>__ACC__ %</b> (stále tipovanie väčšinovej odpovede: __BASE__ %) a s presným modelom sa zhoduje v <b>__AGR__ %</b> prípadov. Je to rýchla náhrada modelu, <b>nie nezávislá predpoveď</b>.</p></section>
<section id="obmedzenia"><h2>Známe obmedzenia</h2><ul>
<li>Ceny pre Málagu sú oficiálne (MIVAU valor tasado – hodnoty z tasácií, nie z kúpnych zmlúv). Nájmy pre Málagu ešte nie sú načítané (SERPAVI sa nedá stiahnuť automaticky). Rast nájmov je celoštátny index HICP.</li>
<li>Výnos z nájmu pochádza z portálov (ponukové nájmy); oficiálne nájmy SERPAVI sú výrazne nižšie. Je to najväčšia neistota.</li>
<li>Celková návratnosť MSCI je odhad (cenový index + 2 % dividendy).</li>
<li>Dlhé horizonty majú málo prekrývajúcich sa okien; jedno desaťročie dát je jedno pozorovanie.</li>
<li>Dnešné dane sú aplikované spätne; španielske údaje o bývaní pred rokom 1971 sú dopočítané.</li>
<li>Nejde o finančné poradenstvo.</li></ul></section>
<section id="zdroje"><h2>Zdroje</h2>__ZDROJE__</section>"""
    body = body.replace("__B1__", bg("ma-malagueta.jpg")).replace("__B2__", bg("ma-katedrala.jpg")) \
        .replace("__E5__", pct(e["5"])).replace("__E10__", pct(e["10"])) \
        .replace("__GLOS__", GLOSAR).replace("__ZDROJE__", ZDROJE) \
        .replace("__ACC__", dec(m["holdout_accuracy"] * 100)).replace("__BASE__", dec(m["majority_baseline"] * 100)).replace("__AGR__", dec(m["agreement_with_exact"] * 100))
    return page("index", "Úvod", body, "", [("start", "Začnite tu"), ("zistenia", "Hlavné zistenia"), ("postup", "Ako to funguje"), ("siet", "Neurónová sieť"), ("obmedzenia", "Obmedzenia"), ("zdroje", "Zdroje")])


# ------------------------------------------------------------------ poradca
CALC_JS = r"""// ---- dáta a pravidlá (rovnaké ako src/model.py: SPAIN) ----
const A = {}; ANNUAL.forEach(r => A[r[0]] = {cpi: r[1], lt: r[2], g: r[3], ry: r[4], eq: r[5]});
const YMAX = Math.max(...ANNUAL.map(r => r[0]));
const SPN = {ltv: 0.8, buy: 0.10, sell: 0.04, upk: 0.012, term: 30, tax: 0.21};
const full = y => A[y] && [A[y].g, A[y].ry, A[y].eq, A[y].lt].every(v => v !== null);
const annuity = (r, n) => Math.abs(r) < 1e-12 ? 1 / n : r / (1 - Math.pow(1 + r, -n));
const geo = xs => Math.exp(xs.reduce((s, x) => s + Math.log(1 + x), 0) / xs.length) - 1;

// ---- jedna simulácia: obe stratégie po každom roku (zhodné so simulate() v model.py) ----
function sim(g, rg, eq, rate, ry0, H) {
  const p = SPN; let price = 1, rent = ry0, bal = p.ltv, left = p.term;
  let renter = (1 - p.ltv) + p.buy, rc = renter, bp = 0, bc = 0; const out = [];
  for (let t = 0; t < H; t++) {
    const pay = bal > 1e-12 ? annuity(rate[t], left) * bal : 0;
    bal = Math.max(bal - (pay - bal * rate[t]), 0); left = Math.max(left - 1, 1);
    const diff = pay + p.upk * price - rent;               // kto má bývanie drahšie, druhý rozdiel investuje
    renter *= 1 + eq[t]; bp *= 1 + eq[t];
    if (diff > 0) { renter += diff; rc += diff; } else { bp -= diff; bc -= diff; }
    price *= 1 + g[t]; rent *= 1 + rg[t];
    const rn = renter - p.tax * Math.max(renter - rc, 0), bn = bp - p.tax * Math.max(bp - bc, 0);
    out.push({buyer: price * (1 - p.sell) - bal + bn, renter: rn});
  }
  return out;
}

// ---- skutočný priebeh: dáta roku y+1 … y+H ----
function actual(y, H) {
  const g = [], eq = [], P = [1];
  for (let k = 1; k <= H; k++) { g.push(A[y + k].g); eq.push(A[y + k].eq); P.push(P[k - 1] * (1 + g[k - 1])); }
  const rp = P.map((p, k) => A[y + k].ry * p);               // nájom_k = výnos_k × cena_k
  const rg = g.map((_, k) => rp[k + 1] / rp[k] - 1);
  const rate = Array(H).fill(Math.max(A[y].lt / 100 + 0.015, 0.01));
  const out = sim(g, rg, eq, rate, A[y].ry, H);
  return out.map((o, k) => ({...o, defl: A[y + k + 1].cpi / A[y].cpi}));
}

// ---- odhady z dát <= y (model „odhad z histórie“; shrink > 0 = návrat k dlhodobému priemeru) ----
function knownInputs(y, shrink) {
  const ys = ANNUAL.map(r => r[0]).filter(v => v <= y);
  const est = list => {
    const g = [], r = [], e = [];
    for (let i = 1; i < list.length; i++) {
      const a = A[list[i - 1]], b = A[list[i]];
      g.push(b.g); r.push(b.ry / a.ry * (1 + b.g) - 1); e.push(b.eq);
    }
    return [geo(g), Math.max(geo(r), 0), geo(e)];
  };
  let [g, rg, eq] = est(ys.slice(-21));                    // posledných 20 rokov
  if (shrink) {
    const [g2, r2, e2] = est(ys.filter(v => A[v].g !== null && A[v].ry !== null && A[v].eq !== null));   // sadzba sa tu nevyžaduje
    g = (1 - shrink) * g + shrink * g2; rg = (1 - shrink) * rg + shrink * r2; eq = (1 - shrink) * eq + shrink * e2;
  }
  return {house_growth: g, rent_growth: rg, equity_return: eq, gross_yield: A[y].ry, mortgage_rate: Math.max(A[y].lt / 100 + 0.015, 0.01)};
}
function estimateAdv(inp, H) {
  const c = v => Array(H).fill(v);
  const o = sim(c(inp.house_growth), c(inp.rent_growth), c(inp.equity_return), c(inp.mortgage_rate), inp.gross_yield, H);
  return o[H - 1].buyer - o[H - 1].renter;
}
function netProb(inp, H) {                                 // neurónová sieť; vstupy orezané na tréningové rozsahy
  const R_ = W.ranges, cl = (k, v) => Math.min(Math.max(v, R_[k][0]), R_[k][1]);
  const x = [H, SPN.ltv, cl('gross_yield', inp.gross_yield), SPN.buy, cl('house_growth', inp.house_growth),
             cl('rent_growth', inp.rent_growth), cl('equity_return', inp.equity_return), cl('mortgage_rate', inp.mortgage_rate)];
  return predict(W, x).pBuyWins;
}
const eur = v => Math.round(v).toLocaleString('sk-SK') + ' €';
const pc = v => (v * 100).toFixed(0) + ' %';

// ---- A: majetok pre zvolený rok ----
document.getElementById('cgo').onclick = () => {
  const y = Math.round(+document.getElementById('cy').value), price = +document.getElementById('cp').value;
  let H = Math.round(+document.getElementById('ch').value);
  if (!(y >= 1950 && y + 1 <= YMAX) || !full(y)) { document.getElementById('cout').innerHTML = '<div class="note">Počiatočný rok musí byť medzi 1950 a ' + (YMAX - 1) + '.</div>'; return; }
  const warn = H > YMAX - y ? '<div class="note">Horizont bol skrátený na ' + (YMAX - y) + ' rokov (dáta končia rokom ' + YMAX + ').</div>' : '';
  H = Math.min(Math.max(H, 1), YMAX - y);
  const a = actual(y, H)[H - 1], d = a.defl;
  const inp = knownInputs(y, 0), e1 = estimateAdv(inp, H) > 0, e2 = estimateAdv(knownInputs(y, 0.5), H) > 0, pn = netProb(inp, H);
  const ans = b => b ? 'hypotéka' : 'podnájom', won = a.buyer > a.renter;
  document.getElementById('cout').innerHTML = `<div class="tw"><table><tr><th>Majetok po ${H} rokoch</th><th>Scenár A · podnájom</th><th>Scenár B · hypotéka</th><th>Rozdiel (B − A)</th></tr>
   <tr><td>v eurách roku ${y + H}</td><td>${eur(a.renter * price)}</td><td>${eur(a.buyer * price)}</td><td>${eur((a.buyer - a.renter) * price)}</td></tr>
   <tr><td>v eurách roku ${y} (bez inflácie)</td><td>${eur(a.renter / d * price)}</td><td>${eur(a.buyer / d * price)}</td><td>${eur((a.buyer - a.renter) / d * price)}</td></tr></table></div>
   <p class="verdict">Skutočne vyhral: ${ans(won)}</p>
   <p>Rada modelov, ktoré poznajú len dáta do roku ${y}: <b>odhad z histórie → ${ans(e1)}</b> · <b>s návratom k priemeru → ${ans(e2)}</b> · <b>neurónová sieť → ${ans(pn > 0.5)}</b> (P(hypotéka) = ${pc(pn)}).</p>${warn}`;
};

// ---- B: vyhodnotenie pre všetky počiatočné roky ----
document.getElementById('ego').onclick = () => {
  const rows = [];
  for (const H of [10, 20, 30]) {
    let n = 0, buy = 0, e1 = 0, e2 = 0, e3 = 0;
    for (let y = 1950; y + H <= YMAX; y++) {
      if (!full(y)) continue;
      const a = actual(y, H)[H - 1], won = a.buyer > a.renter, inp = knownInputs(y, 0);
      n++; buy += won; e1 += (estimateAdv(inp, H) > 0) === won; e2 += (estimateAdv(knownInputs(y, 0.5), H) > 0) === won; e3 += (netProb(inp, H) > 0.5) === won;
    }
    rows.push(`<tr><td><b>${H} rokov</b></td><td>${n}</td><td>${pc(buy / n)}</td><td>${pc(1 - buy / n)}</td><td><b>${pc(e1 / n)}</b></td><td><b>${pc(e2 / n)}</b></td><td>${pc(e3 / n)}</td></tr>`);
  }
  document.getElementById('eout').innerHTML = '<div class="tw"><table><tr><th>Horizont</th><th>Počiatočných rokov</th><th>Vždy hypotéka</th><th>Vždy podnájom</th><th>Odhad z histórie</th><th>S návratom k priemeru</th><th>Neurónová sieť</th></tr>' + rows.join('') + '</table></div>';
};
document.getElementById('cgo').click(); document.getElementById('ego').click();"""


PREDICT_JS = """// Dopredný prechod natrénovanej siete (8 vstupov -> 64 -> 64 -> 2 výstupy)
function predict(w, x) {
  let a = x.map((v, i) => (v - w.mu[i]) / w.sd[i]);           // štandardizácia vstupov
  w.layers.forEach((L, k) => {
    const out = L.b.slice();
    for (let j = 0; j < out.length; j++)
      for (let i = 0; i < a.length; i++) out[j] += a[i] * L.W[i][j];
    a = (k < w.layers.length - 1) ? out.map(v => Math.max(0, v)) : out;   // ReLU na skrytých vrstvách
  });
  return { pBuyWins: 1 / (1 + Math.exp(-a[0])),                // sigmoid -> pravdepodobnosť
           gap: a[1] * w.gapScale };                            // rozdiel majetku, podiel ceny
}"""


def advisor_page():
    m = nn["metrics"]
    d = res["defaults"]
    js_predict = PREDICT_JS
    body = """<div class="hero" __BG__><span class="tag">Interaktívny nástroj</span><h1>Poradca: ktorá možnosť sa hodí vám?</h1>
<p>Vyplňte tri krátke časti. Neurónová sieť odhadne pravdepodobnosť, že kúpa s hypotékou vás po zvolenom čase nechá bohatším než prenájom s investovaním.</p></div>
<div class="note"><b>Najprv si prečítajte:</b> je to vzdelávací model, nie finančné poradenstvo. Sieť napodobňuje presný model projektu na simulovaných scenároch; výsledok je taký dobrý, ako sú vaše predpoklady. Predvyplnené hodnoty sú historické priemery 2006–2025 – nie predpoveď.</div>
<div class="adv"><div>
<fieldset><legend>1 · Vaša situácia</legend>
<p class="cap">Mesto: Málaga (Španielsko). Predvyplnené hodnoty sú pre Španielsko.</p>
<label>Čistý mesačný príjem (€)<small>Slúži len na kontrolu splátky; predpokladáme, že príjem stačí na oba spôsoby.</small><input id="inc" type="number" value="3200"></label>
<label>Cena nehnuteľnosti (€)<input id="price" type="number" value="280000"></label>
<label>Úspory na akontáciu a poplatky (€)<small>Z nich sa platia aj dane a poplatky pri kúpe.</small><input id="dep" type="number" value="70000"></label>
<label>Ako dlho tam plánujete bývať? (roky, 2–30)<input id="yrs" type="number" value="10" min="2" max="30"></label>
<label>Kupujúci do 35 rokov? <small>Andalúzia: znížená daň z prevodu.</small><select id="u35"><option value="0">Nie</option><option value="1">Áno</option></select></label></fieldset>
<fieldset><legend>2 · Hypotéka</legend>
<label>Úroková sadzba (% ročne, fixná)<small>Predvyplnené: posledná sadzba nových hypoték podľa ECB.</small><input id="rate" type="number" step="0.05" value="__RATE__"></label></fieldset>
<fieldset><legend>3 · Čo očakávate od trhu</legend>
<label>Rast cien bytov (% ročne)<input id="hg" type="number" step="0.1" value="__HG__"></label>
<label>Rast nájmov (% ročne)<input id="rg" type="number" step="0.1" value="__RG__"></label>
<label>Výnos z investovania (% ročne)<small>Predvyplnené: MSCI World 2006–2025 s odhadom dividend.</small><input id="eq" type="number" step="0.1" value="__EQ__"></label>
<label>Hrubý výnos z prenájmu (ročný nájom ÷ cena, %)<small>Najneistejší vstup; portálové ponukové nájmy bývajú vyššie než skutočné.</small><input id="yld" type="number" step="0.1" value="5.0"></label></fieldset>
<button class="go" id="go">Odhadnúť výsledok</button></div>
<div class="res"><div id="out" class="card"><b>Výsledok sa zobrazí tu.</b><br><small>Upravte vstupy a stlačte „Odhadnúť výsledok“.</small></div></div></div>
<section id="siet"><h2>Ako sieť funguje</h2>
<p>Osem vstupov → dve skryté vrstvy po 64 neurónoch (ReLU) → dva výstupy: pravdepodobnosť, že vyhrá kúpa, a očakávaný rozdiel majetku. Trénovaná algoritmom Adam na __NTR__ simulovaných scenároch, otestovaná na __NTE__ neviditeľných: presnosť <b>__ACC__ %</b> (základ __BASE__ %), Brierovo skóre __BRIER__, zhoda s presným modelom __AGR__ %. Šum v simulovaných cenách používa historickú volatilitu (byty __SDH__ %/rok, akcie __SDE__ %/rok), preto pravdepodobnosť odráža trhovú neistotu.</p>
<p>Rozdiel majetku sa učil na výsledku bez šumu: medián chyby __GM__ % ceny, v 90 % prípadov do __GP__ % ceny (≈ __GPE__ € pri byte za 280 000 €). Ak je pravdepodobnosť pod 50 %, ale rozdiel kladný, nejde o chybu – zisky z kúpy v dobrých scenároch môžu byť väčšie než straty v zlých.</p>
<div class="chart"><canvas id="cal"></canvas></div><p class="read">Ak bodky sledujú diagonálu, sieť je kalibrovaná: keď tvrdí 70 %, kúpa naozaj vyhrá asi v 70 % prípadov.</p></section>
<section id="kod"><h2>Kód</h2>
<details open><summary>Predikcia v prehliadači (beží na tejto stránke)</summary><pre>__JS__</pre></details>
__C1____C2__</section>
<section><h2>Obmedzenia poradcu</h2><ul><li>Ignoruje vašu osobnú daňovú situáciu nad rámec pravidiel mesta, riziko straty práce a iné využitie peňazí.</li><li>Vstupy mimo tréningových rozsahov (LTV pod 50 % alebo nad 90 %, horizont nad 30 rokov) sa orežú a zobrazí sa upozornenie.</li><li>Sieť napodobňuje presný model; jej overenie proti skutočným výsledkom pre každý rok od 1950 je v <a href="sprava.html#overenie">Správe</a> – a nie je lepšie než tipovanie.</li></ul></section>"""
    body = body.replace("__BG__", bg("ma-malagueta.jpg")).replace("__RATE__", "%.2f" % (d["mortgage_rate_ES"] * 100)) \
        .replace("__HG__", "%.1f" % (d["house_growth_ES"] * 100)).replace("__RG__", "%.1f" % (d["rent_growth_ES"] * 100)).replace("__EQ__", "%.1f" % (d["equity_return"] * 100)) \
        .replace("__NTR__", "{:,}".format(m["n_train"]).replace(",", NB)).replace("__NTE__", "{:,}".format(m["n_test"]).replace(",", NB)) \
        .replace("__ACC__", dec(m["holdout_accuracy"] * 100)).replace("__BASE__", dec(m["majority_baseline"] * 100)).replace("__BRIER__", dec(m["brier"], 3)) \
        .replace("__AGR__", dec(m["agreement_with_exact"] * 100)).replace("__SDH__", dec(m["sd_house"] * 100)).replace("__SDE__", dec(m["sd_equity"] * 100)) \
        .replace("__GM__", dec(m["gap_mae_median"] * 100)).replace("__GP__", "%.0f" % (m["gap_mae_p90"] * 100)).replace("__GPE__", "{:,.0f}".format(m["gap_mae_p90"] * 280000).replace(",", NB)) \
        .replace("__JS__", html.escape(js_predict)) \
        .replace("__C1__", code_block("train_nn.py – simulácia, označovanie a trénovanie (numpy)", "src/train_nn.py")) \
        .replace("__C2__", code_block("model.py – presný výpočet, ktorý označuje scenáre", "src/model.py"))
    script = """
const W = __W__;
__JS__
const D = __D__;
const $ = id => document.getElementById(id);
const eur = v => Math.round(v).toLocaleString('sk-SK') + ' €';
$('go').onclick = () => {
  const price = +$('price').value, dep = +$('dep').value, inc = +$('inc').value;
  const warn = [];
  const buyCost = $('u35').value === '1' ? 0.065 : 0.10;
  // úspory pokryjú akontáciu A náklady pri kúpe; zvyšok ceny je úver
  let ltv = 1 - (dep - buyCost*price) / price;
  if (ltv > 0.9) { warn.push('Vaše úspory sú pod 10 % akontácie plus poplatky; LTV bolo obmedzené na 90 %.'); ltv = 0.9; }
  if (ltv < 0.5) { warn.push('Akontácia presahuje 50 % ceny; LTV bolo obmedzené na 50 % (tréningový rozsah).'); ltv = 0.5; }
  const yrs = Math.min(30, Math.max(2, Math.round(+$('yrs').value)));
  const x = [yrs, ltv, +$('yld').value/100, buyCost, +$('hg').value/100, +$('rg').value/100, +$('eq').value/100, +$('rate').value/100];
  const r = predict(W, x);
  const term = 30, i = x[8]/12, n = term*12;
  const pay = price*ltv * (i/(1-Math.pow(1+i,-n)));
  const dsti = pay/inc;
  if (dsti > 0.40) warn.push('Splátka tvorí ' + (dsti*100).toFixed(0) + ' % čistého príjmu. Projekt predpokladá dostatočný príjem, no overte si dostupnosť úveru.');
  const p = r.pBuyWins, gap = r.gap*price;
  const verdict = p > 0.6 ? 'Kúpa vás pravdepodobne nechá bohatším' : p < 0.4 ? 'Prenájom a investovanie vás pravdepodobne nechá bohatším' : 'Príliš tesné na rozhodnutie';
  $('out').innerHTML = `<div class="verdict">${verdict}</div>
   <p>Pravdepodobnosť, že po ${yrs} rokoch vyhrá kúpa: <b>${(p*100).toFixed(0)} %</b></p>
   <div class="bar"><i style="width:${p*100}%"></i></div><p class="cap">Oranžová = kúpa, modrá = prenájom a investovanie</p>
   <p>Očakávaný rozdiel majetku (kupujúci − nájomník): <b>${gap>=0?'+':'−'}${eur(Math.abs(gap))}</b> (nominálne, na konci).</p>
   <p class="cap">Úver: ${eur(price*ltv)} pri LTV ${(ltv*100).toFixed(0)} %, mesačná splátka ≈ ${eur(pay)} (${(dsti*100).toFixed(0)} % čistého príjmu).</p>
   ${warn.map(w=>'<div class="note">'+w+'</div>').join('')}`;
};
new Chart($('cal'), {type:'line', data:{labels:W.calibration.map(c=>c.predicted.toFixed(2)), datasets:[
 {label:'Skutočná početnosť', data:W.calibration.map(c=>c.observed), borderColor:COL.buy, pointRadius:4},
 {label:'Dokonalá kalibrácia', data:W.calibration.map(c=>c.predicted), borderColor:COL.mut, borderDash:[5,4], pointRadius:0}]},
 options:{scales:{x:{title:{display:true,text:'Predpovedaná pravdepodobnosť, že vyhrá kúpa'}},y:{min:0,max:1}}}});
""".replace("__W__", json.dumps(nn)).replace("__JS__", js_predict).replace("__D__", json.dumps(d))
    return page("advisor", "Poradca", body, script, [("siet", "Ako sieť funguje"), ("kod", "Kód")])


# ------------------------------------------------------------------ správa a overenie (zadanie PDAb)
def sprava_page():
    import pandas as pd
    import walkforward as W
    wf = {int(k): v for k, v in res["walkforward"]["summary"].items()}
    annual = pd.read_csv(os.path.join(ROOT, "data/processed/spain_annual_1870_2025.csv"))
    net = W.load_net(os.path.join(SITE, "model/nn_weights.json"))
    today = {H: W.advice_today(annual, net, H) for H in (10, 20, 30)}
    ex = W.scenario_wealth(annual, 1990, 10)
    p = lambda x: dec(x * 100, 0) + NB + "%"
    rows = "".join("<tr><td><b>%d rokov</b></td><td>%d (%d–%d)</td><td>%s</td><td>%s</td><td><b>%s</b></td><td><b>%s</b></td><td>%s</td></tr>" % (
        H, v["n_years"], v["first"], v["last"], p(v["always_buy"]), p(v["always_rent"]), p(v["estimate"]), p(v["mean_reversion"]), p(v["net"]))
        for H, v in wf.items())
    per = "".join("<tr><td>%d rokov</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        H, k, d["n"], p(d["buy_won"]), p(d["estimate"]), p(d["mean_reversion"])) for H, v in wf.items() for k, d in v["by_period"].items())
    inp = today[10]["inputs"]
    trows = "".join("<tr><td>%d rokov</td><td><b>%s</b> (%+.0f %% ceny)</td><td><b>%s</b> (P(kúpa) = %s)</td></tr>" % (
        H, t["estimate_answer"], t["estimate_adv"] * 100, t["net_answer"], p(t["net_p_buy"])) for H, t in today.items())
    nbsp = lambda v: "{:,.0f}".format(v).replace(",", NB) + NB + "€"
    sens = res["walkforward"]["lookback_sensitivity"]
    sens_rows = "".join("<tr><td>%s rokov</td>%s</tr>" % (L, "".join("<td>%s</td>" % p(v[H]) for H in ("10", "20", "30"))) for L, v in sens.items())
    body = """<div class="hero" __BG__><span class="tag">Správa k zadaniu</span><h1>Podnájom alebo hypotéka? Správa a overenie na histórii</h1>
<p>Presné stratégie, dáta od roku 1950, model-poradca a jeho overenie: pre každý počiatočný rok porovnáme radu modelu so skutočným výsledkom.</p></div>
<section id="prehlad"><div class="sum"><b class="h">V skratke</b>
Pre Španielsko máme dáta od roku 1950 do 2025. V rokoch 1950–2015 (horizont 10 rokov) vyhrala kúpa v __BUY10__ a prenájom v __RENT10__ začiatočných rokov – o víťazovi rozhodli <b>inflácia a sadzby</b>: v 50.–70. rokoch sa kúpa výrazne oplácala, od 80. rokov prevažne nie.
Model „odhad z histórie“ mal pravdu v __E10__ (10 r.), __E20__ (20 r.) a __E30__ (30 r.) rokov; základná stratégia „vždy kúpa“ v __B10__, __B20__ a __B30__. <b>Je to len mierne lepšie než stále tipovanie jednej odpovede, pri 30 rokoch horšie</b> – výsledok uvádzame bez príkras.</div>
<div class="tw"><table><tr><th>Časť zadania</th><th>Kde to je</th><th>Stav</th></tr>
<tr><td>1 · Stratégie</td><td><a href="#strategie">Stratégie</a></td><td>Hotovo – presný návod pre oba scenáre, hypotéka 30 rokov</td></tr>
<tr><td>2 · Dáta od roku 1950</td><td><a href="#data">Dáta</a></td><td>Španielsko 1950–2025 (JST + predĺženie).</td></tr>
<tr><td>3 · Model-poradca</td><td><a href="#model">Model</a>, <a href="advisor.html">Poradca</a></td><td>Odhad z histórie + simulácia; neurónová sieť na webe</td></tr>
<tr><td>4 · Vyhodnotenie</td><td><a href="#overenie">Overenie</a></td><td>Pre každý rok XY odpoveď len z dát do XY vs. skutočný víťaz</td></tr>
<tr><td>5 · Jeden balík</td><td><a href="#balik">Balík</a></td><td>Výpočet priamo na webe bez inštalácie: zvolený rok, rada modelu, vyhodnotenie (aj notebook pre Colab)</td></tr></table></div></section>

<section id="strategie"><h2>1 · Stratégie <small>jednoznačný návod, pri ktorom každý dostane rovnakú sumu</small></h2>
<p>Dvaja ľudia začínajú 1. januára roku XY s rovnakými úsporami a príjmom a bývajú v byte rovnakej hodnoty (cena = 1,0; všetky sumy sú násobkom ceny). Ročné kroky pre rok k = 1 … H:</p>
<div class="two"><div class="card"><b>Scenár A · podnájom</b><ol class="steps">
<li>Na začiatku investuje <b>30 % ceny</b> (akontácia 20 % + 10 % dane a poplatky, ktoré by pri kúpe zaplatil) do akciového indexu.</li>
<li>Platí nájom: v 1. roku výnos z nájmu v roku XY × cena; potom nájom_k = výnos_k × cena_k (z dát).</li>
<li>Má rovnaký rozpočet na bývanie ako kupujúci; <b>čo ušetrí oproti kupujúcemu, na konci roka investuje</b> do indexu.</li>
<li>Na konci roka H predá portfólio, zaplatí 21 % zo zisku. <b>Majetok A = portfólio po dani.</b></li></ol></div>
<div class="card"><b>Scenár B · hypotéka</b><ol class="steps">
<li>Kúpi byt za 1,0: 20 % akontácia + 10 % dane/poplatky z vlastných; <b>úver 0,8 na 30 rokov</b>, anuitná ročná splátka, sadzba = dlhodobá sadzba štátnych dlhopisov v roku XY + 1,5 p. b., fixná.</li>
<li>Každý rok platí splátku + údržbu 1,2 % z hodnoty bytu (údržba, IBI, poistenie).</li>
<li>Ak je nájom vyšší než jeho platby, <b>rozdiel na konci roka investuje</b> do toho istého indexu; inak rozdiel dofinancuje z príjmu.</li>
<li>Na konci roka H byt predá (cena podľa dát − 4 % náklady), splatí zostatok úveru, portfólio po dani. <b>Majetok B = predaj − zostatok + portfólio.</b></li></ol></div></div>
<p>Rozpočet na bývanie je v oboch scenároch rovnaký, takže príjem nerozhoduje a zostáva presne jedno číslo: <b>výhoda = B − A</b> (nominálne, aj reálne – v peniazoch roku XY po odpočítaní inflácie CPI). Kód: <code>simulate()</code> v <code>model.py</code>. <b>Príklad:</b> nákup v roku __EXS__ za __EXP__ s horizontom __EXH__ rokov skončil s majetkom hypotéky __EXB__ a prenájmu __EXR__ (v eurách roku __EXS__) – vyhral <b>__EXW__</b>.</p>
<p class="cap">Zjednodušenia: celoštátne ceny a nájmy, daň zo zisku z predaja bytu 0 % (hlavné bývanie), rovnaké daňové a nákladové pravidlá v celom období (dnešné dane aplikované spätne), konštantná sadzba (bez refinancovania) a rozhodnutie sa počas obdobia nemení.</p></section>

<section id="data"><h2>2 · Dáta <small>odkiaľ sú a ako sme odhadli chýbajúce</small></h2>
<div class="tw"><table><tr><th>Veličina</th><th>Obdobie</th><th>Zdroj</th><th>Odhad / slabina</th></tr>
<tr><td>Rast cien bytov</td><td>1950–2020 / 2021–25</td><td>JST Macrohistory (R6) / BIS (Španielsko)</td><td>Ceny pred 1971 JST dopočítava z nájmov – orientačné</td></tr>
<tr><td>Výnos z nájmu (nájom ÷ cena)</td><td>1950–2020 / 2021–25</td><td>JST / vlastný výpočet z HICP „skutočné nájmy“ a cien</td><td>Rad 2021–25 je pokračovanie ceny a nájmu od posledného bodu JST</td></tr>
<tr><td>Rast akcií (celková návratnosť)</td><td>1950–2020 / 2021–25</td><td>JST (španielske akcie) / MSCI World v EUR + 2 % dividend</td><td>Zmena indexu v roku 2021 (svetové akcie namiesto španielskych); dividendy sú odhad</td></tr>
<tr><td>Sadzba hypotéky</td><td>1950–2025</td><td>JST dlhodobá sadzba (od 2021 ECB 10-r. výnos ES) + 1,5 p. b.</td><td>Hypotéky pred 90. rokmi neboli bežné; marža je predpoklad</td></tr>
<tr><td>Inflácia</td><td>1950–2025</td><td>JST CPI / HICP (ECB)</td><td>–</td></tr>
<tr><td>Dane a náklady</td><td>celé obdobie</td><td>dnešné pravidlá (AEAT, Junta de Andalucía)</td><td>Spätná aplikácia; nepravdivá pre roky pred 80. rokmi</td></tr></table></div>
<details><summary>Predpoklady modelu – tabuľka (dane, náklady, sadzby)</summary>__ASSUMP__</details>
<p>Podrobne je to v <a href="https://github.com/adibuj2804/rent-vs-buy/blob/main/data/SOURCES.md">SOURCES.md</a>. Správa sa venuje Španielsku a Málage. Ceny pre samotnú Málagu existujú až od roku 2005, preto <b>dlhá história od roku 1950 používa celoštátne španielske dáta ako zástupcu Málagy</b>. Dáta stačia na to, aby pre každý začiatočný rok od 1950 (kým obdobie leží v dátach) mali stratégie jasného víťaza.</p></section>

<section id="model"><h2>3 · Model <small>čo berie na vstupe a ako dospeje k odpovedi</small></h2>
<p><b>Model „odhad z histórie“</b> (typ B zo zadania – sústava malých modelov + simulácia) pracuje len s dátami do roku XY:</p>
<ol class="steps"><li><b>Odhad</b> rastu cien bytov, rastu nájmov a výnosu akcií = geometrický priemer za posledných 20 rokov (<code>known_inputs</code>). Výnos z nájmu a dlhodobú sadzbu berie z roku XY.</li>
<li><b>Simulácia</b>: obe stratégie sa vypočítajú pre horizont H s týmito konštantnými hodnotami (rovnaký <code>simulate()</code>).</li>
<li><b>Odpoveď</b>: „hypotéka“, ak majetok B &gt; A, inak „podnájom“.</li></ol>
<p><b>Model s návratom k priemeru</b> je ten istý, ale polovica odhadu sa nahradí dlhodobým priemerom zo všetkých rokov do XY. <b>Pozor:</b> túto druhú verziu sme pridali až po prvom behu, keď sme videli, že čistá extrapolácia posledných 20 rokov zlyháva po boome – je to teda voľba spravená po pohľade na výsledky a hodnotí sa menej prísne než prvá.</p>
<p><b>Neurónová sieť</b> (web, stránka <a href="advisor.html">Poradca</a>) dostane 8 vstupov (horizont, LTV, výnos z nájmu, náklady, očakávaný rast cien, nájmov, akcií, sadzba) a učí sa napodobniť presný model na simulovaných scenároch. Rozsahy vstupov sú široké (ceny −5 až 20 %, sadzby 1–20 %), takže pokrývajú aj vysokú infláciu 50.–90. rokov; na simulovaných scenároch sa s presným modelom zhoduje v __AGR__ % prípadov. Pri vyhodnotení na histórii dostane tie isté odhadnuté vstupy ako model „odhad z histórie“.</p></section>

<section id="overenie"><h2>4 · Vyhodnotenie na histórii <small>pre každý počiatočný rok XY: odpoveď modelu vs. skutočný víťaz</small></h2>
<div class="chart"><canvas id="wfbar"></canvas></div>
<p>Horizont: <select id="wfh"><option>10</option><option>20</option><option>30</option></select> <span class="cap">Stĺpce = skutočná výhoda hypotéky (reálne, podiel ceny). Pod grafom: skutočný víťaz a odpovede modelov pre každý rok (oranžová = hypotéka, modrá = podnájom, ✕ = model sa mýlil).</span></p>
<div id="wfstrip"></div>
<h3>Podiel rokov, v ktorých mal model pravdu</h3>
<div class="tw"><table><tr><th>Horizont</th><th>Počiatočné roky</th><th>Vždy hypotéka</th><th>Vždy podnájom</th><th>Model: odhad z histórie</th><th>Model: s návratom k priemeru</th><th>Neurónová sieť</th></tr>__ROWS__</table></div>
<div class="tw"><table><tr><th>Horizont</th><th>Obdobie nákupu</th><th>Rokov</th><th>Hypotéka vyhrala</th><th>Odhad</th><th>Návrat k priemeru</th></tr>__PER__</table></div>
<div class="note"><b>Ako to čítať:</b> pravdu mal model v 55–67 % rokov pri 10 a 20 rokoch (základ ≈ 50 %); pri 30 rokoch je lepšia stratégia „vždy hypotéka“. Model zlyháva presne tam, kde sa mení režim: po inflácii 70. rokov a po boome 80.–90. rokov odhad z posledných 20 rokov prezerá zmenu. <b>Neurónová sieť</b> dopadla podobne ako odhad: s presným modelom sa zhoduje v __AGR__ %, no jej vstupy – odhady z posledných 20 rokov – nedokážu predpovedať, ktorý režim príde (inflácia, kríza). Chyba je teda v odhadoch vstupov, nie v sieti.</div>
<p class="cap"><b>Čo číslo hovorí a čo nie.</b> Roky sa prekrývajú (okno 10 rokov z roku 1960 a 1961 má 9 spoločných rokov), preto nejde o 66 nezávislých pozorovaní, ale skôr o niekoľko. Rozdiely typu 55 % vs. 50 % nie sú štatisticky významné. Citlivosť na dĺžku okna odhadu (odhad z histórie, podiel správnych rokov): </p>
<div class="tw"><table><tr><th>Okno odhadu</th><th>Horizont 10</th><th>Horizont 20</th><th>Horizont 30</th></tr>__SENS__</table></div>
<p class="cap">Okno 20 rokov bolo zvolené vopred; ostatné sú ukázané len pre úplnosť.</p></section>

<section id="dnes"><h2>5 · Čo by model poradil dnes <small>koniec roku 2025, Španielsko</small></h2>
<p>Odhady z posledných 20 rokov: rast cien __HG__ %, rast nájmov __RG__ %, výnos akcií __EQ__ % ročne, výnos z nájmu __YL__ %, sadzba hypotéky __MR__ %.</p>
<div class="tw"><table><tr><th>Horizont</th><th>Model: odhad z histórie</th><th>Neurónová sieť</th></tr>__TROWS__</table></div>
<p class="cap">Výnos z nájmu 1,5 % (celoštátne dáta JST) je oveľa nižší než 5 %, s ktorými pracuje stránka Málaga (ponukové nájmy v Málage). Preto je odpoveď „podnájom“ pre celoštátnu situáciu; pre vlastné vstupy použite <a href="advisor.html">Poradcu</a>. Vzdelávací model, nie finančné poradenstvo.</p></section>

<section id="balik"><h2>6 · Jeden balík <small>všetko beží priamo na tejto stránke, bez inštalácie</small></h2>
<p>Dáta (ročná tabuľka 1870–2025), kód modelu aj váhy neurónovej siete sú vložené v tejto stránke a výpočty robí prehliadač. Nič sa neinštaluje ani nesťahuje. Nižšie si môžete vypočítať majetok oboch scenárov pre ľubovoľný počiatočný rok, vidieť radu modelu a zopakovať celé vyhodnotenie z kapitoly 4.</p>
<div class="card"><b>A · Majetok v oboch scenároch pre zvolený počiatočný rok</b>
<div class="two" style="margin-top:8px"><label>Počiatočný rok (1950–2015)<input id="cy" type="number" min="1950" max="2015" value="1990"></label>
<label>Horizont (roky, 1–30)<input id="ch" type="number" min="1" max="30" value="10"></label></div>
<label>Cena bytu (€)<input id="cp" type="number" value="250000"></label>
<p><button class="go" id="cgo">Vypočítať</button></p><div id="cout"></div></div>
<div class="card"><b>B · Vyhodnotenie na histórii, prepočítané vo vašom prehliadači</b>
<p class="cap">Rovnaký postup ako v kapitole 4, ale celý výpočet (skutočný víťaz, odhad z histórie, sieť) sa spustí teraz v JavaScripte. Čísla sa musia zhodovať s tabuľkou vyššie (tá bola vypočítaná v Pythone).</p>
<p><button class="go" id="ego">Spustiť vyhodnotenie</button></p><div id="eout"></div></div>
<p class="cap">Voliteľne: ten istý výpočet v Pythone ako notebook pre Google Colab – <a href="https://colab.research.google.com/github/adibuj2804/rent-vs-buy/blob/main/notebooks/podnajom_alebo_hypoteka.ipynb">otvoriť v Colabe</a> · <a href="podnajom_alebo_hypoteka.ipynb" download>stiahnuť</a>.</p>
<details><summary>Kód výpočtu v prehliadači (JavaScript, beží na tejto stránke)</summary><pre>__JSCODE__</pre></details>
<details><summary>walkforward.py – vyhodnotenie a modely (Python)</summary><pre>__WFCODE__</pre></details>
<details><summary>model.py – výpočet oboch stratégií (Python)</summary><pre>__MODELCODE__</pre></details></section>"""
    body = body.replace("__ASSUMP__", ASSUMP).replace("__AGR__", dec(nn["metrics"]["agreement_with_exact"] * 100)).replace("__BG__", bg("ma-pobrezie.jpg")).replace("__ROWS__", rows).replace("__PER__", per).replace("__SENS__", sens_rows).replace("__TROWS__", trows) \
        .replace("__JSCODE__", html.escape(PREDICT_JS + "\n\n" + CALC_JS)).replace("__WFCODE__", code("src/walkforward.py")).replace("__MODELCODE__", code("src/model.py")) \
        .replace("__BUY10__", p(wf[10]["always_buy"])).replace("__RENT10__", p(wf[10]["always_rent"])) \
        .replace("__E10__", p(wf[10]["estimate"])).replace("__E20__", p(wf[20]["estimate"])).replace("__E30__", p(wf[30]["estimate"])) \
        .replace("__B10__", p(wf[10]["always_buy"])).replace("__B20__", p(wf[20]["always_buy"])).replace("__B30__", p(wf[30]["always_buy"])) \
        .replace("__HG__", dec(inp["house_growth"] * 100)).replace("__RG__", dec(inp["rent_growth"] * 100)).replace("__EQ__", dec(inp["equity_return"] * 100)) \
        .replace("__YL__", dec(inp["gross_yield"] * 100)).replace("__MR__", dec(inp["mortgage_rate"] * 100)) \
        .replace("__EXS__", str(ex["start"])).replace("__EXH__", str(ex["horizon"])).replace("__EXP__", nbsp(ex["price"])) \
        .replace("__EXB__", nbsp(ex["real"]["hypoteka"])).replace("__EXR__", nbsp(ex["real"]["prenajom"])).replace("__EXW__", ex["winner"])
    ann = [[int(r.year)] + [None if pd.isna(v) else round(float(v), 6) for v in (r.cpi, r.ltrate, r.housing_capgain, r.housing_rent_yd, r.eq_tr)] for r in annual.itertuples()]
    script = "const ANNUAL = " + json.dumps(ann) + ";\nconst W = " + json.dumps(nn) + ";\n" + PREDICT_JS + "\n" + CALC_JS + """
const WF = R.walkforward.rows; let chart;
function drawWF(H) {
  const rows = WF[H];
  const cell = (buy, ok) => `<i style="display:inline-block;width:11px;height:11px;margin:1px;background:${buy?COL.buy:COL.rent};font-size:9px;line-height:11px;color:#fff;text-align:center;font-style:normal">${ok?'':'✕'}</i>`;
  const lines = [['Skutočnosť', r=>[r[1], true]], ['Odhad z histórie', r=>[r[2], r[2]===r[1]]], ['S návratom k priemeru', r=>[r[5], r[5]===r[1]]], ['Neurónová sieť', r=>[r[3], r[3]===r[1]]]];
  document.getElementById('wfstrip').innerHTML = '<div class="tw" style="overflow-x:auto;white-space:nowrap"><div class="cap">' + rows[0][0] + ' → ' + rows[rows.length-1][0] + ' (rok nákupu)</div>' +
    lines.map(([n,f]) => '<div><span style="display:inline-block;width:150px;font-size:.85rem">'+n+'</span>' + rows.map(r => { const [b, ok] = f(r); return cell(b, ok); }).join('') + '</div>').join('') + '</div>';
  if (chart) chart.destroy();
  chart = new Chart(document.getElementById('wfbar'), {type:'bar', data:{labels:rows.map(r=>r[0]), datasets:[{label:'Výhoda hypotéky (reálne)', data:rows.map(r=>r[6]), backgroundColor:rows.map(r=>r[6]>0?COL.buy:COL.rent)}]},
    options:{animation:false, plugins:{legend:{display:false}}, scales:{y:{title:{display:true,text:'Hypotéka − podnájom, podiel ceny'}}, x:{ticks:{maxTicksLimit:14}}}}});
}
document.getElementById('wfh').onchange = e => drawWF(e.target.value);
if (location.search.includes('print')) document.querySelectorAll('details').forEach(d => { if (!d.querySelector('pre')) d.open = true; else d.remove(); });
drawWF('10');
"""
    return page("sprava", "Správa a overenie", body, script, [("prehlad", "V skratke"), ("strategie", "Stratégie"), ("data", "Dáta"), ("model", "Model"), ("overenie", "Vyhodnotenie"), ("dnes", "Dnes"), ("balik", "Balík")])


# ------------------------------------------------------------------ dáta
def data_page():
    import pandas as pd, shutil
    P = os.path.join(ROOT, "data/processed")
    for f in ("monthly_2003_2025.csv", "spain_annual_1870_2025.csv", "malaga_valor_tasado_quarterly.csv", "walkforward_spain.csv"):
        shutil.copy(os.path.join(P, f), os.path.join(SITE, "data", f))
    m = pd.read_csv(os.path.join(P, "monthly_2003_2025.csv"), index_col=0)
    an = pd.read_csv(os.path.join(P, "spain_annual_1870_2025.csv"))
    mq = pd.read_csv(os.path.join(P, "malaga_valor_tasado_quarterly.csv"))
    nm = lambda v, d=2: dec(float(v), d)

    def mrow(name, col, what, unit, src, note, d=2):
        x = m[col].dropna()
        return "<tr><td><code>%s</code><br><b>%s</b></td><td>%s</td><td>%s</td><td>%s – %s<br><small>%s → %s</small></td><td>%s</td><td>%s</td></tr>" % (
            col, name, what, unit, x.index[0], x.index[-1], nm(x.iloc[0], d), nm(x.iloc[-1], d), src, note)
    monthly_rows = "".join([
        mrow("Euribor 12M", "euribor12m", "Medzibanková sadzba v eurách na 12 mesiacov; základ variabilných hypoték.", "% ročne", "ECB Data Portal, dataset FM", "Priemer mesiaca. Surový rad siaha od 1994."),
        mrow("Sadzba nových hypoték", "mir_es", "Priemerná úroková sadzba nových úverov domácnostiam na kúpu bývania v Španielsku. Je to sadzba, s ktorou „kupujeme“ v modeli.", "% ročne", "ECB, dataset MIR", "Jediný súvislý oficiálny rad sadzieb hypoték; začína až v roku 2003."),
        mrow("Inflácia (HICP, všetky položky)", "hicp_es", "Index spotrebiteľských cien Španielska.", "index, 2015 = 100", "ECB / Eurostat, dataset ICP", "Používa sa na predĺženie CPI 2021–2025 a na prepočet na reálne hodnoty."),
        mrow("Nájomné (HICP, skutočné nájmy)", "hicp_rent_es", "Index nájomného, ktoré skutočne platia nájomníci v Španielsku.", "index, 2015 = 100", "ECB / Eurostat, dataset ICP", "Celoštátny, nie pre Málagu. Určuje rast nájmu v modeli.", 2),
        mrow("Kurz EUR/USD", "eurusd", "Referenčný kurz ECB (mesačný priemer).", "USD za 1 EUR", "ECB, dataset EXR", "Slúži na prepočet indexu MSCI z dolárov na eurá.", 4),
        mrow("MSCI World, cenový index (USD)", "msci_usd_price", "Akciový index veľkých firiem z rozvinutých krajín, bez dividend.", "body indexu", "MSCI cez Yahoo Finance (ticker ^990100-USD-STRD)", "Denné hodnoty; berie sa posledná hodnota mesiaca.", 1),
        mrow("MSCI World v eurách s dividendami", "msci_eur_tr", "Cenový index prepočítaný na eurá a zvýšený o odhadované dividendy (2 % ročne). Do tohto indexu „investujú“ obe domácnosti.", "body indexu v EUR", "vlastný výpočet", "<b>Dividendy sú náš odhad</b>, skutočný index celkovej návratnosti sa zadarmo stiahnuť nepodarilo.", 1),
        mrow("Ceny bytov, Španielsko (BIS)", "hp_es", "Index cien rezidenčných nehnuteľností v celom Španielsku.", "index, 2010 = 100", "BIS, dataset WS_SPP", "Štvrťročný rad, medzi štvrťrokmi lineárne interpolovaný v logaritmoch.", 1),
        mrow("Ceny bytov, Málaga (MIVAU)", "hp_ma", "Priemerná hodnota tasovaného bytu v obci Málaga podľa bankových tasácií. <b>Hlavný rad pre Málagu.</b>", "€ za m²", "MIVAU (španielske ministerstvo bývania), Boletín Online, tabuľka 35103500", "Sú to tasovacie hodnoty, nie ceny z kúpnych zmlúv. Štvrťročne od 2005-Q1, medzi štvrťrokmi interpolované.", 0),
    ])
    jst_rows = "".join("<tr><td><code>%s</code><br><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in [
        ("housing_capgain", "Rast cien bytov", "Ročná zmena cien bytov v Španielsku (podiel, 0,05 = +5 %).", "JST 1901–2020; od 2021 BIS", "JST: ceny pred 1971 sú dopočítané, rady skákavé", "Z BIS: ročný priemer indexu"),
        ("housing_rent_yd", "Výnos z nájmu", "Ročný nájom ÷ cena bytu (0,03 = 3 %). Z neho sa počíta nájom v 1. roku aj jeho ďalší vývoj.", "JST 1900–2020; od 2021 vlastný výpočet", "JST: odhad zo štatistík nájmov a cien", "Pokračovanie od posledného bodu JST podľa rastu nájmov (HICP) a cien (BIS)"),
        ("eq_tr", "Výnos akcií", "Celková ročná návratnosť akcií vrátane dividend (podiel).", "JST 1900–2020 (španielske akcie); od 2021 MSCI World v EUR", "JST", "<b>Zmena indexu v roku 2021</b>: svetové namiesto španielskych akcií"),
        ("ltrate", "Dlhodobá sadzba", "Výnos 10-ročných štátnych dlhopisov Španielska, % ročne. Sadzba hypotéky = tento výnos + 1,5 p. b.", "JST 1870–2020; od 2021 ECB", "JST", "ECB 10-ročný výnos ES (v rokoch 2015–2020 sa zhoduje s JST)"),
        ("cpi", "Index spotrebiteľských cien", "Slúži na prepočet na reálne hodnoty (peniaze roku nákupu).", "JST 1870–2020; od 2021 HICP", "JST", "HICP ES, napojené na JST"),
    ])
    prev = an[(an.year >= 1950)].copy()
    prev_rows = "".join("<tr%s><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        ' style="background:var(--warn)"' if r.source == "extension" else "", r.year, nm(r.housing_capgain * 100, 1) + " %", nm(r.housing_rent_yd * 100, 1) + " %", nm(r.eq_tr * 100, 1) + " %",
        nm(r.ltrate, 2) + " %", nm(r.cpi, 1), "predĺženie" if r.source == "extension" else "JST") for r in prev.itertuples())
    mq_rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (r.period, nm(r.total, 0)) for r in mq.iloc[[0, 1, 2, 3, -4, -3, -2, -1]].itertuples())
    body = """<div class="hero" __BG__><span class="tag">Dáta</span><h1>Aké dáta sme použili a čo v nich je</h1>
<p>Každý rad s jednotkou, obdobím, zdrojom a slabinami – a to, čo sme museli odhadnúť.</p></div>
<section id="prehlad"><div class="sum"><b class="h">V skratke</b>
Používame <b>dve skupiny dát</b>: (1) <b>mesačné rady 2003–2025</b> pre podrobný model Málagy (sadzby, ceny bytov, nájmy, akcie) a (2) <b>ročný rad Španielska 1870–2025</b> pre dlhú históriu od roku 1950. Dôvod: oficiálne ceny pre samotnú Málagu existujú až od roku 2005, takže <b>dlhá história používa celé Španielsko ako zástupcu Málagy</b>. Všetky súbory sú dole na stiahnutie.</div></section>

<section id="mesacne"><h2>1 · Mesačné rady (2003–2025) <small>podrobný model Málagy; súbor monthly_2003_2025.csv, 276 riadkov</small></h2>
<div class="tw"><table><tr><th>Rad</th><th>Čo obsahuje</th><th>Jednotka</th><th>Obdobie (prvá → posledná hodnota)</th><th>Zdroj</th><th>Poznámka</th></tr>__MROWS__</table></div>
<div class="chart"><canvas id="d1"></canvas></div><p class="read">Oficiálna cena bytu v Málage (tasovacia hodnota) v €/m². Vrchol 2007, pád o takmer polovicu do 2014, potom oživenie.</p>
<div class="chart"><canvas id="d2"></canvas></div><p class="read">Sadzby: Euribor 12M a priemerná sadzba nových hypoték v Španielsku.</p>
<details><summary>Ukážka dát: ceny v Málage po štvrťrokoch (malaga_valor_tasado_quarterly.csv, __NQ__ riadkov)</summary><div class="tw"><table><tr><th>Štvrťrok</th><th>Valor tasado, €/m²</th></tr>__MQROWS__</table></div></details></section>

<section id="rocne"><h2>2 · Ročný rad Španielska (1870–2025) <small>dlhá história od roku 1950; súbor spain_annual_1870_2025.csv</small></h2>
<p>Základom je databáza <b>Jordà–Schularick–Taylor Macrohistory Database</b> (vydanie R6; akademická databáza ekonómov Jordàa, Schularicka, Taylora a ďalších). Obsahuje ročné ceny bytov, nájmy, výnosy akcií, sadzby a inflácie pre 18 krajín od roku 1870. My berieme Španielsko. Databáza končí rokom 2020, preto sme roky 2021–2025 <b>doplnili z ECB, BIS a MSCI</b> (žlto v tabuľke nižšie).</p>
<div class="tw"><table><tr><th>Stĺpec</th><th>Čo obsahuje</th><th>Zdroj do 2020 / od 2021</th><th>Slabina v JST</th><th>Ako sme doplnili 2021–2025</th></tr>__JROWS__</table></div>
<div class="chart"><canvas id="d3"></canvas></div><p class="read">Ročný rast cien bytov, výnos akcií a výnos 10-ročných dlhopisov v Španielsku, 1950–2025. Vidno infláciu 70.–80. rokov (vysoké sadzby) a pokles po roku 2000.</p>
<div class="chart"><canvas id="d4"></canvas></div><p class="read">Výnos z nájmu (ročný nájom ÷ cena bytu). Od 50. rokov klesol z 3 % na 1,5 %: byty zdraželi oveľa viac než nájmy.</p>
<details><summary>Celá tabuľka 1950–2025 (kliknite pre rozbalenie)</summary><div class="tw" style="max-height:420px;overflow:auto"><table><tr><th>Rok</th><th>Rast cien bytov</th><th>Výnos z nájmu</th><th>Výnos akcií</th><th>Dlhodobá sadzba</th><th>CPI</th><th>Zdroj</th></tr>__PROWS__</table></div></details></section>

<section id="odhady"><h2>3 · Čo sme museli odhadnúť <small>dáta, ktoré sa nenašli</small></h2>
<div class="tw"><table><tr><th>Čo</th><th>Prečo chýba</th><th>Ako sme to odhadli</th></tr>
<tr><td>Ceny bytov v Málage pred rokom 2005</td><td>MIVAU zverejňuje rad od 2005-Q1</td><td>Pre dlhú históriu používame celoštátne španielske ceny z JST a BIS ako zástupcu Málagy.</td></tr>
<tr><td>Ceny bytov v Španielsku 1950–1970</td><td>Úrovne cien existujú od roku 1971</td><td>JST ich dopočítava z nájmov a nákladov; rad je „skákavý“ (napr. +45 % a potom −23 %). Berte ako orientačné.</td></tr>
<tr><td>Výnos z nájmu v Málage</td><td>Oficiálny lokálny rad (SERPAVI) nejde stiahnuť (chránený reCAPTCHA)</td><td>Pre mesačný model predpoklad 5 % z portálov; ako kontrola poslúžil údaj SERPAVI 2023 (8,9 €/m²), ktorý dáva výnos 4,7 %. Citlivosť na túto hodnotu je na stránke Málaga.</td></tr>
<tr><td>Dividendy MSCI World</td><td>Skutočný index celkovej návratnosti sme nezískali</td><td>Cenový index + 2 % ročne (konštanta <code>MSCI_NET_DIVIDEND_YIELD</code> v kóde).</td></tr>
<tr><td>Sadzba hypotéky 1950–2002</td><td>Rad sadzieb hypoték existuje od 2003</td><td>Dlhodobý výnos štátnych dlhopisov + 1,5 percentuálneho bodu.</td></tr>
<tr><td>Roky 2021–2025 v ročnom rade</td><td>JST končí rokom 2020</td><td>Ceny z BIS, nájmy z HICP, akcie z MSCI World v EUR, sadzba z ECB (skript <code>extend_spain.py</code>).</td></tr>
<tr><td>Dane a poplatky</td><td>Nie sú dáta, sú to pravidlá</td><td>Dnešné pravidlá platia pre celé obdobie (kúpa 10 %, predaj 4 %, údržba 1,2 % ročne, daň zo zisku z investícií 21 %): spätne to nie je presné.</td></tr></table></div></section>

<section id="uprava"><h2>4 · Ako sme dáta upravili</h2>
<ol class="steps"><li><b>Stiahnutie.</b> ECB (cez API SDMX), BIS, Yahoo Finance, Excel MIVAU a CSV databázy JST; uložené v <code>data/raw</code>.</li>
<li><b>Zarovnanie na mesiace.</b> Všetko sa spojí podľa mesiaca; spoločný koniec je 2025-12 (tam končí HICP).</li>
<li><b>Štvrťročné rady</b> (BIS, MIVAU) sa na mesiace prevedú tak, že hodnota štvrťroka platí pre posledný mesiac štvrťroka a medzi nimi sa lineárne interpoluje v logaritmoch.</li>
<li><b>MSCI</b>: posledná denná hodnota mesiaca, prepočet na EUR kurzom ECB a zvýšenie o 2 % ročne za dividendy.</li>
<li><b>Ročný rad</b>: JST pre Španielsko; roky 2021–2025 doplnené skriptom <code>extend_spain.py</code>.</li>
<li><b>Reálne hodnoty</b>: výsledky z dlhej histórie sa delia indexom CPI, takže sú v peniazoch roku nákupu.</li></ol></section>

<section id="stiahnutie"><h2>5 · Dáta na stiahnutie</h2>
<ul><li><a href="data/monthly_2003_2025.csv" download>monthly_2003_2025.csv</a> – mesačná tabuľka (všetky rady vyššie)</li>
<li><a href="data/spain_annual_1870_2025.csv" download>spain_annual_1870_2025.csv</a> – ročná tabuľka Španielska (stĺpec <code>source</code> = JST / extension)</li>
<li><a href="data/malaga_valor_tasado_quarterly.csv" download>malaga_valor_tasado_quarterly.csv</a> – štvrťročné ceny v Málage</li>
<li><a href="data/walkforward_spain.csv" download>walkforward_spain.csv</a> – výsledky vyhodnotenia pre každý rok a horizont</li>
<li>Zoznam všetkých surových súborov a zdrojov: <a href="https://github.com/adibuj2804/rent-vs-buy/blob/main/data/SOURCES.md">SOURCES.md</a></li></ul></section>
<section id="kod"><h2>6 · Kód spracovania dát</h2>__CODE__</section>
<p><a href="sprava.html">→ Správa a overenie (stratégie, model, vyhodnotenie)</a></p>"""
    body = body.replace("__BG__", bg("ma-katedrala.jpg")).replace("__MROWS__", monthly_rows).replace("__JROWS__", jst_rows).replace("__PROWS__", prev_rows) \
        .replace("__MQROWS__", mq_rows).replace("__NQ__", str(len(mq))) \
        .replace("__CODE__", code_block("build_data.py – surové dáta → čisté mesačné tabuľky", "src/build_data.py") + code_block("load_malaga.py – ceny pre Málagu z Excelu ministerstva (MIVAU)", "src/load_malaga.py") + code_block("extend_spain.py – predĺženie ročného radu na roky 2021–2025", "src/extend_spain.py"))
    script = """
const S = R.series, L = R.series_long;
line('d1', S.months, [{label:'Valor tasado, Málaga (€/m²)', data:S.hp_ma_eur_m2, borderColor:COL.buy}], {ytitle:'€/m²'});
line('d2', S.months, [{label:'Euribor 12M (%)', data:S.euribor, borderColor:COL.rent}, {label:'Sadzba nových hypoték, Španielsko (%)', data:S.mir_es, borderColor:COL.buy}], {ytitle:'% ročne'});
line('d3', L.years, [{label:'Rast cien bytov', data:L.housing_capgain.map(v=>v*100), borderColor:COL.buy}, {label:'Výnos akcií', data:L.eq_tr.map(v=>v*100), borderColor:COL.rent}, {label:'Výnos 10-r. dlhopisov', data:L.ltrate, borderColor:COL.mut, borderDash:[5,4]}], {ytitle:'% ročne'});
line('d4', L.years, [{label:'Výnos z nájmu', data:L.rent_yield.map(v=>v*100), borderColor:COL.buy}], {ytitle:'% ceny bytu ročne'});
"""
    return page("data", "Dáta", body, script, [("mesacne", "Mesačné rady"), ("rocne", "Ročný rad"), ("odhady", "Čo sme odhadli"), ("uprava", "Úprava dát"), ("stiahnutie", "Na stiahnutie"), ("kod", "Kód")])


for slug, content in [("index", index_page()), ("malaga", city_page("ES")), ("advisor", advisor_page()), ("sprava", sprava_page()), ("data", data_page())]:
    open(os.path.join(SITE, "%s.html" % slug), "w", encoding="utf-8").write(content)
    print("zapísané", slug, len(content) // 1024, "KB")
