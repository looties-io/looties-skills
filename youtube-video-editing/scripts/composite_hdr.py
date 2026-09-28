#!/usr/bin/env python3
"""Composite transparent overlay chunk(s) onto the untouched HLG master; encode HEVC Main10 HLG.

  composite_hdr.py --master master.mov --audio mix.wav --lut sdr2hlg.cube \
                   --overlay ov_0.mov:NFRAMES [--overlay ov_1.mov:NFRAMES ...] \
                   [--gray A:B ...] [--fps 30] [--crf 14] OUT.mp4

- Overlays: HyperFrames ProRes 4444 + alpha (BT.601-coded). Each chunk is trimmed to NFRAMES then concatenated;
  omit :NFRAMES for a single full-length overlay.
- --gray A:B fades the picture to grayscale between A and B seconds (0.25 s ramps), e.g. a "WASTED" gag.
- The master's pixels are never colour-converted; only graphics go through the BT.2408 LUT.
"""
import argparse, json, subprocess

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('out')
ap.add_argument('--master', required=True); ap.add_argument('--audio', required=True)
ap.add_argument('--lut', required=True)
ap.add_argument('--overlay', action='append', required=True)
ap.add_argument('--gray', action='append', default=[])
ap.add_argument('--fps', type=float, default=30); ap.add_argument('--crf', type=int, default=14)
a = ap.parse_args()

dur = float(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', a.master],
                                      capture_output=True, text=True, check=True).stdout)['format']['duration'])
gray = ''
if a.gray:
    terms = []
    for g in a.gray:
        s, e = map(float, g.split(':'))
        terms.append(f'between(t,{s:.3f},{e:.3f})*min(1,min(t-{s:.3f},{e:.3f}-t)/0.25)')
    gray = f",hue=s='max(0,1-({'+'.join(terms)}))'"

inputs, parts = [], []
for k, spec in enumerate(a.overlay):
    path, _, nf = spec.partition(':')
    inputs += ['-i', path]
    parts.append(f'[{k + 1}:v]' + (f'trim=end_frame={int(nf)},' if nf else '') + f'setpts=PTS-STARTPTS[c{k}]')
n = len(a.overlay)
fc = ';'.join(parts) + ';' + ''.join(f'[c{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[ovraw];' + (
    f'[0:v]format=yuv422p10le{gray}[base];'
    f'[ovraw]scale=in_color_matrix=bt601:in_range=tv,format=rgba64le,lut3d=file={a.lut}:interp=tetrahedral,'
    f'scale=out_color_matrix=bt2020:out_range=tv,format=yuva444p10le[ov];'
    f'[base][ov]overlay=format=yuv422p10:eof_action=pass,format=yuv420p10le[v]')
cmd = ['ffmpeg', '-v', 'error', '-stats_period', '10', '-stats', '-y', '-i', a.master, *inputs, '-i', a.audio, '-filter_complex', fc,
       '-map', '[v]', '-map', f'{n + 1}:a', '-r', str(a.fps),
       '-c:v', 'libx265', '-preset', 'medium', '-crf', str(a.crf),
       '-x265-params', 'log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:repeat-headers=1',
       '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc', '-color_range', 'tv',
       '-tag:v', 'hvc1', '-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', '-t', f'{dur:.4f}', a.out]
print(' '.join(cmd))
subprocess.run(cmd, check=True)
