#!/usr/bin/env python3
"""Why does every bar floor tile have a huge VERTICAL wrap step and (mostly) a zero horizontal one?

A one-question diagnostic, run because the calibration returned a lopsided result that would
otherwise have been carried forward as if it meant the same thing in both axes:

    wrap_x  0.00 on 5 of 7 tiles          left and right columns identical to the pixel
    wrap_y  34 - 147 on 7 of 7 tiles      top and bottom rows nothing like each other

A tile cannot be deliberately edge-matched in one axis and wildly mismatched in the other by
accident. The obvious candidate is a BAKED TOP SHADOW — the band of darkness a floor tile
carries along its north edge to stand in for the wall above it, which is standard practice in
tilesets of this generation and which would show up as exactly this asymmetry.

It matters because bible §6.3 is LOCKED and RATIFIED: assets are authored to RECEIVE light, not
to depict it, and a baked shadow is depicted lighting. If that is what the bar's seam statistic
is made of, then the bar cannot calibrate Yarl's seam threshold — it would be calibrating
against a construction Yarl refuses — and the honest output is to say so rather than to adopt
the number.

MEASUREMENTS LEAVE; PIXELS NEVER DO (§13.3). This prints row means. Nothing is written.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools/sighted_round"))
import calibrate_against_bar as CB      # noqa: E402
import measure_bar as MB                # noqa: E402

maps, tiles, rejected, _coll = CB.bar_floor_tiles()
print("row-mean luminance profile, bar floor tiles (48px). source: %s\n" % MB.BAR_ROOT)
for (sheet, gid), n, rgb in tiles:
    L = MB.lum(rgb)
    rows = L.mean(axis=1)
    cols = L.mean(axis=0)
    body = float(np.median(rows[4:-4]))
    print("gid %-5d cells=%-3d  body=%6.1f | row0=%6.1f row1=%6.1f row2=%6.1f  "
          "rowN-1=%6.1f  | col0=%6.1f colN-1=%6.1f"
          % (gid, n, body, rows[0], rows[1], rows[2], rows[-1], cols[0], cols[-1]))
    print("      top band vs body: row0 %+.0f%%   bottom vs body: rowN-1 %+.0f%%   "
          "left vs right: %+.1f"
          % (100 * (rows[0] / body - 1), 100 * (rows[-1] / body - 1), cols[0] - cols[-1]))
