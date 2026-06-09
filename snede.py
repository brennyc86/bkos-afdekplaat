#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, trimesh

onder = trimesh.load("/home/claude/bkos-afdekplaat/afdekplaat_onder.stl")
boven = trimesh.load("/home/claude/bkos-afdekplaat/afdekplaat_boven.stl")
WAND=10.0; OPEN_H=245.0; OPEN_B=235.0

def yz(mesh, x):
    s = mesh.section(plane_origin=[x,0,0], plane_normal=[1,0,0])
    if s is None: return []
    return [s.vertices[e.points][:,1:3] for e in s.entities]   # (Y,Z)

def xz(mesh, y):
    s = mesh.section(plane_origin=[0,y,0], plane_normal=[0,1,0])
    if s is None: return []
    return [s.vertices[e.points][:,[0,2]] for e in s.entities]  # (X,Z)

def refs(ax, edges):
    ax.axhline(0, color="k", lw=.7, ls=":")          # buitenkant schot
    ax.axhline(WAND, color="g", lw=.7, ls=":")        # binnenkant schot
    for e in edges: ax.axvline(e, color="r", lw=.7, ls="--")  # openingsrand

fig, axes = plt.subplots(3, 1, figsize=(13,11))

ax=axes[0]
for segs,col in ((yz(onder,0),"tab:blue"),(yz(boven,0),"tab:orange")):
    for s in segs: ax.plot(s[:,0], s[:,1], col, lw=1.6)
refs(ax, [-OPEN_H/2, OPEN_H/2])
ax.set_title("Snede x=0  | horizontaal=Y (hoogte), verticaal=Z (diepte). rood=openingsrand, zwart=buiten, groen=binnen")
ax.set_xlabel("Y"); ax.set_ylabel("Z"); ax.invert_yaxis(); ax.grid(alpha=.3)
ax.set_aspect(2.5)

ax=axes[1]
for segs,col in ((yz(onder,60),"tab:blue"),(yz(boven,60),"tab:orange")):
    for s in segs: ax.plot(s[:,0], s[:,1], col, lw=1.6)
refs(ax, [-OPEN_H/2, OPEN_H/2])
ax.set_title("Snede x=60  (door schroef-boss + lap-naad)")
ax.set_xlabel("Y"); ax.set_ylabel("Z"); ax.invert_yaxis(); ax.grid(alpha=.3)
ax.set_aspect(2.5)

ax=axes[2]
for segs,col in ((xz(onder,-95),"tab:blue"),):
    for s in segs: ax.plot(s[:,0], s[:,1], col, lw=1.6)
refs(ax, [-OPEN_B/2, OPEN_B/2])
ax.set_title("Snede y=-95  (door kabeldoorvoer)  horizontaal=X")
ax.set_xlabel("X"); ax.set_ylabel("Z"); ax.invert_yaxis(); ax.grid(alpha=.3)
ax.set_aspect(2.5)

fig.tight_layout(); fig.savefig("/home/claude/bkos-afdekplaat/sneden.png", dpi=95); plt.close(fig)
print("sneden klaar")
