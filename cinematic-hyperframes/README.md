# cinematic-hyperframes

A Codex / Claude Code skill for producing cinematic, VFX-friendly Hyperframes and HTML-to-video product films.

Part of [looties-skills](https://github.com/looties-io/looties-skills) — open-source agent skills by [Looties](https://looties.io).

## What it does

Packages production guidance from a full motion-design iteration cycle:

- Composition rules for cinematic framing
- GSAP and typography transition design
- Responsive dual-orientation (16:9 / 9:16) layout
- Hyperframes catalog dependency management
- Rendering validation checklist

**Best for:** SaaS launch videos, ecommerce reels, app onboarding videos — especially converting website UI into motion design, or improving videos that feel too flat.

## Install

```bash
npx skills.sh install looties-io/looties-skills/cinematic-hyperframes
```

## Contents

```
cinematic-hyperframes/
├── SKILL.md          ← main workflow guide (agent entry point)
├── README.md         ← this file
├── agents/           ← sub-agent definitions for delegated tasks
└── references/       ← Hyperframes catalog dependencies + validation checklists
```

## Usage

Once installed, activate the skill in Claude Code or Codex with:

```
Use the cinematic-hyperframes skill to create a product video for [your product].
```

The agent loads `SKILL.md` as its workflow guide and references the catalog in `references/` for Hyperframes-specific dependencies.

## License

MIT — see [LICENSE](../../LICENSE).

---

Built by Looties · [looties.io](https://looties.io) · Forged in the French Alps during ranked queue.
