# Brief intake

## What the user typically hands over

A folder containing:
- **Raw takes** of the talking head (several full run-throughs of the same script, 10–25 min each).
- **Script / "conducteur"**: the guiding text. The edit follows it, but freer, more natural phrasing wins over reading.
- **Official thumbnail(s)** 16:9 (and sometimes a vertical one). The thumbnail is also the visual reference for intro/outro.
- **Context photos** and **event / b-roll videos** (often vertical phone clips) used as illustration inserts and sound bites.
- Assets added during feedback (selfies, screenshots of a product page, links to reels/podcasts).

## Reference brief (the standing expectations, reusable for any episode)

- Analyse every take frame by frame; understand which parts must go.
- The goal is **not** removing all silences: pauses that give rhythm stay. Useless silences go.
- Cut stutters, word repetitions, restarts ("je recommence"), a pause followed by the same sentence said again, hesitations, and **head-down moments that are obviously reading**. Replace them with a fluent passage from another take.
- Head movements, hand gestures, looking away briefly while thinking: OK. It should feel like a conversation, nobody looks straight into the lens 100 % of the time.
- Prefer passages with more natural context and improvisation, even off-script, as long as they add interaction and humanity.
- Also cut: camera on/off moments, the background screen going to sleep, mic dropouts, any technical glitch.
- Keep all natural voice. **No audio distortion or processing.** Pure editing.
- If parts of the image are slightly altered, make quality homogeneous across takes (by choice of take and matching, not by grading the image).
- **Hook / intro**: after the greeting and the topic announcement, a short title animation with the exact episode title and a jingle. **Outro**: same jingle, a short goodbye animation. Respect the brand's art direction (colours, fonts), even if the animation is basic.
- Music: same jingle intro and outro, pop, warm fat bass, a bit jazzy, nothing shrill or high-pitched.
- Inserts (b-roll, photos) are used **once each**. The left third of the frame is deliberately left free for inserts; respect placement, size and text room.
- Cut-outs and screenshots must be clean (proper matting, proper captures). **No generative image AI.**
- Burned-in captions, no onomatopoeia. Dubbing is done natively by YouTube at upload, so also ship the `.srt`.
- Transitions where relevant, mostly between big parts; never at the expense of cutting a sentence or making a passage unintelligible. Calibrated on the speech cadence.
- No target duration; soft cap ~15 min.
- Full freedom on tooling (HyperFrames or Remotion, install what is missing).
- Heavy self-checking, frame by frame, end to end coherence, before delivering.

## Things to pin down at intake (investigate first, ask only if not discoverable)

| Item | Where to find it | Default |
|---|---|---|
| Exact title | brief, thumbnail text | ask if absent |
| Brand palette/fonts | the product's live CSS, logo files, thumbnail | extract, write `design.md` |
| Channel/social handle | brief, previous descriptions | ask |
| Free zone for inserts | look at the framing of the takes | the side opposite the face |
| Colour transfer of each source | `ffprobe -show_streams` (`color_transfer`) | keep native |
| Which take is the base | transcripts + fluency | the most natural take, others as patches |
| Proper-noun spellings | script, event programme, web | verify on the web, flag uncertain ones |

`ffprobe` checklist per file: `width,height,r_frame_rate,color_transfer,color_primaries,pix_fmt,side_data (rotation),sample_rate`. Vertical phone clips often carry a rotation flag; HDR b-roll mixed into an SDR render makes HyperFrames extract 16-bit frames (hundreds of GB): another reason to keep camera footage out of the HyperFrames render entirely.
