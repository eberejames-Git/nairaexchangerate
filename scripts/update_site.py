"""Update the data block inside index.html.

Usage:
  python3 scripts/update_site.py patch.json

patch.json may contain any of these top-level keys, which replace the
matching keys in the site data:
  "cbn":      {"date": "YYYY-MM-DD", "rates": {"usd": {"buy":..,"middle":..,"sell":..}, ...}}
  "parallel": {"send": 1825, "buy": 1920, "updated": "YYYY-MM-DDTHH:MM"}
              (history is appended automatically, max 30 days)
  "news":     [{"source":"..","title":"..","summary":"..","url":"https://..","date":"YYYY-MM-DD"}]
              (merged with existing stories, sorted newest first by date; keeps the 6 newest)
  "partners", "whatsappChannel": replaced as given.
"""
import json, re, sys

PATH = "index.html"
# Competitor sites whose stories must never appear in the news list.
BLOCKED_NEWS = ("nairametrics",)
pat = re.compile(r'(<script type="application/json" id="site-data">)(.*?)(</script>)', re.S)

def main(patch_path):
    html = open(PATH, encoding="utf-8").read()
    m = pat.search(html)
    if not m:
        sys.exit("site-data block not found")
    data = json.loads(m.group(2))
    patch = json.load(open(patch_path, encoding="utf-8"))

    if "cbn" in patch:
        c = patch["cbn"]
        assert re.match(r"\d{4}-\d{2}-\d{2}$", c["date"]), "bad cbn date"
        for k, r in c["rates"].items():
            assert r["buy"] > 0 and r["middle"] > 0 and r["sell"] > 0, k
        data["cbn"] = c

    if "parallel" in patch:
        p = patch["parallel"]
        send, buy = float(p["send"]), float(p["buy"])
        assert 500 < send < 10000 and 500 < buy < 10000, "parallel rate out of range"
        par = data.setdefault("parallel", {})
        par.update({"send": send, "buy": buy, "updated": p["updated"]})
        day = p["updated"][:10]
        hist = [h for h in par.get("history", []) if h["date"] != day]
        hist.append({"date": day, "send": send, "buy": buy})
        par["history"] = sorted(hist, key=lambda h: h["date"])[-30:]

    if "news" in patch:
        # New stories go first; older ones fill the rest. Always keep up to 6, no duplicate links.
        merged, seen = [], set()
        for n in patch["news"] + data.get("news", []):
            assert n["url"].startswith("https://"), "news url must be https"
            if n.get("example") or n["url"] in seen:
                continue
            if any(b in (n["url"] + " " + n.get("source", "")).lower() for b in BLOCKED_NEWS):
                continue
            seen.add(n["url"])
            merged.append(n)
        # Newest first by publication date (stable, so same-day order is kept).
        merged.sort(key=lambda n: n.get("date", ""), reverse=True)
        data["news"] = merged[:6]

    for k in ("partners", "whatsappChannel"):
        if k in patch:
            data[k] = patch[k]

    new = html[:m.start(2)] + "\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n" + html[m.end(2):]
    open(PATH, "w", encoding="utf-8").write(new)
    print("updated:", ", ".join(k for k in patch))

if __name__ == "__main__":
    main(sys.argv[1])
