# changelog-to-video

Turn a changelog (release notes / shipped-feature list) into a polished feature-showcase video where **every feature gets a real mock-up** — a screenshot, recording, or faithful UI illustration — instead of the same generic text card.

The core idea is an **asset waterfall**: for each feature, try ① reuse an approved prior mock-up → ② live-capture the feature's public page → ③ build a simple synthetic mock → ④ fall back to a generic motion card only as a last resort. Plus deduping overlapping entries ("X is live" + "X now supports Y" → one scene) and deterministic, render-safe motion.

Engine-aware: pairs with an HTML-to-video engine (HyperFrames or Remotion) — see the `cinematic-hyperframes` skill for the motion layer.

## Install

```bash
npx skills@latest add looties-io/looties-skills --skill changelog-to-video
```

See [`SKILL.md`](./SKILL.md) for the full workflow.
