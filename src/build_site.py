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
footer{margin-top:60px;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:.86rem}
"""

NAV = [("index", "Úvod"), ("malaga", "Málaga"), ("bratislava", "Bratislava"), ("advisor", "Poradca")]


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

ASSUMP = """<div class="tw"><table><tr><th>Predpoklad</th><th>Španielsko / Málaga</th><th>Slovensko / Bratislava</th><th>Zdroj / základ</th></tr>
<tr><td>LTV</td><td colspan="2">80 %</td><td>Bežná prax bánk (ES); limity NBS 80–90 % (SK)</td></tr>
<tr><td>Dane a poplatky pri kúpe</td><td>10 %</td><td>0,6 %</td><td>ES: daň z prevodu ITP 7 % + notár, register (Junta de Andalucía). SK: bez dane z prevodu, poplatok katastru + právnik</td></tr>
<tr><td>Náklady pri predaji</td><td>4 %</td><td>3 % (+19 % daň zo zisku pri predaji do 5 rokov)</td><td>Provízia makléra, obecná plusvalía</td></tr>
<tr><td>Údržba + daň z nehnuteľnosti</td><td>1,2 % hodnoty ročne</td><td>1,05 % hodnoty ročne</td><td>IBI, poplatky spoločenstva, opravy</td></tr>
<tr><td>Splatnosť úveru</td><td>25 rokov</td><td>30 rokov</td><td>INE (priemer), maximum NBS</td></tr>
<tr><td>Hrubý výnos z prenájmu v 1. roku</td><td>5,0 %</td><td>4,5 %</td><td>Ponukové nájmy z portálov (idealista, realitymap) – <b>nie oficiálne dáta</b>; preto robíme test citlivosti</td></tr>
<tr><td>Rast nájmu</td><td colspan="2">Skutočný index HICP „skutočné nájomné za bývanie“</td><td>ECB / Eurostat</td></tr>
<tr><td>Sadzba hypotéky</td><td colspan="2">Sadzba nových hypoték v čase kúpy (ECB MIR); buď fixná na celú dobu, alebo Euribor 12M + pôvodná marža</td><td>ECB MIR, Euribor</td></tr>
<tr><td>Investovanie</td><td colspan="2">MSCI World v EUR + 2 % odhadované čisté dividendy</td><td>Cenový index MSCI, <b>dividendy sú náš odhad</b></td></tr>
<tr><td>Daň zo ziskov z investícií</td><td>21 % pri speňažení (plochá aproximácia 19–30 %)</td><td>0 % (po 1 roku oslobodené)</td><td>AEAT; zákon o dani z príjmov SR</td></tr>
<tr><td>Pravidlo férovosti</td><td colspan="3">Obe domácnosti míňajú mesačne rovnako. Kto má bývanie lacnejšie, rozdiel investuje. Nájomník navyše hneď na začiatku investuje vlastné zdroje a poplatky, ktoré by išli do kúpy.</td></tr></table></div>"""

ZDROJE = """<ul>
<li><b>ECB Data Portal</b> (SDMX API): Euribor 12M, sadzby hypoték (ES od 2003, SK od 2008), inflácia HICP a „skutočné nájomné“, kurz EUR/USD – <a href="https://data.ecb.europa.eu">data.ecb.europa.eu</a></li>
<li><b>MIVAU (Ministerio de Vivienda y Agenda Urbana)</b> – <i>valor tasado</i> priemerná hodnota tasovaného bytu v obci Málaga, štvrťročne od 2005-Q1 do 2026-Q2 – <a href="https://apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS">tabuľka v Exceli</a></li>
<li><b>Národná banka Slovenska</b> – ceny nehnuteľností na bývanie podľa krajov v €/m², štvrťročne od 2005-Q1 do 2026-Q3 (ponukové ceny) – <a href="https://nbs.sk/export/sk/real-estate-price-by-region/csv">CSV</a></li>
<li><b>BIS</b> – ceny rezidenčných nehnuteľností (nominálny index; Španielsko od 1971, Slovensko od 2006) – <a href="https://data.bis.org/topics/RPP">data.bis.org</a></li>
<li><b>MSCI World</b> – cenový index v USD, denné údaje od 1972 (Yahoo Finance), prepočet na EUR podľa ECB; dividendy 2 % ročne sú <i>odhad</i></li>
<li><b>Jordà–Schularick–Taylor Macrohistory Database</b>, vydanie R6 (1870–2020) – <a href="https://www.macrohistory.net/database/">macrohistory.net</a>. Jordà, Knoll, Kuvshinov, Schularick, Taylor (2019): „The Rate of Return on Everything, 1870–2015“, <i>Quarterly Journal of Economics</i></li>
<li><b>Dane a náklady</b>: Junta de Andalucía (ITP), AEAT, katastrálny portál SR / NBS – z úvodnej rešerše (<code>Claude.pdf</code>); údaje prevzaté z médií je vhodné overiť na primárnych portáloch.</li>
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
    ES = city == "ES"
    name = "Málaga" if ES else "Bratislava"
    slug = "malaga" if ES else "bratislava"
    hp, rent = ("hp_ma", "rent_es") if ES else ("hp_ba", "rent_sk")
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
<li><b>Nájmy:</b> oficiálny lokálny rad (SERPAVI) sa automaticky stiahnuť nedá (aplikácia chránená reCAPTCHA). Preto rast nájmov je celoštátny index HICP a <b>počiatočný výnos 5 %% je predpoklad</b>. Kontrola: nájom 8,9 €/m² mesačne (SERPAVI 2023, podľa našej rešerše) voči oficiálnej cene za 2023 dáva výnos <b>%s %%</b>, teda blízko predpokladu.</li>
<li><b>Porovnanie s celoštátnym indexom:</b> keby sme použili ceny celého Španielska (BIS), kúpa by vyhrala v %s mesiacov po 5 rokoch a v %s po 10 rokoch – záver sa teda nemení.</li></ul></div>""" % (
            dec(mf["first"][1], 0), mf["last_quarter"][0].replace("-", " "), dec(mf["last_quarter"][1], 0), mf["peak"][0], dec(mf["peak"][1], 0), mf["trough"][0], dec(mf["trough"][1], 0),
            dec(abs(mf["peak_to_trough"]) * 100, 0), dec((mf["last_quarter"][1] / mf["peak"][1] - 1) * 100, 0), dec(mf["implied_yield_2023"] * 100), pct(nat["5"]), pct(nat["10"]))
        tier_note = "2005"
    else:
        zhrnutie = ("Bratislava má takmer nulové náklady pri kúpe a zisky z ETF po roku oslobodené od dane. Kúpa vyhrala v <b>%s</b> testovaných mesiacov pri 5-ročnom a v <b>%s</b> pri 10-ročnom horizonte – teda približne <b>vyrovnané</b>. "
                    "Rozhoduje najmä nájom: pri výnose %s %% vyhráva kúpa len v %s, pri %s %% až v %s. "
                    "Rýchly rast cien (od 2006 ≈ %s %% ročne) pomáhal kupujúcim, no mnohí z nich kupovali pri vysokých sadzbách po roku 2008.") % (
            pct(w5), pct(w10), dec(s["yield"][0][0] * 100), pct(s["yield"][0][1]), dec(s["yield"][3][0] * 100), pct(s["yield"][3][1]),
            dec(res["defaults"]["house_growth_SK"] * 100))
        hero_img, lead = "ba-hrad.jpg", "Kontrastný prípad: bez dane z prevodu a so ziskami z ETF oslobodenými od dane po roku."
        photos = fig("ba-hrad.jpg", "Bratislavský hrad") + fig("ba-michalska.jpg", "Michalská brána") + fig("ba-most-snp.jpg", "Most SNP a Dunaj")
        bf = res["bratislava_facts"]
        natsk = res["SK_national"]["fixed"]["winshare"]
        scope = """<div class="sum"><b class="h">Aké dáta sú oficiálne pre Bratislavu</b>
