---
name: youtube-video-editing
description: "Edit raw talking-head takes into a finished YouTube episode, then derive a 30-second vertical 9:16 short and the publishing copy. Use when a folder of raw takes, a script, a thumbnail and b-roll is handed over for an episode, or on requests like \"edit my YouTube video\", \"derush these takes\", \"cut the stutters and restarts\", \"monte ma vidéo YouTube\", \"make a vertical short from the video\", or a list of timecoded notes on a previous cut. Covers derushing several takes against a script (stutters, restarts, inhales, head-down reading moments cut; natural pauses and improvisation kept), HDR-safe mastering of phone footage, branded intro/outro, chapter cards, inserts, humorous gags and SFX, burned captions plus SRT, frame-level self-QA and feedback rounds. Topic-agnostic. Not for faceless explainers, pure motion graphics, adding captions to an otherwise finished video, or colour grading."
license: MIT
metadata:
  author: Looties
  version: "1.0.0"
---

# YouTube Video Editing: talking head to episode, short and posts

A talking-head edit is judged on two things the editor tends to underrate: **the cut points** and **the picture the camera actually recorded**. Most rework comes from cuts that land on an inhale or a lowered gaze, and from a "harmless" colour conversion that makes phone footage look warm and soft. This skill makes both non-negotiable, keeps camera pixels out of the graphics renderer, and verifies every cut by transcription and frame strips because an agent cannot listen.

It generalizes a full production edit: brief, first cut, one long round of timecoded feedback, an HDR second cut, a vertical short and the launch posts. The subject of the video does not matter; the craft does.

Stack: ffmpeg for everything that touches camera footage, an HTML-to-video engine (HyperFrames by default, Remotion works too) for graphics only, rendered as a transparent overlay. Python 3 with numpy, scipy and opencv-python for the helper scripts; `whisper-cli` (whisper.cpp) and whisperX for transcription.

## Quick reference

| Situation | Go to |
|---|---|
| New folder of rushes + script | Steps 0 → 7 |
| "The image looks warm / lower quality than my rushes" | `references/hdr-pipeline.md`: remove the conversion, don't tweak it |
| "You cut on my breath / I look down before the transition" | `references/cut-rules.md`, rerun detection over the whole master |
| Timecoded notes on a previous cut | Step 8, `references/feedback-loop.md` |
| "Make a 30 s vertical version" | Step 9, `references/short-vertical.md` |
| Title, description, social posts | Step 10, `references/publishing.md` |
| Cards, gags, captions, music | `references/overlays-and-gags.md` |
| Long overlay render fails on disk space | `references/hdr-pipeline.md` § chunked render |

## Rules (each one came from a rejected cut)

1. **Never touch the look of the footage.** Phone rushes are often HDR (HLG, BT.2020, 10-bit). Do not convert to SDR, grade or LUT the camera image. Keep the master in 10-bit HLG; a light temporal denoise (`hqdn3d=1:1:3.5:3.5`) against flicker is the only allowed filter. Composite graphics *into* HLG.
2. **The voice is sacred.** No EQ, compression, denoise or pitch processing. Only a static per-take gain to match takes and 6 ms click guards at cuts. Report loudness (unprocessed speech lands around −21 LUFS) and *offer* a limiter to −14 LUFS instead of applying one.
3. **A cut starts on the voice attack and ends before the next inhale or head-down.** Silence detection alone fails: an inhale is loud, and a lowered gaze before a transition is the most-flagged defect.
4. **On-screen text must be readable.** Chapter cards get their own hold (≈ 2.4 s, ≈ 1.7 s fully readable); add a little blank rather than flash information. Trim long definitions instead of shortening their hold.
5. **No generative imagery.** Real photos, screenshots, archive footage, deterministic cut-outs, code-drawn graphics. Fonts under open licences (OFL). Keep a credits list for every third-party asset as you go.
6. **You cannot hear.** Verify every boundary by transcribing the first and last ~2 s of each segment alone, and every gaze/pose by frame strips around each cut. State in the report which audio (jingle, SFX) was only checked by spectrogram.

