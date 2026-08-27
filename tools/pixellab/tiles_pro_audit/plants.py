#!/usr/bin/env python3
"""The positive control: two plants per critic set (§4, bible §13.5).

An instrument's pass does not count until it has demonstrated it can fail, and for a blind
critic the substitute for "name them cold" is a deliberately wrong candidate seeded into the
set. **If the critic does not catch a plant, the round is VOID — not discounted, void** — and
its findings are not read, because a soft critic's findings are worse than none: they get
acted on.

Two plants, and the second is the one that matters.

  PLANT A — MECHANICAL. An isometric object from the §6.4 wall morgue: a candidate produced
  when a wall was asked for and a box arrived. Wrong on two independent grounds
  (object-not-surface AND wrong-projection), so a critic has to miss both to pass it.

  ⚠ The morgue images sit on an opaque grey field, and a plant identifiable by its BACKGROUND
  is not a plant — it is a spot-the-odd-file puzzle, and passing it would prove nothing about
  whether the critic can read a wall. The grey is keyed out and the object is composited onto
  the same transparent canvas the real candidates use.

  PLANT B — THE BAR'S OWN DESTINATION, and the reason this file exists. A wall-gauntlet
  candidate: flat, edge-to-edge coursed masonry with no top surface and no segment identity —
  exactly the thing that cleared the gauntlet's *usable-as-wall* bar and exactly what this
  audit's bar was written to exclude. It is tiled through the ALPHA MASK OF A REAL CANDIDATE,
  so its silhouette is a genuine wall-piece silhouette and the only thing wrong with it is the
  construction. It cannot be spotted by shape, by canvas, by background or by filename.

  A critic that passes Plant B has not enforced this bar. That is the outcome this control
  exists to make visible, and it is worth more than any verdict it might otherwise return.

Plants are hand-picked and recorded by name. A random morgue draw could pull a borderline tile
and turn the control into a coin toss.
"""
import hashlib
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

# Chosen by eye, recorded by name so the control is auditable and cannot be quietly swapped
# for something easier.
PLANT_A_SRC = os.path.join(REPO, "tools/pixellab/probe_6_4/stage1/A/wall/A_wall_11.png")
PLANT_B_SRC = os.path.join(REPO, "tools/pixellab/wall_gauntlet/rounds/round10/images/r10_06.png")

# The silhouette Plant B borrows: a straight run of wall. Chosen because it is the most
# ordinary piece in the set — the plant should be caught on construction, not on being odd.
PLANT_B_MASK_TILE = 1


def key_out_background(im, tol=12):
    """Drop a uniform opaque field, sampled from the corners. Anything within `tol` of the
    modal corner colour becomes transparent."""
    im = im.convert("RGBA")
    w, h = im.size
    corners = [im.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    bg = max(set(corners), key=corners.count)
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and abs(r - bg[0]) <= tol and abs(g - bg[1]) <= tol and abs(b - bg[2]) <= tol:
                px[x, y] = (r, g, b, 0)
    return im


def make_plant_a(canvas_size, ref_tile):
    """Object, keyed out, centred on the reference candidate's own bounding box."""
    obj = key_out_background(Image.open(PLANT_A_SRC))
    out = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    bbox = ref_tile.getbbox() or (0, 0, canvas_size[0], canvas_size[1])
    cx = bbox[0] + (bbox[2] - bbox[0] - obj.width) // 2
    cy = bbox[1] + (bbox[3] - bbox[1] - obj.height) // 2
    out.alpha_composite(obj, (max(0, cx), max(0, cy)))
    return out


def make_plant_b(canvas_size, mask_tile):
    """Wallpaper poured through a real candidate's alpha. Same silhouette, wrong construction."""
    swatch = Image.open(PLANT_B_SRC).convert("RGBA")
    tiled = Image.new("RGBA", canvas_size, (0, 0, 0, 255))
    for y in range(0, canvas_size[1], swatch.height):
        for x in range(0, canvas_size[0], swatch.width):
            tiled.paste(swatch, (x, y))
    alpha = mask_tile.convert("RGBA").split()[3]
    tiled.putalpha(alpha)
    return tiled


def build(kit_dir, out_dir):
    """Write both plants into `out_dir` and return the manifest."""
    ref = Image.open(os.path.join(kit_dir, "tile_%02d.png" % PLANT_B_MASK_TILE)).convert("RGBA")
    size = ref.size
    os.makedirs(out_dir, exist_ok=True)
    made = []
    for name, img, src, why in (
            ("plant_a", make_plant_a(size, ref), PLANT_A_SRC,
             "isometric object from the §6.4 wall morgue; background keyed out so only the "
             "content can betray it"),
            ("plant_b", make_plant_b(size, ref), PLANT_B_SRC,
             "wall-gauntlet edge-to-edge masonry poured through candidate %02d's alpha: the "
             "bar's own destination, wearing a real silhouette" % PLANT_B_MASK_TILE)):
        p = os.path.join(out_dir, name + ".png")
        img.save(p)
        made.append({"plant": name, "file": os.path.basename(p),
                     "source": os.path.relpath(src, REPO),
                     "source_sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                     "canvas": list(size), "why": why})
    with open(os.path.join(out_dir, "plants.json"), "w") as f:
        json.dump(made, f, indent=2, sort_keys=True)
    return made


def main():
    kit = os.path.join(HERE, "yield", "kit_A0")
    out = os.path.join(HERE, "plants")
    for p in build(kit, out):
        print("%-8s <- %-58s %s" % (p["plant"], p["source"], p["canvas"]))


if __name__ == "__main__":
    main()
