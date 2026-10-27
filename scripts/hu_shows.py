"""Kigyűjti a TVmaze-ről az összes magyar műsort a hu-shows.json fájlba.

Futtatás a repo gyökeréből:  python3 scripts/hu_shows.py
"""
import json, time, urllib.request, urllib.error

shows, page = [], 0
while True:
    try:
        with urllib.request.urlopen(f"https://api.tvmaze.com/shows?page={page}") as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            break
        if e.code == 429:
            time.sleep(5)
            continue
        raise
    for s in data:
        ch = s.get("network") or s.get("webChannel") or {}
        country = (ch.get("country") or {}).get("code")
        if country == "HU" or s.get("language") == "Hungarian":
            shows.append({
                "id": s["id"],
                "name": s["name"],
                "status": s.get("status"),
                "premiered": s.get("premiered"),
                "network": ch.get("name") or "",
                "image": (s.get("image") or {}).get("medium"),
            })
    page += 1
    time.sleep(0.3)

shows.sort(key=lambda s: s["id"])
with open("hu-shows.json", "w", encoding="utf-8") as f:
    json.dump(shows, f, ensure_ascii=False, separators=(",", ":"))
print(f"{len(shows)} magyar műsor")
