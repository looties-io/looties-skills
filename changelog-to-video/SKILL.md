---
name: changelog-to-video
description: Use when turning a changelog, release notes, or a list of shipped features into a polished feature-showcase video (weekly changelog video, release recap, "what's new" reel, launch montage) and you want each feature shown as a REAL animated mock-up instead of a generic text card. Triggers include "our changelog videos all look like the same card", deduping overlapping entries, and rendering HTML/GSAP motion to MP4.
---

# Changelog to Video

## Overview

Turn a changelog into a feature-showcase video where **every feature gets a real mock-up** — a screenshot, recording, or faithful UI illustration — not a generic text card. The default failure mode of these systems is that *every* scene degrades to the same card; the fix is an explicit **asset waterfall** that exhausts real-mockup options before ever falling back, plus deduping overlapping entries.

Engine-dependent: this pairs with an HTML-to-video engine (**HyperFrames** or **Remotion**). For the motion layer, use the **cinematic-hyperframes** skill.

## When to use

- A weekly/periodic changelog or "what's new" video.
- A release recap or feature-launch reel from release notes / shipped PRs.
- Symptom: your generated videos all look like the same neon card with a title and no real UI.

Not for: a single talking-head recut, or a one-feature launch film (use a product-launch flow).

## The asset waterfall (the core)

For each feature, walk these rungs **in order — first hit wins** — and only fall back when truly stuck:

| # | Rung | Use when | Source |
|---|---|---|---|
| ① | **Reuse** | a prior/approved mock-up of this feature already exists (especially "improvement" re-mentions) | a small committed registry, keyed by feature |
| ② | **Live capture** | the feature has a public page (product / catalog / social / content) | Playwright screenshot of the public route → render as a framed image |
| ③ | **Synthetic** | no asset, but you know the feature's shape | a simple, faithful UI mock built from the description / codebase |
| ④ | **Card** | genuinely nothing to show | the generic motion card — last resort ONLY |

Principle: **the context of the feature decides the rung.** Product, social, and content features almost always have real assets — use them. The card is a fallback, never the default.

## Dedup related entries

Before building scenes, group entries by feature and **merge related ones** into a single scene at the latest state: "X is live" + "X now supports Y" → one "X (now with Y)" scene. One scene per feature.

## Render-safe motion

Whichever engine, keep scene motion **deterministic and GPU-cheap** — animate only `opacity` / `x` / `y` / `scale` (and `scaleX/Y`). No animated CSS filters, no `Math.random`, no `Date.now`, no network at render time. This keeps frames reproducible and the renderer fast.

## Pipeline

1. Parse the changelog into entries `{date, tag, title, desc}`.
2. **Dedup** by feature (above).
3. Per feature, resolve the **asset waterfall** into an `asset_plan` (`reuse` | `capture` | `synthetic` | `card`) plus an archetype.
4. Resolve plans into real image files: reuse copies from the registry; capture screenshots the public route; failures downgrade one rung (never crash the render).
5. Compose intro → per-feature scenes (real mock-ups) → outro, with kinetic transitions.
6. Render both 16:9 and 9:16.

## Mock vocabulary (archetypes)

A scene archetype maps structured slots → a `.mock` illustration. A useful set:

- `asset-grid` — real screenshots in a 1/2/3-column grid
- `product-card` — one framed hero screenshot
- `flow` — a multi-step UI recreation (e.g. a moderation/checkout flow)
- `duration-timeline` — a before/after metric bar
- `artifact-card` — a code-styled card for a shipped repo / skill / API
- `card` — the generic motion card (fallback)

**Every archetype your router can pick MUST exist.** A router that routes to an unimplemented archetype silently falls back to a card — the #1 cause of "always generic cards".

## Common mistakes

- **Always-card trap:** no asset pipeline + strict slot validation → every feature degrades to the card. Build the waterfall; make the card the last rung.
- **Phantom archetypes:** routing to `asset-grid`/`product-card` that were never implemented → instant card. Implement every archetype the router references, and wire the real-asset lookup (don't hardcode "no assets available").
- **No dedup:** "X is live" and "X now supports Y" render as two near-identical scenes.
- **Non-deterministic motion:** filter/random/time-based animation breaks reproducible rendering.
- **Capturing logged-in pages first:** start with public routes only; authenticated capture is a separate, heavier concern (seeded test account + secrets).

## Reference implementation

Looties' `looties-changelog-video/`: HyperFrames + GSAP, with `archetypes.py` (asset-grid / product-card / flow / …), `registry.py` (the reuse rung), `capture.py` (the public-route Playwright waterfall), and `build_video.py` (renders asset archetypes; emits a card only when the plan says so). A render-only CI workflow performs the capture + render at `contents: read` (least privilege).