<ul><li><b>Ceny:</b> rad Národnej banky Slovenska (NBS) – priemerné ceny nehnuteľností na bývanie v <b>Bratislavskom kraji</b>, štvrťročne od 2005-Q1 (%s €/m²) do %s (%s €/m²). Sú to <b>ponukové ceny</b> z inzercie (nie ceny z kúpnych zmlúv), za byty aj domy, a za celý kraj, nie len mesto.</li>
<li><b>Dva cykly:</b> po vrchole %s (%s €/m²) ceny do %s klesli na %s €/m² (−%s %%). Šok zo sadzieb ich po vrchole %s (%s €/m²) znížil o %s %% (dno %s).</li>
<li><b>Nájmy:</b> oficiálny rad nájmov pre Bratislavu neexistuje. Rast nájmov je celoštátny index HICP. Ponukové nájmy z rešerše (vrátane energií) voči ponukovým cenám NBS dávajú hrubý výnos <b>%s – %s %%</b>, čo je viac než náš predpoklad %s %% – predpoklad je teda skôr opatrný a v teste citlivosti nižšie vidno, ako by sa výsledok zmenil.</li>
<li><b>Porovnanie s celoštátnym indexom:</b> s cenami celého Slovenska (BIS) by kúpa vyhrala v %s mesiacov po 5 rokoch a v %s po 10 rokoch.</li>
<li><b>Model od roku 1950 pre Slovensko nie je možný</b> – krajina nie je v dlhodobých databázach a pred rokom 1990 tu nebol trh s bývaním.</li></ul></div>""" % (
            dec(bf["first"][1], 0), bf["last_quarter"][0].replace("-", " "), dec(bf["last_quarter"][1], 0),
            bf["peak1"][0], dec(bf["peak1"][1], 0), bf["trough1"][0], dec(bf["trough1"][1], 0), dec(abs(bf["trough1"][1] / bf["peak1"][1] - 1) * 100, 0),
            bf["peak2"][0], dec(bf["peak2"][1], 0), dec(abs(bf["peak2_to_trough2"]) * 100, 0), bf["trough2"][0],
            dec(bf["yield_realitymap"] * 100), dec(bf["yield_bencont"] * 100), "4,5", pct(natsk["5"]), pct(natsk["10"]))
        tier_note = "2008"

    tier2 = ""
    toc = [("zhrnutie", "V skratke"), ("trh", "Čo sa dialo na trhu"), ("horizont", "Kedy sa kúpa oplatí"), ("citlivost", "Citlivosť")]
    if ES:
        d = res["tier2"]["decades"]
        fmt = lambda v: "n/a" if v is None else ("%+.0f %%" % (v * 100))
        rows = "".join("<tr><td>%s. roky</td><td>%s</td><td>%s</td></tr>" % (k, pct(v["winshare10"]), fmt(v["median10"])) for k, v in d.items())
        tier2 = """<section id="historia"><h2>Dlhá história 1950–2020 <small>Úroveň 2 · Španielsko celoštátne · reálne hodnoty</small></h2>
