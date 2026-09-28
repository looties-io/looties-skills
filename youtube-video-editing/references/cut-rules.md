# Cut rules

## What to remove
- Stutters, repeated words ("so, so", "the the problem"), false starts and restarts, a sentence said twice to self-correct (keep the better one).
- Hesitations searching for a word or name ("and then… what was his name again?") unless the hesitation *is* the joke.
- Inhales before a sentence, sighs, turning the gaze away with a breath (a 3.5 s "looking away + puff" moment was flagged).
- **Head-down moments.** Speakers often lower their head on purpose at the end of a passage to mark a cut point for the editor. Every one of these must disappear. This was the single most repeated feedback.
- Tech glitches: camera start/stop, screen sleeping in the background (detect luminance drops), mic dropouts.
- Slips that can be fixed by another take (wrong number, wrong year, wrong word): swap to a take that says it right. If no take has it right, keep it and turn it into self-mockery (see gags).

## What to keep
- Pauses that give rhythm, reactions, smiles, improvised asides, voice variations, mimed drum rolls, spontaneous jokes.
- Glances while thinking, hand gestures, head movements.

## Boundary precision
- **Start** on the voice attack: first frame of a voiced run (≥ 40 ms voiced within the next 40 ms), with a small pre-roll only if the pre-roll is silence (never an inhale).
- **End** after the last voiced frame + its unvoiced tail (consonant decay, ≤ 150 ms) + a short natural silence (≈ 220 ms; ≈ 150 ms before a designed slot like a chapter card).
- If the tail silence contains a head-down (≥ 50 % of sampled frames), end 120 ms after the last voiced frame.
- Split internal pauses when `gap ≥ 0.8 s`, or `gap ≥ 0.45 s` and the head is down for most of it. Drop resulting slivers shorter than 0.2 s.
- Before a chapter transition: finish on the last word, *before* the inhale and before the gaze drops. The transition card then gets its own time; don't let it absorb the breath.
- Never cut inside a word or a number. When the speaker enumerates digits (a seven- or eight-digit figure), make sure the whole number is inside the segment; a flagged bad cut resumed on the next sentence before the last digits were spoken.

## Verification loop (you cannot hear)
For each segment part `[a, b]`:
1. Transcribe `[a, min(b, a+2.4)]` alone; it must begin with the expected first word(s). Otherwise move the start 120 ms earlier and retry (≤ 12 times).
2. Transcribe `[max(a, b−2.4), b]` alone; it must end with the expected last word(s). Otherwise move later.
3. Anything still unverified goes to a log and gets a manual override (`exact_start`, `force_end`) after listening-by-transcription at several candidate points.
4. Fuzzy word match (normalised, ratio ≥ 0.72 or prefix) — ASR spells names and numbers differently (a year heard as its two-digit short form).
Cache every transcription keyed by `path|a|b`.

## Detector notes
- Voiced detector: 16 kHz mono, 25 ms windows, 10 ms hop; `silence = dB < p90 − 30`; `voiced = dB > p90 − 28 and spectral flatness (80–4000 Hz) < 0.30`. Breaths are loud but flat, so they are not "voiced".
- Head pose: YuNet face landmarks every 6th frame; `ratio = (nose_y − eyes_y) / (mouth_y − eyes_y)`. Head down when `ratio ≥ 0.60` or no face. Isolated single-frame hits are usually a glance: check before acting.
- Do not let a helper module silently re-run and overwrite exact cut points at import time (it happened: a refiner executed on import and discarded manual boundaries). Keep resolver, refiner and builder as separate explicit steps with their own caches.

## EDL format (suggested)
```python
# kind, src, search_from_s, first words, last words, options
('A',    'T4', 58,  "So here is the thing", "and that is the whole story", dict(force_end=84.82)),
('SLOT', 'ch1', 2.4),
('BITE', 'GUEST', 14, "Our message is simple", "across the continent", dict(pre=0.1, post=0.35)),
```
Options: `tag` (anchor name for graphics), `pre`/`post` (max silence kept), `exact_start`/`exact_end`, `force_start`/`force_end` (search from here instead of word times).
