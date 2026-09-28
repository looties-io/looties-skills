#!/usr/bin/env python3
"""Write the two ITU-R BT.2408 display-referred 3D LUTs (.cube, 65^3).

  sdr2hlg.cube  SDR/BT.709 graphics -> HLG/BT.2020. SDR 100 % = 203 cd/m2, so graphics white lands at HLG 75 %.
                Used in the final composite. Input: full-range R'G'B'.
  hlg2sdr.cube  HLG/BT.2020 -> SDR/BT.709 with a soft highlight roll-off. PREVIEWS ONLY, never the deliverable.

  make_luts.py OUT_DIR
"""
import os, sys
import numpy as np

N = 65
A, B = 0.17883277, 1 - 4 * 0.17883277
C = 0.5 - A * np.log(4 * A)
LW, GAMMA, REF_WHITE = 1000.0, 1.2, 203.0
Y2020 = np.array([0.2627, 0.6780, 0.0593])
M709_2020 = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]])
M2020_709 = np.array([[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]])


def grid():
    g = np.linspace(0, 1, N)
    b, gg, r = np.meshgrid(g, g, g, indexing='ij')  # .cube order: R varies fastest
    return np.stack([r, gg, b], -1).reshape(-1, 3)


def hlg_oetf(e):
    e = np.clip(e, 0, 1)
    return np.where(e <= 1 / 12, np.sqrt(3 * e), A * np.log(np.maximum(12 * e - B, 1e-9)) + C)


def hlg_inv_oetf(e):
    e = np.clip(e, 0, 1)
    return np.where(e <= 0.5, e * e / 3.0, (np.exp((e - C) / A) + B) / 12.0)


def bt709_oetf(l):
    l = np.clip(l, 0, 1)
    return np.where(l < 0.018, 4.5 * l, 1.099 * l ** 0.45 - 0.099)


def rolloff(x, knee=0.8):
    over, span = np.maximum(x - knee, 0), 1 - knee
    return np.where(x <= knee, x, knee + span * (over / span) / (1 + over / span))


def sdr2hlg(rgb):
    fd = ((rgb ** 2.4) @ M709_2020.T) * REF_WHITE                      # display light, cd/m2
    ys = np.power(np.maximum((fd @ Y2020) / LW, 1e-12), 1 / GAMMA)      # inverse OOTF
    return hlg_oetf(fd / (LW * np.power(ys, GAMMA - 1))[:, None])


def hlg2sdr(rgb):
    e = hlg_inv_oetf(rgb)
    fd = LW * np.power(np.maximum(e @ Y2020, 1e-9), GAMMA - 1)[:, None] * e
    lin = (fd / REF_WHITE) @ M2020_709.T
    y = np.maximum(lin @ np.array([0.2126, 0.7152, 0.0722]), 0)
    mn = lin.min(1)
    k = np.where(mn < 0, -mn / np.maximum(y - mn, 1e-9), 0).clip(0, 1)[:, None]
    lin = np.maximum(lin + k * (y[:, None] - lin), 0)                  # gamut: pull toward luminance
    mx = np.maximum(lin.max(1, keepdims=True), 1e-9)
    return bt709_oetf(lin * (rolloff(mx) / mx))                        # hue-preserving roll-off


def write(path, title, out):
    with open(path, 'w') as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {N}\n')
        f.writelines(f'{r:.6f} {g:.6f} {b:.6f}\n' for r, g, b in out)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        sys.exit(__doc__)
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    rgb = grid()
    s2h = sdr2hlg(rgb)
    write(f'{d}/sdr2hlg.cube', 'SDR709 graphics to HLG2020 (BT.2408)', s2h)
    write(f'{d}/hlg2sdr.cube', 'HLG2020 to SDR709 (BT.2408), previews only', hlg2sdr(rgb))
    print('graphics white ->', s2h[-1].round(3), '(expect ~0.75)')
