#!/usr/bin/env python3
"""Final mix: the voice untouched + music/SFX cues. If the sum would clip, only the bed is lowered.

  mix.py VOICE.wav CUES.json OUT.wav [--assets DIR]

CUES.json: {"cues": [{"file": "sfx/whoosh.wav", "start": 12.34, "gain": 0.5,
                      "dur": 2.0,                       # optional: truncate
                      "env": [[0, 0], [0.3, 1], [2, 0]]  # optional: gain envelope (s from cue start, factor)
                     }, ...]}
All WAVs must be 48 kHz PCM16 (mono or stereo). `file` is relative to --assets (default: CUES.json's folder).
"""
import argparse, json, os, wave
import numpy as np

SR = 48000


def read(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR, f'{path}: resample to {SR} Hz first'
        a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
        return a.reshape(-1, 2) if w.getnchannels() == 2 else np.repeat(a[:, None], 2, 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('voice'); ap.add_argument('cues'); ap.add_argument('out'); ap.add_argument('--assets')
    a = ap.parse_args()
    base = a.assets or os.path.dirname(os.path.abspath(a.cues))
    voice = read(a.voice)
    n = len(voice)
    bed = np.zeros_like(voice)
    for c in json.load(open(a.cues))['cues']:
        x = read(os.path.join(base, c['file']))
        if c.get('dur'):
            x = x[:int(c['dur'] * SR)]
        g = np.full(len(x), c.get('gain', 1.0), np.float32)
        if c.get('env'):
            pts = np.array(c['env'], float)
            g *= np.interp(np.arange(len(x)) / SR, pts[:, 0], pts[:, 1]).astype(np.float32)
        x = x * g[:, None]
        i = int(round(c['start'] * SR))
        if i < 0:
            x, i = x[-i:], 0
        m = min(len(x), n - i)
        if m > 0:
            bed[i:i + m] += x[:m]
    lim = 0.97
    hot = np.abs(voice + bed).max(1) > lim
    if hot.any():
        from scipy.ndimage import minimum_filter1d, uniform_filter1d
        need = np.ones(n, np.float32)
        idx = np.where(hot)[0]
        need[idx] = np.clip((lim - np.abs(voice[idx]).max(1)) / (np.abs(bed[idx]).max(1) + 1e-9), 0, 1)
        k = int(0.01 * SR)
        bed *= uniform_filter1d(minimum_filter1d(need, k), k)[:, None]   # smooth: never clicks
        print('bed ducked on', int(hot.sum()), 'samples')
    out = voice + bed
    print(f'peak {20 * np.log10(np.abs(out).max() + 1e-12):.2f} dBFS')
    with wave.open(a.out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
