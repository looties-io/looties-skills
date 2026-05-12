# Hyperframes Catalog And Dependency Reference

Use this reference before choosing Hyperframes blocks, components, and transitions. Prefer checking the live catalog when network access is available:

- Catalog index: https://hyperframes.heygen.com/catalog/
- Documentation index: https://hyperframes.mintlify.app/llms.txt

## Required Hyperframes Docs For Website-To-Video Projects

Read these before implementation when the user asks for a website/app-to-video project or explicitly mentions `/website-to-hyperframes`:

- Website-to-video guide: https://hyperframes.heygen.com/guides/website-to-video
- Prompting guide: https://hyperframes.heygen.com/guides/prompting
- Compositions concept: https://hyperframes.heygen.com/concepts/compositions
- Frame adapters concept: https://hyperframes.heygen.com/concepts/frame-adapters
- Determinism concept: https://hyperframes.heygen.com/concepts/determinism

Use those docs to ground capture strategy, composition structure, frame resizing/adaptation, and deterministic render behavior. Do not rely on memory if the project needs current Hyperframes behavior.

## Core Dependencies

- Hyperframes CLI: initialize projects, add catalog assets, inspect, validate, snapshot, and render.
- Hyperframes plugin skills: install with `codex plugin marketplace add heygen-com/hyperframes --sparse .codex-plugin --sparse skills --sparse assets` when missing and the environment permits plugin installation.
- Node 22+: preferred runtime for current Hyperframes projects.
- FFmpeg/FFprobe: required for rendering, metadata checks, sample extraction, and compression validation.
- Chrome/Chromium: required for browser-based capture/render. HTML-in-Canvas blocks may need browser feature flags for preview; the CLI enables required flags during render when supported.
- GSAP: preferred timeline system for product/UI motion, registered paused timelines, and deterministic frame stepping.
- Website-to-Video skill: required when the source of truth is a real website or app. Use it for capture/context, design extraction, script/storyboard, composition planning, validation, and render handoff.
- Local motion skill: `.agents/skills/hyperframes-typography-animation/SKILL.md` for strong typography beats and vertical text-led scenes.

## Catalog Block Map

Install catalog items with:

```bash
npx hyperframes add <catalog-id>
```

Then mount block compositions like:

```html
<div
  data-composition-id="<id>"
  data-composition-src="compositions/<id>.html"
  data-start="0"
  data-duration="6"
  data-track-index="1"
  data-width="1920"
  data-height="1080"></div>
```

Components/snippets are different: open the installed snippet file and paste/customize its contents in the target composition.

## High-Value Blocks And Components

### 3D UI Reveal

- URL: https://hyperframes.heygen.com/catalog/blocks/ui-3d-reveal
- Install: `npx hyperframes add ui-3d-reveal`
- Use for: opening product UI reveals, marketplace/app introductions, perspective UI entrances, hook-to-product transitions.
- Default details: block, 1920x1080, 13s, file `compositions/ui-3d-reveal.html`.

### App Showcase

- URL: https://hyperframes.heygen.com/catalog/blocks/app-showcase
- Install: `npx hyperframes add app-showcase`
- Use for: feature sequences, three-step flows, multi-screen product demonstrations, before/action/result structures.
- Default details: block, 1920x1080, 5.5s, file `compositions/app-showcase.html`.

### VFX Text Cursor

- URL: https://hyperframes.heygen.com/catalog/blocks/vfx-text-cursor
- Install: `npx hyperframes add vfx-text-cursor`
- Use for: cinematic interstitials, title cards, dramatic chapter transitions, high-impact hook copy.
- Motion character: cursor glow, chromatic rays, directional lighting, shader-style post-processing.
- Default details: block, 1920x1080, 8s, file `compositions/vfx-text-cursor.html`.

### Shimmer Sweep

- URL: https://hyperframes.heygen.com/catalog/components/shimmer-sweep
- Install: `npx hyperframes add shimmer-sweep`
- Use for: AI accents, premium activation, generated-state reveals, button/status highlight sweeps, badge polish.
- Default details: component/snippet, file `compositions/components/shimmer-sweep.html`. Paste snippet contents into the target composition.

### Logo Outro

- URL: https://hyperframes.heygen.com/catalog/blocks/logo-outro
- Install: `npx hyperframes add logo-outro`
- Use for: final brand lockup, tagline reveal, logo assembly, URL pill, final CTA.
- Default details: block, 1920x1080, 6s, file `compositions/logo-outro.html`.

### Instagram Follow

- URL: https://hyperframes.heygen.com/catalog/blocks/instagram-follow
- Install: `npx hyperframes add instagram-follow`
- Use for: social follow CTA, creator/brand follow cards, final social overlay.
- Default details: block, 1080x1920, 4.5s, files `compositions/instagram-follow.html` and `assets/avatar.jpg`.

## Transition Vocabulary

Use transitions as storytelling devices, not decoration.

Shader transitions available in the catalog include:

- Chromatic Radial Split
- Cinematic Zoom
- Cross Warp Morph
- Domain Warp Dissolve
- Flash Through White
- Glitch
- Gravitational Lens
- Light Leak
- Ridged Burn
- Ripple Waves
- SDF Iris
- Swirl Vortex
- Thermal Distortion
- Whip Pan

CSS transition categories available in the catalog include:

- 3D
- Blur
- Cover
- Destruction
- Dissolve
- Distortion
- Grid
- Light
- Mechanical
- Push
- Radial
- Scale

## Selection Guide

- Opening hook into product: 3D UI Reveal, Cinematic Zoom, VFX Text Cursor.
- Text-only story beat: VFX Text Cursor or the local typography animation skill.
- AI generation/enhancement: App Showcase plus Shimmer Sweep and a visible before -> loading -> after sequence.
- Product click/action: click ring, hover state, button depression, small impact burst, then directional transition.
- Success/payoff: scale hit, burst, shockwave, controlled confetti, light impact.
- Abundance/ecosystem: overflowing logo grid, parallax layers, camera push, repeated recognizable marks.
- Outro: Logo Outro, optionally combined with Instagram Follow for social CTA.

## Validation Checklist

- Inspect/lint/validate the Hyperframes composition.
- Snapshot narrative, UI, transition, success, and outro beats in each aspect ratio.
- Confirm no internal catalog/template labels are visible.
- Confirm click indicators land on the target button.
- Confirm mobile variants are redesigned, not merely scaled.
- Confirm foreground text is not dimmed by background image opacity.
- Confirm decorative particles/confetti do not pile into ugly horizontal artifacts.
- Confirm final logo edges and halo alignment are clean.
- Check MP4 duration, dimensions, frame rate, and file size with FFprobe.
