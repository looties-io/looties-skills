# Overlays, inserts, gags, sound

## Layout
- The talking head sits off-centre; the opposite third (e.g. left: x 70–720, y 110–800 on 1920×1080) is the **insert zone**. All cards live there, never over the face.
- Captions: bottom centre, max 2 lines, safe band ≈ y 900–1010, never overlapping an insert.
- Sound bites: full-frame cutaway, blurred plate + sharp vertical clip centred + name/role tag on the side.
- Cards: brand surface colour as glass (`rgba(bg, .86)`), 20–26 px radius, 2 px accent border with soft glow. One ambient motion per card at most.
- Write the brand spec in `design.md` first (palette from the product's real CSS, fonts, zones, motion). Everything else reads it.

## Timing
- Entrances 0.35–0.55 s (`power3.out`, `back.out(1.4)` for pops); exits 0.25–0.35 s (`power2.in`).
- Chapter cards: a wipe that masks the cut (0.35 s in, hold, 0.35 s out), total ≈ 2.4 s with ≈ 1.7 s fully readable, plus a whoosh SFX. It is fine to add a bit of blank to give the card room.
- Name/portrait cards: ≥ 4 s. Definition cards: ≈ 3 s, so trim long definitions.
- A card whose on-screen time computes to something absurd (51 s) or negative is a generator bug: assert durations in the generator.

## Content of inserts
- **Relevance first.** An insert must illustrate what is being said at that moment. Remove anything decorative or off-message ("aujourd'hui" label, a recap card, a photo of someone unrelated to the sentence). When in doubt, fewer inserts.
- **Each b-roll clip and photo is used once.** Enforce by script over the generated composition.
- When a person is named, show their **portrait** in the card (real photo, cut out deterministically; look up a licensed/CC photo on the web if none is provided, note the credit).
- When a social account is mentioned, prefer a playful "follow me" card (handle, cursor clicking "Follow", hearts, click SFX) over a random photo.
- Mentioned media (podcast episode, reel, article): build a native-looking card from the real metadata (Spotify-style: cover, episode title, duration; Instagram reel: muted panel of the clip). Fetch the metadata, don't invent it.
- Screenshots provided by the user (product page, merch): crop cleanly, show once, at readable size.
- Low-resolution assets (e.g. a 164×218 selfie): display small (polaroid style) rather than upscale into blur.
- Reuse the official thumbnail as is for the title moment (animate it: zoom, flash, light sweep) instead of rebuilding a lookalike.
- Frame 1–3 of the video = the thumbnail, so the upload auto-picks it.
- The speaker's own quote does not need a quote card of itself.

## Humour and self-mockery (creators and audiences respond to these)
Nerdy, internet-culture gags timed on the word:
- **"WASTED"** (GTA style) when someone is caught lying/wrong: image fades to grayscale over 0.25 s, red Bangers text, SFX.
- **Drum roll** SFX on a mimed or announced drum roll, landing exactly on the reveal word.
- **Comic "BOUM !"** text on an explosion word.
- **Escalating pop-ups**: e.g. dozens of Clippy-like mascots popping faster and faster, ending in a full-frame archive explosion (public-domain archive footage, cropped to remove watermarks) on the punchline.
- **"Oops, slip" correction card** when the speaker gets a title/name wrong and no take has it right: strike through the wrong words, a sparkling arrow, the correct title.
- **Analysis bar / counter** animation during "and the result is…".
Keep gags short, on the beat, and only where the speech already carries the joke. Use real images (memes, archive, public domain), never generated ones.

## Captions
- Burned in, 1–2 lines, no onomatopoeia ("euh", "hmm"), no filler repetitions.
- Split text on word boundaries with non-breaking spaces treated as part of the word (a bug once split a name from its closing guillemet).
- Proof-read all of it: agreements and plurals, proper nouns, capitalisation (`l'État`), French typography (non-breaking space before `% ? ! : ;`, « » with inner spaces), hyphenated imperatives (`dites-le-moi`).
- Captions follow what is said, even when wrong; the correction goes in a card.
- Keep a list of uncertain words for the report instead of guessing silently.
- When writing JS strings in the generator, escape apostrophes (French text is full of them) or use template literals.

## Music and SFX
- One jingle, reused at intro and outro: pop, warm, round bass, Rhodes-like keys, slightly jazzy, nothing shrill. Either a licence-free track from the `/media-use` catalogue or synthesised in code. A discreet bed may run under the hook and the ending.
- SFX catalogue per gag (whoosh on chapter cards, click on follow card, drum roll, boom, pop for each mascot, record-scratch/sting for WASTED).
- Everything goes into `cues.json` as `{file, start, gain, dur?, env?[[t, g], …]}`; the voice is never modified, only the bed is ducked if the sum would clip.
- Say in the report that jingle and SFX were checked by spectrogram only.

## Licensing and credits
Fonts OFL only. Keep a running credits list: photographer of event photos, CC licences (e.g. "TechCrunch, CC BY 2.0"), public-domain sources (government photos, archive footage), short quotations of TV extracts or trademarks (named as such). This list goes straight into the description.
