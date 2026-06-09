#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np, trimesh

def add(ax, mesh, color, alpha=1.0):
    tri = mesh.triangles
    pc = Poly3DCollection(tri, alpha=alpha)
    pc.set_facecolor(color); pc.set_edgecolor((0,0,0,0.08)); pc.set_linewidth(0.2)
    ax.add_collection3d(pc)

def setlims(ax, meshes):
    allv = np.vstack([m.vertices for m in meshes])
    mn, mx = allv.min(0), allv.max(0)
    c = (mn+mx)/2; r = (mx-mn).max()/2
    ax.set_xlim(c[0]-r, c[0]+r); ax.set_ylim(c[1]-r, c[1]+r); ax.set_zlim(c[2]-r, c[2]+r)
    ax.set_box_aspect((1,1,1))

onder = trimesh.load("/home/claude/bkos-afdekplaat/afdekplaat_onder.stl")
boven = trimesh.load("/home/claude/bkos-afdekplaat/afdekplaat_boven.stl")

views = [
    ("buiten",  (20, -90)),   # van buitenaf (kijkt op de flens, -Z kant)
    ("binnen",  (18,  90)),   # van binnenuit (haken/rand zichtbaar)
    ("driekwart",(28, -55)),
]

# 1) Geassembleerd, 3 hoeken
for naam, (el, az) in views:
    fig = plt.figure(figsize=(7,7)); ax = fig.add_subplot(111, projection="3d")
    add(ax, onder, (0.30,0.45,0.75)); add(ax, boven, (0.80,0.55,0.25))
    setlims(ax, [onder, boven]); ax.view_init(elev=el, azim=az)
    ax.set_title(f"Geassembleerd - {naam}"); ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    fig.tight_layout(); fig.savefig(f"/home/claude/bkos-afdekplaat/preview_{naam}.png", dpi=90); plt.close(fig)

# 2) Exploded (bovendeel naar +Y en boven onderdeel uit elkaar) + losse delen
fig = plt.figure(figsize=(8,8)); ax = fig.add_subplot(111, projection="3d")
bov2 = boven.copy(); bov2.apply_translation([0, 60, 0])
add(ax, onder, (0.30,0.45,0.75)); add(ax, bov2, (0.80,0.55,0.25))
setlims(ax, [onder, bov2]); ax.view_init(elev=26, azim=-60)
ax.set_title("Exploded"); fig.tight_layout()
fig.savefig("/home/claude/bkos-afdekplaat/preview_exploded.png", dpi=90); plt.close(fig)

# 3) Doorsnede-achtig: onderdeel van binnen (haak + rand + boss)
fig = plt.figure(figsize=(8,8)); ax = fig.add_subplot(111, projection="3d")
add(ax, onder, (0.30,0.45,0.75))
setlims(ax, [onder]); ax.view_init(elev=22, azim=70)
ax.set_title("Onderdeel - binnenzijde (haak/rand/boss)"); fig.tight_layout()
fig.savefig("/home/claude/bkos-afdekplaat/preview_onder_binnen.png", dpi=90); plt.close(fig)
print("renders klaar")
