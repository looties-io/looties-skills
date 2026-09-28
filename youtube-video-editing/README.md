# youtube-video-editing

Turn raw talking-head takes into a finished YouTube episode, then derive a 30-second vertical short and the launch posts, without the two defects that cause most rework: **cuts that land on a breath or a lowered gaze**, and **a colour conversion that makes phone footage look warm and soft**.

What it covers:

- **Derushing several takes against a script.** Stutters, restarts, repeated sentences, inhales and head-down reading moments are cut. Rhythm pauses and warm improvisation stay. The edit is a phrase EDL (first words / last words), not raw timecodes.
- **Cut points verified without ears.** Each boundary snaps to the voice attack (energy + spectral flatness, so breaths don't count as voice) and to head-pose data. Each segment's head and tail is re-transcribed alone to prove no word was clipped.
- **HDR-safe mastering.** Phone HLG footage stays 10-bit HLG end to end. Graphics are rendered alone on a transparent overlay and mapped into HLG with an ITU-R BT.2408 LUT. The output is HEVC Main10 HLG, which YouTube accepts.
- **Branded packaging.** Intro/outro with a jingle, readable chapter cards, portrait and media cards in a reserved insert zone, well-timed humorous gags with SFX, burned captions plus an `.srt`, and chunked overlay renders for long videos.
- **Self-QA and feedback rounds.** Black/freeze detection, loudness and voice-integrity checks, contact sheets around every cut, and a method for answering a long list of timecoded notes point by point.
- **Vertical short and publishing copy.** A face-tracked 9:16 cut with safe-zone captions and a cover, plus the title, description, chapters, credits and posts for YouTube, LinkedIn, X and Instagram.

Topic-agnostic: it was built on a real episode edit and generalized.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill youtube-video-editing
```

Requires ffmpeg, Python 3 with numpy, scipy and opencv-python, `whisper-cli` (whisper.cpp) with `ggml-large-v3-turbo.bin`, and whisperX for alignment. The overlay layer assumes HyperFrames; Remotion works with the same pipeline shape.

See [`SKILL.md`](./SKILL.md) for the full workflow.
