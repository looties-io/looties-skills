#!/usr/bin/env python3
"""Voiced-speech and silence masks at 100 frames/s, plus cut-boundary helpers.

Energy + spectral flatness: breaths are loud but noise-like (flat spectrum), voice is harmonic.
  silence = dB < p90 - 30
  voiced  = dB > p90 - 28 and flatness(80-4000 Hz) < 0.30

CLI:  voiced.py FILE [--at SECONDS ...]   prints voice onset/offset around each time.
Lib:  from voiced import masks, onset_from, offset_before, pre_roll, tail
"""
import argparse, functools, subprocess
import numpy as np

FR = 100  # frames per second (10 ms hop)


@functools.lru_cache(None)
def features(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    hop, win = 160, 400
    n = (len(a) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    sp = np.abs(np.fft.rfft(a[idx] * np.hanning(win)[None, :], axis=1)) ** 2 + 1e-12
    f = np.fft.rfftfreq(win, 1 / 16000)
    p = sp[:, (f > 80) & (f < 4000)]
    flat = np.exp(np.log(p).mean(1)) / p.mean(1)
    db = 10 * np.log10(sp.sum(1) / win + 1e-12)
    return db, flat


def masks(path):
    """-> (db, flatness, silent, voiced) arrays, one value per 10 ms."""
    db, flat = features(path)
    p90 = np.percentile(db, 90)
    return db, flat, db < p90 - 30, (db > p90 - 28) & (flat < 0.30)


def onset_from(v, i, lim):
    """First frame >= i that starts a voiced run (>= 2 of the next 3 frames voiced)."""
    while i < lim - 4:
        if v[i] and v[i + 1:i + 4].sum() >= 2:
            return i
        i += 1
    return None


def offset_before(v, i, lim):
    """Last voiced frame <= i (not before lim)."""
    while i > lim:
        if v[i] and v[i - 3:i].sum() >= 1:
            return i
        i -= 1
    return None


def pre_roll(sil, v, on, maxf=14):
    """Start frame for a cut: back off from the onset only through true silence, never into an inhale."""
    j = on
    while j > on - maxf and not sil[j - 1] and not v[j - 1]:
        j -= 1
    return j - 2 if sil[j - 1] else j


def tail(sil, v, off, keep=22):
    """End frame for a cut: unvoiced decay (<= 150 ms) then up to `keep` frames of silence."""
    j, k = off + 1, 0
    while k < 15 and not sil[j] and not v[j]:
        j += 1; k += 1
    k = 0
    while k < keep and sil[j]:
        j += 1; k += 1
    return j


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file')
    ap.add_argument('--at', type=float, nargs='*', default=[], help='times (s) to inspect')
    ap.add_argument('--window', type=float, default=1.5, help='search radius (s)')
    a = ap.parse_args()
    db, flat, sil, v = masks(a.file)
    print(f'{len(v) / FR:.2f} s analysed, voiced {v.mean():.0%}, silent {sil.mean():.0%}')
    for t in a.at:
        i, w = int(t * FR), int(a.window * FR)
        on = onset_from(v, i, min(len(v), i + w))
        off = offset_before(v, i, max(0, i - w))
        print(f'@{t:.2f}: next onset {on / FR if on else None}  (cut in at {pre_roll(sil, v, on) / FR if on else None})'
              f' | previous offset {off / FR if off else None}  (cut out at {tail(sil, v, off) / FR if off else None})')
