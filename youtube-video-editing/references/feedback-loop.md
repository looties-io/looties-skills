# Handling feedback rounds

Feedback comes as a long list of `À m:ss, …` notes against the last export, mixing cut fixes, insert changes, new assets and new gags.

## Process
1. Parse every note into a table: timestamp → old master time → EDL segment / overlay element → action type (cut, add insert, remove insert, portrait, SFX, gag, caption fix, timing).
2. Separate **systemic** issues from point fixes. Signals: the same defect flagged 3+ times, or wording like "globally", "everywhere", "you missed this level of detail". Systemic = rerun detection/refinement over the whole master, then still hand-check each flagged spot.
3. Global complaints about the image (colour, sharpness, "warm", "low quality") are pipeline issues, never tweak-level: find the conversion/re-encode causing it and remove it.
4. New assets appear in the folder during the round: re-inventory before building.
5. Links (reels, podcasts) → fetch metadata/frames; if the page blocks scraping, ask for the file rather than faking it.
6. Rebuild incrementally (hashed segments), regenerate overlay from the new `timeline.json`, full QA again.

## Report format (in the user's language)
- Lead with the most important fix (usually the image or the systemic cut issue) and its cause in one sentence.
- Warn that timestamps moved (cuts shorten, chapter cards lengthen).
- Then **point by point, in the user's order and with their timestamps**, what was done. Group identical fixes ("1:22, 4:01, 5:44 (transitions): …").
- Then what was verified and how, then what they must check themselves (by ear), then credits.
- If a request could not be satisfied as asked (no take has the right title), say what was done instead and why.

## Typical note → action mapping
| Note | Action |
|---|---|
| "on me voit baisser la tête / je reprends une aspiration avant la transition" | Move segment end before inhale/gaze drop; give the chapter card its own hold |
| "transition trop courte, on n'a pas le temps de lire" | Lengthen the card hold to ≥ 1.7 s readable, add blank if needed |
| "mauvaise coupe, j'ai pas fini les chiffres" | Extend end to the true offset of the last digit; verify by ear |
| "petit bégaiement" | Trim the stutter inside the segment, or swap take |
| "enlève l'insert X, pas cohérent" | Remove, don't replace unless asked |
| "rajoute le portrait de …" | Find a real photo, cut out, add to the existing card, add credit |
| "rajoute un bruitage sur …" | SFX cue on the exact word |
| "je me suis planté (titre/année)" | Swap take; if impossible, self-mockery correction card |
| "fautes dans les sous-titres" | Full proof-read pass, not only the flagged line |
