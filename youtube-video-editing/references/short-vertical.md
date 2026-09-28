# Vertical short 9:16 (Reels / Shorts / TikTok)

Request pattern: "a 30-second version, ultra-short cuts, vertical, only the juiciest passages: the funniest, strongest, most intriguing".

## Selection
- Pick 6–8 moments from the **edited master's** timeline: the concept hook, the most surprising claim (ideally a guest bite), the confrontation line, the gag payoffs (drum roll → WASTED, BOUM, mascots → explosion). Each moment 1.5–5 s, cut tight on voice attack/offset.
- Target 30 s; if something strong doesn't fit, drop it and say so ("removed X to stay at 30 s, can put it back at ~35 s").
- Re-verify every short boundary by re-transcribing the short's audio.

## Picture
- Source = the clean HLG master (no 16:9 overlay), not the composite.
- Talking head: detect the face (YuNet) on 5 frames per clip, take the median x, crop `608×1080` around it, scale to `1080×1920` (lanczos). Keep HLG 10-bit tags.
- Sound bites: use the original vertical b-roll file directly at full resolution (better than re-cropping the master's blurred plate).
- Full-frame archive moments (explosion): start where the action is visible (the fireball appeared at 1.5 s, start at 1.3 s) and shift the vertical crop onto it.
- Freeze-frames for gags (e.g. 1 s grayscale freeze on WASTED).

## Graphics
- Overlay rendered separately (1080×1920 alpha) and composited into HLG exactly like the long video.
- Captions: big (≈ 80 px, weight 900, stroke + shadow), 2–3 words at a time, the spoken word highlighted in the brand accent, placed **below the face and above the bottom UI** (≈ y 1420 on 1920). Stay out of the Reels UI zones: top ≈ 220 px, bottom ≈ 380 px, right ≈ 140 px (action buttons).
- Hook text at the top (y ≈ 230) in the first second: episode title + the question.
- Restore punctuation and capitals in captions ("là ?", "mytho !").
- End card ≈ 1.8 s: "Full video on YouTube · Link in bio · @handle", on the jingle's last chord.
- Frame 1 = the 9:16 cover.

## Cover 9:16
Recompose the 16:9 thumbnail vertically (speaker, key faces, title, banner, badge), keeping title and faces inside the central area visible in the profile grid (the grid crops to ~4:5 or 1:1). Check emoji and accent-coloured words aren't clipped.

## Delivery notes for the user
- Post from the mobile app (it handles HDR best).
- On the cover screen, "add from camera roll" and pick the PNG (sharper than a video frame).
