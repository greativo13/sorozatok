"""Közelgő sorozatpremierek (TVmaze) és mozifilmek (Wikidata) -> upcoming.json

A GitHub naponta lefuttatja (.github/workflows/frissites.yml), de kézzel is
futtatható a repo gyökeréből:  python3 scripts/upcoming.py
"""
import json, re, time, urllib.parse, urllib.request
from datetime import date, timedelta

UA = {"User-Agent": "Nezonaplo/1.0 (https://greativo13.github.io/sorozatok/)"}
TODAY = date.today()
SERIES_DAYS, FILM_DAYS = 150, 180
MIN_WEIGHT = 80      # TVmaze népszerűség (0-100); a magyar műsorok mindig bekerülnek
MIN_SITELINKS = 8    # ennyi Wikipédia-nyelven legyen cikke a filmnek


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def series():
    out, seen = [], set()
    limit = (TODAY + timedelta(days=SERIES_DAYS)).isoformat()
    for e in get("https://api.tvmaze.com/schedule/full"):
        s = e.get("_embedded", {}).get("show") or {}
        ch = s.get("network") or s.get("webChannel") or {}
        hu = (ch.get("country") or {}).get("code") == "HU" or s.get("language") == "Hungarian"
        if e.get("number") != 1 or not e.get("airdate") or not (TODAY.isoformat() <= e["airdate"] <= limit):
            continue
        if not hu and (s.get("weight") or 0) < MIN_WEIGHT:
            continue
        key = (s["id"], e["season"])
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "id": s["id"], "name": s["name"], "season": e["season"],
            "date": e["airdate"], "stamp": e.get("airstamp"),
            "network": ch.get("name") or "", "status": s.get("status"),
            "premiered": s.get("premiered"), "genres": s.get("genres") or [],
            "image": (s.get("image") or {}).get("medium"), "weight": s.get("weight") or 0, "hu": hu,
        })
    out.sort(key=lambda x: (x["date"], -x["weight"]))
    return out


SPARQL = """
SELECT DISTINCT ?f WHERE {
  ?f wdt:P31/wdt:P279? wd:Q11424 ; p:P577 ?st ; wikibase:sitelinks ?links .
  ?st ps:P577 ?d ; wikibase:rank ?rank . FILTER(?rank != wikibase:DeprecatedRank)
  FILTER(?d >= NOW() - "P1D"^^xsd:duration && ?d < NOW() + "P%dD"^^xsd:duration)
  FILTER(?links >= %d)
} LIMIT 600
""" % (FILM_DAYS, MIN_SITELINKS)


def films():
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": SPARQL, "format": "json"})
    ids = [b["f"]["value"].rsplit("/", 1)[1] for b in get(url)["results"]["bindings"]]
    out = []
    for i in range(0, len(ids), 50):
        ents = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({
            "action": "wbgetentities", "ids": "|".join(ids[i:i + 50]),
            "props": "labels|descriptions|claims|sitelinks", "sitefilter": "enwiki",
            "languages": "hu|en", "format": "json"}))["entities"]
        for qid, x in ents.items():
            f = parse_film(x)
            if f:
                f["_en"] = ((x.get("sitelinks") or {}).get("enwiki") or {}).get("title")
                out.append(dict(f, qid=qid))
        time.sleep(1)
    add_posters(out)
    out.sort(key=lambda f: f["sort"])
    return out


def add_posters(films):
    """A Wikidatán ritkán van plakát; az angol Wikipédia cikkéből vesszük. Hiba esetén kép nélkül marad."""
    need = [f for f in films if not f["image"] and f.get("_en")]
    for i in range(0, len(need), 40):
        part = need[i:i + 40]
        try:
            j = get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query", "titles": "|".join(f["_en"] for f in part), "prop": "pageimages",
                "piprop": "thumbnail", "pithumbsize": "200", "pilicense": "any", "redirects": "1", "format": "json"}), tries=2)
        except Exception as e:
            print("plakát hiba:", e)
            break
        q = j.get("query") or {}
        alias = {r["from"]: r["to"] for r in (q.get("normalized") or []) + (q.get("redirects") or [])}
        thumbs = {p["title"]: p["thumbnail"]["source"] for p in (q.get("pages") or {}).values() if p.get("thumbnail")}
        for f in part:
            t = f["_en"]
            while t in alias:
                t = alias[t]
            if t in thumbs:
                f["image"] = thumbs[t]
        time.sleep(1)
    for f in films:
        f.pop("_en", None)


def parse_film(x):
    """Ugyanaz a logika, mint az index.html parseFilm függvényében."""
    c = x.get("claims") or {}
    dates = []
    for p in c.get("P577", []):
        if p.get("rank") == "deprecated":
            continue
        v = ((p.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if not v:
            continue
        m = re.match(r"^([+-]\d+)-(\d\d)-(\d\d)", v["time"])
        if not m:
            continue
        y, mo, da = int(m[1]), int(m[2]), int(m[3])
        prec = 11 if v.get("precision", 0) >= 11 and da else (10 if v.get("precision", 0) >= 10 and mo else 9)
        hu = any(((q.get("datavalue") or {}).get("value") or {}).get("id") == "Q28"
                 for q in (p.get("qualifiers") or {}).get("P291", []))
        dates.append({"d": f"{y:04d}-{max(mo, 1):02d}-{max(da, 1):02d}", "prec": prec, "hu": hu})
    precise = sorted((d for d in dates if d["prec"] == 11), key=lambda d: d["d"])
    first = precise[0] if precise else (sorted(dates, key=lambda d: d["d"])[0] if dates else None)
    huf = next((d for d in precise if d["hu"]), None)
    if not first:
        return None
    key = huf or first
    if not (TODAY.isoformat() <= key["d"] <= (TODAY + timedelta(days=FILM_DAYS)).isoformat()):
        return None  # már bemutatták (pl. külföldön régen, itthon nincs dátum)
    img = ((c.get("P3383") or c.get("P18") or [{}])[0].get("mainsnak") or {}).get("datavalue", {}).get("value")
    lbl = lambda l: ((x.get("labels") or {}).get(l) or {}).get("value", "")
    desc = ((x.get("descriptions") or {}).get("hu") or (x.get("descriptions") or {}).get("en") or {}).get("value", "")
    return {
        "name": lbl("hu") or lbl("en") or x["id"], "orig": lbl("en"), "desc": desc,
        "release": first["d"], "prec": first["prec"], "huRelease": huf["d"] if huf else None,
        "image": f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(img)}?width=200" if img else None,
        "sort": key["d"],
    }


if __name__ == "__main__":
    data = {"generated": TODAY.isoformat(), "series": series(), "films": films()}
    with open("upcoming.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(data['series'])} sorozatpremier, {len(data['films'])} film")
