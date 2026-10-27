# Nézőnapló

Saját sorozat- és filmfigyelő, iPhone-on appként: hol tartasz, mit akartál megnézni, mikor jön új rész, új évad vagy filmpremier.
A sorozatadatokat a [TVmaze](https://www.tvmaze.com), a filmadatokat a [Wikidata](https://www.wikidata.org) adja (ingyenes, nem kell regisztráció).

## Feltöltés GitHub Pages-re (egyszer kell megcsinálni)

1. Lépj be a [github.com](https://github.com)-ra (ha nincs fiókod, regisztrálj).
2. Jobb fent **+ → New repository**. Név pl. `sorozatok`, legyen **Public**, aztán **Create repository**.
3. Az új repo oldalán: **uploading an existing file** link → húzd be ezt a 7 fájlt:
   `index.html`, `manifest.webmanifest`, `sw.js`, `icon-180.png`, `icon-192.png`, `icon-512.png`, `README.md`
   → **Commit changes**.
4. **Settings → Pages** → *Branch*: `main`, mappa: `/ (root)` → **Save**.
5. 1–2 perc múlva megjelenik a cím: `https://<felhasználóneved>.github.io/sorozatok/`

## Telepítés iPhone-ra

1. Nyisd meg a fenti címet **Safariban**.
2. Alul **Megosztás** gomb (négyzet felfelé nyíllal) → **Főképernyőhöz adás** → **Hozzáadás**.
3. Ezentúl a „Nézőnapló” ikonról indítsd – teljes képernyős app lesz.

## Használat

- **+** gomb: fent válts *Sorozat* / *Film* között, keress cím alapján (magyarul vagy angolul).
  Sorozat → *Nézem* vagy *Tervezem*; film → *Megnézném* vagy *Láttam*. Ha nincs találat: kézi hozzáadás.
- **Nézem**: a kártyán a „✓ S2E06” gombbal jelölöd, hogy megnézted a következő részt. A kártyára koppintva beállíthatod pontosan, hol tartasz.
- **Tervezem**: sorozatok, amiket el akarsz kezdeni, és filmek, amiket meg akarsz nézni (szűrhető). Sorozatnál „Elkezdem”, filmnél „Láttam”.
- **Közelgő**: mi jön ma, a héten, később – sorozatrészek, új évadok és filmpremierek (ha van, a magyar premier). A naptár ikonnal a telefon Naptárába teheted emlékeztetővel.
- **Beállítások**: mentés fájlba / visszatöltés, megnézett filmek listája. Az adatok csak a telefonon vannak, ezért néha ments (pl. iCloud Drive-ra).

## Frissítés

Ha módosítod az `index.html`-t, töltsd fel újra ugyanígy a repóba. Az app a következő megnyitáskor (netkapcsolattal) frissül.

## Magyar műsorok listája

A `hu-shows.json` a TVmaze-en szereplő összes magyar műsort tartalmazza. Az alkalmazás ebből keres először, így a magyar műsorok (pl. *Most Wanted – A hajsza*) akkor is előre kerülnek, ha sok külföldi műsornak hasonló a címe. Az üres keresőnél a most futó magyar műsorok jelennek meg.

Frissítés (néhány havonta érdemes): `python3 scripts/hu_shows.py`, majd a `sw.js` fájlban a `VERSION` értékét kell növelni.
