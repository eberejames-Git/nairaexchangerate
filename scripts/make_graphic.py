"""Render the daily rate graphics from the site data in index.html.

Usage:  python3 scripts/make_graphic.py
Writes: social/rates-square.png  (1080x1080, Facebook / Instagram)
        social/rates-wide.png    (1600x900,  X / Twitter)
        social/caption.txt       (ready-to-paste caption)
"""
import json, re, os, datetime
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
D = json.loads(re.search(r'id="site-data">(.*?)</script>', html, re.S).group(1))
cbn, par = D["cbn"], D["parallel"]

def money(v, dp=2):
    return f"{v:,.{dp}f}"

def nice(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return d.strftime("%a %-d %b %Y")

def when(iso):
    s = nice(iso)
    return s + (f", {iso[11:16]}" if len(iso) > 10 else "")

today = datetime.date.today().strftime("%A %-d %B %Y")
main = [("usd", "US Dollar", "$"), ("gbp", "British Pound", "£"), ("eur", "Euro", "€")]
extra = [("cny", "CNY"), ("aed", "AED"), ("zar", "ZAR"), ("chf", "CHF")]

def card(code, name, sym):
    r = cbn["rates"][code]
    return f"""<div class="rate"><div class="sym">{sym}1</div><div class="nm">{name}</div>
      <div class="v">₦{money(r['middle'])}</div><div class="bs">Buy {money(r['buy'])} · Sell {money(r['sell'])}</div></div>"""

def page(w, h, wide):
    rates = "".join(card(*m) for m in main)
    mini = "".join(f"<span><b>{c}</b> ₦{money(cbn['rates'][k]['middle'])}</span>" for k, c in extra if k in cbn["rates"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:{w}px;height:{h}px;font-family:Inter,'Inter Display',Arial,sans-serif;background:#7d0a1c;color:#fff;overflow:hidden}}
.wrap{{position:absolute;inset:0;padding:{56 if not wide else 52}px {64 if not wide else 72}px;display:flex;flex-direction:column;
  background:radial-gradient(120% 90% at 100% 0%,#c8102e 0%,#a00c24 40%,#6a0817 100%)}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.logo{{display:flex;align-items:center;gap:16px;font-family:'Inter Display',Inter;font-weight:900;font-size:{38 if not wide else 36}px;letter-spacing:-.02em}}
.logo i{{display:grid;place-items:center;width:58px;height:58px;border-radius:14px;background:#fff;color:#7d0a1c;font-style:normal;font-size:36px}}
.date{{font-weight:700;font-size:26px;background:rgba(0,0,0,.22);padding:10px 20px;border-radius:999px}}
h1{{font-family:'Inter Display',Inter;font-weight:900;font-size:{78 if not wide else 70}px;letter-spacing:-.03em;line-height:1;margin-top:{44 if not wide else 30}px}}
.sub{{font-size:26px;font-weight:600;color:#ffd7dc;margin-top:12px}}
.grid{{display:grid;grid-template-columns:{'1fr' if not wide else '1fr 1fr 1fr'};gap:{16 if not wide else 20}px;margin-top:{30 if not wide else 28}px}}
.rate{{background:#fff;color:#140a0c;border-radius:22px;padding:{'20px 28px' if not wide else '24px 26px'};display:grid;
  grid-template-columns:{'110px 1fr auto' if not wide else '1fr'};grid-template-areas:{'"sym nm v" "sym bs v"' if not wide else '"sym" "nm" "v" "bs"'};align-items:center;column-gap:20px}}
.sym{{grid-area:sym;font-family:'Inter Display';font-weight:900;font-size:{50 if not wide else 40}px;color:#c8102e}}
.nm{{grid-area:nm;font-weight:800;font-size:{26 if not wide else 24}px}}
.v{{grid-area:v;font-family:'Inter Display';font-weight:900;font-size:{58 if not wide else 54}px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.bs{{grid-area:bs;font-size:20px;font-weight:600;color:#3d3134;font-variant-numeric:tabular-nums}}
.mini{{display:flex;flex-wrap:wrap;gap:12px 26px;margin-top:{20 if not wide else 18}px;font-size:24px;font-weight:600;color:#ffe3e6}}
.mini b{{color:#fff;font-weight:900}}
.dealer{{margin-top:auto;background:#140a0c;border-radius:22px;padding:22px 28px;display:flex;justify-content:space-between;align-items:center;gap:20px}}
.dealer .l{{font-size:22px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#ff8a98}}
.dealer .t{{font-size:18px;color:#cdbfc2;margin-top:6px;font-weight:600}}
.dealer .q{{display:flex;gap:30px}}
.dealer .q div{{text-align:right}}
.dealer .q small{{display:block;font-size:17px;font-weight:700;color:#cdbfc2;text-transform:uppercase;letter-spacing:.05em}}
.dealer .q b{{font-family:'Inter Display';font-weight:900;font-size:40px}}
.foot{{display:flex;justify-content:space-between;align-items:center;margin-top:20px;font-size:22px;font-weight:700;color:#ffd7dc}}
.foot b{{color:#fff;font-size:26px}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo"><i>₦</i>NairaExchangeRate</div><div class="date">{today}</div></div>
<h1>Naira rates today</h1>
<div class="sub">Naira for 1 unit of each currency · Official CBN rate ({nice(cbn['date'])})</div>
<div class="grid">{rates}</div>
<div class="mini">{mini}</div>
<div class="dealer"><div><div class="l">UK parallel rate · GBP</div><div class="t">Dealer rate, updated {when(par['updated'])}</div></div>
  <div class="q"><div><small>Send £1, get</small><b>₦{money(par['send'],0)}</b></div><div><small>Buy £1 for</small><b>₦{money(par['buy'],0)}</b></div></div></div>
<div class="foot"><span>Live rates &amp; converter</span><b>nairaexchangerate.com</b></div>
</div></body></html>"""

os.makedirs(os.path.join(ROOT, "social"), exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, wide in [("rates-square.png", 1080, 1080, False), ("rates-wide.png", 1600, 900, True)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(page(w, h, wide))
        pg.wait_for_timeout(200)
        pg.screenshot(path=os.path.join(ROOT, "social", name))
    b.close()

r = cbn["rates"]
caption = (f"🇳🇬 Naira exchange rates · {datetime.date.today().strftime('%a %-d %b %Y')}\n\n"
           f"Official CBN rate ({nice(cbn['date'])}):\n"
           f"$1 = ₦{money(r['usd']['middle'])}\n£1 = ₦{money(r['gbp']['middle'])}\n€1 = ₦{money(r['eur']['middle'])}\n\n"
           f"UK parallel rate (updated {when(par['updated'])}):\n"
           f"Send £1 → ₦{money(par['send'],0)} · Buy £1 for ₦{money(par['buy'],0)}\n\n"
           "Live rates & converter: nairaexchangerate.com\n#Naira #NairaToPound #NairaToDollar #ExchangeRate #Nigeria")
open(os.path.join(ROOT, "social", "caption.txt"), "w", encoding="utf-8").write(caption)
print(caption)
