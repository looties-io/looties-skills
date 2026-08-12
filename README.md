# looties-skills

Agent skills published by [Looties](https://looties.io) — the marketplace where developers and tech enthusiasts can buy and sell conference swag, limited-edition merch, and developer gear from the events they love.

These are skills we actually use to build Looties. Each skill is a self-contained folder you can install into your Claude Code or Codex workflow.

## Skills

| Skill | Description |
|---|---|
| [a11y-audit](./a11y-audit/) | Evidence-based WCAG 2.1 AA audit (keyboard, focus, screen-reader semantics, contrast) plus a non-breaking fix pass — additive changes ship now, visible ones are quarantined with measured ratios for design sign-off |
| [changelog-to-video](./changelog-to-video/) | Turn a changelog into a feature-showcase video where every feature gets a real mock-up (asset waterfall), not a generic card |
| [cinematic-hyperframes](./cinematic-hyperframes/) | Cinematic, VFX-friendly Hyperframes motion design for HTML-to-video product films |
| [code-cleanup](./code-cleanup/) | Safe, behavior-preserving code cleanup for staged or recently changed files |
| [endpoint-surface-map](./endpoint-surface-map/) | Know who can actually call each endpoint: a manifest of caller, credential and authority, a CI gate that fails on undeclared routes, and a live check for deployed config drift |
| [google-ai-seo-fundamentals](./google-ai-seo-fundamentals/) | Google Search guidance for safe, people-first AI-assisted content |
| [google-ai-seo-optimization](./google-ai-seo-optimization/) | Google-specific SEO workflow for AI Overviews and AI Mode readiness |
| [ground-truth](./ground-truth/) | Confirm a finding against the running system before acting on it: is it happening, since when, how far it reaches, and why a scheduler that reports success proves nothing |
| [harness-testing](./harness-testing/) | Design harness tests that boot real code into a controlled, mocked environment and assert end-to-end |
| [impossible-by-design](./impossible-by-design/) | Turn a convention into a constraint so the wrong path stops being buildable, because the correct mechanism usually already existed and using it was optional |
| [legacy-code-review](./legacy-code-review/) | Review and test code nobody has read, without freezing its defects into your suite: never derive an assertion from the code under test |
| [website-ai-agent-readiness](./website-ai-agent-readiness/) | Website readiness for AI agents, answer engines, and machine-readable assets |

## Install

Via [skills.sh](https://skills.sh):

```bash
npx skills@latest add looties-io/looties-skills --skill a11y-audit
npx skills@latest add looties-io/looties-skills --skill changelog-to-video
npx skills@latest add looties-io/looties-skills --skill cinematic-hyperframes
npx skills@latest add looties-io/looties-skills --skill code-cleanup
npx skills@latest add looties-io/looties-skills --skill endpoint-surface-map
npx skills@latest add looties-io/looties-skills --skill google-ai-seo-fundamentals
npx skills@latest add looties-io/looties-skills --skill google-ai-seo-optimization
npx skills@latest add looties-io/looties-skills --skill ground-truth
npx skills@latest add looties-io/looties-skills --skill harness-testing
npx skills@latest add looties-io/looties-skills --skill impossible-by-design
npx skills@latest add looties-io/looties-skills --skill legacy-code-review
npx skills@latest add looties-io/looties-skills --skill website-ai-agent-readiness
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
