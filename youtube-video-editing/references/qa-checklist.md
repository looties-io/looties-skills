# Self-QA checklist (before every delivery)

Run everything; report what was checked and how.

## Cuts
- [ ] Every segment's head/tail re-transcribed alone matches the expected first/last words (`hear.py`).
- [ ] Full master re-transcribed; diff against the expected text of the EDL (no missing or doubled phrase).
- [ ] Contact sheets: 4 frames around each cut (`qa.py`), plus a 0.5 s before/after scan for head-down or inhale. Single-frame "head down" hits are often a glance: look before acting.
- [ ] Background screen/lights stable across kept segments (luminance scan).

## Image
- [ ] `ffprobe` final: HEVC Main10, `color_transfer=arib-std-b67`, `bt2020`, `hvc1`, frame count = master frames, fps exact.
- [ ] No black or freeze outside designed moments (`blackdetect`, `freezedetect ≥ 1.2 s`).
- [ ] ~50 snapshots of the overlay at key instants composited over the matching master frames (every card type, bites, chapter cards, intro, outro, gags). Check: nothing cut off-frame, spaces between words intact, text readable, portraits complete, no overlap with captions or face.
- [ ] Chunked render: per-chunk frame counts sum to the master; pixel-diff chunk vs full comp = 0 on sample instants.

## Audio
- [ ] Voice correlation with `master_audio.wav` ≈ 1.0000, gain 0.00 dB on speech-only windows.
- [ ] Integrated loudness and true peak reported (expect ≈ −21 LUFS without processing).
- [ ] Every SFX cue lands on its word (check cue time vs word time in `timeline.json`).

## Content
- [ ] Each insert used once (script).
- [ ] All captions proof-read; uncertain words listed.
- [ ] Every removed/added insert from the latest feedback verified at its new timestamp.
- [ ] HyperFrames lint: 0 errors (Studio-organisation warnings are acceptable).
- [ ] Credits list complete.

## Deliverables
- [ ] Final video, `.srt`, chapters `.txt`, jingle WAVs in the export folder.
- [ ] Previous version renamed (e.g. "(superseded)"), not deleted.
