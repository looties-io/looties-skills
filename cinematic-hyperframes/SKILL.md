---
name: cinematic-hyperframes
description: Cinematic motion design workflow for Hyperframes/Hyperframer and HTML-to-video product films. Use when creating or revising SaaS, app, ecommerce, launch, social, or brand videos that need the /website-to-hyperframes or Website-to-Video pipeline, Hyperframes compositions, catalog-backed blocks/components/transitions, GSAP timelines, VFX-friendly motion, kinetic typography, responsive 16:9/9:16 variants, mock UI states, and export validation.
---

# Cinematic Hyperframes Motion

Use this skill to make Hyperframes videos feel like motion-led product films, not animated decks. Keep the product story readable, but make transitions, typography, UI actions, and payoff moments carry cinematic intent.

## Load Order

1. Use `/website-to-hyperframes` or the Website-to-Video skill first when the work starts from a real website, product UI, or codebase. If that skill is unavailable, follow the same pipeline: capture/context -> `DESIGN.md` -> `SCRIPT.md` -> `STORYBOARD.md` -> narration plan -> compositions -> snapshots -> render.
2. Read `references/hyperframes-catalog.md` before choosing effects, blocks, components, or transitions.
3. Read `.agents/skills/hyperframes-typography-animation/SKILL.md` when the video has vertical text-led beats, hook cards, kinetic typography, cursor-like reveals, or word-by-word interstitials. Reuse its typography principles; do not force its short 5-scene template onto longer product films.

## Prerequisites

Before rendering or installing catalog blocks, verify the local project has:

- Hyperframes plugin/skills installed when the environment supports it:
  `codex plugin marketplace add heygen-com/hyperframes --sparse .codex-plugin --sparse skills --sparse assets`
- Node 22+ available for Hyperframes.
- FFmpeg and FFprobe available for render and metadata checks.
- A Hyperframes project with `hyperframes.json`.
- Local deterministic assets for all images, logos, fonts, audio, and mock data.
- GSAP or equivalent timeline control for motion-heavy scenes.
- No dependency on authenticated routes, live personal data, or unstable screenshot-only states.

Preferred setup:

```bash
npx hyperframes init <project-name>
npx hyperframes add <catalog-id>
npx hyperframes inspect
npx hyperframes validate
```

When starting a serious Website-to-Video project, read the current Hyperframes docs listed in `references/hyperframes-catalog.md` before capture or implementation.

## Production Workflow

1. Capture source truth.
   - Inspect the real app code, design tokens, fonts, UI components, routes, responsive behavior, and copy.
   - Use screenshots only as reference. Rebuild animated, protected, or dynamic states as deterministic HTML/CSS/GSAP.
   - Replace real users, emails, addresses, payments, orders, and private data with realistic mock data.

2. Write the rhythm map before animating.
   - Mark calm beats, setup cards, product actions, transition beats, payoff beats, and outro.
   - Decide where music hits, click pulses, speed ramps, booms, silence, and success bursts should land.
   - Keep linear clarity when explaining a product, but avoid repetitive text -> visual -> text -> visual pacing.

3. Use narrative title cards as chapter beats.
   - Add short interstitials before section changes.
   - Use word-by-word, cursor, mask, punch, compression, snap, or scale reveals.
   - Remove template/internal labels such as "App Showcase", "3D Reveal", or "Feature Frame".

4. Make transitions explain transformation.
   - Pain -> product: rupture, assembly, reconstruction, or wipe.
   - Creation -> live state: click feedback, loading, shimmer, activation glow.
   - Browse -> buy: hover, pulse, click ring, speed ramp, directional pull.
   - Purchase -> success: burst, shockwave, confetti, scale, light impact.
   - Object -> ecosystem: logo floods, overflow grids, parallax, zoom, or dimensional collage.

5. Add dimensionality.
   - Use foreground/background layers, perspective, parallax, masks, z-depth, shadows, blur, and camera moves.
   - Avoid placing every UI panel on the same visual plane.
   - Let important objects feel revealed, assembled, activated, or accelerated.

6. Keep product UI credible.
   - Match real navigation states, buttons, prices, badges, avatars, empty states, mobile states, and final confirmation states.
   - Show cause and effect for UI actions. A click should visibly trigger the next frame.
   - For AI features, show before -> loading -> generated/enhanced result.

7. Design variants, not resizes.
   - Treat 16:9 and 9:16 as separate compositions when density changes.
   - Use mobile-native UI for vertical format when the real product behaves differently.
   - Check text fit, button hit indicators, centered halos, confetti accumulation, and opacity inheritance in each ratio.

8. Validate before claiming done.
   - Run Hyperframes inspect/validate/lint where available.
   - Snapshot key beats in every requested variant.
   - Render only the variants the user asks for.
   - Check duration, dimensions, frame rate, file size, and obvious visual artifacts with FFprobe and snapshots.

## Motion Heuristics

- Calm before impact makes impact stronger.
- Clicks need visible cause and consequence.
- A generated feature should visibly transform, not just appear finished.
- Success frames should feel like payoff moments.
- Brand walls and conference walls should communicate abundance instantly.
- Text cards should feel like cinematic chapters, not subtitles.
- Background opacity should not dim foreground copy.
- Glow and pulse are accents, not art direction.

## Hyperframes Composition Rules

- Use explicit `data-start`, `data-duration`, `data-track-index`, `data-width`, and `data-height`.
- Prefer catalog compositions for specialized motion, then customize them to the story.
- Register paused GSAP timelines so rendering is deterministic.
- Keep external assets local by render time.
- Mount catalog blocks as `data-composition-src` children when they stay modular.
- Inline catalog snippets only when the catalog marks them as components/snippets.
- When staticizing variants, regenerate only the requested variants.

## Quality Bar

The final video should be clear enough to understand, dynamic enough to remember, premium enough to trust, and cinematic enough to create desire.
