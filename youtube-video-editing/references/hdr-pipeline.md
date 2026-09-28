# HDR-safe pipeline

## Why
Phone rushes are frequently HLG / BT.2020 10-bit (`color_transfer=arib-std-b67`). A V1 converted them to SDR with a home-made LUT, extracted frames as JPEG during the render and re-encoded twice in 8-bit: warm cast, visible quality loss, rejected. The fix is architectural: **camera pixels never go through the graphics renderer.**

## Shape
```
takes (HLG 10-bit) ──ffmpeg cut──▶ master.mov (ProRes 422 HQ 10-bit HLG) ─┐
                                   master_audio.wav (voice, untouched)     │
timeline.json ──generator──▶ HyperFrames overlay (graphics only, alpha)    │
                              └─render─▶ ov_K.mov (ProRes 4444 + alpha) ───┤
cues.json ──mix.py──▶ mix.wav ─────────────────────────────────────────────┤
                                                        composite_hdr.py ◀─┘
                                     final.mp4 (HEVC Main10 HLG, hvc1, AAC)
```

## Master segments
```
-vf "format=yuv422p10le,hqdn3d=1:1:3.5:3.5,[punch-in scale/crop],fps=30,format=yuv422p10le,
     setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv"
-c:v prores_ks -profile:v 3 -vendor apl0 -pix_fmt yuv422p10le
-color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv
```
- Seek with `-ss` before `-i` and cut by frame count (`-frames:v`), never by duration, so the concat is frame-exact.
- The light `hqdn3d` reduced measured flicker by ~61 % without losing hair detail. Nothing else touches the image.
- Name each segment file by a hash of `(src, in, nframes, filter)`: rebuilding after feedback only re-encodes the changed segments (a full rebuild is ~40 min for 10 min of 4K-ish footage).
- `SLOT` segments are black ProRes of the designed duration (the overlay covers them).
- Designed grayscale moments (e.g. a "WASTED" freeze) are done in the composite, on the 10-bit signal: neutral chroma is 512; `hue=s=…` with a time expression fades saturation in/out over 0.25 s.

## Graphics into HLG
- Graphics are authored in sRGB/BT.709. Map them with the BT.2408 display-referred LUT (`sdr2hlg.cube` from `make_luts.py`): SDR 100 % → 203 cd/m² → graphics white at **HLG 75 %**. Never put graphics at HLG 100 %, they glare.
- HyperFrames' ProRes 4444 alpha output is BT.601-coded: read it with `scale=in_color_matrix=bt601:in_range=tv`, convert to `rgba64le`, apply `lut3d` (tetrahedral), then `scale=out_color_matrix=bt2020:out_range=tv,format=yuva444p10le`, then `overlay=format=yuv422p10`.
- Final encode: `libx265 -preset medium -crf 14`, x265 params `colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:repeat-headers=1`, `-tag:v hvc1`, `-movflags +faststart`. YouTube accepts it; the HDR version appears a bit after upload, YouTube derives SDR itself.
- Sound bites from b-roll: they are also HDR; bring them into the master the same way (full frame, blurred plate background + sharp vertical foreground), not into HyperFrames.

## Chunked overlay render (long videos)
HyperFrames alpha renders reserve roughly **8 MB per frame of free disk upfront** (an 11-min 30 fps overlay did not fit). Render in time windows:
- Cut windows at static moments (e.g. 1.2 s into each chapter card).
- For each window, rebase every clip's `data-start`/`data-duration` (hide clips fully outside), shift video `data-media-start` for clips that began earlier, and shift every GSAP position by `−t0`.
- Tweens whose position becomes negative: set `duration:0`, `stagger:0`, position 0 (land on the end state). Negative GSAP positions break the timeline.
- Guard word-by-word (karaoke) loops so they skip words outside the window.
- Pad the timeline with `tl.set({}, {}, windowDuration)`.
- Validate: timeline duration of each chunk equals its window (a bad regex once left a 145 613 s chunk); pixel-diff 3 instants of one chunk against the full composition → must be 0.
- In the composite, `trim=end_frame=N` each chunk to its exact frame count, then `concat`.
- Launch long renders properly detached (background task), or they die with the parent.

## LUT for previews
`hlg2sdr.cube` (BT.2408 HLG→SDR with soft roll-off) is only for SDR previews/contact sheets and for checking graphics over footage. Never for the deliverable.