<div class="note"><b>Kvalita dát:</b> úrovne cien bytov v Španielsku existujú až od roku 1971. Roky 1950–1970 databáza JST dopočítava z nájomných ukazovateľov a rady sú značne „skákavé“ (napr. +45 % a potom −23 %). Berte ich ako orientačné. Všetko je <b>reálne</b> (očistené o infláciu), s dnešnými daňami a poplatkami a sadzbou hypotéky = dlhodobý výnos štátnych dlhopisov + 1,5 p. b.</div>
<div class="chart"><canvas id="t2"></canvas></div><p class="read">Každý bod = rok nákupu. Nad nulou vyhráva kúpa, pod nulou prenájom s investovaním.</p>
<div class="two"><div class="tw"><table><tr><th>Desaťročie nákupu</th><th>Kúpa vyhráva (10 r.)</th><th>Medián výhody kúpy</th></tr>__ROWS__</table></div>
<div><p>Kúpa sa výrazne oplácala v 50.–70. rokoch (záporné reálne sadzby, rýchly rast cien). Naopak, pri nákupe v 80. rokoch (vysoké sadzby) a pri boome a páde 2000. rokov sa neoplatila. Z __N__ začiatočných rokov vyhrala kúpa po 10 rokoch v __W10__, po 30 rokoch v __W30__.</p></div></div></section>""".replace("__ROWS__", rows).replace("__N__", str(res["tier2"]["n_starts"]["10"])).replace("__W10__", pct(res["tier2"]["winshare"]["10"])).replace("__W30__", pct(res["tier2"]["winshare"]["30"]))
        toc.append(("historia", "Dlhá história 1950+"))
    toc += [("predpoklady", "Predpoklady"), ("kod", "Kód")]

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
<section id="predpoklady"><h2>Predpoklady modelu</h2>__ASSUMP__</section>
<section id="kod"><h2>Kód <small>všetko, čo za výsledkami stojí</small></h2>__CODE__</section>
<p><a href="advisor.html">→ Vyskúšajte poradcu na vlastných číslach</a> · <a href="index.html#zdroje">Zdroje dát</a></p>"""
    body = body.replace("__BG__", bg(hero_img)).replace("__TAG__", "Hlavný prípad" if ES else "Kontrastný prípad").replace("__NAME__", name) \
        .replace("__LEAD__", lead).replace("__PHOTOS__", photos).replace("__ZHR__", zhrnutie).replace("__SCOPE__", scope) \
        .replace("__T__", tier_note).replace("__CARDS__", key_cards(city)).replace("__SENS__", sens_table(city)) \
        .replace("__TIER2__", tier2).replace("__ASSUMP__", ASSUMP) \
        .replace("__EURCHART__", '<div class="chart"><canvas id="c4"></canvas></div><p class="read">' + ("Priemerná tasovaná hodnota bytu v obci Málaga v eurách na m² (oficiálny rad MIVAU)." if ES else "Priemerná ponuková cena nehnuteľností na bývanie v Bratislavskom kraji v eurách na m² (rad NBS).") + '</p>') \
        .replace("__CODE__", code_block("model.py – výpočet kúpa vs. prenájom", "src/model.py") + code_block("build_data.py – surové dáta → čisté tabuľky", "src/build_data.py") + (code_block("load_malaga.py – oficiálny rad cien pre Málagu z Excelu ministerstva", "src/load_malaga.py") if ES else code_block("load_bratislava.py – rad NBS pre Bratislavský kraj", "src/load_bratislava.py")))

    eurjs = """
line('c4', S.months, [{label:'__EURLABEL__', data:S.__EURKEY__, borderColor:COL.buy}], {ytitle:'€/m²'});""".replace("__EURLABEL__", "Valor tasado, Málaga (€/m²)" if ES else "Ponukové ceny, Bratislavský kraj (€/m²)").replace("__EURKEY__", "hp_ma_eur_m2" if ES else "hp_ba_eur_m2")
    t2js = """
const T = R.tier2.by_start;
line('t2', T['10'].map(x=>x[0]), [
 {label:'Horizont 10 rokov', data:T['10'].map(x=>x[1]), borderColor:COL.buy},
 {label:'Horizont 20 rokov', data:T['10'].map(x=>{const f=T['20'].find(y=>y[0]===x[0]);return f?f[1]:null}), borderColor:COL.rent}],
 {ytitle:'Výhoda kúpy (reálne, podiel ceny)', title:'Španielsko: výhoda kúpy podľa roka nákupu'});""" if ES else ""
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
""".replace("__C__", city).replace("__HP__", hp).replace("__RENT__", rent).replace("__HPLABEL__", "Ceny bytov v Málage (MIVAU)" if ES else "Ponukové ceny, Bratislavský kraj (NBS)") + t2js + eurjs
    return page(slug, name, body, script, toc)


# ------------------------------------------------------------------ úvod
def index_page():
    m = nn["metrics"]
    e, k = res["ES"]["fixed"]["winshare"], res["SK"]["fixed"]["winshare"]
    body = """<div class="hero split"><div class="half" __B1__></div><div class="half" __B2__></div>
