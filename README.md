# BKOS – Afdekplaat scheepsopening (2-delig)

3D-printbaar afdekplaatje voor een opening in het schot, zodat de kat niet bij de
zware/gevaarlijke elektrakabels kan. Parametrisch ontworpen: alle maten staan
bovenaan `afdekplaat.py` en zijn met één getal aan te passen.

![driekwart](preview_driekwart.png)

## Het ontwerp in het kort

De opening is **235 mm breed × 245 mm hoog**, met **flink afgeronde hoeken (~10 cm
radius)** in een schot van **±10 mm dik**. Omdat het gat met de hand gezaagd is, zit
er overal **1,5 mm speling** op de insteek.

Twee delen die in elkaar haken en met 2 schroeven van buitenaf vastzitten:

| Onderdeel | Hoe het vastzit |
|---|---|
| **ONDER** | Schuin insteken → onderhaak achter de binnenkant → omhoog draaien tot hij valt. Flens buiten houdt 'm tegen indrukken, haak binnen tegen eruit vallen. |
| **BOVEN** | Bovenhaak grijpt achter de binnenkant-boven; de zijkanten steunen op de buitenflens. De onderrand overlapt het onderdeel (lap-naad). |
| **Verbinding** | 2 schroeven van buitenaf door de lap-naad klemmen boven + onder aan elkaar → het geheel kan niet meer los. |

Verder:
- **Buitenflens** grijpt rondom 10 mm over de rand → dekt de handgezaagde kant netjes af (kat-dicht).
- **Kabeldoorvoer** links-onder: gat van **70 × 20 mm** (20 mm is te laag voor een kattenkop). Ingerekend op de grote hoekradius zodat het binnen het materiaal valt.
- Zijkanten hebben **geen** haak (alleen buitenflens) — precies zoals gevraagd.

### Doorsneden (bewijs dat het mechaniek klopt)

![sneden](sneden.png)

- Rood = rand van de opening, zwart stippel = buitenkant schot (Z=0), groen = binnenkant (Z=10).
- Links flens + insteekrand + onderhaak áchter het schot; rechts idem met bovenhaak; midden de lap-naad (binnen- + buitenhelft samen vol, buitenkant vlak).

## Bestanden

| Bestand | Wat |
|---|---|
| `afdekplaat_onder.stl` | Onderdeel — klaar om te printen |
| `afdekplaat_boven.stl` | Bovendeel — klaar om te printen |
| `afdekplaat.py` | Parametrische bron (Python: shapely + trimesh + manifold3d) |
| `snede.py` / `render.py` | Genereren de doorsneden en previews |

## Printen

> ⚠️ **Bedmaat:** de delen zijn ±**255 mm** in één richting (opening 235 + 2× flens 10).
> Past op een 256-bed (Bambu/CR-10/Ender-5 Plus). Op een 220-bed: **45° gedraaid**
> printen (diagonaal ≈ 311 mm past). Of `FLENS_OVER` verlagen.

- **Oriëntatie:** flens-kant op het bed (de platte buitenkant naar beneden).
- **Support:** alleen nodig onder de binnenhaken (kleine richels). Slicer zet die automatisch. Rest is support-vrij.
- **Materiaal:** PETe of ASA i.v.m. vocht/UV op een boot (PLA kan, maar minder bestendig).
- **Wanden/infill:** 4 wanden, 25–30 % infill is ruim voldoende; dit is geen dragend deel.
- **Schroeven:** 2× **M4 zelftappend, ±16 mm** (RVS A4 voor op het water). Voorboorgaten Ø3,3 zitten al in de bossen. Upgrade-optie: heat-set inserts + M4 machineschroef.

## Monteren

1. **Onderdeel** schuin in de opening steken, onderhaak achter de binnenkant haken, omhoog draaien tot de flens vlak ligt.
2. **Bovendeel** met de bovenhaak achter de binnenkant-boven haken, naar beneden draaien; de onderrand legt over het onderdeel.
3. 2 schroeven van buitenaf door de lap-naad in de bossen draaien. Klaar.
4. Kabels door het slot links-onder leiden.

## Maten aanpassen

Open `afdekplaat.py`, pas de parameters bovenaan aan en draai opnieuw:

```bash
pip install --break-system-packages numpy shapely trimesh manifold3d
python3 afdekplaat.py          # schrijft de twee STL's
python3 snede.py && python3 render.py   # optioneel: plaatjes
```

Handige knoppen:
- `MARGE` – speling in het gat (groter = ruimer, makkelijker passen).
- `FLENS_OVER` – hoeveel de flens over de rand grijpt (en de totale buitenmaat).
- `OPENING_R` – **meet je echte hoekradius na** en zet 'm hier.
- `HAAK_OVER` – hoe diep de haken grijpen (kleiner = makkelijker insteken).
- `KABEL_*` – plek/maat kabelslot. Wil je 'm open aan de onderrand i.p.v. een dicht gat? Verlaag `KABEL_Y` tot voorbij de rand.

## Belangrijk: eerst test-passen

Het gat is handgezaagd. Print eventueel eerst een **strook van de rand** (of accepteer
dat v1 een test-fit is) en stel `MARGE` / `OPENING_R` bij vóór de definitieve print.
