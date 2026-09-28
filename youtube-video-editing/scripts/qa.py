#!/usr/bin/env python3
"""Automatic QA of a final render.

  qa.py FINAL.mp4 --voice master_audio.wav [--cuts 12.3 45.6 ... | --timeline timeline.json]
        [--windows 60:100 300:340] [--out qa/] [--fps 30]

Reports: streams + colour tags, black runs, freezes > 1.2 s, integrated loudness + true peak,
voice integrity (correlation / gain vs the untouched voice on speech-only windows),
and contact sheets of 4 frames around every cut (12 cuts per sheet).
timeline.json: {"segments": [{"start": s, ...}, ...]} (every segment start > 0 is a cut).
"""
import argparse, json, os, re, subprocess
import numpy as np


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pcm(path, a, b):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', path, '-ac', '1',
                                         '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)


ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('final'); ap.add_argument('--voice')
ap.add_argument('--cuts', type=float, nargs='*', default=[]); ap.add_argument('--timeline')
ap.add_argument('--windows', nargs='*', default=[]); ap.add_argument('--out', default='qa')
ap.add_argument('--fps', type=float, default=30)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

p = json.loads(sh(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', a.final]).stdout)
for s in p['streams']:
    print(s['codec_type'], s.get('codec_name'), s.get('profile'), s.get('width'), s.get('height'), s.get('r_frame_rate'),
          s.get('pix_fmt'), s.get('color_transfer'), s.get('color_primaries'), s.get('codec_tag_string'), s.get('sample_rate'))
dur = float(p['format']['duration'])
print(f'duration {dur:.3f} s')

err = sh(['ffmpeg', '-v', 'info', '-i', a.final, '-vf', 'blackdetect=d=0.05:pix_th=0.06,freezedetect=n=0.001:d=1.2',
          '-an', '-f', 'null', '-']).stderr
print('black runs:', [(round(float(x), 2), round(float(y), 2)) for x, y in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', err)])
print('freezes > 1.2 s:', [(round(float(x), 2), round(float(y), 2)) for x, y in re.findall(r'freeze_start: ([\d.]+).*?freeze_end: ([\d.]+)', err, re.S)])

loud = sh(['ffmpeg', '-nostats', '-i', a.final, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
print('loudness', re.findall(r'I:\s+(-?[\d.]+) LUFS', loud)[-1], 'LUFS, true peak', re.findall(r'Peak:\s+(-?[\d.]+) dBFS', loud)[-1], 'dBFS')

if a.voice:
    wins = [tuple(map(float, w.split(':'))) for w in a.windows] or [(dur * f, dur * f + 30) for f in (0.2, 0.5, 0.8)]
    for x0, x1 in wins:
        x, y = pcm(a.voice, x0, x1), pcm(a.final, x0, x1)
        m = min(len(x), len(y))
        print(f'voice {x0:.0f}-{x1:.0f}s: correlation {np.corrcoef(x[:m], y[:m])[0, 1]:.4f}, '
              f'gain {20 * np.log10(np.std(y[:m]) / np.std(x[:m])):+.2f} dB  (music under speech lowers correlation)')

cuts = list(a.cuts)
if a.timeline:
    cuts += [s['start'] for s in json.load(open(a.timeline))['segments'] if s['start'] > 0]
cuts = sorted({round(c, 3) for c in cuts})
strips = []
for k, t in enumerate(cuts):
    f = f'{a.out}/cut_{k:03d}.jpg'
    sh(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, t - 2 / a.fps):.3f}', '-i', a.final, '-frames:v', '4',
        '-vf', 'scale=320:-2,tile=4x1', f])
    strips.append(f)
for i in range(0, len(strips), 12):
    grp = strips[i:i + 12]
    args = sum((['-i', s] for s in grp), [])
    sh(['ffmpeg', '-v', 'error', '-y', *args, '-filter_complex', f'vstack=inputs={len(grp)}' if len(grp) > 1 else 'null',
        f'{a.out}/sheet_{i // 12:02d}.jpg'])
print(f'{len(cuts)} cuts -> contact sheets in {a.out}/ (read them: head down? inhale? flash frame?)')