<div class="txt"><h1>Hypotéka, alebo prenájom a investovanie?</h1><p>Dátová analýza pre Málagu a Bratislavu: čo sa viac oplatí a za akých podmienok.</p></div></div>
<section id="start"><h2>Začnite tu <small>stránky odporúčame prejsť v tomto poradí</small></h2>
<div class="grid">
<a class="card photo-card" href="malaga.html"><img src="img/ma-katedrala.jpg" alt="Málaga"><div><b>1 · Málaga →</b><br><small>Hlavný prípad. Vysoké náklady pri kúpe (≈ 10 %). Podrobný model 2005–2025 aj dlhá história 1950–2020.</small></div></a>
<a class="card photo-card" href="bratislava.html"><img src="img/ba-most-snp.jpg" alt="Bratislava"><div><b>2 · Bratislava →</b><br><small>Kontrastný prípad. Takmer nulové náklady pri kúpe, ETF bez dane. Podrobný model 2008–2025.</small></div></a>
<a class="card photo-card" href="advisor.html"><img src="img/ma-pobrezie.jpg" alt="Poradca"><div><b>3 · Poradca →</b><br><small>Zadajte vlastnú situáciu; neurónová sieť odhadne, ktorá možnosť vás s väčšou pravdepodobnosťou nechá bohatším.</small></div></a></div></section>
<section id="zistenia"><h2>Hlavné zistenia</h2>
<div class="tw"><table><tr><th>Mesto</th><th>Kúpa vyhráva po 5 rokoch</th><th>Kúpa vyhráva po 10 rokoch</th><th>Čo za tým stojí</th></tr>
<tr><td><b>Málaga</b> (Španielsko)</td><td>__E5__</td><td>__E10__</td><td>Nákupné náklady ≈ 10 %, dane z výnosov investícií, výdatný rast svetových akcií.</td></tr>
<tr><td><b>Bratislava</b> (Slovensko)</td><td>__K5__</td><td>__K10__</td><td>Takmer žiadne nákupné náklady, ETF po roku bez dane, ale vysoké sadzby pri nákupe v rokoch 2008–2012.</td></tr></table></div>
<p class="cap">Podiel testovaných mesiacov nákupu (fixná hypotéka), v ktorých mal kupujúci na konci vyšší majetok než nájomník. Nad 50 % = kúpa vyhráva častejšie.</p>
<div class="sum"><b class="h">Hlavná myšlienka</b>O výsledku nerozhoduje „kúpa verzus prenájom“ samo osebe, ale <b>koľko rokov v byte ostanete</b>, <b>aké sú náklady pri kúpe</b>, <b>akú sadzbu získate</b> a <b>aký je nájom vzhľadom na cenu bytu</b>. V Málage prenájom v posledných 20 rokoch zvyčajne vyhrával, v Bratislave je výsledok vyrovnaný a veľmi závisí od výšky nájmu.</div></section>
<section id="postup"><h2>Ako analýza funguje <small>štyri kroky</small></h2>
<ol class="steps"><li><b>Dáta.</b> Sťahujeme oficiálne rady: sadzby hypoték a Euribor (ECB), ceny bytov (BIS), nájomné a inflácia (Eurostat/ECB), akciový index MSCI World a dlhú históriu od roku 1870 (databáza JST).</li>
<li><b>Model.</b> Dve domácnosti míňajú mesačne rovnako. Jedna kúpi byt s hypotékou, druhá prenajíma a rozdiel investuje. Na konci horizontu obe „speňažíme“ a porovnáme majetok.</li>
<li><b>Spätný test.</b> Model spustíme pre každý možný mesiac nákupu v histórii a pre horizonty 1–20 rokov.</li>
<li><b>Neurónová sieť.</b> Sieť sa naučí odhadovať výsledok pre ľubovoľné vstupy – aj ktoré v histórii nenastali (poradca).</li></ol>
<div class="tw"><table><tr><th>Úroveň</th><th>Obdobie</th><th>Frekvencia</th><th>Pokrytie</th><th>Na čo slúži</th></tr>
<tr><td><b>1 · Podrobná</b></td><td>2005 (ES) / 2008 (SK) → 2025</td><td>mesačne</td><td>Málaga aj Bratislava, skutočné sadzby, nájom, výnosy akcií</td><td>Presný bod zvratu a testy citlivosti</td></tr>
<tr><td><b>2 · Dlhá história</b></td><td>1950 → 2020</td><td>ročne</td><td>Španielsko celoštátne (JST). Slovensko nie je dostupné.</td><td>Platí záver aj v iných obdobiach (inflácia, vysoké sadzby, krízy)?</td></tr></table></div>
__GLOS__</section>
<section id="siet"><h2>Neurónová sieť poradcu</h2>
<p>Z lokálnej histórie máme len ~20 rokov, čo je pre sieť príliš málo. Preto scenáre simulujeme: rozsahy vstupov berieme z histórie, k „skutočnému“ priebehu pridávame šum historickej veľkosti a každý scenár označí presný model. Na neviditeľných scenároch dosahuje sieť presnosť <b>__ACC__ %</b> (stále tipovanie väčšinovej odpovede: __BASE__ %) a s presným modelom sa zhoduje v <b>__AGR__ %</b> prípadov. Je to rýchla náhrada modelu, <b>nie nezávislá predpoveď</b>.</p></section>
<section id="obmedzenia"><h2>Známe obmedzenia</h2><ul>
<li>Ceny pre Málagu sú oficiálne (MIVAU valor tasado – hodnoty z tasácií, nie z kúpnych zmlúv). Nájmy pre Málagu ešte nie sú načítané (SERPAVI sa nedá stiahnuť automaticky). Ceny pre Bratislavu sú rad NBS za Bratislavský kraj (ponukové ceny, nie ceny z kúpnych zmlúv); oficiálny rad nájmov pre Bratislavu neexistuje. Rast nájmov je v oboch mestách celoštátny index HICP.</li>
<li>Výnos z nájmu pochádza z portálov (ponukové nájmy); oficiálne nájmy SERPAVI sú výrazne nižšie. Je to najväčšia neistota.</li>
<li>Celková návratnosť MSCI je odhad (cenový index + 2 % dividendy).</li>
<li>Dlhé horizonty majú málo prekrývajúcich sa okien; jedno desaťročie dát je jedno pozorovanie.</li>
<li>Dnešné dane sú aplikované spätne; španielske údaje o bývaní pred rokom 1971 sú dopočítané.</li>
<li>Nejde o finančné poradenstvo.</li></ul></section>
<section id="zdroje"><h2>Zdroje</h2>__ZDROJE__</section>"""
    body = body.replace("__B1__", bg("ma-malagueta.jpg")).replace("__B2__", bg("ba-hrad.jpg")) \
        .replace("__E5__", pct(e["5"])).replace("__E10__", pct(e["10"])).replace("__K5__", pct(k["5"])).replace("__K10__", pct(k["10"])) \
        .replace("__GLOS__", GLOSAR).replace("__ZDROJE__", ZDROJE) \
        .replace("__ACC__", dec(m["holdout_accuracy"] * 100)).replace("__BASE__", dec(m["majority_baseline"] * 100)).replace("__AGR__", dec(m["agreement_with_exact"] * 100))
    return page("index", "Úvod", body, "", [("start", "Začnite tu"), ("zistenia", "Hlavné zistenia"), ("postup", "Ako to funguje"), ("siet", "Neurónová sieť"), ("obmedzenia", "Obmedzenia"), ("zdroje", "Zdroje")])


# ------------------------------------------------------------------ poradca
def advisor_page():
    m = nn["metrics"]
    d = res["defaults"]
    js_predict = """// Dopredný prechod natrénovanej siete (9 vstupov -> 64 -> 64 -> 2 výstupy)
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
    body = """<div class="hero" __BG__><span class="tag">Interaktívny nástroj</span><h1>Poradca: ktorá možnosť sa hodí vám?</h1>
<p>Vyplňte tri krátke časti. Neurónová sieť odhadne pravdepodobnosť, že kúpa s hypotékou vás po zvolenom čase nechá bohatším než prenájom s investovaním.</p></div>
<div class="note"><b>Najprv si prečítajte:</b> je to vzdelávací model, nie finančné poradenstvo. Sieť napodobňuje presný model projektu na simulovaných scenároch; výsledok je taký dobrý, ako sú vaše predpoklady. Predvyplnené hodnoty sú historické priemery 2006–2025 – nie predpoveď.</div>
<div class="adv"><div>
<fieldset><legend>1 · Vaša situácia</legend>
<label>Mesto<select id="city"><option value="0">Málaga (Španielsko)</option><option value="1">Bratislava (Slovensko)</option></select></label>
<label>Čistý mesačný príjem (€)<small>Slúži len na kontrolu splátky; predpokladáme, že príjem stačí na oba spôsoby.</small><input id="inc" type="number" value="3200"></label>
<label>Cena nehnuteľnosti (€)<input id="price" type="number" value="280000"></label>
<label>Úspory na akontáciu a poplatky (€)<small>Z nich sa platia aj dane a poplatky pri kúpe.</small><input id="dep" type="number" value="70000"></label>
<label>Ako dlho tam plánujete bývať? (roky, 2–25)<input id="yrs" type="number" value="10" min="2" max="25"></label>
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
<p>Deväť vstupov → dve skryté vrstvy po 64 neurónoch (ReLU) → dva výstupy: pravdepodobnosť, že vyhrá kúpa, a očakávaný rozdiel majetku. Trénovaná algoritmom Adam na __NTR__ simulovaných scenároch, otestovaná na __NTE__ neviditeľných: presnosť <b>__ACC__ %</b> (základ __BASE__ %), Brierovo skóre __BRIER__, zhoda s presným modelom __AGR__ %. Šum v simulovaných cenách používa historickú volatilitu (byty __SDH__ %/rok, akcie __SDE__ %/rok), preto pravdepodobnosť odráža trhovú neistotu.</p>
<p>Rozdiel majetku sa učil na výsledku bez šumu: medián chyby __GM__ % ceny, v 90 % prípadov do __GP__ % ceny (≈ __GPE__ € pri byte za 280 000 €). Ak je pravdepodobnosť pod 50 %, ale rozdiel kladný, nejde o chybu – zisky z kúpy v dobrých scenároch môžu byť väčšie než straty v zlých.</p>
<div class="chart"><canvas id="cal"></canvas></div><p class="read">Ak bodky sledujú diagonálu, sieť je kalibrovaná: keď tvrdí 70 %, kúpa naozaj vyhrá asi v 70 % prípadov.</p></section>
<section id="kod"><h2>Kód</h2>
<details open><summary>Predikcia v prehliadači (beží na tejto stránke)</summary><pre>__JS__</pre></details>
__C1____C2__</section>
<section><h2>Obmedzenia poradcu</h2><ul><li>Ignoruje vašu osobnú daňovú situáciu nad rámec pravidiel mesta, riziko straty práce a iné využitie peňazí.</li><li>Vstupy mimo tréningových rozsahov (LTV pod 50 % alebo nad 90 %, horizont nad 25 rokov) sa orežú a zobrazí sa upozornenie.</li><li>Dvadsať rokov lokálnej histórie nestačí na overenie siete proti skutočným výsledkom; overuje sa voči presnému modelu.</li></ul></section>"""
    body = body.replace("__BG__", bg("ba-most-snp.jpg")).replace("__RATE__", "%.2f" % (d["mortgage_rate_ES"] * 100)) \
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
$('city').onchange = () => {
  const sk = $('city').value === '1';
  $('rate').value = ((sk ? D.mortgage_rate_SK : D.mortgage_rate_ES)*100).toFixed(2);
  $('hg').value = ((sk ? D.house_growth_SK : D.house_growth_ES)*100).toFixed(1);
  $('rg').value = ((sk ? D.rent_growth_SK : D.rent_growth_ES)*100).toFixed(1);
  $('yld').value = sk ? 4.5 : 5.0;
  $('u35').disabled = sk;
};
$('go').onclick = () => {
  const sk = +$('city').value, price = +$('price').value, dep = +$('dep').value, inc = +$('inc').value;
  const warn = [];
  const buyCost = sk ? 0.006 : ($('u35').value === '1' ? 0.065 : 0.10);
  // úspory pokryjú akontáciu A náklady pri kúpe; zvyšok ceny je úver
  let ltv = 1 - (dep - buyCost*price) / price;
  if (ltv > 0.9) { warn.push('Vaše úspory sú pod 10 % akontácie plus poplatky; LTV bolo obmedzené na 90 %.'); ltv = 0.9; }
  if (ltv < 0.5) { warn.push('Akontácia presahuje 50 % ceny; LTV bolo obmedzené na 50 % (tréningový rozsah).'); ltv = 0.5; }
  const yrs = Math.min(25, Math.max(2, Math.round(+$('yrs').value)));
  const x = [sk, yrs, ltv, +$('yld').value/100, buyCost, +$('hg').value/100, +$('rg').value/100, +$('eq').value/100, +$('rate').value/100];
  const r = predict(W, x);
  const term = sk ? 30 : 25, i = x[8]/12, n = term*12;
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


for slug, content in [("index", index_page()), ("malaga", city_page("ES")), ("bratislava", city_page("SK")), ("advisor", advisor_page())]:
    open(os.path.join(SITE, "%s.html" % slug), "w", encoding="utf-8").write(content)
    print("zapísané", slug, len(content) // 1024, "KB")
