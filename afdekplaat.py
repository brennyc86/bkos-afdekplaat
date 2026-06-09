#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BKOS - Afdekplaat scheepsopening (2-delig)
==========================================
Parametrisch model. Alle maten in mm.

Coordinatenstelsel:
  X = breedte (gecentreerd op 0)
  Y = hoogte  (gecentreerd op 0)
  Z = diepte door het schot. Z=0 = BUITENkant schot, +Z loopt naar BINNEN (de boot in).
      Schot bezet Z in [0, WAND]. Buiten = Z<0 (flens). Binnen = Z>WAND (haken).

Bouwt twee delen (ONDER + BOVEN), exporteert STL en rendert preview-PNG's.
"""
import numpy as np
import trimesh
from shapely.geometry import box as sbox

ENGINE = "manifold"

# ============================================================
#  PARAMETERS  -- pas deze aan na het opmeten van je echte gat
# ============================================================
OPENING_B = 235.0   # breedte van de opening
OPENING_H = 245.0   # hoogte  van de opening
OPENING_R = 95.0    # hoekradius (~10 cm); meet na, hoeken zijn flink afgerond
WAND      = 10.0    # dikte van het schot (buiten -> binnen)

MARGE     = 1.5     # speling rondom de insteek in het gat (per zijde) - handzaag

FLENS_OVER = 10.0   # hoeveel de buitenflens over de rand grijpt (rondom)
FLENS_DIK  = 4.0    # dikte van de buitenflens (de zichtbare plaat)

RAND_DIK   = 3.5    # wanddikte van de insteekrand (in het gat)

HAAK_OVER  = 8.0    # hoe ver de binnenhaak achter het schot grijpt
HAAK_DIK   = 3.5    # dikte van de haak
HAAK_BAND  = 60.0   # haak loopt vanaf de rand tot |y| > (helft - dit) ... zie code

SPLIT_Y    = 0.0    # hoogte van de scheidingslijn onder/boven (0 = midden)
LAP_OVER   = 25.0   # lengte van de overlap-naad (lap joint)

# Schroeven (verbinden onder+boven, van buitenaf)
SCHROEF_X     = 60.0   # x-afstand van de 2 schroeven t.o.v. midden
SCHROEF_CLEAR = 4.6    # doorvoergat in bovendeel (M4 ruim)
SCHROEF_KERN  = 3.3    # voorboorgat / zelftap-kern in onderdeel-boss (M4)
KOP_D         = 9.0    # verzonken/counterbore kop diameter
KOP_DIEP      = 1.2    # counterbore diepte in bovendeel
BOSS_D        = 10.0   # diameter schroefkolom in onderdeel
BOSS_LEN      = 10.0   # lengte boss de boot in (Z+)

# Kabeldoorvoer (links onder)
KABEL_AAN = True
KABEL_B   = 70.0
KABEL_H   = 20.0
KABEL_X   = -35.0   # midden x
KABEL_Y   = -95.0   # midden y
KABEL_R   = 6.0     # afronding van het slot

QS = 24             # quad-segments voor afrondingen (gladheid)

# ============================================================
#  HELPERS
# ============================================================
def rr(w, h, r):
    """Afgeronde rechthoek (shapely Polygon), overall w x h, hoekradius r, gecentreerd."""
    r = max(0.01, min(r, w/2 - 0.01, h/2 - 0.01))
    return sbox(-(w/2 - r), -(h/2 - r), (w/2 - r), (h/2 - r)).buffer(r, quad_segs=QS, join_style=1)

def solid(poly, z0, z1):
    """Extrudeer een shapely polygon van z0 tot z1."""
    m = trimesh.creation.extrude_polygon(poly, height=(z1 - z0))
    m.apply_translation([0, 0, z0])
    return m

def ybox(ylow, yhigh):
    b = trimesh.creation.box(extents=[4000, yhigh - ylow, 4000])
    b.apply_translation([0, (ylow + yhigh) / 2.0, 0])
    return b

def cyl(radius, z0, z1, x=0.0, y=0.0):
    h = z1 - z0
    c = trimesh.creation.cylinder(radius=radius, height=h, sections=48)
    c.apply_translation([x, y, z0 + h / 2.0])
    return c

def U(meshes):
    return trimesh.boolean.union(meshes, engine=ENGINE)

def D(a, b):
    return trimesh.boolean.difference([a, b], engine=ENGINE)

def I(a, b):
    return trimesh.boolean.intersection([a, b], engine=ENGINE)

# ============================================================
#  OUTLINES (2D)
# ============================================================
opening    = rr(OPENING_B, OPENING_H, OPENING_R)
insert_out = rr(OPENING_B - 2*MARGE, OPENING_H - 2*MARGE, OPENING_R - MARGE)
insert_in  = rr(OPENING_B - 2*MARGE - 2*RAND_DIK, OPENING_H - 2*MARGE - 2*RAND_DIK, OPENING_R - MARGE - RAND_DIK)
flange     = rr(OPENING_B + 2*FLENS_OVER, OPENING_H + 2*FLENS_OVER, OPENING_R + FLENS_OVER)
hook_out   = rr(OPENING_B + 2*HAAK_OVER, OPENING_H + 2*HAAK_OVER, OPENING_R + HAAK_OVER)

rim_ring   = insert_out.difference(insert_in)        # insteekrand-ring
hook_ring  = hook_out.difference(insert_out)         # haak-richel-ring

# ============================================================
#  GEDEELDE 3D-ONDERDELEN
# ============================================================
# Flens: Z in [-FLENS_DIK, 0]
flange_full = solid(flange, -FLENS_DIK, 0.0)
# Insteekrand: Z in [0, WAND]
rim_full    = solid(rim_ring, 0.0, WAND)

# Lap-band (volledige breedte) tussen SPLIT_Y en SPLIT_Y+LAP_OVER
lap_band_2d = flange  # begrensd door ybox hieronder
half = FLENS_DIK / 2.0
bottom_lap = I(solid(flange, -half, 0.0),            ybox(SPLIT_Y, SPLIT_Y + LAP_OVER))  # binnenhelft
top_lap    = I(solid(flange, -FLENS_DIK, -half),     ybox(SPLIT_Y, SPLIT_Y + LAP_OVER))  # buitenhelft

# Haken (richel + 45-graden wig als steun) langs onder- resp. bovenrand.
def haak(onder=True):
    # Vlakke richel die achter de binnenkant van het schot grijpt.
    # De binnenrand sluit aan op de bovenkant van de insteekrand (insert_out @ Z=WAND).
    h = solid(hook_ring, WAND, WAND + HAAK_DIK)
    if onder:
        sel = ybox(-3000, -(OPENING_H/2 - HAAK_BAND))
    else:
        sel = ybox(OPENING_H/2 - HAAK_BAND, 3000)
    return I(h, sel)

# ============================================================
#  ONDERDEEL
# ============================================================
def maak_onder():
    flange_b = I(flange_full, ybox(-3000, SPLIT_Y))
    rim_b    = I(rim_full,    ybox(-3000, SPLIT_Y + LAP_OVER))
    hk       = haak(onder=True)
    # bosses
    bosses = []
    for sx in (-1, 1):
        bosses.append(cyl(BOSS_D/2.0, -half, BOSS_LEN, x=sx*SCHROEF_X, y=SPLIT_Y + LAP_OVER/2.0))
    part = U([flange_b, bottom_lap, rim_b, hk] + bosses)
    # voorboorgaten
    holes = []
    for sx in (-1, 1):
        holes.append(cyl(SCHROEF_KERN/2.0, -half - 0.5, BOSS_LEN + 0.5, x=sx*SCHROEF_X, y=SPLIT_Y + LAP_OVER/2.0))
    part = D(part, U(holes))
    # kabeldoorvoer
    if KABEL_AAN:
        slot = solid(rr(KABEL_B, KABEL_H, KABEL_R), -FLENS_DIK - 1, WAND + HAAK_DIK + 1)
        slot.apply_translation([KABEL_X, KABEL_Y, 0])
        part = D(part, slot)
    return part

# ============================================================
#  BOVENDEEL
# ============================================================
def maak_boven():
    flange_t = I(flange_full, ybox(SPLIT_Y + LAP_OVER, 3000))
    rim_t    = I(rim_full,    ybox(SPLIT_Y + LAP_OVER, 3000))
    hk       = haak(onder=False)
    part = U([flange_t, top_lap, rim_t, hk])
    # doorvoergaten + counterbore
    cuts = []
    for sx in (-1, 1):
        x = sx*SCHROEF_X; y = SPLIT_Y + LAP_OVER/2.0
        cuts.append(cyl(SCHROEF_CLEAR/2.0, -FLENS_DIK - 1, 0.5, x=x, y=y))
        cuts.append(cyl(KOP_D/2.0, -FLENS_DIK - 0.1, -FLENS_DIK + KOP_DIEP, x=x, y=y))
    part = D(part, U(cuts))
    return part

if __name__ == "__main__":
    import sys
    onder = maak_onder()
    boven = maak_boven()
    onder.export("/home/claude/bkos-afdekplaat/afdekplaat_onder.stl")
    boven.export("/home/claude/bkos-afdekplaat/afdekplaat_boven.stl")
    for naam, m in (("ONDER", onder), ("BOVEN", boven)):
        print(f"{naam}: watertight={m.is_watertight} volume={m.volume/1000:.1f} cm3 "
              f"bbox={np.round(m.extents,1)} tris={len(m.faces)}")
