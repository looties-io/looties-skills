# looties-skills

Agent skills published by [Looties](https://looties.io) — the marketplace where developers and tech enthusiasts can buy and sell conference swag, limited-edition merch, and developer gear from the events they love.

These are skills we actually use to build Looties. Each skill is a self-contained folder you can install into your Claude Code or Codex workflow.

## Skills

| Skill | Description |
|---|---|
| [cinematic-hyperframes](./cinematic-hyperframes/) | Cinematic, VFX-friendly Hyperframes motion design for HTML-to-video product films |
| [code-cleanup](./code-cleanup/) | Safe, behavior-preserving code cleanup for staged or recently changed files |
| [google-ai-seo-fundamentals](./google-ai-seo-fundamentals/) | Google Search guidance for safe, people-first AI-assisted content |
| [google-ai-seo-optimization](./google-ai-seo-optimization/) | Google-specific SEO workflow for AI Overviews and AI Mode readiness |

## Install

Via [skills.sh](https://skills.sh):

```bash
npx skills add looties-io/looties-skills --skill cinematic-hyperframes
npx skills add looties-io/looties-skills --skill code-cleanup
npx skills add looties-io/looties-skills --skill google-ai-seo-fundamentals
npx skills add looties-io/looties-skills --skill google-ai-seo-optimization
```

Or clone the collection:

```bash
git clone https://github.com/looties-io/looties-skills.git
```

## Adding a skill

Each skill lives in its own subfolder at the root of this repo. The folder must contain at minimum a `SKILL.md` (the workflow guide the agent loads) and a `README.md`. See an existing skill for reference.

## About Looties

Looties is the marketplace where developer culture meets resale. Browse rare conference merch, archived launch gear, and developer collectibles.

→ [looties.io](https://looties.io) · [GitHub org](https://github.com/looties-io) · [Discord](https://discord.gg/A6UcsyCHCb)

## License

MIT