## Steps

### 0. Intake
Inventory the folder: raw takes, script, official thumbnail(s), b-roll, photos, brand kit. `ffprobe` every file for resolution, fps, `color_transfer` (`arib-std-b67` means HLG), rotation, sample rate. Collect the exact title, the brand palette and fonts (from the product's live CSS if there is a site), the social handle, the free zone for inserts, the intro/outro wording and a soft maximum length. Write `design.md` (palette, type, layout zones, motion) before any graphics. Details and the reusable standing brief: `references/brief-intake.md`.

### 1. Transcribe and align every source
Word-level timestamps for each take and each b-roll clip with speech (whisperX `large-v3-turbo` + wav2vec2 alignment, with an `initial_prompt` containing hesitations and the episode's proper nouns). Keep a second, independent recogniser (`whisper-cli` + `ggml-large-v3-turbo.bin`) for boundary checks. Word times drift near numbers, restarts and weak unvoiced onsets; never cut on them unverified.

### 2. Derush into a phrase EDL
Map the script onto the takes passage by passage and pick the most fluent and most *human* take for each. Improvisation that adds warmth or a joke stays, even off-script. Encode the edit as a phrase EDL (`kind, source, search-from, first words, last words, options`) rather than raw timecodes: it survives re-transcription and a human can review it. Kinds: `A` (talking head), `BITE` (sound bite from b-roll), `SLOT` (designed gap such as a title or chapter card).

### 3. Refine every boundary, then build the HDR master
Resolve phrases to timecodes, snap to voiced onset/offset (`scripts/voiced.py`), trim head-down moments (`scripts/headpose.py`), split long or head-down internal pauses, verify each boundary by ear-transcription (`scripts/hear.py`) and cache the results. Keep manual overrides (`exact_start`, `force_end`) in the EDL for what the detector gets wrong. Cut into ProRes 422 HQ 10-bit HLG segments, named by a hash of their parameters so feedback rounds only re-encode what changed; concat; write `timeline.json` (every segment and word in master time) and the untouched voice WAV. Alternate a subtle 1.08 punch-in, anchored on the face, on consecutive jump cuts from the same take.

### 4. Overlay composition (graphics only, transparent)
Generate the composition from `timeline.json` with a script, never by hand: captions, inserts, chapter cards, bites, intro/outro, gags, plus `cues.json` (music/SFX, grayscale windows) and the `.srt`. Anchor graphics to *words*, not segments (adjacent segments of one take merge). Lint to zero errors, snapshot ~50 key instants over the matching master frames, fix, then render ProRes 4444 with alpha, in chunks if long. Design rules: `references/overlays-and-gags.md`.

### 5. Mix and composite
`scripts/mix.py`: voice untouched plus cues with envelopes; if the sum would clip, only the bed is lowered. `scripts/composite_hdr.py`: overlay through the BT.2408 SDR→HLG LUT (graphics white at HLG 75 %), alpha over the 10-bit master, HEVC Main10 HLG (`hvc1`) + AAC. Make the first 3 frames the thumbnail so the upload picks it up.

### 6. Self-QA
`scripts/qa.py` on the final file, full re-transcription diffed against the EDL, a full caption proof-read, and a script that proves each insert is used once. Checklist: `references/qa-checklist.md`.

### 7. Deliver and report
Export: final video, `.srt` (same text as the burned captions, no filler sounds), YouTube chapters computed from chapter-card positions, the jingle as WAV. Rename superseded versions instead of deleting them. Report value first: what changed, each feedback point answered, what was verified and how, what the creator must check by ear, the credits line.

### 8. Feedback rounds
Map each note's timestamp back through the *previous* `timeline.json` to an EDL segment or overlay element before editing, and warn that timestamps move. When the same class of defect is flagged several times, treat it as systemic and rerun detection over the whole master. `references/feedback-loop.md`.

### 9. Vertical short 9:16
About 30 s of the strongest moments (hook, most surprising claim, gag payoffs), cut from the clean HDR master rather than the 16:9 composite, face-tracked crop, big 2–3-word karaoke captions inside the platform safe zone, cover as frame 1, end card pointing to the full video. `references/short-vertical.md`.

### 10. Publishing copy
Title, description (hook, programme, chapters, links, credits, hashtags), community post as a poll, LinkedIn launch post, X, Instagram caption. Ask for links you don't have instead of inventing them. `references/publishing.md`.

## Pitfalls

- **A colour conversion "for consistency" ruined a whole cut.** Converting HLG takes to SDR so they matched SDR b-roll produced a warm cast and visible softness, compounded by JPEG frame extraction inside the renderer and two 8-bit re-encodes. The fix was architectural: camera pixels never enter the graphics renderer.
- **HDR b-roll inside an HTML render** made the engine plan a 16-bit frame extraction of several hundred GB. Bring b-roll through ffmpeg into the master, not into the composition.
- **A helper module re-ran on import** and silently overwrote hand-verified cut points. Keep resolver, refiner and builder as separate explicit steps with their own caches.
- **Head-down frames are deliberate cut markers.** Speakers lower their head at the end of a passage so the editor knows where to cut. Missing them was the most repeated note.
- **Numbers get cut short.** A segment ended on the word timing of a long spoken number and resumed on the next sentence before the last digits. Extend to the true voiced offset and re-verify.
- **Chunked overlay renders drift.** A regex rebasing GSAP positions left a chunk timeline of 145,613 s. Assert each chunk's duration and pixel-diff chunk against full composition.
- **Negative GSAP positions** after rebasing break the timeline; land past tweens on their end state at t = 0.
- **A non-breaking space treated as a word separator** split a name from its closing quotation mark in the captions.
- **Renders launched without detaching** died with the parent process after a long capture.

## Verification

The work is done when:
- `ffprobe` shows HEVC Main10, `arib-std-b67`, `bt2020`, `hvc1`, and the frame count equals the master's;
- every segment head and tail re-transcribes to the expected words, and the full re-transcription matches the EDL text;
- voice correlation with the untouched voice is ≈ 1.0000 at 0.00 dB on speech-only windows;
- no black or frozen frames outside designed moments, and the cut contact sheets show no head-down, inhale or flash frame;
- the ~50 snapshots show nothing cropped, overlapping the face or captions, or unreadable;
- the captions are proof-read, uncertain words are listed in the report, and each insert is used exactly once;
- the report answers every feedback note in the creator's order.

## Scripts

| Script | Purpose |
|---|---|
| `voiced.py` | Voiced/silence masks at 100 fps (energy + spectral flatness: breaths are flat, voice is harmonic) and onset/offset helpers |
| `hear.py` | Transcribe a window of a file alone (cached) to verify a cut boundary |
| `headpose.py` | Face landmarks (OpenCV YuNet) → head-down timeline; ratio ≥ 0.60 or no face = head down |
| `make_luts.py` | Writes `sdr2hlg.cube` (graphics into HLG) and `hlg2sdr.cube` (previews only), ITU-R BT.2408 |
| `mix.py` | Voice + cue list → final WAV, bed-only anti-clip ducking |
| `composite_hdr.py` | Overlay chunk(s) + HLG master + mix → HEVC Main10 HLG, optional grayscale windows |
| `qa.py` | Streams, black/freeze, loudness, voice integrity, contact sheets around every cut |

Each has `--help`. The EDL resolver, the composition generator and the chunker are episode-specific: write them per project following the references.

## Related

HyperFrames skills (`hyperframes`, `hyperframes-core`, `hyperframes-cli`, `media-use`) for the overlay composition, music and background removal; [`cinematic-hyperframes`](../cinematic-hyperframes/) for the motion layer.
