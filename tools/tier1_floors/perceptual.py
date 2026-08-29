#!/usr/bin/env python3
"""ONE CURRENCY FOR TWO CHANNELS — the value lever and the chroma lever, compared honestly.

The joint lever moves LIGHTNESS. The chroma lever moves COLOUR. The ruling asks for a verdict on
the two together, and there is no honest way to add a Weber luminance contrast to a hue shift:
they are not in the same units, and a quadrature sum of them would be an assumption of
independence wearing a number's clothing.

So both are converted into **CIELAB ΔE2000**, which is a perceptual distance that already knows
how to weigh lightness against chroma, and §13.8's ruled floor is converted into the same unit
rather than a new threshold being invented for colour:

    THE FLOOR IS DERIVED, NOT CHOSEN. §13.8 rules a Weber luminance contrast of 0.1440. Two
    neutral patches at the floor's own mean luminance, differing by exactly that Weber contrast,
    are some distance apart in ΔE2000. THAT distance is the floor for the combined signal. A
    colour lever therefore has to be as visible as the luminance signal the gate already ruled on
    — no more, and no less.

ΔE2000 rather than ΔE76 deliberately. ΔE76 over-credits chroma differences, and the lever being
measured here is a chroma lever the author built. The conservative metric is the honest one when
you are marking your own homework.
"""
import numpy as np

# sRGB D65. The floor is authored in 8-bit sRGB and viewed in it, so the conversion starts there.
_M = np.array([[0.4124564, 0.3575761, 0.1804375],
               [0.2126729, 0.7151522, 0.0721750],
               [0.0193339, 0.1191920, 0.9503041]])
_WHITE = np.array([0.95047, 1.00000, 1.08883])


def srgb_to_lab(rgb):
    """rgb in 0..255, any leading shape. Returns L*a*b*."""
    a = np.asarray(rgb, dtype=float) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M.T / _WHITE
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16.0 / 116.0)
    return np.stack([116.0 * f[..., 1] - 16.0,
                     500.0 * (f[..., 0] - f[..., 1]),
                     200.0 * (f[..., 1] - f[..., 2])], axis=-1)


def delta_e2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    """CIEDE2000. Written out rather than imported so the evidence has no hidden dependency."""
    L1, a1, b1 = [np.asarray(lab1, dtype=float)[..., i] for i in range(3)]
    L2, a2, b2 = [np.asarray(lab2, dtype=float)[..., i] for i in range(3)]

    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cbar = (C1 + C2) / 2.0
    G = 0.5 * (1.0 - np.sqrt(Cbar ** 7 / (Cbar ** 7 + 25.0 ** 7 + 1e-30)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0

    dLp = L2 - L1
    dCp = C2p - C1p
    dhp = h2p - h1p
    dhp = np.where(dhp > 180, dhp - 360, np.where(dhp < -180, dhp + 360, dhp))
    dhp = np.where(C1p * C2p == 0, 0.0, dhp)
    dHp = 2.0 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2.0)

    Lbp = (L1 + L2) / 2.0
    Cbp = (C1p + C2p) / 2.0
    hsum = h1p + h2p
    hdiff = np.abs(h1p - h2p)
    hbp = np.where(C1p * C2p == 0, hsum,
                   np.where(hdiff <= 180, hsum / 2.0,
                            np.where(hsum < 360, (hsum + 360) / 2.0, (hsum - 360) / 2.0)))

    T = (1
         - 0.17 * np.cos(np.radians(hbp - 30))
         + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6))
         - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dTheta = 30.0 * np.exp(-(((hbp - 275.0) / 25.0) ** 2))
    Rc = 2.0 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7 + 1e-30))
    Sl = 1.0 + (0.015 * (Lbp - 50) ** 2) / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1.0 + 0.045 * Cbp
    Sh = 1.0 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dTheta)) * Rc

    return np.sqrt((dLp / (kL * Sl)) ** 2 + (dCp / (kC * Sc)) ** 2 + (dHp / (kH * Sh)) ** 2
                   + Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh)))


def floor_delta_e(mean_luminance, weber=0.1440, tint=(1.0, 1.0, 1.0)):
    """§13.8's ruled Weber luminance contrast, restated as a ΔE2000 distance.

    Two patches of the family's own material at the given mean, one `weber` above the mean and one
    below, in the ratio the clause rules. What separates them in ΔE2000 is what any signal on this
    floor — lightness, colour, or both — has to be worth.
    """
    hi = mean_luminance * (1.0 + weber / 2.0)
    lo = mean_luminance * (1.0 - weber / 2.0)
    t = np.asarray(tint, dtype=float)
    p1 = np.clip(hi * t, 0, 255)
    p2 = np.clip(lo * t, 0, 255)
    return float(delta_e2000(srgb_to_lab(p1), srgb_to_lab(p2)))


def relative_chroma(rgb):
    """Chroma as a fraction of the pixel's own luminance — what survives the rig.

    THIS IS WHY CHROMA IS WORTH TRYING AT ALL. The light rig multiplies every channel by the same
    falloff, so an authored VALUE difference arrives at the far corner of a room scaled down with
    everything else. A ratio between channels is untouched by that multiplication: a stone that is
    5% greener than its neighbour is still 5% greener in the dark.
    """
    a = np.asarray(rgb, dtype=float)
    L = a.max(axis=-1)
    return (a.max(axis=-1) - a.min(axis=-1)) / np.maximum(L, 1e-6)
